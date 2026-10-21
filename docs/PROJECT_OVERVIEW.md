# LA-LoRA 复现项目总览

本文件是项目目标、源码导航和管理约定的统一权威入口。更新日期：2026-10-21（Asia/Shanghai）。具体进度以 [REPRO_STATUS](REPRO_STATUS.md) 为准。

## 论文与来源

- 论文：*Rethinking LoRA for Privacy-Preserving Federated Learning in Large Models*。
- 作者：Jin Liu、Yinbin Miao、Ning Xi、Junkang Liu；ICLR 2026。
- 一手来源：[ICLR 会议页面](https://proceedings.iclr.cc/paper_files/paper/2026/hash/34b13425b5ba8ad05d97b0043df52ed3-Abstract-Conference.html)、[论文 PDF](https://openreview.net/pdf?id=BPzSV4uw0x)、[arXiv:2602.19926](https://arxiv.org/abs/2602.19926)。本轮核对了论文元数据，尚未逐式完成实现与论文的系统审计。
- 官方仓库：[junkangLiu0/LA-LORA](https://github.com/junkangLiu0/LA-LORA)。当前官方 `main`：`578e49278e731f26d12457dbc3e4bec89d017a3c`。
- 个人仓库：[PPEE523/LA-LORA-Reproduction](https://github.com/PPEE523/LA-LORA-Reproduction)。2026-10-21 经 GitHub API 确认是公开 Fork，parent 为官方仓库，不需要重复创建。

## 目标与职责

目标是建立可信、可追溯的论文复现基线，为后续算法研究提供依据。先完成机制、采样假设与隐私会计核验，再在明确的资源约束下开展正式基线、消融和论文结果对照。

用户负责算法编写、修改与运行，并通过 ChatGPT 获取科研指导。仓库维护任务负责版本、结构、状态与实验档案。本轮仅增加管理文档、忽略规则和协作约束；不修改核心算法、DP 实现或训练配置，不训练、不下载数据或权重。

## 当前实验环境

| 项目 | 当前信息 | 证据边界 |
| --- | --- | --- |
| 本地项目 | `/home/pppe/LoRA/LA-LORA` | 本轮工作目录 |
| 开发方式 | Windows + VS Code Remote WSL | 用户提供 |
| Conda 环境 | `la-lora`；`/home/pppe/miniconda3/envs/la-lora` | 本轮读取安装元数据 |
| GPU | RTX 5060 Laptop，8 GB | 用户提供；本轮未调用 GPU |
| Python | 3.10.22 | Conda 元数据 |
| PyTorch / torchvision | 2.11.0+cu130 / 0.26.0+cu130 | 安装元数据；cu130 不等同于系统 CUDA Toolkit 版本 |
| Ray / NumPy | 2.59.0 / 1.26.4 | 安装元数据 |
| Opacus / PEFT / timm | 1.5.3 / 0.13.2 / 1.0.30 | 安装元数据；安装不代表实际调用或机制通过验收 |

CUDA、PyTorch、Ray 的可运行性来自用户既有验证；本轮只做静态与 Git 管理检查。官方 `requirements.txt` 含其他机器的 `file:///...` 依赖路径，不是当前环境的可移植锁定文件，不应直接据此覆盖现有环境。

## 算法框架与源码导航

论文提出 Local Alternating LoRA。下面描述当前本地代码结构，不等同于已经确认与论文完全一致：

1. 生成 Dirichlet Non-IID 客户端划分，并按轮选取参与客户端。
2. 在预训练视觉骨干的注意力模块注入 LoRA，冻结骨干；分类头是否训练取决于配置。
3. 本地 step 交替更新 B、A；启用 `privacy` 时，当前 LA-LoRA 路径调用逐样本梯度裁剪与 Gaussian 加噪。
4. 启用 `la_filter` 时对 LoRA 梯度施加固定 `[1, 4, 6, 4, 1] / 16` 滤波，然后进行优化器更新。
5. Ray 客户端返回模型差分，服务器聚合并评估。

| 核心模块 | 源码位置 | 说明 |
| --- | --- | --- |
| 视觉联邦训练入口 | `DP_lora.py` | 参数解析、客户端选择、Ray actor、聚合、评估与输出 |
| 交替更新 | `DP_lora.py::DataWorker.update_FedAvg_AL` | 本地 B/A 交替、DP 调用及滤波；含前两步断言 |
| 梯度滤波 | `DP_lora.py::gaussian_lowpass_1d_along_dim`、`gaussian_lowpass_lora_grad` | A 沿输入维、B 沿输出维；当前边界为 replicate padding |
| 逐样本机制 | `dp_per_sample.py::dp_backward` | 对当前可训练参数拼接范数裁剪，裁剪和上加噪后除实际 batch 大小 |
| Non-IID 划分 | `dirichlet_data.py::data_from_dirichlet` | 独立 RNG 的 Dirichlet 划分；样本复用假设尚待审计 |
| Ray 数据加载 | `ray_worker_loader.py` | 独立加载 CIFAR，`SubsetRandomSampler`；与会计假设的对应关系未验收 |
| 模型源码 | `model.py`、`vit_model.py`、`models/` | Swin、ViT、其他视觉网络；不能忽略或删除 `models/` |
| 数据处理源码 | `dataset/` | 源码目录，与本地数据目录 `data/` 不同 |
| 已有验证脚本 | `test_gaussian_filter.py`、`test_dp_per_sample.py`、`verify_pretrained.py` | 滤波数值、CPU 裁剪示例、预训练加载验证 |
| 隐私会计候选代码 | `eps.py`、`eps_computer.py` | 有公式实现不代表已接入当前训练并验证 |
| 官方其他路径 | `DP_LLM.py`、`sam.py`、`roberta_base/config.json` | 保留原有内容；本轮未验证 NLP 路径 |
| 历史本地修补脚本 | `patch_local.py` | 会改写训练脚本，不自动执行 |

`model/`、`pretrained/`、`checkpoint/` 是输出或权重目录；`log/`、`plot/`、`runs/` 是运行产物。保留本地实物，新增产物由 `.gitignore` 排除。原 `README.md` 与 `readme.md` 保留作上游材料，其中环境名、入口或目录描述可能过时；本地项目管理信息以本文件及状态文档为准。

## 当前复现阶段与问题优先级

当前处于“训练链路与机制的初步验证完成，严格机制审计及正式性能复现尚未完成”阶段。20 轮无 DP、无滤波交替 LoRA 诊断得到 15.67% CIFAR-100 测试准确率；它不是论文性能复现或隐私预算下的正式结果。**当前不能宣称已经完整实现或验证论文的 `(epsilon, delta)-DP` 保证。**

| 编号 / 优先级 | 已知问题与下一目标 |
| --- | --- |
| GIT-01 / 已完成 | 干净分支已推送至个人 Fork main 并核验；旧的大型实验历史仅保留本地 |
| DP-01 / P0 | 严格裁剪上界、Gaussian 噪声分布及缩放测试尚缺 |
| DP-02 / P0 | 客户端选择、样本加载、跨客户端样本复用与会计采样假设尚未对应 |
| DP-03 / P0 | 邻接定义、保护单位、组合步数、delta 及隐私会计尚未验收 |
| REP-01 / P1 | 历史命令、运行时 SHA、若干开关缺失；需完善配置和运行归档 |
| REP-02 / P1 | 正式基线、消融、多 seed 与论文结果逐项对照未开展 |
| ENV-01 / P1 | 当前环境尚无可移植依赖锁定；上游 requirements 含绝对本地路径 |
| OBS-01 / P1 | 历史日志 train/test loss 均为 0，需核查评估记录语义；本轮不修复 |

## Git 状态与发布方案

当前开发分支为 `reproduction/managed`，跟踪 `origin/main`。初始化时的 `reproduce-local` 保留在管理提交 `1a43153fd26b03659b7bec8642db17fea5d9ce47`，其祖先含既有源码归档 `417b359c75bb57134b9baa1879484b87ba17f519`；其他本地分支 `main`、`reproduction/local-8gb` 仍保留在官方基准。`origin` 的 fetch 地址为 `https://github.com/PPEE523/LA-LORA-Reproduction.git`，push 地址为 `git@github.com:PPEE523/LA-LORA-Reproduction.git`。`upstream` 的 fetch/push 均保留为 `https://github.com/junkangLiu0/LA-LORA.git`。

用户已明确确认发布到现有个人 Fork 的 `main`，并同意独立干净发布分支方案。首次发布快照 `dd50765c63377aeafeb29e916656082a49e24e7e` 已通过 SSH 普通快进推送，远端默认分支为 `main`；GitHub API 验证其 55 个文件的路径、mode 和 blob ID 与本地完全一致。首次发布树为 `0553396dd39e28c225b046c65d0d9819afa17ffd`，共 2,622,925 bytes（约 2.50 MiB），最大文件为上游原有 `data/cola/train.csv`（1,213,192 bytes）。本地旧分支及原有 91 个文件的大小和 SHA-256 均保持不变。后续管理验证记录随单独的 docs 提交更新；最新 SHA 用 `git log -1 --format='%H %s'` 或 GitHub main 的最近提交查看。

### 已跟踪文件审计

既有算法归档 `417b359` 共 91 个文件，约 986.90 MiB。下列数据/权重已进入该历史，其中 8 个对象超过 100 MiB；仅补 `.gitignore` 或新增删除提交都无法让这些祖先对象消失。这里是旧分支审计，不是干净发布树的大小。

| 文件（或同类路径） | 数量 | 大小 | 本轮处理 |
| --- | ---: | ---: | --- |
| `data/cifar-100-python.tar.gz` | 1 | 161.17 MiB | 保留原文件和历史，不推送该历史 |
| `data/cifar-100-python/train` | 1 | 148.06 MiB | 同上 |
| `data/cifar-100-python/test` | 1 | 29.61 MiB | 同上 |
| `pretrained/swin_tiny_patch4_window7_224.pth` | 1 | 109.05 MiB | 同上 |
| `model/model_LA-LORA-*`（无扩展名） | 5 | 每个约 107.28 MiB | 同上；目录规则也覆盖无后缀权重 |
| `__pycache__/`、嵌套缓存 | 25 | 总计 174,111 bytes | 不新增；原有跟踪状态本轮不改 |
| 本地新增 `log/`、`plot/`、`runs/` | 3 / 5 / 9 | 均为轻量产物 | 保留本地证据，不纳入发布快照 |

五个权重的完整文件名可用只读命令查看：

```bash
git ls-tree -rl 417b359 -- model/ pretrained/ data/cifar-100-python data/cifar-100-python.tar.gz
```

### 已执行的发布方案

1. 保留 `reproduce-local`、`417b359` 及其全部后续本地提交、所有其他分支与本地数据实物。
2. 在同一仓库创建本地 `reproduction/managed`，以已核验的官方 `578e492...` 为父提交；纳入经清单审核的当前源码、测试和管理文档，共 55 个文件。9 个既有源码/编辑器配置路径逐一保持原 blob 不变；本轮只编辑管理文档。不把含大型对象的 `417b359` 作为其祖先。
3. 发布快照保留全部官方原有源码和轻量实验材料，包括原有 `data/cola/`、示例图、示例日志及上游历史；不加入本地新生成的数据、权重、缓存和运行产物。不直接删除或取消跟踪当前分支的已有文件。
4. 使用独立索引构造快照，切换开发分支时仅更新 Git 分支/索引，保持工作区文件实物不变；不重新克隆、不创建仓库副本。发布树排除 43 个本地生成文件；切换前后对原有 91 个文件比对 SHA-256 和大小。
5. 将干净发布分支以普通快进方式推送到已获确认的个人 Fork `main`，让默认页面包含最新源码和文档；不覆盖官方 upstream，不强推，不推送全部本地分支。若远端已前进，先停止并重新检查差异。
6. 已核验远端 SHA、树与本地发布快照一致；扫描首次发布所有可达历史的 64 个 blob（含 11 个二进制对象），没有超过 10 MiB 的对象，常见敏感模式无匹配。原本地分支保留作溯源，不再用于日常推送；从 `reproduction/managed` 继续工作。

该方案保留现有本地历史与官方祖先历史；个人 Fork 将以新的干净提交归档本地源码，不上传旧的大文件提交。若要求个人 Fork 也包含 `417b359` 的完整历史，则与“不上传大型实验文件、不重写历史”冲突，需另行决定，不能用强推解决。

WSL 当前未安装 `gh`，无可运行的 `gh auth status`；Git 提交身份可用。GitHub 连接器已确认账号与仓库权限；本轮 `ssh -T` 认证为 PPEE523，SSH `git ls-remote` 成功读取个人 Fork。首次推送可使用现有 SSH，无需 Token 或安装 gh。若后续需要 CLI，在 WSL 终端自行登录（不向聊天提供 Token）：

```bash
sudo apt update
sudo apt install gh
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git
gh auth status
```

## 文档与日常交接

- [REPRO_STATUS](REPRO_STATUS.md)：当前事实、证据边界、下一项工作。
- [EXPERIMENT_LOG](EXPERIMENT_LOG.md)：实验逐次追加与模板。
- [CODE_CHANGES](CODE_CHANGES.md)：按类别记录改动与 commit。
- [REPRO_CHECKLIST](REPRO_CHECKLIST.md)：以明确标准验收。
- [AGENTS.md](../AGENTS.md)：后续仓库协作约束。

日常开发使用 `reproduction/managed`，其远端对应个人 Fork 的 `main`；本地 `main` 仍跟踪官方基准。不要推送 `reproduce-local`。每轮先更新状态和变更记录，做了实验才追加实验记录，检查后暂存明确文件：

```bash
conda activate la-lora
cd /home/pppe/LoRA/LA-LORA
git branch --show-current
git status
git diff --stat
git diff
# 将实际改动的源码、测试、轻量配置逐个补入，不要使用 git add .
git add -- docs/REPRO_STATUS.md docs/CODE_CHANGES.md
# 本轮确有实验时：git add -- docs/EXPERIMENT_LOG.md
git diff --cached --stat
git diff --cached --name-only
git diff --cached --check
git diff --cached
git commit -m "experiment: record <本轮具体目标与结果>"
# 仅在干净发布分支上，推送到已确认的个人 Fork main
git push origin HEAD:main
git status --short --branch
git log -1 --format='%H %s'
```

实验启动前记录 `git rev-parse HEAD` 与 `git status --short`；若工作区不干净，先归档源码 commit 或明确保留差异，不能把未提交代码的结果归给旧 SHA。推送前还需检查所有待推送历史中的大型对象与敏感内容，不能只看最后一次差异。
