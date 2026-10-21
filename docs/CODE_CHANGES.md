# 代码与管理变更记录

每轮追加修改文件、原因、内容、算法定义影响、已有实验影响和 commit。分类固定为：环境兼容性修复、Bug 修复、论文算法复现、算法改进、测试及文档修改。混合修改逐项标注；缺少论文逐项对照时不能声明完全等价。

## 2026-10-21：建立复现管理体系（首次本地准备）

- 分类：测试及文档修改 / 仓库管理配置（`setup:`）。
- 对应 Git commit：`1a43153fd26b03659b7bec8642db17fea5d9ce47`，`setup: establish reproducibility project management`，保留在本地 reproduce-local。
- 修改原因：让后续 ChatGPT 审查能快速定位当前代码、已知事实、真实证据与未完成任务，同时防止新数据/权重被误暂存。

| 修改文件 | 修改内容 |
| --- | --- |
| `.gitignore` | 完善缓存、环境、密钥、本地数据、无后缀模型输出、预训练权重、Ray、TensorBoard、训练日志/图表及临时文件规则；保留源码和轻量配置 |
| `AGENTS.md` | 固定授权边界、检查/记录流程、提交消息、文件审查与不破坏历史规则 |
| `docs/PROJECT_OVERVIEW.md` | 唯一总览：论文一手来源、环境、源码地图、阶段、优先级、远程与大型历史处理方案、日常 Git 命令 |
| `docs/REPRO_STATUS.md` | 分开记录历史事实、证据边界、本轮管理状态和未完成机制/性能工作 |
| `docs/EXPERIMENT_LOG.md` | 追溯登记真实历史结果与缺失字段，提供后续追加模板；本轮没有新实验 |
| `docs/CODE_CHANGES.md` | 本记录及后续变更模板 |
| `docs/REPRO_CHECKLIST.md` | 各阶段可检验的验收条件，区分初步通过与严格未验收 |

- 是否改变论文算法定义：否。没有改动任何 Python 源码、DP 实现、训练配置、官方 README 或依赖文件。
- 对已有实验的影响：无运行或数值影响。原有数据、权重、日志、分支与提交历史保留；忽略规则不追溯改变已跟踪文件。历史结果补档不代表已重新验证。
- Git remote：fetch 地址原本正确，个人 Fork 已存在，未重复创建。验证现有 SSH 身份及个人 Fork 读取后，配置 `origin` 的 SSH push 地址；fetch 与 upstream 地址保持原值。此项是本地 `.git/config` 设置，不属于提交文件。
- 大型文件：列出既有 9 个超过 10 MiB 的数据/权重对象，其中 8 个超过 100 MiB；未删除、取消跟踪或重写原提交。待确认干净发布分支方案。
- 当时的推送状态：尚未执行，等待用户确认具体目标及发布方案；远端为官方 `578e49278e731f26d12457dbc3e4bec89d017a3c`。此为历史阶段记录，最新发布状态见下方条目。

### 本轮验证记录

只运行管理和静态检查，不导入训练入口、不启用 GPU、不运行科研单测：

- Git 检查：`git rev-parse --show-toplevel`、`git status --short --branch`、`git branch -vv`、`git remote -v`、`git var GIT_AUTHOR_IDENT` / `GIT_COMMITTER_IDENT`。有效仓库、原分支保留、提交身份可用。
- CLI 检查：`command -v gh`、`gh --version`、`gh auth status`；WSL 没有安装 `gh`。GitHub 连接器读取确认个人 Fork 的关联、默认分支和权限。
- 远端检查：`git ls-remote --symref origin HEAD` 与 GitHub branches API，确认个人 Fork 仅 `main`，SHA 与本地 `origin/main` / 官方 `main` 一致。
- SSH 检查：`ssh -T -o BatchMode=yes -o StrictHostKeyChecking=yes git@github.com` 成功认证为 PPEE523（GitHub 不提供 shell，返回码 1）；SSH `git ls-remote` 成功读取个人 Fork main，再配置其为 origin push 传输。
- 环境检查：读取 Conda 的 JSON 与包 METADATA，没有导入 PyTorch、调用 CUDA 或更改环境。
- 历史审计：`git ls-tree -rl HEAD`、`git rev-list --objects upstream/main` 配合 `git cat-file --batch-check`；官方可达历史 48 个 blob，没有超过 10 MiB 的对象。本地实验提交有大对象，详见总览。
- 敏感信息检查：扫描既有 HEAD 的轻量文本与官方可达历史文本，规则覆盖常见 Token、私钥、凭据 URL 和硬编码敏感赋值；只报告规则/路径，未发现匹配。此结论是规则扫描结果，不是绝对无泄漏保证。
- 静态检查：相对文档链接全部有效；24 项产物忽略、18 项源码/轻量配置保留检查通过；28 个 Python 文件仅经 AST 解析通过，没有导入训练模块或生成缓存。
- 提交前核验：按七文件清单暂存，检查 `git status`、`git diff --stat`、`git diff --cached --stat`、`git diff --cached --name-only`、`git diff --cached --check`；扫描暂存内容的大小与敏感信息。
- 保护范围核验：比较本轮前后 Git 树，既有 91 个路径的对象 ID 不变；本轮只新增管理七文件。未在工作区删除任何已有文件。

## 2026-10-21：按确认方案构造干净发布分支

