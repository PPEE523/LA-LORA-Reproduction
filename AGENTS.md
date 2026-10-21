# LA-LoRA 仓库协作规则

## 任务边界

1. 修改前先阅读 [PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md) 和 [REPRO_STATUS.md](docs/REPRO_STATUS.md)，再检查 `git status`、相关源码接口及调用链。项目总纲只维护一份，以 PROJECT_OVERVIEW 为准。
2. 算法参考原论文和官方源码。用户负责算法编写与实验；未经本轮明确授权，不改变已验证的算法逻辑、DP 实现、训练配置、数据划分或基线定义。发现问题先记入状态文档。
3. 一次任务聚焦一个可验证目标。区分环境兼容性修复、Bug 修复、论文算法复现、算法改进、测试及文档修改；不要把算法改进计入忠实复现。
4. 每次修改后运行与改动匹配的必要轻量检查，并记录实际命令及结果。文档改动使用链接、差异、忽略规则及文件扫描；代码改动按需使用语法和针对性的 CPU 单元检查。
5. 不自动启动耗时训练或 GPU 实验。不直接导入有数据初始化副作用的 `DP_lora.py` 做文档检查。
6. 不自动下载大型模型或数据集，不自动重装或升级科研环境。
7. 不创建冗余备份、整个仓库副本、无用日志和大型模型快照。不删除已有科研证据。`models/`、`dataset/`、`model.py` 是源码，`model/` 是权重输出。
8. 每轮完成后更新 REPRO_STATUS 与 CODE_CHANGES；开展实验时追加 EXPERIMENT_LOG，不覆盖历史记录。无实验时明确写“未开展实验”，不伪造实验条目。按 REPRO_CHECKLIST 的证据标准决定勾选状态。
9. 明确区分真实运行结果、用户提供的历史结论、静态源码观察、理论预期和未经验证的结论。缺失命令、运行 commit 或日志开关时写“未记录”，不得反推为已验证。当前不得宣称已经完整实现或验证论文的 `(epsilon, delta)-DP` 保证。
10. Git 提交前检查敏感文件和大型文件；扫描发现只报告路径与规则，不输出密钥值。不请求用户提供 Access Token。

## 版本管理

- 保留现有 Git 历史、分支和工作区修改。禁止 `git reset --hard`、强制推送、重写历史、破坏性清理、重新克隆或复制整个仓库。
- `upstream` 指向 `junkangLiu0/LA-LORA`，`origin` 指向个人 Fork。先检查是否已有 Fork，不重复创建。
- 创建公开 Fork 或首次推送前，须取得用户对具体目标仓库的确认；确认一经给出，在同一授权范围内不反复询问。
- 只按明确文件清单暂存，禁止 `git add .`、`git add -A` 或无审查的批量提交。
- 已跟踪的大文件先列出路径、大小、历史影响与处理方案，不直接删除或取消跟踪。`.gitignore` 不会清除既有提交中的大文件；后续新增删除提交也无法移除其祖先中的对象。
- `reproduce-local` 的历史含大型数据和权重，只保留在本地，不推送该分支、不合并其历史到发布分支，不执行 `git push --all` / `git push --mirror`。日常开发使用 `reproduction/managed`，推送命令为 `git push origin HEAD:main`；本地 `main` 仍保留官方基准。具体方案见 PROJECT_OVERVIEW。
- 提交前必须执行：

  ```bash
  git status
  git diff --stat
  git diff --cached --stat
  git diff --cached --name-only
  git diff --cached --check
  ```

- 提交消息使用有意义的 `setup:`、`fix:`、`test:`、`reproduce:`、`experiment:`、`docs:` 前缀，禁用 `update`、`fix code`。
- 每轮以 commit 固定源码与文档快照。记录实验实际运行的源码 SHA；结果归档 commit 可以是另一个 SHA，二者不能混用。文档自身提交可用包含该条目的 commit 定位，避免循环写入自身 SHA。
- 推送后验证远程分支 SHA、文件清单和内容；分别报告默认分支、实验分支和本地状态，不能把本地提交当成已上传。

## 与 ChatGPT 交接

提供个人 Fork 的具体分支/commit 链接，连同 REPRO_STATUS、EXPERIMENT_LOG、CODE_CHANGES。只保留必要指标、错误摘要和可复现命令，不把大量终端输出粘入 Markdown。若默认分支尚未包含最新工作，明确说明。
