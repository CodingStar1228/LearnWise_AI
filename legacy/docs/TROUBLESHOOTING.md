# 故障排查指南

## 问题：无法访问 http://localhost:3003

### 1. 确认正确的访问地址

**❌ 错误**：`http://0.0.0.0:3003` （浏览器不支持）

**✅ 正确**：
- `http://localhost:3003`
- `http://127.0.0.1:3003`
- `http://192.168.1.107:3003` （从其他设备访问）

### 2. 检查启动日志

启动时应该看到完整的日志：
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:3003 (Press CTRL+C to quit)
```

如果只看到最后一行，可能应用启动失败。

### 3. 检查是否有错误

启动时查看是否有：
- `ERROR` 开头的错误信息
- `ImportError` 导入错误
- `ModuleNotFoundError` 模块未找到
- 其他异常信息

### 4. 检查端口占用

```bash
# macOS/Linux
lsof -i :3003

# 如果端口被占用，会显示进程信息
# 可以杀掉占用进程或更换端口
```

### 5. 检查防火墙

macOS 可能阻止了端口访问，检查系统偏好设置 > 安全性与隐私 > 防火墙

### 6. 测试连接

在终端中测试：
```bash
# 测试本地连接
curl http://localhost:3003

# 如果返回HTML内容，说明服务器正常
```

### 7. 常见问题

#### 问题：ImportError 或 ModuleNotFoundError
**解决**：
```bash
# 确保在项目根目录
cd /path/to/EasyEdu

# 安装依赖
pip install -r requirements.txt

# 检查Python路径
python -c "import sys; print(sys.path)"
```

#### 问题：端口已被占用
**解决**：
```bash
# 查找占用进程
lsof -i :3003

# 杀掉进程（替换PID为实际进程ID）
kill -9 <PID>

# 或更换端口
python -m uvicorn web.main:app --host 0.0.0.0 --port 3004
```

#### 问题：应用启动失败但没有明显错误
**解决**：
```bash
# 使用详细模式启动
python -m uvicorn web.main:app --host 0.0.0.0 --port 3003 --log-level debug

# 或检查应用是否能正常导入
python -c "from web.main import app; print('OK')"
```

### 8. 验证步骤

1. **启动服务器**：
   ```bash
   bash run_web.sh
   ```

2. **等待完整启动**（看到 "Application startup complete"）

3. **在浏览器访问**：
   ```
   http://localhost:3003
   ```

4. **如果还是无法访问**，尝试：
   - 检查浏览器控制台（F12）是否有错误
   - 尝试使用 `curl` 测试
   - 检查是否有代理设置影响

### 9. 快速诊断命令

```bash
# 1. 检查Python和依赖
python --version
pip list | grep uvicorn
pip list | grep fastapi

# 2. 测试导入
python -c "from web.main import app"

# 3. 测试端口
netstat -an | grep 3003  # Linux
lsof -i :3003            # macOS

# 4. 使用curl测试
curl -v http://localhost:3003
```

### 10. 如果仍然无法解决

请提供以下信息：
1. 完整的启动日志（从启动到显示运行信息）
2. 浏览器访问时的错误信息
3. 浏览器控制台的错误（F12 > Console）
4. `curl http://localhost:3003` 的输出
