# Contributing

这个仓库是一个 Codex skill 项目。修改时请保持目录结构清晰，并确保别人复制整个文件夹后可以直接使用。

## 修改 `SKILL.md`

- `SKILL.md` 是 skill 的入口说明。
- 修改工作流时，要写清楚触发条件、默认行为、失败恢复方式和最终交付要求。
- 对“分块图片”流程的修改必须保持三步结构：模块完整分块、逐张生成、最终整理。

## 修改脚本

脚本位于 `scripts/`：

- `chatgpt-generate-save-images.js`：负责打开 ChatGPT、上传参考图、等待生成、导出图片。
- `prepare_ip_board_job.py`：负责准备 IP 展板生成任务。

修改脚本后，至少要确认：

- 路径中包含中文时仍能正常运行。
- 输出目录和文件名清晰。
- 失败时能保留会话 URL 或足够的恢复信息。

## 修改参考文档

参考文档位于 `references/`：

- `ip-board-workflow.md`：IP 展板工作流。
- `split-board-workflow.md`：分块图片工作流。
- `pitfalls.md`：常见问题和恢复策略。

参考文档应服务于实际执行，不要写成泛泛介绍。

## 发布检查

发布前建议检查：

1. `README.md` 能说明项目是什么、怎么安装、怎么用。
2. `INSTALL.md` 没有乱码。
3. `SKILL.md` 中“分块图片”的默认流程是逐张上传生成。
4. `scripts/` 和 `references/` 没有缺失。
5. GitHub 文件树没有重复目录，如 `scripts/scripts` 或 `references/references`。
