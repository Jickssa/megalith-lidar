package uk.megalith.lidar

import android.Manifest
import android.annotation.SuppressLint
import android.app.Activity
import android.content.ActivityNotFoundException
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.view.ViewGroup
import android.view.WindowInsets
import android.webkit.GeolocationPermissions
import android.webkit.JavascriptInterface
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.FrameLayout
import android.widget.Toast
import androidx.core.content.FileProvider
import androidx.webkit.WebViewAssetLoader
import java.io.ByteArrayInputStream
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL

class MainActivity : Activity() {

    private lateinit var rootLayout: FrameLayout
    private lateinit var webView: WebView
    private var pendingGeoOrigin: String? = null
    private var pendingGeoCallback: GeolocationPermissions.Callback? = null
    private var fileUploadCallback: ValueCallback<Array<Uri>>? = null
    @Volatile private var activityDestroyed = false
    private val diagnosticCacheLock = Any()

    private fun showToastIfActive(message: String, duration: Int = Toast.LENGTH_SHORT) {
        if (activityDestroyed) return
        runOnUiThread {
            if (!activityDestroyed) {
                Toast.makeText(this@MainActivity, message, duration).show()
            }
        }
    }
    inner class AndroidBridge {
        @JavascriptInterface
        fun saveOrShareFile(filename: String, mimeType: String, content: String) {
            if (activityDestroyed) return
            if (content.length > MAX_EXPORT_BYTES) {
                showToastIfActive("Export refused: file exceeds 25 MiB.", Toast.LENGTH_LONG)
                return
            }
            val bytes = content.toByteArray(Charsets.UTF_8)
            if (bytes.size > MAX_EXPORT_BYTES) {
                showToastIfActive("Export refused: file exceeds 25 MiB.", Toast.LENGTH_LONG)
                return
            }
            val safeMime = when (mimeType.lowercase()) {
                "application/geo+json", "application/json", "text/plain",
                "application/gpx+xml", "application/xml" -> mimeType.lowercase()
                else -> "application/octet-stream"
            }
            val safeName = filename.replace(Regex("[^A-Za-z0-9._-]"), "_")
                .trim('.', '_')
                .ifEmpty { "megalith_export.txt" }
                .take(120)
            val suffix = safeName.substringAfterLast('.', "")
                .takeIf { it.matches(Regex("[A-Za-z0-9]{1,10}")) }
                ?.let { ".$it" } ?: ".txt"

            // File I/O stays off the UI thread. A completed export is discarded if
            // the Activity is destroyed before its UI hand-off can run.
            Thread {
                var temporaryFile: File? = null
                try {
                    val exportsDir = File(cacheDir, "exports").apply { mkdirs() }
                    val outFile = File.createTempFile("monolith-", suffix, exportsDir)
                    temporaryFile = outFile
                    outFile.writeBytes(bytes)
                    runOnUiThread {
                        if (activityDestroyed) {
                            outFile.delete()
                            return@runOnUiThread
                        }
                        try {
                            shareExportedFile(outFile, safeMime)
                        } catch (e: Exception) {
                            outFile.delete()
                            showToastIfActive("Export failed: ${e.message}")
                        }
                    }
                } catch (e: Exception) {
                    temporaryFile?.delete()
                    showToastIfActive("Export failed: ${e.message}")
                }
            }.start()
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        window.statusBarColor = Color.parseColor("#1F2E28")
        window.navigationBarColor = Color.parseColor("#1F2E28")

        rootLayout = FrameLayout(this).apply {
            setBackgroundColor(Color.parseColor("#1F2E28"))
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            rootLayout.setOnApplyWindowInsetsListener { view, insets ->
                val bars = insets.getInsets(
                    WindowInsets.Type.systemBars() or WindowInsets.Type.displayCutout()
                )
                view.setPadding(bars.left, bars.top, bars.right, bars.bottom)
                insets
            }
        }

        webView = WebView(this).apply {
            setBackgroundColor(Color.parseColor("#F2ECE1"))
            layoutParams = FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
        }
        rootLayout.addView(webView)
        setContentView(rootLayout)

        val assetLoader = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
            .build()

        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            setGeolocationEnabled(true)
            allowFileAccess = false
            allowContentAccess = false
            mediaPlaybackRequiresUserGesture = false
            cacheMode = WebSettings.LOAD_DEFAULT
            builtInZoomControls = false
            displayZoomControls = false
        }

        webView.addJavascriptInterface(AndroidBridge(), "MegalithAndroid")

        webView.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(
                view: WebView,
                request: WebResourceRequest
            ): WebResourceResponse? {
                val url = request.url
                val path = url.path ?: ""
                if (url.host == APP_HOST && path.startsWith("/assets/web/docs/diagnostics/")) {
                    val fileName = path.removePrefix("/assets/web/docs/diagnostics/")
                    return serveDiagnosticPng(fileName)
                }
                return assetLoader.shouldInterceptRequest(url)
            }

            override fun shouldOverrideUrlLoading(
                view: WebView,
                request: WebResourceRequest
            ): Boolean {
                val uri = request.url ?: return false
                val scheme = uri.scheme?.lowercase() ?: ""
                if (scheme == "geo") {
                    openExternalUri(uri)
                    return true
                }
                if (
                    scheme == "https" &&
                    uri.host == APP_HOST &&
                    uri.userInfo == null &&
                    (uri.port == -1 || uri.port == 443)
                ) {
                    val path = uri.path ?: ""
                    if (isDownloadableAssetPath(path)) {
                        shareBundledAsset(path.removePrefix("/assets/"))
                        return true
                    }
                    return false
                }
                if (scheme == "http" || scheme == "https") {
                    openExternalUri(uri)
                    return true
                }
                // Block intent:, file:, content: and unknown custom schemes.
                return true
            }
        }

