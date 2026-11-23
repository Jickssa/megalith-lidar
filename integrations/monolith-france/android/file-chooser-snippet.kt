// À fusionner dans le WebChromeClient existant ; ne pas installer un second WebChromeClient.
private var monolithFranceFileCallback: ValueCallback<Array<Uri>>? = null
@Suppress("DEPRECATION")
override fun onShowFileChooser(webView: WebView, filePathCallback: ValueCallback<Array<Uri>>, params: WebChromeClient.FileChooserParams): Boolean {
    monolithFranceFileCallback?.onReceiveValue(null)
    monolithFranceFileCallback = filePathCallback
    val intent = Intent(Intent.ACTION_GET_CONTENT).apply {
        addCategory(Intent.CATEGORY_OPENABLE)
        type = "*/*"
        putExtra(Intent.EXTRA_MIME_TYPES, arrayOf("application/geo+json", "application/json", "text/plain"))
    }
    return try { startActivityForResult(Intent.createChooser(intent, "Importer GeoJSON"), 4107); true }
    catch (_: ActivityNotFoundException) { monolithFranceFileCallback?.onReceiveValue(null); monolithFranceFileCallback = null; false }
}
// Dans onActivityResult, renvoyer l'URI sélectionnée au callback puis l'effacer.
