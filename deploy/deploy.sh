#!/bin/bash

# Buddy Dashboard 部署脚本
# 部署到 172.31.3.199

set -e

SERVER_IP="172.31.3.199"
SERVER_USER="root"
DEPLOY_DIR="/opt/buddy-dashboard"
GIT_REPO="https://github.com/zhanghw2016/buddy-desktop.git"

echo "=================================================="
echo "Buddy Dashboard 部署脚本"
echo "=================================================="
echo ""

# 1. 克隆代码
echo "[1/6] 克隆代码..."
if [ ! -d "$DEPLOY_DIR" ]; then
    git clone $GIT_REPO $DEPLOY_DIR
else
    cd $DEPLOY_DIR
    git pull
fi

# 2. 安装 Python 依赖
echo "[2/6] 安装 Python 依赖..."
cd $DEPLOY_DIR
pip3 install -r requirements.txt

# 3. 配置环境变量
echo "[3/6] 配置环境变量..."
cat > .env <<EOF
DATABASE_URL=postgresql://buddy_desktop:zhu88jie@172.31.3.199:5432/buddy_desktop
APP_NAME=Buddy Dashboard
APP_VERSION=1.0.0
DEBUG=False
EOF

# 4. 初始化数据库（如果需要）
echo "[4/6] 初始化数据库..."
python3 buddy/scripts/init_simple.py

# 5. 构建前端
echo "[5/6] 构建前端..."
cd frontend
npm install
npm run build
mkdir -p /var/www/buddy-frontend
cp -r dist/* /var/www/buddy-frontend/

# 6. 配置 Systemd 服务
echo "[6/6] 配置 Systemd 服务..."
cat > /etc/systemd/system/buddy-dashboard.service <<EOF
[Unit]
Description=Buddy Dashboard API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$DEPLOY_DIR
Environment="DATABASE_URL=postgresql://buddy_desktop:zhu88jie@172.31.3.199:5432/buddy_desktop"
ExecStart=/usr/bin/python3 -m buddy.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
systemctl daemon-reload
systemctl enable buddy-dashboard
systemctl restart buddy-dashboard

# 配置 Nginx
echo "配置 Nginx..."
cp $DEPLOY_DIR/nginx.conf /etc/nginx/sites-available/buddy-dashboard
ln -sf /etc/nginx/sites-available/buddy-dashboard /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

echo ""
echo "=================================================="
echo "✓ 部署完成！"
echo "=================================================="
echo ""
echo "访问地址:"
echo "  - 前端界面: http://$SERVER_IP"
echo "  - API 文档: http://$SERVER_IP/docs"
echo "  - API ReDoc: http://$SERVER_IP/redoc"
echo ""
echo "服务状态:"
echo "  systemctl status buddy-dashboard"
echo ""