        webView.webChromeClient = object : WebChromeClient() {
            override fun onGeolocationPermissionsShowPrompt(
                origin: String,
                callback: GeolocationPermissions.Callback
            ) {
                if (hasLocationPermission()) {
                    callback.invoke(origin, true, false)
                } else {
                    pendingGeoOrigin = origin
                    pendingGeoCallback = callback
                    requestPermissions(
                        arrayOf(
                            Manifest.permission.ACCESS_FINE_LOCATION,
                            Manifest.permission.ACCESS_COARSE_LOCATION
                        ),
                        REQ_LOCATION_PERMISSION
                    )
                }
            }

            override fun onShowFileChooser(
                webView: WebView,
                filePathCallback: ValueCallback<Array<Uri>>,
                fileChooserParams: FileChooserParams
            ): Boolean {
                fileUploadCallback?.onReceiveValue(null)
                fileUploadCallback = filePathCallback
                val requestedTypes = fileChooserParams.acceptTypes
                    .flatMap { it.split(",") }
                    .map { it.trim().lowercase() }
                    .flatMap { type ->
                        when (type) {
                            ".json" -> listOf("application/json")
                            ".geojson" -> listOf("application/geo+json", "application/json")
                            "application/json", "application/geo+json", "text/json" -> listOf(type)
                            else -> emptyList()
                        }
                    }
                    .distinct()
                    .ifEmpty { listOf("application/json", "application/geo+json", "text/plain") }
                val intent = Intent(Intent.ACTION_GET_CONTENT).apply {
                    addCategory(Intent.CATEGORY_OPENABLE)
                    type = if (requestedTypes.size == 1) requestedTypes.first() else "*/*"
                    if (requestedTypes.size > 1) {
                        putExtra(Intent.EXTRA_MIME_TYPES, requestedTypes.toTypedArray())
                    }
                }
                return try {
                    startActivityForResult(
                        Intent.createChooser(intent, "Select Survey Notes JSON"),
                        REQ_FILE_CHOOSER
                    )
                    true
                } catch (_: ActivityNotFoundException) {
                    fileUploadCallback?.onReceiveValue(null)
                    fileUploadCallback = null
                    false
                }
            }
        }

