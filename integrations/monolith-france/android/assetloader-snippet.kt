// Vérifier que le WebViewAssetLoader existant sert les assets sous /assets/.
val assetLoader = WebViewAssetLoader.Builder()
    .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
    .build()
// Le WebView doit charger :
// https://appassets.androidplatform.net/assets/web/france/web/index.html