- 分类：仓库管理配置 / 测试及文档修改（`setup:`）。用户已明确确认目标为现有公开 Fork `PPEE523/LA-LORA-Reproduction` 的 `main`。
- 对应 Git commit：`dd50765c63377aeafeb29e916656082a49e24e7e`，`setup: publish clean reproduction snapshot`，父提交为官方基准。
- 修改文件：AGENTS.md、PROJECT_OVERVIEW、REPRO_STATUS、CODE_CHANGES、REPRO_CHECKLIST，更新确认状态、开发分支与后续命令。EXPERIMENT_LOG 没有新增科研实验。
- 发布清单：以官方 `578e49278e731f26d12457dbc3e4bec89d017a3c` 的完整树为基础，覆盖当前 9 个源码/轻量配置路径及 7 个管理文件，得到 55 文件发布树。9 路径为 `.vscode/settings.json`、`DP_lora.py`、`dirichlet_data.py`、`dp_per_sample.py`、`patch_local.py`、`ray_worker_loader.py`、`test_dp_per_sample.py`、`test_gaussian_filter.py`、`verify_pretrained.py`；它们与原有本地归档内容保持一致。
- 排除内容：43 个本地新增数据、权重、缓存、训练日志、npy 曲线与 TensorBoard 事件。原有官方轻量数据/示例图/日志和上游历史保留。
- 是否改变论文算法定义：否。只转存已有源码 blob，不编辑源码、DP 或训练配置。
- 历史与实物保护：reproduce-local 保持在 `1a43153`；其他旧分支保持原值。切换只更新分支与索引，排除文件留在原路径；切换前后原有 91 文件的 SHA-256 与大小逐个比较通过。
- 验证范围：管理文档、忽略规则、文件清单、源码 blob、完整可达历史的大文件与敏感模式扫描；不运行训练或科研单测。
- 发布状态：已成功普通快进推送到个人 Fork main，具体验证见下条。

## 2026-10-21：首次推送后验证与交接

- 分类：测试及文档修改（`docs:`）。对应 commit 为包含本条的 `docs: record verified GitHub publication`，用 `git log -1 --format='%H %s' -- docs/CODE_CHANGES.md` 定位。
- 修改文件：PROJECT_OVERVIEW、REPRO_STATUS、CODE_CHANGES、REPRO_CHECKLIST；将发布阶段更新为完成，保留初次本地准备时的历史记录。没有新增实验，EXPERIMENT_LOG 不变。
- 实际推送命令：`git -c core.sshCommand='ssh -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=yes' push -u origin reproduction/managed:main`。
- 结果：`578e492..dd50765 reproduction/managed -> main`，退出码 0；本地 reproduction/managed 已跟踪 origin/main。
- 远端核验：GitHub branches API 确认 main 为 `dd50765c63377aeafeb29e916656082a49e24e7e`；递归 tree API 返回树 `0553396dd39e28c225b046c65d0d9819afa17ffd`，55 个文件的路径/mode/blob ID 与本地完全一致，未截断。
- 文件体积：首次发布树 2,622,925 bytes，最大文件为官方 `data/cola/train.csv` 的 1,213,192 bytes。保留官方原有轻量实验材料，没有加入本地 CIFAR 或权重。
- 全历史检查：发布谱系所有 64 个可达 blob 均已扫描（含 11 个二进制对象），无超过 10 MiB 的对象，私钥/常见 Token/凭据 URL/硬编码敏感赋值规则无匹配；该结论为规则检查结果。
- 保护检查：原有 91 个文件共 1,034,836,336 bytes，切换前后 SHA-256 和大小完全一致。旧本地分支全部保留；`417b359` 不是发布分支祖先，官方 `578e492` 是祖先。临时独立索引已清理，没有复制仓库。
- 是否改变论文算法定义 / 实验影响：否；原源码、DP 与训练配置不变。没有运行科研单测、训练或 GPU 实验。
- 本次验证记录提交后，再普通推送本分支至同一 origin/main，并复核最终远端 SHA 与树，保持默认分支可直接审查。

## 既有本地代码快照（追溯登记）

- Commit：`417b359c75bb57134b9baa1879484b87ba17f519`，消息 `reproduce: validate LA-LoRA training and DP components`。
- 这是本轮开始前已经存在的提交，包含代码及大型运行产物；本轮没有修改或重写它。
- 涉及 `DP_lora.py`、`dirichlet_data.py`、新增 `dp_per_sample.py`、`ray_worker_loader.py`、`patch_local.py`、两个 `test_*.py`、`verify_pretrained.py` 及 `.vscode/settings.json`。
- 观察到的改动涉及环境兼容/加载、Ray 数据加载、交替 LoRA、逐样本裁剪和滤波及测试。它们跨多个类别，不能将整个历史提交笼统记为环境修复，也不能未经审计全部判定为论文忠实复现。
- 具体算法定义影响：尚未完成论文/官方代码逐项对照；相关假设列入状态和验收清单。本轮只登记，不补写当时没有保存的修改动机或实验执行 SHA。

## 后续追加模板

```markdown
## YYYY-MM-DD：具体可验证目标

- 分类：环境兼容性修复 / Bug 修复 / 论文算法复现 / 算法改进 / 测试及文档修改。
- 对应 Git commit：实际 SHA，或包含本条记录的 commit 定位方式。
- 修改文件：逐个列出。
- 修改原因：触发问题、证据和预期行为。
- 修改内容：必要实现摘要。
- 是否改变论文算法定义：是/否/待核验；涉及何种假设。
- 对已有实验的影响：哪些结果仍适用，哪些必须重新验证。
- 轻量验证：实际执行命令、结果和未执行项；失败如实记录。
- 实验：如有，链接 EXPERIMENT_LOG 条目；否则明确未开展。
- 发布：远端仓库/分支/SHA 与验证状态，或说明仅本地。
```
