$inputFile = "C:\Users\shange\.openclaw-autoclaw\workspace\linknest\backend\batch_dev.jsonl"
$lines = Get-Content $inputFile
$err = 0
for ($i = 0; $i -lt $lines.Count; $i++) {
    try {
        $lines[$i] | ConvertFrom-Json | Out-Null
    } catch {
        $preview = $lines[$i].Substring(0, [Math]::Min(80, $lines[$i].Length))
        Write-Host "Line $($i+1) FAIL: $preview"
        $err++
    }
}
Write-Host "Total: $($lines.Count) lines, $err errors"
