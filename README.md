# AI 游戏运维助手

一个基于大语言模型的智能运维助手，支持自然语言查询服务器指标、分析错误日志、执行服务重启。

## 功能特点

- 📊 **指标查询**：获取在线人数、CPU/内存使用率
- 📝 **智能日志分析**：自动分析错误日志并给出修复建议
- ⚠️ **安全操作**：危险操作（重启）需要二次确认
- 💬 **自然语言交互**：像聊天一样运维

## 快速开始

### 1. 环境要求
- Python 3.8+
- openAi API Key

### 2. 安装后端依赖
```bash
cd backend
pip install -r requirements.txt
```

### 3.配置 API Key
```bash
export DEEPSEEK_API_KEY="your-api-key"
```
或者在 config.py 中直接修改

### 4. 启动后端服务
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 打开前端页面
直接用浏览器打开 frontend/index.html（注意：由于跨域，建议使用 Live Server 或直接通过后端挂载静态文件）。

### 6. 使用示例
• 输入：查询 lobby-01 的在线人数  
• 输入：重启 game-01 服务器 → 助手要求确认 → 输入 YES  
• 输入：分析 game-02 的错误日志  

### 扩展开发
• 将 tools.py 中的模拟函数替换为真实 SSH/Prometheus 调用  
• 增加更多工具（如查看 Pod 状态、执行脚本）  
• 集成到钉钉机器人  
