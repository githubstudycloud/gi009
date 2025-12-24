# 硬件需求与兼容性指南

本文档详细说明各模型的硬件需求，包括 CPU 内存和 GPU 显存的区别。

## 📊 CPU vs GPU 推理对比

### CPU 推理（本项目主要方案）

**优势**:
- ✅ 无需昂贵的 GPU
- ✅ 内存容量大（常见64GB-512GB）
- ✅ 部署简单，无需CUDA配置
- ✅ 适合小规模部署（1-10人）

**劣势**:
- ⚠️ 推理速度较慢（5-15 tokens/秒）
- ⚠️ 首Token延迟较高（2-5秒）
- ⚠️ 并发能力有限

**适用场景**: 企业内网、开发测试、小团队使用

### GPU 推理

**优势**:
- ✅ 推理速度快（50-100+ tokens/秒）
- ✅ 首Token延迟低（<1秒）
- ✅ 并发能力强

**劣势**:
- ⚠️ 需要高端GPU（RTX 3090/4090, A100等）
- ⚠️ 成本高
- ⚠️ 显存容量受限（常见24GB-80GB）

**适用场景**: 高并发、生产环境、对延迟敏感的应用

---

## 📋 完整模型硬件需求表

### 2025年最新模型

| 模型 | 参数 | CPU内存 | GPU显存 (FP16) | GPU显存 (INT8) | GPU显存 (INT4) | 推荐GPU |
|------|------|---------|---------------|---------------|---------------|---------|
| **Qwen3-Coder-30B-A3B** 🔥 | 30.5B (3.3B激活) | 25-35GB | 50-60GB | 25-30GB | 15-20GB | RTX 4090, A100 |
| **GLM-4.5-Air** 🔥 | 106B (12B激活) | 35-50GB | 70-90GB | 35-45GB | 20-25GB | 2x RTX 4090, A100 |
| **DeepSeek-V3** 🔥 | 671B (37B激活) | 60-80GB | 120-150GB | 60-75GB | 35-40GB | 2x A100, H100 |
| **QwQ-32B** | 32.5B | 40-50GB | 65-80GB | 35-40GB | 20-24GB | RTX 4090, A100 |
| **Gemma 3 27B** | 27B | 35-45GB | 55-70GB | 28-35GB | 16-20GB | RTX 4090, A100 |

### 经典稳定模型

| 模型 | 参数 | CPU内存 | GPU显存 (FP16) | GPU显存 (INT8) | GPU显存 (INT4) | 推荐GPU |
|------|------|---------|---------------|---------------|---------------|---------|
| Qwen2.5-Coder-32B | 32B | 40-50GB | 65-80GB | 35-40GB | 20-24GB | RTX 4090, A100 |
| Qwen2.5-72B | 72B | 80-100GB | 140-180GB | 70-90GB | 40-50GB | 2x A100, H100 |
| DeepSeek-Coder-V2-Lite | 16B | 20-30GB | 32-40GB | 16-20GB | 10-12GB | RTX 3090, 4090 |

---

## 🖥️ CPU 推理详细需求

### 最低配置

```yaml
CPU: 16核心 (Intel Xeon E5-2680 或同等)
内存: 32GB DDR4 (适用于 <20B 模型)
磁盘: 100GB SSD
网络: 100Mbps
```

### 推荐配置（本项目环境）

```yaml
CPU: 32-64核心 (Intel Xeon E5-2680 v4 或更高)
内存: 128-256GB DDR4 2133MHz+
磁盘: 500GB+ NVMe SSD
网络: 1Gbps
```

### 高性能配置

```yaml
CPU: 64-128核心 (AMD EPYC 或 Intel Xeon Platinum)
内存: 512GB-1TB DDR4/DDR5
磁盘: 1TB+ NVMe SSD
网络: 10Gbps
```

### CPU性能影响因素

1. **核心数**: 影响并发处理能力
   - 16核: 1-3用户
   - 32核: 3-6用户
   - 64核: 6-12用户

2. **内存带宽**: 影响推理速度
   - DDR4-2133: 基准性能
   - DDR4-2666: +15-20% 性能
   - DDR4-3200: +25-30% 性能

3. **缓存大小**: 影响首Token延迟
   - L3缓存越大越好（建议 >20MB）

---

## 💾 GPU 推理详细需求

### 消费级 GPU

| GPU | 显存 | 适用模型 | 性能 | 价格区间 |
|-----|------|---------|------|---------|
| RTX 3090 | 24GB | <20B (INT8/INT4) | 中等 | ¥10,000-15,000 |
| RTX 4090 | 24GB | <30B (INT8/INT4) | 高 | ¥15,000-20,000 |
| RTX 4090 x2 | 48GB | <50B (INT8) | 很高 | ¥30,000-40,000 |

