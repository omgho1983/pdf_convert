#!/bin/bash

# 更新系统包
echo "Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

# 安装必要的依赖
echo "Installing necessary dependencies..."
sudo apt-get install -y python3 python3-pip python3-venv git

# 创建项目目录
echo "Creating project directory..."
mkdir -p ~/pdf_convert
cd ~/pdf_convert

# 克隆项目文件（假设项目在Git仓库中）
# 如果不是从Git仓库克隆，请替换为适当的复制命令
echo "Cloning project files..."
git clone https://your-repository-url.git .

# 创建并激活虚拟环境
echo "Creating and activating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 安装Python依赖
echo "Installing Python dependencies..."
pip install -r requirements.txt

# 运行setup.py（如果需要）
echo "Running setup.py..."
python setup.py install

# 创建系统服务文件
echo "Creating system service file..."
sudo tee /etc/systemd/system/pdf_convert.service > /dev/null <<EOT
[Unit]
Description=PDF Convert Service
After=network.target

[Service]
User=$(whoami)
WorkingDirectory=/home/$(whoami)/pdf_convert
ExecStart=/home/$(whoami)/pdf_convert/venv/bin/python /home/$(whoami)/pdf_convert/sample.py
Restart=always

[Install]
WantedBy=multi-user.target
EOT

# 启用并启动服务
echo "Enabling and starting the service..."
sudo systemctl daemon-reload
sudo systemctl enable pdf_convert
sudo systemctl start pdf_convert

echo "Deployment completed successfully!"