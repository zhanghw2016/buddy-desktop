# SSH 连接测试脚本
$serverIP = "172.31.3.199"
$sshKey = "C:\Users\zhanghw\.ssh\id_ed25519"
$user = "root"

Write-Host "测试 SSH 连接到 $serverIP ..." -ForegroundColor Green

# 测试连接
$result = ssh -i $sshKey -o StrictHostKeyChecking=no -o ConnectTimeout=10 "$user@$serverIP" "echo 'Connection successful' && hostname && pwd"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ SSH 连接成功！" -ForegroundColor Green
    Write-Host $result
} else {
    Write-Host "✗ SSH 连接失败" -ForegroundColor Red
    Write-Host "请检查："
    Write-Host "  1. 服务器是否启动"
    Write-Host "  2. SSH 密钥是否正确"
    Write-Host "  3. 网络是否通畅"
}