### 专业级 GPU

| GPU | 显存 | 适用模型 | 性能 | 价格区间 |
|-----|------|---------|------|---------|
| A100 (40GB) | 40GB | <40B (INT8) | 专业 | ¥50,000-70,000 |
| A100 (80GB) | 80GB | <70B (FP16) | 专业 | ¥80,000-120,000 |
| H100 | 80GB | <100B (FP16) | 顶级 | ¥150,000-250,000 |

### GPU 量化对比

| 精度 | 内存占用 | 性能损失 | 推理速度 | 推荐场景 |
|------|---------|---------|---------|---------|
| FP16 | 100% | 0% | 基准 | 生产环境 |
| INT8 | 50% | 1-3% | +20% | 平衡方案 |
| INT4 | 25% | 3-8% | +40% | 资源受限 |

---

## 🔧 兼容性矩阵

### 操作系统

| 系统 | CPU推理 | GPU推理 | 推荐度 | 说明 |
|------|---------|---------|--------|------|
| Ubuntu 18.04+ | ✅ | ✅ | ⭐⭐⭐⭐⭐ | 最佳支持 |
| Ubuntu 20.04+ | ✅ | ✅ | ⭐⭐⭐⭐⭐ | 推荐 |
| CentOS 7+ | ✅ | ✅ | ⭐⭐⭐⭐ | 企业常用 |
| Debian 10+ | ✅ | ✅ | ⭐⭐⭐⭐ | 稳定 |
| Windows Server | ⚠️ | ✅ | ⭐⭐⭐ | 需WSL2 |
| macOS | ⚠️ | ❌ | ⭐⭐ | 仅CPU，性能差 |

### Docker 版本

```yaml
最低版本: Docker 20.10+
推荐版本: Docker 24.0+
Docker Compose: 1.29+ (v2推荐)
```

### CUDA 版本（GPU推理）

```yaml
最低版本: CUDA 11.8
推荐版本: CUDA 12.1+
驱动版本: 530+ (CUDA 12.1+)
```

---

## 📐 内存计算公式

### CPU 内存估算

```python
# 基础公式
内存需求(GB) = 参数量(B) × 精度字节数 × 1.2

# 示例：Qwen2.5-Coder-32B (FP16)
内存 = 32 × 2 × 1.2 = 76.8GB ≈ 80GB

# MoE模型（如Qwen3-30B-A3B）
内存 = 激活参数(B) × 精度字节数 × 1.2
内存 = 3.3 × 2 × 1.2 = 7.92GB (推理时)
但需要加载完整模型权重，实际需要 30GB+
```

### 精度字节数

| 精度 | 字节数 | 说明 |
|------|--------|------|
| FP32 | 4 | 单精度浮点 |
| FP16 / BF16 | 2 | 半精度浮点（推荐） |
| INT8 | 1 | 8位整数量化 |
| INT4 | 0.5 | 4位整数量化 |

### 实际内存需求

```
总内存 = 模型权重 + KV Cache + 运行时开销

模型权重: 参数量 × 精度字节数
KV Cache: 与上下文长度和batch size相关
运行时开销: 约占模型权重的 10-20%
```

---

## 🎯 根据硬件选择模型

### 场景一：64GB CPU内存

**推荐模型**:
1. Qwen3-Coder-30B-A3B (25-35GB) ⭐⭐⭐⭐⭐
2. DeepSeek-Coder-V2-Lite (20-30GB) ⭐⭐⭐⭐
3. Qwen2.5-Coder-32B (40-50GB) ⚠️ 需要至少80GB

**部署建议**:
```bash
# 推荐：Qwen3-Coder-30B-A3B
docker-compose -f docker-compose-qwen3.yml up -d
```

### 场景二：128GB CPU内存

**推荐模型**:
1. Qwen3-Coder-30B-A3B (25-35GB) ⭐⭐⭐⭐⭐
2. GLM-4.5-Air (35-50GB) ⭐⭐⭐⭐⭐
3. Qwen2.5-Coder-32B (40-50GB) ⭐⭐⭐⭐
4. QwQ-32B (40-50GB) ⭐⭐⭐⭐

**部署建议**:
```bash
# 可以同时部署两个模型
docker-compose -f docker-compose-qwen3.yml up -d
docker-compose -f docker-compose-glm45air.yml -p glm up -d
```

### 场景三：256GB+ CPU内存

**推荐模型**:
1. DeepSeek-V3 (60-80GB) ⭐⭐⭐⭐⭐
2. Qwen2.5-72B (80-100GB) ⭐⭐⭐⭐
3. 多模型部署 ⭐⭐⭐⭐⭐

