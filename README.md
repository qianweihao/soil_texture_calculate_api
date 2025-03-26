# 土壤质地查询API

## 项目简介

这是一个基于SoilGrids数据集的土壤质地查询API，通过HTTP请求可以获取全球任意经纬度位置的土壤质地组成（粘土、砂粒、粉粒含量）及其百分比。该API提供了不同深度层（0-5cm、5-15cm、15-30cm、30-60cm）的土壤数据。

### 数据来源

本API使用的数据来源于[SoilGrids](https://soilgrids.org)，这是一个全球土壤信息系统，提供250m分辨率的全球土壤属性预测。

## 功能特点

- **简单易用**：通过HTTP请求获取特定经纬度的土壤质地数据
- **多层次数据**：提供不同深度层的土壤组成信息
- **完整组成分析**：返回粘土、砂粒、粉粒的原始含量及占比
- **Web界面**：提供简单的Web界面用于直接查询
- **高效处理**：使用并行查询和临时文件处理减少查询时间
- **跨域支持**：支持跨域请求，方便前端应用集成

## 安装指南

### 环境要求

- Python 3.7+
- 依赖包（详见requirements.txt）

### 安装步骤

1. 克隆或下载本仓库：
   ```bash
   git clone [仓库地址]
   cd soilgird250m-world
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 启动API服务（开发环境）：
   ```bash
   python soil_texture_web_api.py
   ```

## 使用方法

### Web界面使用

1. 启动服务后，在浏览器中访问 `http://localhost:5000/`
2. 在界面输入经度和纬度
3. 点击"查询"按钮
4. 查看返回的JSON格式结果

### API调用

#### 请求格式

```
GET /api/soil-texture?longitude={经度}&latitude={纬度}
```

#### 参数说明

- `longitude`: 经度值，范围 -180 到 180
- `latitude`: 纬度值，范围 -90 到 90

#### 示例请求

```
GET /api/soil-texture?longitude=115.0&latitude=30.5
```

#### 返回格式

```json
[
  {
    "depth": "0-5cm",
    "clay_content": 32.5,
    "sand_content": 45.2,
    "silt_content": 22.3,
    "total": 100.0,
    "clay_percent": 32.5,
    "sand_percent": 45.2,
    "silt_percent": 22.3
  },
  {
    "depth": "5-15cm",
    "clay_content": 33.1,
    "sand_content": 44.7,
    "silt_content": 22.2,
    "total": 100.0,
    "clay_percent": 33.1,
    "sand_percent": 44.7,
    "silt_percent": 22.2
  },
  // 更多深度层数据
]
```

## 部署指南

### 在本地服务器部署

#### 开发环境

```bash
python soil_texture_web_api.py
```

#### 生产环境（Linux/Mac）

```bash
# 安装gunicorn
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:5000 soil_texture_web_api:app
```

#### 生产环境（Windows）

```bash
# 安装waitress
pip install waitress

# 启动服务
waitress-serve --port=5000 soil_texture_web_api:app
```

### 在阿里云上部署

#### 1. 使用阿里云ECS（弹性计算服务）

1. **创建ECS实例**：
   - 登录阿里云控制台，选择ECS服务
   - 选择操作系统（推荐Ubuntu 20.04或CentOS 7）
   - 根据需求选择配置（2核4G内存即可满足一般需求）
   - 设置安全组，开放5000端口（或您计划使用的端口）

2. **服务器环境配置**：
   ```bash
   # 更新系统
   sudo apt update && sudo apt upgrade -y   # Ubuntu系统
   # 或
   sudo yum update -y   # CentOS系统
   
   # 安装Python和pip
   sudo apt install python3-pip python3-dev -y   # Ubuntu
   # 或
   sudo yum install python3-pip python3-devel -y   # CentOS
   
   # 安装git
   sudo apt install git -y   # Ubuntu
   # 或
   sudo yum install git -y   # CentOS
   ```

3. **部署应用**：
   ```bash
   # 下载代码
   git clone [仓库地址]
   # 或上传代码到服务器
   
   # 进入项目目录
   cd soilgird250m-world
   
   # 安装依赖
   pip3 install -r requirements.txt
   
   # 使用gunicorn启动服务
   gunicorn -w 4 -b 0.0.0.0:5000 soil_texture_web_api:app --daemon
   ```

4. **设置开机自启动**：
   ```bash
   # 创建systemd服务
   sudo nano /etc/systemd/system/soil-api.service
   
   # 添加以下内容
   [Unit]
   Description=Soil Texture API Service
   After=network.target
   
   [Service]
   User=your_username
   WorkingDirectory=/path/to/soilgird250m-world
   ExecStart=/usr/local/bin/gunicorn -w 4 -b 0.0.0.0:5000 soil_texture_web_api:app
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   
   # 启用并启动服务
   sudo systemctl enable soil-api
   sudo systemctl start soil-api
   ```

5. **使用Nginx作为反向代理**（推荐）：
   ```bash
   # 安装Nginx
   sudo apt install nginx -y   # Ubuntu
   # 或
   sudo yum install nginx -y   # CentOS
   
   # 配置Nginx
   sudo nano /etc/nginx/sites-available/soil-api   # Ubuntu
   # 或
   sudo nano /etc/nginx/conf.d/soil-api.conf   # CentOS
   
   # 添加以下内容
   server {
       listen 80;
       server_name your_domain_or_ip;
   
       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   
   # 在Ubuntu上启用站点
   sudo ln -s /etc/nginx/sites-available/soil-api /etc/nginx/sites-enabled/
   
   # 重启Nginx
   sudo systemctl restart nginx
   ```

#### 2. 使用阿里云容器服务（ACK）

1. **创建Dockerfile**：
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   EXPOSE 5000
   
   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "soil_texture_web_api:app"]
   ```

2. **构建并推送Docker镜像**：
   ```bash
   # 登录阿里云容器镜像服务
   sudo docker login --username=your_username registry.cn-hangzhou.aliyuncs.com
   
   # 构建镜像
   sudo docker build -t registry.cn-hangzhou.aliyuncs.com/your_namespace/soil-api:v1 .
   
   # 推送镜像
   sudo docker push registry.cn-hangzhou.aliyuncs.com/your_namespace/soil-api:v1
   ```

3. **在阿里云ACK中部署**：
   - 创建Kubernetes集群
   - 使用控制台或kubectl部署镜像
   - 创建服务暴露API

## 性能优化

- **缓存结果**：频繁查询的坐标结果可以缓存
- **调整并行度**：根据服务器性能调整`max_workers`参数
- **减小查询范围**：可以进一步减小查询区域范围减少数据量
- **使用CDN**：如果服务面向全球用户，可以使用CDN加速

## 安全建议

- **添加认证**：考虑添加API密钥或其他认证机制
- **速率限制**：限制API调用频率防止滥用
- **HTTPS加密**：使用SSL证书确保数据传输安全
- **输入验证**：确保经纬度值在有效范围内

## 常见问题

1. **API速度慢**：SoilGrids数据查询本身需要一定时间，可以通过缓存机制优化
2. **数据不准确**：数据来源于SoilGrids，精度有限，具体使用时需要结合实际情况
3. **服务崩溃**：检查是否有足够的服务器资源，考虑增加错误处理和自动重启机制

## 许可证

[添加您的许可证信息]

## 联系方式

[添加您的联系方式] 