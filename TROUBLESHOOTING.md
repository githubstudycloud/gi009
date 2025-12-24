# 故障排查指南

本文档提供常见问题的解决方案和调试技巧。


## 快速诊断

### 健康检查脚本

创建 `check-health.sh`:

```bash
#!/bin/bash

echo "=== 系统健康检查 ==="
echo ""

# 1. 检查 Docker
echo "1. 检查 Docker..."
if command -v docker &> /dev/null; then
    echo "✓ Docker 已安装: $(docker --version)"
else
    echo "✗ Docker 未安装"
fi

# 2. 检查容器状态
echo ""
echo "2. 检查容器状态..."
docker-compose ps

# 3. 检查资源使用
echo ""
echo "3. 检查资源使用..."
docker stats --no-stream

# 4. 检查 API
echo ""
echo "4. 检查 API..."
curl -f http://localhost:8000/health && echo "✓ API 正常" || echo "✗ API 异常"

# 5. 检查日志错误
echo ""
echo "5. 最近错误日志..."
docker-compose logs --tail=20 | grep -i error
```


## 常见问题

### 1. 服务启动失败

#### 问题：容器无法启动

**症状**：
```
docker-compose up -d
# 容器立即退出
```

**诊断**：
```bash
# 查看容器状态
docker-compose ps

# 查看完整日志
docker-compose logs

# 查看最后 50 行日志
docker-compose logs --tail=50
```

**可能原因与解决方案**：

##### a) 端口被占用

```bash
# 检查端口占用
netstat -tunlp | grep 8000
# 或
lsof -i :8000

# 解决：修改 docker-compose.yml 中的端口
ports:
  - "8001:8000"  # 改为其他端口
```

##### b) 内存不足

```bash
# 检查可用内存
free -h

# 解决：使用更小的模型或增加内存
docker-compose -f docker-compose-deepseek.yml up -d
```

##### c) Docker 权限问题

```bash
# 添加用户到 docker 组
sudo usermod -aG docker $USER

# 重新登录或执行
newgrp docker
```


### 2. 模型下载问题

#### 问题：模型下载失败或很慢

**症状**：
```
Downloading model... (stuck)
Connection timeout
```

**解决方案**：

##### 方案 A：使用镜像（已配置）

```yaml
# docker-compose.yml 中已包含
environment:
  - HF_ENDPOINT=https://hf-mirror.com
```

##### 方案 B：手动下载模型

```bash
# 创建模型目录
mkdir -p models

# 使用 huggingface-cli 下载
pip install huggingface_hub

# 设置镜像
export HF_ENDPOINT=https://hf-mirror.com

# 下载模型
huggingface-cli download Qwen/Qwen2.5-Coder-32B-Instruct \
  --local-dir models/Qwen2.5-Coder-32B-Instruct

# 修改 docker-compose.yml 使用本地模型
command: >
  --model /root/.cache/huggingface/Qwen2.5-Coder-32B-Instruct
```

##### 方案 C：使用离线模型

```bash
# 从其他机器拷贝模型
scp -r user@host:/path/to/models ./models

# 挂载到容器
volumes:
  - ./models:/root/.cache/huggingface
```


### 3. 内存不足 (OOM)

#### 问题：容器因内存不足被杀死

**症状**：
```bash
docker-compose logs
# Killed
# Out of memory: Kill process...
```

**诊断**：
```bash
# 查看内存使用
docker stats

# 查看系统日志
dmesg | grep -i "out of memory"
```

**解决方案**：

##### 方案 A：使用更小的模型

```bash
# 停止当前服务
docker-compose down

# 使用 DeepSeek-Coder-V2-Lite
docker-compose -f docker-compose-deepseek.yml up -d
```

##### 方案 B：减少上下文长度

```yaml
# 编辑 docker-compose.yml
command: >
  ...
  --max-model-len 4096    # 从 8192 减少到 4096
  --max-num-seqs 5        # 从 10 减少到 5
```