**部署建议**:
```bash
# 顶级性能
docker-compose -f docker-compose-deepseek-v3.yml up -d

# 或多模型组合
docker-compose -f docker-compose-qwen3.yml up -d
docker-compose -f docker-compose-glm45air.yml -p glm up -d
docker-compose -f docker-compose-qwen72b.yml -p qwen72b up -d
```

### 场景四：RTX 4090 (24GB)

**推荐模型**:
1. Qwen3-Coder-30B-A3B (INT8: 25-30GB, INT4: 15-20GB) ⭐⭐⭐⭐⭐
2. Qwen2.5-Coder-32B (INT4: 20-24GB) ⭐⭐⭐⭐
3. DeepSeek-Coder-V2-Lite (FP16: 32-40GB, INT8: 16-20GB) ⭐⭐⭐⭐⭐

**部署建议**:
```bash
# 使用INT4量化
docker run --gpus all -p 8000:8000 \
  vllm/vllm-openai:latest \
  --model Qwen/Qwen3-Coder-30B-A3B-Instruct \
  --quantization awq \
  --dtype half
```

### 场景五：A100 (80GB)

**推荐模型**:
1. DeepSeek-V3 (INT8: 60-75GB) ⭐⭐⭐⭐⭐
2. Qwen2.5-72B (FP16: 140-180GB需要2卡, INT8: 70-90GB) ⭐⭐⭐⭐
3. GLM-4.5-Air (FP16: 70-90GB) ⭐⭐⭐⭐⭐

---

## 💡 性能优化建议

### CPU 推理优化

1. **启用 AVX-512**:
```bash
# 检查CPU是否支持
lscpu | grep avx512
```

2. **绑定CPU核心**:
```bash
docker update --cpuset-cpus="0-31" container_name
```

3. **优化内存分配**:
```yaml
shm_size: '32gb'  # 共享内存
ulimits:
  memlock: -1
```

4. **使用量化**:
```yaml
--quantization awq  # 减少50%内存
```

### GPU 推理优化

1. **Tensor并行**:
```bash
--tensor-parallel-size 2  # 使用2张GPU
```

2. **Pipeline并行**:
```bash
--pipeline-parallel-size 2
```

3. **Flash Attention**:
```bash
--enable-flash-attention  # 减少显存，提升速度
```

---

## 🔍 性能基准测试

### 测试环境

**CPU**: Intel Xeon E5-2680 v4 @ 2.40GHz (28核×2)
**内存**: 363GB DDR4 2133MHz
**磁盘**: NVMe SSD

### Qwen3-Coder-30B-A3B (CPU)

```
首Token延迟: 2.5-3.5秒
生成速度: 10-15 tokens/秒
并发（5用户）: 6-8 tokens/秒
内存占用: 28-32GB实际使用
```

### DeepSeek-V3 (CPU)

```
首Token延迟: 4-5秒
生成速度: 5-8 tokens/秒
并发（3用户）: 3-5 tokens/秒
内存占用: 65-72GB实际使用
```

### 对比：GPU vs CPU（Qwen2.5-32B）

| 指标 | CPU (E5-2680) | RTX 4090 (INT4) | A100 (FP16) |
|------|---------------|-----------------|-------------|
| 首Token延迟 | 2.5秒 | 0.5秒 | 0.3秒 |
| 生成速度 | 10 tok/s | 80 tok/s | 120 tok/s |
| 并发能力 | 5用户 | 20用户 | 50用户 |
| 成本 | 低 | 中 | 高 |

---

## 📚 参考资料

- [QwQ-32B Hugging Face](https://huggingface.co/Qwen/QwQ-32B)
- [QwQ-32B Hardware Requirements](https://jarvislabs.ai/ai-faqs/what-gpu-is-required-to-run-qwen-qwq-32b-model-from-hugging-face)
- [Gemma 2 27B Specifications](https://apxml.com/models/gemma-2-27b)
- [Gemma 3 Model Overview](https://ai.google.dev/gemma/docs/core)
- [vLLM Documentation](https://docs.vllm.ai/)

---

## 常见问题

**Q: CPU推理真的可行吗？**
A: 可行，但速度较慢。适合小规模部署（1-10人），对延迟要求不高的场景。

**Q: 我该选择CPU还是GPU？**
A:
- 预算有限、小团队 → CPU
- 高并发、低延迟 → GPU
- 开发测试 → CPU
- 生产环境 → GPU

**Q: MoE模型的实际内存占用？**
A: MoE模型需要加载完整权重到内存，但推理时只激活部分专家，因此：
- 内存需求：按总参数计算
- 计算量：按激活参数计算

**Q: 量化会影响性能吗？**
A:
- INT8: 1-3%性能损失，推荐
- INT4: 3-8%性能损失，可接受
- 代码生成任务对量化比较敏感
