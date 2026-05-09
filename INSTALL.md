# save-mall-comments skill 安装说明

把整个 `save-mall-comments` 文件夹复制到目标机器的 Codex skills 目录中：

```text
%USERPROFILE%\.codex\skills\save-mall-comments
```

安装后重启 Codex 或开启新会话即可识别。

当前默认“分块图片”流程：

1. 第一阶段：按画面内容模块完整性保存 4 张分块图。
2. 第二阶段：逐张上传分块图，每次只上传 1 张，生成对应 2 张模块图，保存后再处理下一张，共 4 次生成 8 张。
3. 第三阶段：整理桌面最终交付文件夹，包含分块图、GPT 生成图、会话记录和本地备份。

注意：ChatGPT 网页生成和保存依赖目标机器已登录的 ChatGPT/Playwright 浏览器环境。