##### 方案 C：启用量化

```yaml
command: >
  ...
  --quantization awq      # 减少 40% 内存
```

##### 方案 D：配置 swap

```bash
# 创建 swap 文件（不推荐，会降低性能）
sudo fallocate -l 32G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久启用
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```


### 4. API 响应慢

#### 问题：请求响应时间过长

**症状**：
```bash
curl http://localhost:8000/v1/chat/completions ...
# 等待时间 > 30秒
```

**诊断**：
```bash
# 运行性能测试
python3 benchmark.py

# 查看资源使用
docker stats

# 检查并发数
docker-compose logs | grep "max_num_seqs"
```

**解决方案**：

##### 方案 A：减少生成长度

```json
{
  "max_tokens": 500  // 从 2000 减少
}
```

##### 方案 B：降低温度

```json
{
  "temperature": 0.3  // 从 0.7 降低，更确定性
}
```

##### 方案 C：减少并发

```yaml
# docker-compose.yml
--max-num-seqs 5  # 减少并发数
```

##### 方案 D：优化 CPU 亲和性

```bash
# 绑定到特定 CPU 核心
docker update --cpuset-cpus="0-15" qwen-coder-32b-vllm
```


### 5. Function Calling 不工作

#### 问题：模型不调用工具

**症状**：
```
请求包含 tools 参数，但模型没有调用工具
```

**检查清单**：

1. **模型支持**
```bash
# 确认使用支持工具调用的模型
# ✓ Qwen2.5-Coder-32B
# ✓ Qwen2.5-72B
# ✓ DeepSeek-Coder-V2-Lite
# ✗ 其他模型可能不支持
```

2. **请求格式**
```json
{
  "model": "qwen2.5-coder-32b-instruct",
  "messages": [...],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "tool_name",
        "description": "清晰的工具描述",
        "parameters": {
          "type": "object",
          "properties": {...},
          "required": [...]
        }
      }
    }
  ],
  "tool_choice": "auto"
}
```

3. **工具描述质量**
```json
// ✗ 不好
"description": "工具"

// ✓ 好
"description": "搜索代码仓库中的文件和函数，支持按文件名、函数名、关键词搜索"
```

4. **检查模型版本**
```bash
# 使用最新版本的 vLLM
docker-compose pull
docker-compose up -d
```


### 6. 连接问题

#### 问题：无法连接到 API

**症状**：
```bash
curl http://localhost:8000/health
# Connection refused
```

**诊断步骤**：

1. **检查服务状态**
```bash
docker-compose ps
# 应该显示 "Up"
```

2. **检查端口绑定**
```bash
docker-compose logs | grep "listening"
# 应该看到 "Uvicorn running on http://0.0.0.0:8000"
```

3. **检查防火墙**
```bash
# Ubuntu
sudo ufw status
sudo ufw allow 8000

# CentOS
sudo firewall-cmd --add-port=8000/tcp --permanent
sudo firewall-cmd --reload
```

4. **检查网络**
```bash
# 测试容器网络
docker network ls
docker network inspect llm-network
```


### 7. 模型加载问题

#### 问题：模型加载失败或挂起

**症状**：
```
Loading model...
(长时间没有进展)
```

**解决方案**：

##### 方案 A：检查磁盘空间

```bash
# 检查可用空间
df -h

# 清理 Docker 缓存
docker system prune -a

# 清理未使用的镜像
docker image prune -a
```

##### 方案 B：增加启动超时

```yaml
# docker-compose.yml
healthcheck:
  start_period: 600s  # 从 300s 增加到 600s
```

##### 方案 C：查看详细日志

```bash
# 启用 DEBUG 日志
docker-compose logs -f

# 或修改日志级别
environment:
  - LOG_LEVEL=DEBUG
```


### 8. 性能问题

#### 问题：Token 生成速度慢

**诊断**：
```bash
# 运行基准测试
python3 benchmark.py

# 查看 CPU 使用
top -H -p $(docker inspect -f '{{.State.Pid}}' qwen-coder-32b-vllm)
```

