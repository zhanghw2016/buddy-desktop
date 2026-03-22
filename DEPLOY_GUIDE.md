# 部署到生产环境指南

**目标服务器**: 172.31.3.199
**数据库**: PostgreSQL (buddy_desktop)
**Web 服务器**: Nginx

---

## 📋 部署步骤

### 方式 1: 自动部署（推荐）

```bash
# 1. 测试 SSH 连接
powershell -ExecutionPolicy Bypass -File deploy/connect.ps1

# 2. 执行部署脚本
ssh root@172.31.3.199 "bash -s" < deploy/deploy.sh
```

### 方式 2: 手动部署

#### Step 1: 连接到服务器

```bash
ssh -i C:\Users\zhanghw\.ssh\id_ed25519 root@172.31.3.199
```

#### Step 2: 克隆代码

```bash
cd /opt
git clone https://github.com/zhanghw2016/buddy-desktop.git
cd buddy-desktop
```

#### Step 3: 安装依赖

```bash
# Python 依赖
pip3 install -r requirements.txt

# 前端依赖
cd frontend
npm install
npm run build
cd ..
```

#### Step 4: 配置环境变量

```bash
cat > .env <<EOF
DATABASE_URL=postgresql://buddy_desktop:zhu88jie@172.31.3.199:5432/buddy_desktop
APP_NAME=Buddy Dashboard
DEBUG=False
EOF
```

#### Step 5: 初始化数据库

```bash
python3 buddy/scripts/init_simple.py
```

#### Step 6: 配置 Systemd 服务

```bash
# 创建服务文件
cat > /etc/systemd/system/buddy-dashboard.service <<EOF
[Unit]
Description=Buddy Dashboard API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/buddy-desktop
Environment="DATABASE_URL=postgresql://buddy_desktop:zhu88jie@172.31.3.199:5432/buddy_desktop"
ExecStart=/usr/bin/python3 -m buddy.main
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
systemctl daemon-reload
systemctl enable buddy-dashboard
systemctl start buddy-dashboard
systemctl status buddy-dashboard
```

#### Step 7: 配置 Nginx

```bash
# 复制 Nginx 配置
cp nginx.conf /etc/nginx/sites-available/buddy-dashboard
ln -s /etc/nginx/sites-available/buddy-dashboard /etc/nginx/sites-enabled/

# 部署前端
mkdir -p /var/www/buddy-frontend
cp -r frontend/dist/* /var/www/buddy-frontend/

# 测试并重载 Nginx
nginx -t
systemctl reload nginx
```

---

## 🔧 配置文件

### Docker (可选)

```bash
# 使用 Docker 部署
docker-compose up -d
```

### Nginx 配置

已包含在 `nginx.conf` 文件中：
- 前端静态文件服务
- API 反向代理
- WebSocket 支持
- 缓存优化

---

## ✅ 验证部署

### 1. 检查服务状态

```bash
systemctl status buddy-dashboard
```

### 2. 检查端口

```bash
netstat -tlnp | grep 8001
netstat -tlnp | grep 80
```

### 3. 测试访问

```bash
# 前端界面
curl http://172.31.3.199/

# API 文档
curl http://172.31.3.199/docs

# API 端点
curl http://172.31.3.199/api/agents
```

---

## 🌐 访问地址

部署完成后，通过以下地址访问：

- **前端界面**: http://172.31.3.199
- **API 文档**: http://172.31.3.199/docs
- **ReDoc**: http://172.31.3.199/redoc

---

## 🔍 故障排查

### 服务无法启动

```bash
# 查看日志
journalctl -u buddy-dashboard -f

# 检查配置
python3 -c "from buddy.core.database import engine; print(engine.url)"
```

### 数据库连接失败

```bash
# 测试数据库连接
psql -h 172.31.3.199 -U buddy_desktop -d buddy_desktop

# 检查环境变量
echo $DATABASE_URL
```

### Nginx 错误

```bash
# 查看 Nginx 日志
tail -f /var/log/nginx/error.log

# 测试配置
nginx -t
```

---

## 📊 系统要求

- **操作系统**: Ubuntu 20.04+
- **Python**: 3.12+
- **Node.js**: 18+
- **PostgreSQL**: 15+
- **Nginx**: 1.18+

---

## 🚀 快速命令

```bash
# 重启服务
systemctl restart buddy-dashboard

# 查看日志
journalctl -u buddy-dashboard -f

# 更新代码
cd /opt/buddy-desktop && git pull && systemctl restart buddy-dashboard

# 重新构建前端
cd frontend && npm run build && cp -r dist/* /var/www/buddy-frontend/
```

---

## 📝 注意事项

1. **数据库**: 使用现有的 PostgreSQL (buddy_desktop)
2. **端口**: 
   - 前端: 80
   - API: 8001
3. **防火墙**: 确保 80 和 8001 端口开放
4. **SELinux**: 如果启用，可能需要配置权限

---

*部署脚本已准备好，可以开始执行！*
