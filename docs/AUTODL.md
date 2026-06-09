# 在 AutoDL 上运行 LearnWise_AI / Running on AutoDL

手把手：从连接 4090 到跑通模型 + 网页 + 训练。

## 1. 连接到 4090

1. AutoDL 控制台点 **开机**。
2. 控制台「SSH登录」会给一条命令，形如：
   ```bash
   ssh -p 12345 root@region-x.autodl.com   # 密码也在控制台
   ```
   在你 Mac 的终端里运行它登录。
3. 用数据盘目录（关机不丢数据）：
   ```bash
   cd /root/autodl-tmp
   ```

## 2. 一键安装（拉代码 + 依赖 + 模型）

```bash
source /etc/network_turbo
git clone https://github.com/CodingStar1228/LearnWise_AI.git
cd LearnWise_AI
bash scripts/setup_autodl.sh
```

`setup_autodl.sh` 会：装 `requirements.txt` + GPU 栈（vllm/peft/bitsandbytes 等）+ 用 ModelScope 下载 Qwen2.5-7B 到 `/root/autodl-tmp/models/`。

## 3. 单卡分时使用（重要）

24GB 显存放不下「同时服务 + 训练」。要么服务、要么训练。

### A. 起自有模型服务

```bash
export LEARNWISE_MODEL_PATH=/root/autodl-tmp/models/Qwen2.5-7B-Instruct
./scripts/serve_model_vllm.sh        # 占用 GPU，监听 :8000
```

### B. 启动网页（新开一个 SSH 终端）

```bash
cd /root/autodl-tmp/LearnWise_AI
export LEARNWISE_LLM_BACKEND=local_vllm
export LEARNWISE_LLM_BASE_URL=http://127.0.0.1:8000/v1
export LEARNWISE_WEB_PORT=6006
bash run_web.sh
```

## 4. 在浏览器看网页（两种方式）

- **方式一（推荐）AutoDL 自定义服务**：网页跑在 `6006` 端口，控制台开「自定义服务」会给一个公网地址，直接点开。
- **方式二 SSH 端口转发**：在你 Mac 终端：
  ```bash
  ssh -p 12345 -L 6006:127.0.0.1:6006 root@region-x.autodl.com
  ```
  然后本地浏览器开 `http://127.0.0.1:6006`。

## 5. 生成 AP/IB 数据集（模型在线时）

```bash
export LEARNWISE_LLM_BACKEND=local_vllm
export LEARNWISE_LLM_BASE_URL=http://127.0.0.1:8000/v1
python scripts/ingest_textbooks.py --course all --max-chunks 10
```

> 注意：`textbooks/` 里的 PDF 是 gitignored 的，不会随 git 同步。要在 AutoDL 上生成数据，需先把 PDF 上传到 `textbooks/AP|IB/`（用 AutoDL 文件上传或 scp）。

## 6. 训练自有模型

```bash
# 先 Ctrl+C 停掉 vLLM 腾出显存
python scripts/build_sft_data.py
bash src/models/rlhf/sft/train.sh
# 产物在 output/learnwise_feynman-<时间戳>/
```

## 7. 用训练好的模型上线

```bash
export LEARNWISE_MODEL_PATH=/root/autodl-tmp/LearnWise_AI/output/learnwise_feynman-XXXX
export LEARNWISE_LLM_MODEL=LearnWise-7B-Feynman
./scripts/serve_model_vllm.sh
```

## 常见问题

- **vllm 装不上 / CUDA 不匹配**：确认实例镜像是 PyTorch 2.x + CUDA 12.x；不行就在控制台换镜像。
- **下模型慢**：`setup_autodl.sh` 用的是 ModelScope（国内快）。
- **端口打不开**：AutoDL 自定义服务固定用 6006，确保 `LEARNWISE_WEB_PORT=6006`。
