# save-mall-comments

`save-mall-comments` 是一个 Codex skill，用于通过 ChatGPT 网页和 Playwright/Chrome 自动完成中文 IP 展板、产品海报、分块图片的生成、保存和交付整理。

它的核心用途是把复杂的展板制作流程固化成可复用工作流：上传参考图、调用 ChatGPT 生成图片、导出干净 PNG、记录会话链接，并按最终交付要求整理到桌面文件夹。

## 主要功能

- **IP 展板生成**：根据参考展板、IP 角色图和设计说明生成中文 IP 展板候选图。
- **图片保存**：从 ChatGPT 会话中导出真实图片内容，避免保存到网页 UI 截图。
- **分块图片流程**：当用户说“分块图片”时，默认执行模块完整分块流程。
- **逐张生成**：第二阶段不再一次上传 4 张分块图，而是每次只上传 1 张，生成对应 2 张模块图，保存后再处理下一张。
- **会话记录**：保存 `last-conversation-url.txt` 和 `chatgpt-conversations.jsonl`，方便恢复和重新导出。
- **本地备份**：在需要时生成本地精确裁切备份，便于核对拼接和模块完整性。

## 默认“分块图片”流程

现在只要用户说“分块图片”，默认执行以下三步：

1. **第一步：模块完整分块**
   - 按画面内容模块完整性保存 4 张分块图。
   - 优先保证标题、边框、人物、产品展示、说明文字等完整，不机械等分。

2. **第二步：逐张上传生成**
   - 使用第一步保存的 4 张分块图作为输入。
   - 每次只上传 1 张分块图到 ChatGPT。
   - 每张分块图生成 2 张对应模块图。
   - 一共执行 4 次，最终得到 8 张 GPT 生成模块图。

3. **第三步：最终交付**
   - 在桌面创建最终交付文件夹。
   - 包含第一步分块图、第二步 GPT 生成图、会话记录、本地备份。

## 安装方法

把整个 `save-mall-comments` 文件夹复制到目标机器的 Codex skills 目录：

```text
%USERPROFILE%\.codex\skills\save-mall-comments
```

安装后重启 Codex，或开启一个新的 Codex 会话，即可识别这个 skill。

## 使用方式

在 Codex 中直接提出需求，例如：

```text
分块图片
```

或：

```text
参考这张图生成 IP 展板
```

当需求匹配本 skill 的说明时，Codex 会读取 `SKILL.md` 并按其中流程执行。

## 目录结构

```text
save-mall-comments/
├── SKILL.md                         # skill 主说明文件
├── INSTALL.md                       # 安装说明
├── README.md                        # 项目说明
├── agents/
│   └── openai.yaml                  # agent 配置
├── references/
│   ├── ip-board-workflow.md         # IP 展板流程参考
│   ├── pitfalls.md                  # 常见问题和恢复策略
│   └── split-board-workflow.md      # 分块图片流程参考
└── scripts/
    ├── chatgpt-generate-save-images.js
    └── prepare_ip_board_job.py
```

## 环境要求

- 已安装 Codex，并支持本地 skills。
- 目标机器能打开 ChatGPT 网页。
- ChatGPT 账号已在对应浏览器配置中登录。
- 本机有可用的 Playwright/Chrome 环境。
- Windows 环境下默认使用 `%USERPROFILE%` 路径。

## 常见问题

### GitHub 上别人怎么安装？

下载整个仓库，把 `save-mall-comments` 文件夹复制到：

```text
%USERPROFILE%\.codex\skills\save-mall-comments
```

然后重启 Codex 或开启新会话。

### ChatGPT 没有登录怎么办？

先在目标机器上用对应浏览器打开 ChatGPT 并登录。登录完成后重新运行任务。

### 图片没有保存下来怎么办？

查看输出目录里的 `last-conversation-url.txt`，重新打开该 ChatGPT 会话，再执行无提示词导出流程。

### 分块不完整怎么办？

当前默认流程要求第一步按模块完整性分块。若 GPT 生成结果边界不理想，应优先保留本地模块完整分块作为边界参考，再逐张重新生成。

### 可以直接把 4 张分块图一次上传吗？

默认不可以。当前标准流程是逐张上传：1 张输入生成 2 张输出，连续执行 4 次。只有用户明确要求旧批量流程时才一次上传 4 张。

## License

MIT License. See `LICENSE` for details.
