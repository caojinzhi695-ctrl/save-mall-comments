# IP 展板网页端生成工作流

Use this reference when the user wants ChatGPT website generation for IP 展板, not OpenAI API calls.

## End-to-End Flow

1. Collect inputs:
   - IP 名称
   - IP 身份
   - 物种
   - 年龄, default `8岁`
   - 性格标签, generate 3-5 if absent
   - Slogan, generate one if absent
   - 原始设计说明
   - 图1 参考展板图片 path
   - 图2 IP 人物图片 path
   - Verify each image path exists with `Test-Path` before generating. If any user-provided reference path is missing, stop and report the exact missing path instead of generating without it.
   - Verify these are not the same file. Do not use the reference board as the IP image. If the only available image is a full board, pause and ask for an independent IP character image.
2. Run `scripts/prepare_ip_board_job.py`.
3. The script writes project materials to `output/IP名字_展板` and creates a Desktop folder named `IP名字展板`.
4. Run every generated `chatgpt_job_版本*_*.json` through `scripts/chatgpt-generate-save-images.js`. The default is 2 total generated board images.
5. Verify the Desktop folder contains generated board PNGs only.

## Folder Policy

- Project folder: `output/IP名字_展板`
  - Keep prompts, short design copy, copied source images, JSON job configs, and README here.
- Desktop folder: `Desktop/IP名字展板`
  - Keep only generated board images here.
  - If the folder exists, create `IP名字展板_2`, `IP名字展板_3`, etc.

## Prompt Lessons

- Start with: `请不要输出分析过程、说明文字或排版建议，直接生成图片。`
- Keep the design description short, about half of a 150-character board paragraph, usually 75-90 Chinese characters.
- If the user asks for a standard IP dossier, preserve this exact Chinese copy structure in the prompt and generated board:

```text
一、IP 基础档案

姓名：
{中文名（拼音） / 英文名：English Name}

身份：
{身份}

物种：
{物种（补充说明）}

年龄：
{外观年龄｜实际/能量年龄}

性格标签：
{标签1、标签2、标签3、标签4、标签5}

核心 Slogan：
「{Slogan}」

设计说明：
{约80字，单独成段}
```

- Do not rewrite the dossier into a loose paragraph when prompting ChatGPT. Keep labels, line breaks, punctuation, and the user's wording as close as possible.
- Default to 2 total candidate board images. Generate more only when the user explicitly asks.
- Run each candidate as a separate single-image job. ChatGPT website is more reliable with one generated image per prompt than asking for multiple images in one message.
- Preserve the required image roles:
  - 图1 is the reference board layout.
  - 图2 is the IP character image.
- Keep version endings distinct:
  - 版本 1: close to the reference layout.
  - 版本 2: more design-oriented while keeping the reference structure.
  - 版本 3: more lively and youth-oriented while preserving the IP style.

## Browser Lessons

- Always start with `playwright-cli close-all`.
- If Chrome says the profile is already open, close stale Playwright sessions and rerun the Node script; do not kill normal user Chrome windows.
- If ChatGPT asks for login, CAPTCHA, account choice, or permissions, pause and let the user handle it.
- Wait longer for board generation than poster generation. Use `maxWaitMs` around 15 minutes and `pollMs` around 15 seconds.
- If a status file says `Creating an IP board...`, ChatGPT accepted the prompt but may still be generating or stuck.

## Save/Export Lessons

- Do not save screenshots. Export actual `main img` pixels through canvas.
- Uploaded source images can appear as new `main img` elements. Filter them out by exact dimensions of the uploaded files.
- If a saved PNG has the same dimensions as the uploaded IP image or reference image, inspect it. It may be a source image, not a generated board.
- The final success check is visual: open at least one saved PNG and confirm it is a complete board, not the uploaded character.

## Role Verification Lesson

Do not infer image roles from filenames alone. Open or inspect the provided images before preparing the job:

- If both generated copies in the project output have the same byte length or the same source path, the job is wrong.
- If `chatgpt_job_*.json` has two identical `referenceImagePaths`, stop and regenerate the job.
- If the user provides a board image plus an unrelated IP image, warn about the mismatch before generation rather than silently substituting the board for the IP image.

## Current Reliable Command Pattern

```powershell
playwright-cli close-all
node C:\Users\Administrator\.codex\skills\save-mall-comments\scripts\chatgpt-generate-save-images.js "C:\path\to\chatgpt_job_版本1_01.json"
```