**优化方案**：

##### 优化 1：调整 vLLM 参数

```yaml
command: >
  ...
  --enable-chunked-prefill        # 启用分块预填充
  --max-num-batched-tokens 16384  # 增加批处理 tokens
  --disable-log-requests          # 禁用请求日志
```

##### 优化 2：使用量化模型

```yaml
--quantization awq  # AWQ 量化，性能损失小
```

##### 优化 3：CPU 优化

```bash
# 设置 CPU governor 为 performance
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# 禁用超线程（可选，视情况而定）
echo off | sudo tee /sys/devices/system/cpu/smt/control
```


### 9. Docker 问题

#### 问题：Docker Compose 版本问题

**症状**：
```
ERROR: The Compose file is invalid
```

**解决**：
```bash
# 检查版本
docker-compose --version

# 如果版本过低，升级
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```


### 10. 日志问题

#### 问题：日志过大导致磁盘满

**解决**：

##### 方案 A：配置日志轮转

```yaml
# docker-compose.yml
services:
  vllm:
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "3"
```

##### 方案 B：清理旧日志

```bash
# 清理容器日志
sudo sh -c "truncate -s 0 /var/lib/docker/containers/**/*-json.log"

# 清理项目日志
rm -f logs/*.log
```


## 调试技巧

### 启用详细日志

```yaml
# docker-compose.yml
environment:
  - LOG_LEVEL=DEBUG
  - VLLM_LOGGING_LEVEL=DEBUG
```

### 进入容器调试

```bash
# 进入运行中的容器
docker exec -it qwen-coder-32b-vllm bash

# 查看进程
ps aux

# 查看内存
free -h

# 查看磁盘
df -h

# 测试网络
curl http://localhost:8000/health
```

### 监控资源使用

```bash
# 实时监控
docker stats

# 查看特定容器
docker stats qwen-coder-32b-vllm
```

### 导出日志

```bash
# 导出所有日志
docker-compose logs > debug.log

# 导出最近 1000 行
docker-compose logs --tail=1000 > recent.log

# 导出特定时间范围
docker-compose logs --since="2024-12-24T10:00:00" > time-range.log
```


## 性能基准

### 正常性能指标

| 指标 | Qwen2.5-Coder-32B | DeepSeek-V2-Lite |
|------|-------------------|------------------|
| 首 Token 延迟 | 2-3秒 | 1-2秒 |
| 生成速度 | 8-12 tok/s | 12-18 tok/s |
| 内存使用 | 45-52GB | 24-30GB |
| CPU 使用 | 800-1200% | 600-900% |

如果你的指标明显低于上述值，说明存在性能问题。


## 获取帮助

如果以上方案都无法解决问题：

1. **收集信息**
```bash
# 系统信息
uname -a
docker --version
docker-compose --version

# 服务状态
docker-compose ps
docker stats --no-stream

# 日志
docker-compose logs --tail=100 > debug.log
```

2. **提交 Issue**
- 仓库: https://github.com/githubstudycloud/gi009/issues
- 包含：问题描述、复现步骤、系统信息、日志

3. **查看文档**
- [README.md](./README.md)
- [DEPLOYMENT.md](./DEPLOYMENT.md)
- [API.md](./API.md)


## 预防措施

### 定期维护

```bash
# 每周执行
docker system prune -f
docker-compose logs --tail=0 -f > /dev/null

# 每月执行
docker-compose pull
docker-compose up -d
```

### 监控告警

考虑设置监控：
- Prometheus + Grafana
- Uptime monitoring
- Disk space alerts


## 应急恢复

### 完全重置

```bash
# ⚠️ 警告：将删除所有数据

# 停止服务
docker-compose down -v

# 清理容器
docker system prune -a -f

# 清理模型
rm -rf models/* logs/*

# 重新启动
docker-compose up -d
```


---

如有其他问题，欢迎提交 Issue！
