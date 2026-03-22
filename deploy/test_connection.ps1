$serverIP = "172.31.3.199"
$sshKey = "C:\Users\zhanghw\.ssh\id_ed25519"
$user = "root"

Write-Host "Testing SSH connection to $serverIP ..." -ForegroundColor Green
Write-Host ""

$result = ssh -i $sshKey -o StrictHostKeyChecking=no -o ConnectTimeout=10 "$user@$serverIP" "echo 'SUCCESS' && hostname && pwd"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "SSH connection successful!" -ForegroundColor Green
    Write-Host $result
} else {
    Write-Host ""
    Write-Host "SSH connection failed" -ForegroundColor Red
}
