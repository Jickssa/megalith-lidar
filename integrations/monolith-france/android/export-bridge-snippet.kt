// Fragment à fusionner dans le pont existant. Ne pas exposer ce pont à des pages distantes arbitraires.
@JavascriptInterface
fun saveOrShareFile(filename: String, mimeType: String, content: String) {
    runOnUiThread {
        val safeName = filename.replace(Regex("[^A-Za-z0-9._-]"), "_").take(120).ifBlank { "monolith-france-export.geojson" }
        val safeMime = when (mimeType.lowercase()) {
            "application/geo+json" -> "application/geo+json"
            "application/json" -> "application/json"
            "text/plain" -> "text/plain"
            else -> "application/octet-stream"
        }
        val exportDir = File(cacheDir, "monolith-france-exports").apply { mkdirs() }
        val output = File(exportDir, safeName)
        output.writeText(content, Charsets.UTF_8)
        val uri = FileProvider.getUriForFile(this@MainActivity, "$packageName.fileprovider", output)
        val send = Intent(Intent.ACTION_SEND).apply {
            type = safeMime
            putExtra(Intent.EXTRA_STREAM, uri)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        startActivity(Intent.createChooser(send, safeName))
    }
}
