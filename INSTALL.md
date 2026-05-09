# save-mall-comments 安装说明

这是一个 Codex skill 文件夹。别人拿到这个仓库后，只需要把整个 `save-mall-comments` 文件夹放到自己的 Codex skills 目录中即可使用。

## 安装路径

Windows 默认路径：

```text
%USERPROFILE%\.codex\skills\save-mall-comments
```

也就是类似：

```text
C:\Users\你的用户名\.codex\skills\save-mall-comments
```

## 安装步骤

1. 下载或复制整个 `save-mall-comments` 文件夹。
2. 确认文件夹内包含 `SKILL.md`、`scripts/`、`references/`、`agents/`。
3. 把整个文件夹复制到 `%USERPROFILE%\.codex\skills\` 下面。
4. 重启 Codex，或开启一个新的 Codex 会话。
5. 在会话中输入“分块图片”等相关需求，Codex 会自动读取并使用这个 skill。

## 默认分块流程

当用户说“分块图片”时，默认执行：

1. 按画面内容模块完整性保存 4 张分块图。
2. 逐张上传分块图，每次只上传 1 张，并生成对应 2 张模块图。
3. 整理最终交付文件夹，包含分块图、GPT 生成图、会话记录和本地备份。

## 依赖环境

- Codex 本地 skills 功能可用。
- 目标机器能访问 ChatGPT 网页。
- ChatGPT 账号已在对应浏览器配置中登录。
- 本机具备 Playwright/Chrome 运行环境。

## 注意事项

- 不要只复制 `SKILL.md`，脚本和参考文档也需要一起复制。
- 如果 ChatGPT 没有登录，生成和导出图片会失败。
- 如果分块边界不理想，应优先检查第一步的模块完整分块图。
