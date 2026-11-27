package app.monolith.integration

import android.annotation.SuppressLint
import android.webkit.WebSettings
import android.webkit.WebView

/** Helpers à fusionner dans l'Activity hôte ; ne crée pas une seconde Activity. */
object MonolithFranceWebView {
    const val START_URL = "https://appassets.androidplatform.net/assets/web/france/web/index.html"
    @SuppressLint("SetJavaScriptEnabled")
    fun configureSettings(webView: WebView) {
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            setGeolocationEnabled(true)
            allowFileAccess = false
            allowContentAccess = false
            mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
            cacheMode = WebSettings.LOAD_DEFAULT
            builtInZoomControls = false
            displayZoomControls = false
        }
    }
}
