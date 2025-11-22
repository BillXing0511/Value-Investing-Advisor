# 部署指南

## Web 应用部署

本项目提供了基于 Streamlit 的 Web 界面，可以通过多种方式部署。

### 方式 1: 本地运行

最简单的方式，适合个人使用。

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动应用
streamlit run app.py

# 3. 打开浏览器访问
# 默认地址: http://localhost:8501
```

**优点:**
- 简单快速
- 完全本地控制
- 无需服务器

**缺点:**
- 只能本地访问
- 关闭终端后停止

---

### 方式 2: Streamlit Cloud（推荐）

免费的云端部署方案，适合个人和小团队。

#### 步骤：

1. **将代码推送到 GitHub**
   ```bash
   git push origin main
   ```

2. **访问 Streamlit Cloud**
   - 访问 https://streamlit.io/cloud
   - 使用 GitHub 账号登录

3. **创建新应用**
   - 点击 "New app"
   - 选择您的仓库
   - 主文件路径: `app.py`
   - 点击 "Deploy"

4. **等待部署完成**
   - 首次部署约需 2-5 分钟
   - 完成后会得到公开访问链接
   - 例如: `https://your-app.streamlit.app`

**优点:**
- 完全免费
- 自动部署（推送代码后自动更新）
- 提供公开访问链接
- 无需服务器管理

**缺点:**
- 资源限制（1GB RAM）
- 仅适合小规模使用

**配置文件:**
- `.streamlit/config.toml` - 已包含在项目中
- `requirements.txt` - 确保所有依赖都已列出

---

### 方式 3: Docker 部署

使用 Docker 容器化部署，适合生产环境。

#### 创建 Dockerfile

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8501

# 启动命令
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### 构建和运行

```bash
# 构建镜像
docker build -t value-investing-advisor .

# 运行容器
docker run -p 8501:8501 value-investing-advisor

# 访问 http://localhost:8501
```

#### 使用 Docker Compose

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./config:/app/config
      - ./logs:/app/logs
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
```

运行:
```bash
docker-compose up -d
```

**优点:**
- 环境一致性
- 易于扩展
- 便于部署到云平台

---

### 方式 4: 云服务器部署

部署到 VPS 或云服务器（如 AWS EC2, Google Cloud, Azure）。

#### 在 Ubuntu 服务器上部署

```bash
# 1. 连接到服务器
ssh user@your-server-ip

# 2. 安装 Python 和依赖
sudo apt update
sudo apt install python3 python3-pip git -y

# 3. 克隆项目
git clone https://github.com/yourusername/value-investing-advisor.git
cd value-investing-advisor

# 4. 安装依赖
pip3 install -r requirements.txt

# 5. 使用 screen 或 tmux 保持运行
screen -S via

# 6. 启动应用
streamlit run app.py --server.port=8501 --server.address=0.0.0.0

# 7. 按 Ctrl+A+D 退出 screen（应用继续运行）

# 8. 配置防火墙
sudo ufw allow 8501
```

#### 使用 Nginx 反向代理

```nginx
# /etc/nginx/sites-available/via
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置:
```bash
sudo ln -s /etc/nginx/sites-available/via /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 使用 systemd 服务

创建服务文件 `/etc/systemd/system/via.service`:

```ini
[Unit]
Description=Value Investing Advisor Web App
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/value-investing-advisor
ExecStart=/usr/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl daemon-reload
sudo systemctl enable via
sudo systemctl start via
sudo systemctl status via
```

---

### 方式 5: Heroku 部署

免费的 PaaS 平台（有使用限制）。

#### 步骤:

1. **创建必要文件**

`Procfile`:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

`runtime.txt`:
```
python-3.10.12
```

2. **部署到 Heroku**

```bash
# 安装 Heroku CLI
# 访问 https://devcenter.heroku.com/articles/heroku-cli

# 登录
heroku login

# 创建应用
heroku create your-app-name

# 推送代码
git push heroku main

# 打开应用
heroku open
```

---

## 性能优化

### 1. 缓存配置

在 `app.py` 中使用 Streamlit 缓存:

```python
import streamlit as st

@st.cache_data(ttl=3600)  # 缓存1小时
def get_stock_data(symbol):
    # 获取数据的代码
    pass
```

### 2. 数据库替代 JSON

对于大量数据，考虑使用 SQLite 或 PostgreSQL 替代 JSON 文件。

### 3. 异步加载

使用后台任务处理耗时操作。

---

## 安全建议

### 1. 环境变量

不要在代码中硬编码敏感信息:

```bash
# .env 文件
API_KEY=your-api-key
DATABASE_URL=your-database-url
```

使用 python-dotenv 加载:
```python
from dotenv import load_dotenv
load_dotenv()
```

### 2. 访问控制

对于公开部署，考虑添加认证:

```python
import streamlit as st
import hmac

def check_password():
    def password_entered():
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.text_input("密码", type="password", on_change=password_entered, key="password")
    if "password_correct" in st.session_state:
        st.error("密码错误")
    return False

if not check_password():
    st.stop()
```

### 3. HTTPS

在生产环境使用 HTTPS:
- Streamlit Cloud 自动提供
- 使用 Let's Encrypt 为自建服务器配置 SSL

---

## 监控和日志

### 1. 应用监控

```python
import logging

logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 2. 错误追踪

考虑使用 Sentry:

```bash
pip install sentry-sdk
```

```python
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

---

## 常见问题

### Q: 应用启动很慢？
A:
- 使用 `@st.cache_data` 缓存数据
- 减少初始加载的数据量
- 考虑使用数据库而不是 JSON

### Q: 内存不足？
A:
- 优化数据存储
- 限制同时处理的股票数量
- 升级服务器配置

### Q: API 请求限制？
A:
- 添加请求间隔
- 使用缓存减少请求
- 考虑付费 API 服务

---

## 推荐部署方案

| 使用场景 | 推荐方案 | 成本 |
|---------|---------|------|
| 个人使用 | 本地运行 或 Streamlit Cloud | 免费 |
| 小团队 | Streamlit Cloud | 免费 |
| 企业内部 | Docker + 云服务器 | $10-50/月 |
| 公开服务 | Docker + Nginx + SSL | $20-100/月 |

---

## 下一步

部署完成后：
1. 测试所有功能
2. 设置数据备份
3. 配置监控和告警
4. 制定更新流程
5. 编写用户文档

需要帮助？查看 [GitHub Issues](https://github.com/yourusername/value-investing-advisor/issues)