        webView.setDownloadListener { url, _, _, mimeType, _ ->
            val parsed = Uri.parse(url)
            if (parsed.host == APP_HOST && parsed.path != null) {
                shareBundledAsset(parsed.path!!.removePrefix("/assets/"), mimeType)
            } else if (parsed.scheme == "http" || parsed.scheme == "https") {
                openExternalUri(parsed)
            }
        }

        if (savedInstanceState == null) {
            webView.loadUrl(START_URL)
        } else {
            webView.restoreState(savedInstanceState)
        }
    }

    private fun isDownloadableAssetPath(path: String): Boolean {
        val low = path.lowercase()
        return low.endsWith(".osf") ||
            low.endsWith(".gpx") ||
            low.endsWith(".osm") ||
            low.endsWith("candidates.geojson") ||
            low.endsWith("maproulette_os1888_antiquities.geojson") ||
            low.endsWith("survey_summary.json")
    }

    private fun shareBundledAsset(assetRelPath: String, overrideMime: String? = null) {
        try {
            val fileName = assetRelPath.substringAfterLast('/')
            val exportsDir = File(cacheDir, "exports").apply { mkdirs() }
            val outFile = File(exportsDir, fileName)
            assets.open(assetRelPath).use { input ->
                FileOutputStream(outFile).use { output ->
                    input.copyTo(output)
                }
            }
            val mime = when {
                fileName.endsWith(".osf", true) -> "application/octet-stream"
                fileName.endsWith(".gpx", true) -> "application/gpx+xml"
                fileName.endsWith(".geojson", true) -> "application/geo+json"
                fileName.endsWith(".json", true) -> "application/json"
                fileName.endsWith(".osm", true) -> "application/xml"
                !overrideMime.isNullOrBlank() -> overrideMime
                else -> "application/octet-stream"
            }
            shareExportedFile(outFile, mime)
        } catch (e: Exception) {
            Toast.makeText(this, "Unable to export file: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }

    private fun shareExportedFile(file: File, mimeType: String) {
        val uri = FileProvider.getUriForFile(this, "$packageName.fileprovider", file)
        val sendIntent = Intent(Intent.ACTION_SEND).apply {
            type = mimeType
            putExtra(Intent.EXTRA_STREAM, uri)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        val chooser = Intent.createChooser(sendIntent, file.name).apply {
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        startActivity(chooser)
    }

    private fun serveDiagnosticPng(rawName: String): WebResourceResponse {
        val safeName = rawName.replace(Regex("[^A-Za-z0-9._-]"), "")
        if (safeName.isEmpty() || safeName != rawName || !safeName.endsWith(".png", ignoreCase = true)) {
            return emptyResponse(404, "Not Found")
        }

        return synchronized(diagnosticCacheLock) {
            val diagDir = File(cacheDir, "diagnostics").apply { mkdirs() }
            val cachedFile = File(diagDir, safeName)
            if (!isValidDiagnosticPng(cachedFile)) {
                cachedFile.delete()
                downloadDiagnosticPng(diagDir, cachedFile, safeName)
            } else {
                cachedFile.setLastModified(System.currentTimeMillis())
            }

            if (!isValidDiagnosticPng(cachedFile)) {
                return@synchronized emptyResponse(404, "Not Found")
            }

            trimDiagnosticCache(diagDir, cachedFile)
            WebResourceResponse(
                "image/png",
                null,
                200,
                "OK",
                mapOf(
                    "Access-Control-Allow-Origin" to "*",
                    "Cache-Control" to "public, max-age=86400"
                ),
                FileInputStream(cachedFile)
            )
        }
    }

    private fun isValidDiagnosticPng(file: File): Boolean {
        if (!file.isFile || file.length() < PNG_SIGNATURE.size ||
            file.length() > MAX_DIAGNOSTIC_FILE_BYTES
        ) {
            return false
        }
        return try {
            FileInputStream(file).use { input ->
                val signature = ByteArray(PNG_SIGNATURE.size)
                var offset = 0
                while (offset < signature.size) {
                    val count = input.read(signature, offset, signature.size - offset)
                    if (count < 0) return false
                    offset += count
                }
                signature.contentEquals(PNG_SIGNATURE)
            }
        } catch (_: Exception) {
            false
        }
    }

    private fun downloadDiagnosticPng(directory: File, target: File, fileName: String): Boolean {
        val connection = try {
            (URL("$REMOTE_DIAG_BASE$fileName").openConnection() as HttpURLConnection).apply {
                connectTimeout = 8000
                readTimeout = 12000
                requestMethod = "GET"
                instanceFollowRedirects = false
                setRequestProperty("Accept", "image/png")
            }
        } catch (_: Exception) {
            return false
        }

        var temporaryFile: File? = null
        try {
            if (connection.responseCode != 200) return false
            val contentType = connection.contentType
                ?.substringBefore(";")
                ?.trim()
                ?.lowercase()
            if (contentType != "image/png") return false

            val declaredLength = connection.getHeaderField("Content-Length")?.toLongOrNull() ?: -1L
            if (declaredLength > MAX_DIAGNOSTIC_FILE_BYTES ||
                (declaredLength >= 0L && declaredLength < PNG_SIGNATURE.size)
            ) {
                return false
            }

            val temp = File.createTempFile("monolith-diag-", ".tmp", directory)
            temporaryFile = temp
            var totalBytes = 0L
            connection.inputStream.use { input ->
                FileOutputStream(temp).use { output ->
                    val buffer = ByteArray(8192)
                    while (true) {
                        val count = input.read(buffer)
                        if (count < 0) break
                        totalBytes += count.toLong()
                        if (totalBytes > MAX_DIAGNOSTIC_FILE_BYTES) {
                            throw IOException("Diagnostic image exceeds the 8 MiB limit")
                        }
                        output.write(buffer, 0, count)
                    }
                }
            }

            if (!isValidDiagnosticPng(temp)) return false
            if (target.exists() && !target.delete()) return false
            val renamed = temp.renameTo(target)
            if (renamed) temporaryFile = null
            return renamed
        } catch (_: Exception) {
            // Offline, malformed response or oversized file: do not cache it.
            return false
        } finally {
            temporaryFile?.delete()
            connection.disconnect()
        }
    }

    private fun trimDiagnosticCache(directory: File, keep: File) {
        val now = System.currentTimeMillis()
        val files = directory.listFiles()
            ?.filter { it.isFile && it.extension.equals("png", ignoreCase = true) }
            ?: emptyList()
        val keepPath = try { keep.canonicalPath } catch (_: Exception) { keep.absolutePath }
        var totalBytes = files.sumOf { it.length() }
        var fileCount = files.size

        for (file in files.sortedBy { it.lastModified() }) {
            val path = try { file.canonicalPath } catch (_: Exception) { file.absolutePath }
            val isCurrent = path == keepPath
            val expired = !isCurrent && now - file.lastModified() > MAX_DIAGNOSTIC_CACHE_AGE_MS
            val overLimit = fileCount > MAX_DIAGNOSTIC_CACHE_FILES ||
                totalBytes > MAX_DIAGNOSTIC_CACHE_BYTES
            if (expired || (overLimit && !isCurrent)) {
                val size = file.length()
                if (file.delete()) {
                    fileCount--
                    totalBytes -= size
                }
            }
        }

        directory.listFiles()
            ?.filter { it.isFile && it.name.endsWith(".tmp", ignoreCase = true) }
            ?.forEach { it.delete() }
    }

    private fun emptyResponse(code: Int, reason: String): WebResourceResponse {
        return WebResourceResponse(
            "text/plain",
            "utf-8",
            code,
            reason,
            mapOf("Access-Control-Allow-Origin" to "*"),
            ByteArrayInputStream(ByteArray(0))
        )
    }

    private fun openExternalUri(uri: Uri) {
        try {
            val intent = Intent(Intent.ACTION_VIEW, uri).apply {
                addCategory(Intent.CATEGORY_BROWSABLE)
            }
            startActivity(intent)
        } catch (_: ActivityNotFoundException) {
            Toast.makeText(this, "No app installed to open ${uri.scheme} link", Toast.LENGTH_SHORT)
                .show()
        }
    }

    private fun hasLocationPermission(): Boolean {
        return checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) ==
            PackageManager.PERMISSION_GRANTED ||
            checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) ==
            PackageManager.PERMISSION_GRANTED
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (activityDestroyed) {
            pendingGeoOrigin = null
            pendingGeoCallback = null
            return
        }
        if (requestCode == REQ_LOCATION_PERMISSION) {
            val granted = grantResults.any { it == PackageManager.PERMISSION_GRANTED }
            val origin = pendingGeoOrigin
            val cb = pendingGeoCallback
            pendingGeoOrigin = null
            pendingGeoCallback = null
            if (origin != null && cb != null) {
                cb.invoke(origin, granted, false)
            }
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (activityDestroyed) {
            fileUploadCallback?.let { callback -> runCatching { callback.onReceiveValue(null) } }
            fileUploadCallback = null
            return
        }
        if (requestCode == REQ_FILE_CHOOSER) {
            val cb = fileUploadCallback ?: return
            fileUploadCallback = null
            if (resultCode == RESULT_OK && data?.data != null) {
                cb.onReceiveValue(arrayOf(data.data!!))
            } else {
                cb.onReceiveValue(null)
            }
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        webView.saveState(outState)
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (activityDestroyed || !::webView.isInitialized) {
            super.onBackPressed()
            return
        }
        webView.evaluateJavascript(
            "(function(){var d=document.getElementById('osmandQrDialog');if(d&&d.open){d.close();return true;}return false;})()"
        ) { res ->
            if (res == "true") {
                return@evaluateJavascript
            }
            if (webView.canGoBack()) {
                webView.goBack()
            } else {
                @Suppress("DEPRECATION")
                super.onBackPressed()
            }
        }
    }


    override fun onDestroy() {
        activityDestroyed = true

        val geoOrigin = pendingGeoOrigin
        val geoCallback = pendingGeoCallback
        pendingGeoOrigin = null
        pendingGeoCallback = null
        if (geoOrigin != null && geoCallback != null) {
            runCatching { geoCallback.invoke(geoOrigin, false, false) }
        }

        fileUploadCallback?.let { callback -> runCatching { callback.onReceiveValue(null) } }
        fileUploadCallback = null

        if (::webView.isInitialized) {
            runCatching { webView.stopLoading() }
            runCatching { webView.webChromeClient = null }
            runCatching { webView.setDownloadListener(null) }
            runCatching { webView.removeJavascriptInterface("MegalithAndroid") }
            runCatching { (webView.parent as? ViewGroup)?.removeView(webView) }
            runCatching { webView.removeAllViews() }
            runCatching { webView.destroy() }
        }
        if (::rootLayout.isInitialized) {
            runCatching { rootLayout.removeAllViews() }
        }
        super.onDestroy()
    }

    companion object {
        private const val APP_HOST = "appassets.androidplatform.net"
        private const val START_URL =
            "https://appassets.androidplatform.net/assets/web/atlas-home.html"
        private const val REMOTE_DIAG_BASE =
            "https://raw.githubusercontent.com/GlassOnTin/megalith-lidar/main/docs/diagnostics/"
        private const val REQ_LOCATION_PERMISSION = 1001
        private const val REQ_FILE_CHOOSER = 1002
        private const val MAX_EXPORT_BYTES = 25 * 1024 * 1024
        private const val MAX_DIAGNOSTIC_FILE_BYTES = 8L * 1024 * 1024
        private const val MAX_DIAGNOSTIC_CACHE_BYTES = 64L * 1024 * 1024
        private const val MAX_DIAGNOSTIC_CACHE_FILES = 24
        private const val MAX_DIAGNOSTIC_CACHE_AGE_MS = 30L * 24 * 60 * 60 * 1000
        private val PNG_SIGNATURE = byteArrayOf(
            0x89.toByte(), 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A
        )
    }
}
