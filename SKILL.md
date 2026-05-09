---
name: save-mall-comments
description: Open ChatGPT in a headed persistent Playwright/Chrome browser, upload reference images, generate Chinese IP posters/product posters/IP presentation boards, split a complete board into top-to-bottom horizontal block images, split existing block images into left/right halves, and export clean generated PNGs from ChatGPT conversations to a local folder. Use when the user asks to generate 展板/IP展板/IP设计展板, generate IP posters or product posters, upload reference images to ChatGPT, save/download images from a ChatGPT conversation URL, repeat the save_mall_comments workflow, or asks for 分块图片/展板分块/横向分块/左右分块/从上到下拆成4张图片/每个分块再分左右两块. For IP board and split-board jobs, operate ChatGPT on the website rather than using local-only image tools as the final output.
metadata:
  short-description: Generate and save ChatGPT IP posters
---

# save_mall_comments

Use this skill whenever the user wants Codex to operate `https://chatgpt.com/` or a specific ChatGPT conversation, generate an image/poster/IP 展板, upload reference images, and save the final image files locally.

## Default Behavior

- Current default for any "分块图片" request: use the 2026-05-09 module-preserving workflow. Stage 1 saves 4 module-complete blocks. Stage 2 processes those blocks one by one: upload one saved block, generate exactly 2 images for that block, save/export them, then continue with the next block. Stage 3 creates the final Desktop delivery folder. This current default overrides any older batch instruction that says to upload all 4 blocks together.
- Use ChatGPT in a headed persistent Playwright session, not the built-in image generation tool.
- If the user provides a ChatGPT conversation URL, open that exact URL.
- If the user asks to "download/save the image from the conversation", do not send a new prompt; export the existing large image from the page.
- If the user asks to "generate an IP poster" and gives a reference image path, upload the reference image first, then send a short prompt.
- If the user asks to "生成展板" or gives an IP 人物图, 参考展板图, and 设计说明, follow the IP 展板 workflow below.
- If the user asks for 分块图片 / 展板分块 / 从上到下拆成4张 and does not explicitly limit the scope, run the complete three-step split delivery: Stage 1 top-to-bottom 4 images, Stage 2 left/right 8 images, and Stage 3 final archive folder. Do not stop after Stage 1.
- If the user asks to split already-generated block images into left/right halves, upload all block images in one ChatGPT conversation when requested and generate 2 images per uploaded block. Then run a prompt-less export from that conversation and finish with the Stage 3 final archive folder.
- Save output directly to the user-requested folder. For board split jobs (`分块图片` / `展板分块`) with no explicit output folder, the final user-facing archive must be a new folder on the Desktop root, e.g. `C:\Users\Administrator\Desktop\敦煌神女图片分块_最终交付`, not only inside the current workspace.
- Use clear user-facing filenames, preferably Chinese when the user is working in Chinese.

## ChatGPT Profile And Recovery Rules

- Prefer the known logged-in ChatGPT profile:
  `C:\Users\Administrator\AppData\Local\ms-playwright\daemon\541ca920c10645c5\ud-default-chrome`.
- The bundled `chatgpt-generate-save-images.js` already uses that profile before falling back to the newest Playwright session. Do not rely on the newest session when generating boards, because the newest session may be a broken or logged-out browser profile.
- Do not run `playwright-cli close-all` or `playwright-cli kill-all` before generation unless the user explicitly asks you to clean all Playwright browser sessions. Multiple board jobs may be running at the same time, and closing all sessions can break another job's browser window.
- The generation script creates a lock for the selected ChatGPT profile. If several board projects use the same logged-in profile, run the generated job JSON files normally and let the script wait for the lock instead of killing another job.
- Every generation run records the ChatGPT conversation URL in the output folder:
  - `last-conversation-url.txt`
  - `chatgpt-conversations.jsonl`
- If a job is interrupted or the image was generated but not saved, open the recorded conversation URL, for example `https://chatgpt.com/c/69fccdc5-19d8-83ea-b4ea-79f9372bbc7c`, and rerun the same script with a config that has `conversationUrl`, `outputDir`, `expectedCount`, and `filenames`, but no `prompt`. That exports the existing generated image instead of sending a new prompt.
- If the saved PNG is clearly the wrong project, a previous project, or an uploaded source image, do not assume the generation failed. First open the exact recorded `conversationUrl` from `last-conversation-url.txt` / `chatgpt-conversations.jsonl` and export from that conversation. ChatGPT can finish the correct image in the conversation while the automation accidentally grabs an older large image from the page.
- If the user says the images were not saved or says "不是你直接切块保存", immediately treat that as a resave/export request. Reopen the exact ChatGPT conversation and run a prompt-less export config into a new clearly named folder such as `从GPT会话保存_4张分块图`.
- If ChatGPT replies with text claiming images were generated but the page shows no actual image outputs, treat it as a failed generation. Reprompt with explicit "use image generation, do not only reply with text, actual downloadable images must appear" language.
- If ChatGPT generates the correct images but in the wrong order, visually remap and rename the generated files into a final folder instead of trusting the page order.
- Known recovery example: for the 云香灵 / 云白国际 board job on 2026-05-08, the correct ChatGPT conversation to reopen was `https://chatgpt.com/c/69fcd279-98f4-83ea-a546-334d60d65bb5`. Use that exact conversation URL when asked to recover or resave that generated web image.

## Core Workflow

1. Use the known logged-in profile. Usually no manual browser open is needed because the generation script launches this profile itself:

```powershell
$env:PLAYWRIGHT_CHATGPT_PROFILE="C:\Users\Administrator\AppData\Local\ms-playwright\daemon\541ca920c10645c5\ud-default-chrome"
```

If you need to inspect ChatGPT manually, open the same profile in a persistent browser only when no generation job is currently using it:

```powershell
playwright-cli open https://chatgpt.com/ --headed --persistent
```

For an existing conversation, replace the URL with the exact conversation URL.

2. Create a JSON config in the workspace.

For generating with a reference image:

```json
{
  "conversationUrl": "https://chatgpt.com/",
  "outputDir": "C:/Users/Administrator/Desktop/新建文件夹 (2)",
  "expectedCount": 1,
  "filenames": ["国小棉-IP产品宣传海报.png"],
  "referenceImagePaths": ["C:/path/to/reference.png"],
  "prompt": "参考上传图片，生成 1 张好看的中文竖版 IP 产品宣传海报。主体是白色棉花娃娃“国小棉”，保留可爱 3D 潮玩质感，画面干净高级、温暖治愈、有商品宣传感。文字只放：主标题“国小棉”，副标题“软乎乎的棉花小精灵”。请直接生成图片。"
}
```

For saving an existing generated image from a ChatGPT conversation:

```json
{
  "conversationUrl": "https://chatgpt.com/c/CONVERSATION_ID",
  "outputDir": "C:/Users/Administrator/Desktop/新建文件夹 (2)",
  "expectedCount": 1,
  "filenames": ["ChatGPT会话下载图.png"]
}
```

3. Run the bundled script:

```powershell
node C:\Users\Administrator\.codex\skills\save-mall-comments\scripts\chatgpt-generate-save-images.js .\poster-config.json
```

4. Verify the image and the recorded conversation URL:

```powershell
Get-Item -LiteralPath "C:\target\folder\filename.png" | Select-Object FullName,Length,LastWriteTime
Get-Content -LiteralPath "C:\target\folder\last-conversation-url.txt"
```

## Two-Stage Board Split Workflow

2026-05-09 override for board split jobs:

- Stage 1 now starts by saving 4 top-to-bottom block images with complete visual modules preserved. Prefer module boundaries over equal-height cuts when the board layout makes modules obvious. Keep whole panels, titles, captions, decorative separators, and border ornaments inside a single block whenever possible.
- Stage 1 module-preserving crops are valid saved Stage 1 deliverables and are the default inputs for Stage 2. Keep any equal-pixel crops or GPT-generated Stage 1 variants in clearly labeled backup folders.
- Stage 2 must process the 4 Stage 1 blocks one by one by default. Upload exactly one saved block image, ask ChatGPT to generate exactly 2 actual downloadable images for that block, save/export those 2 images, then move to the next block.
- Do not upload all 4 Stage 1 blocks in one ChatGPT conversation unless the user explicitly asks to use the old batch flow.
- Stage 3 final archive behavior stays the same: create one Desktop final delivery folder containing Stage 1 deliverables, Stage 2 deliverables, conversation records, and clearly labeled local backups when present.

Use this end-to-end flow when the user says they want to "分块图片", "继续第二步", "先上下分块再左右分块", or anything equivalent.

Hard completion rule:

- "分块图片" means the full delivery unless the user explicitly asks for only one stage.
- Do not send the final response until all three steps are complete:
  1. Stage 1: GPT conversation-exported 4 top-to-bottom block images.
  2. Stage 2: GPT conversation-exported 8 left/right block images from Stage 1.
  3. Stage 3: one clean final archive folder containing Stage 1 and Stage 2 deliverables, conversation records, and optional clearly labeled exact local backup folders.
- If Stage 1 GPT output is imperfect but usable as the required GPT source, continue to Stage 2 with the GPT-exported files, and also create exact local crop backups for stitch-accurate use. Do not use the backup as a substitute for the GPT delivery unless the user explicitly accepts local-only output.
- If any GPT stage returns only text, too few images, uploaded source images, a four-panel grid, or obvious wrong content, treat that run as failed and retry or export from the recorded conversation. Do not call the job complete while Stage 2 or Stage 3 is missing.

Stage 1: complete board to 4 top-to-bottom blocks:

1. Verify the original complete board image exists.
2. Open ChatGPT through `chatgpt-generate-save-images.js`, upload the complete board image, and send a prompt that explicitly asks ChatGPT to use image generation and create 4 independent horizontal block images: top, upper-middle, lower-middle, bottom.
3. Do not use local crops as final outputs. If helper crops are created, upload them only as references for boundaries.
4. Save the generated images from the ChatGPT conversation. Then run a prompt-less export from the recorded `last-conversation-url.txt` into a final folder such as `从GPT会话保存_4张分块图`.
5. Verify the folder contains 4 real PNG images, not screenshots of text, uploaded source images, or local crops.

Stage 2: 4 block images to 8 left/right block images:

Current default: do not upload all 4 blocks together. Process the Stage 1 blocks one at a time. For each of the 4 saved module-complete blocks, open a separate ChatGPT job/conversation, upload only that one block, generate exactly 2 actual downloadable images based on that block's module content, save/export those 2 images, record the conversation URL, then continue to the next block. The final Stage 2 deliverable is the collected 8 images from the 4 separate runs.

1. Use the 4 GPT-conversation-exported block images from Stage 1 as inputs.
2. Upload all 4 block images in one ChatGPT conversation when the user says this is acceptable.
3. Send a prompt that explicitly requires ChatGPT's image generation capability and says the reply must contain 8 actual downloadable images, not text saying "已裁切".
4. Save the generated images from the ChatGPT conversation. Then run a prompt-less export from the recorded conversation into a final folder such as `第二步_从GPT会话保存_8张左右分块图`.
5. Create a temporary contact sheet when needed to visually check order. If ChatGPT outputs images out of order, remap and rename the generated files into a final folder by actual content. Remove contact sheets and review files before delivery.

Final delivery rules:

- After both stages are done, create one archive folder on the Desktop root named after the board content plus `图片分块` or `图片分块_最终交付`, for example `C:\Users\Administrator\Desktop\绒娘春绾图片分块_最终交付`. If working files were created under the current workspace, copy the final saved image files into this new Desktop folder before responding.
- Put the Stage 1 final GPT conversation-exported contents into `第一次分块_上下4张_GPT会话保存` inside that archive folder.
- Put the Stage 2 final GPT conversation-exported contents into `第二次分块_左右8张_GPT会话保存` inside that archive folder.
- If exact local backups were created, put them into clearly labeled folders such as `备份_本地精确裁切_上下4张` and `备份_本地精确裁切_左右8张`. These are backups, not replacements for the GPT outputs.
- Copy files into the archive folder instead of moving originals, unless the user explicitly asks to move/clean up.
- Verify counts before responding: Stage 1 GPT folder must contain 4 PNGs and Stage 2 GPT folder must contain 8 PNGs. If backup folders are included, verify their counts too.
- Provide the Desktop final archive folder path, Stage 1 conversation URL, and Stage 2 conversation URL.
- Keep final folders clean: only deliverable PNGs plus `last-conversation-url.txt` / run records.
- If ChatGPT only returns text, or images are missing, wrong, or only source uploads, treat the run as failed and regenerate with a stricter prompt.
- For detailed prompt skeletons, naming conventions, and pitfalls, read `references/split-board-workflow.md`.

## Horizontal Split Board Workflow

Use this when the user wants a complete board/poster split into several horizontal block images, especially requests like "分块图片", "从上到下拆成4张", "4张横向长条图", or "可拼回原图".

Hard guardrails:

- Operate ChatGPT in Chrome and generate/export from the ChatGPT website. Do not use local cropping as the final deliverable.
- Local crops are allowed only as optional reference images to help ChatGPT understand the block boundaries. Name them as references internally and never present them as the generated result.
- Upload the complete original board first. If local helper crops exist, upload them after the full board as boundary references.
- Ask ChatGPT to output independent images, not a four-panel grid, not a scaled full board, and not four different designs.
- Save the final files from the ChatGPT conversation with `chatgpt-generate-save-images.js`. If there is any doubt, run a second prompt-less export from the recorded conversation into a folder whose name says it came from the GPT conversation.

Recommended generation config shape:

```json
{
  "conversationUrl": "https://chatgpt.com/",
  "outputDir": "C:/Users/Administrator/Desktop/GPT分块生成",
  "expectedCount": 4,
  "filenames": [
    "01_GPT生成_顶部区域.png",
    "02_GPT生成_上中区域.png",
    "03_GPT生成_下中区域.png",
    "04_GPT生成_底部区域.png"
  ],
  "referenceImagePaths": [
    "C:/path/to/完整展板.png"
  ],
  "maxWaitMs": 1200000,
  "pollMs": 10000,
  "initialWaitMs": 8000,
  "conversationUrlWaitMs": 90000,
  "prompt": "请严格参考我上传的完整展板，生成 4 张独立高清横向长条图片。任务不是重新设计、不是重新排版、不是四宫格。请按原展板从上到下拆成 4 张：1 顶部区域，2 上中区域，3 下中区域，4 底部区域。每张只展示对应区域，不要把完整展板缩小放进去。4 张图上下拼接后应能完整还原原展板。严格保留原图文字、版式、模块位置、装饰、边框、色彩、IP人物形象、表情、服饰、比例和姿态。不要新增、删除、改字、改顺序、改版式。请直接输出 4 张图片。"
}
```

After generation, always verify and, when the user's wording emphasizes saving generated images, resave from the recorded conversation:

```json
{
  "conversationUrl": "https://chatgpt.com/c/CONVERSATION_ID",
  "outputDir": "C:/Users/Administrator/Desktop/从GPT会话保存_4张分块图",
  "expectedCount": 4,
  "filenames": [
    "01_GPT会话生成图_顶部区域.png",
    "02_GPT会话生成图_上中区域.png",
    "03_GPT会话生成图_下中区域.png",
    "04_GPT会话生成图_底部区域.png"
  ],
  "maxWaitMs": 600000,
  "pollMs": 5000,
  "initialWaitMs": 10000
}
```

Verification checklist:

- Read `last-conversation-url.txt` and include the conversation link in the final response.
- List or inspect the saved PNGs in the final output folder, including dimensions and file sizes.
- Check that every split output is landscape (`width > height`) and roughly plausible for its requested block. If any image is portrait, a full-board image, a four-panel grid, or obviously the wrong block, do not present it as complete; resubmit a stricter prompt or tell the user the GPT output needs regeneration.
- If there is a helper crop folder, do not copy it as the final result. Open the final GPT-conversation folder for the user when useful.
- If exported dimensions differ across files, report that they are GPT conversation exports. Do not resize unless the user asks for post-processing.

## IP 展板 Workflow

Use this when the user says “生成展板”, “生成 IP 展板”, “批量生成展板”, or provides an IP 人物图, 参考展板图, and 原始设计说明.

Hard guardrails for IP board jobs:

- If the user provides reference-image paths or attached local image paths, verify every path with `Test-Path` before preparing or generating. If a required reference image is missing, pause and tell the user the exact missing path; do not silently generate without uploading references.
- When valid reference images exist, include them in `referenceImagePaths` and upload them before prompting. Do not substitute a newly generated candidate as the reference unless the user explicitly approves that fallback.
- Preserve the user's requested copy structure. For Chinese IP boards, default to the standard block below when the user asks for "IP 基础档案":

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
```

- Write the design description as a separate `设计说明：` paragraph of about 80 Chinese characters unless the user asks for another length. Keep it concise enough to fit on the board.
- Put the same standard block and the 80-character design description into the prompt sent to ChatGPT; do not compress it into a loose summary before generation.

1. Prepare the local job with `scripts/prepare_ip_board_job.py`. It creates:
   - project files in `output/IP名字_展板`;
   - short design copy, about 75-90 Chinese characters;
   - three prompt files;
   - two single-image ChatGPT job JSON files by default;
   - a Desktop image-only folder named `IP名字展板`, or `_2`, `_3` if needed.

Before running generation, verify the two image roles. 图1 must be the reference board and 图2 must be a distinct IP character image. The prepare script rejects identical paths by default; do not bypass this unless the user explicitly says the same image should serve both roles.

```powershell
python C:\Users\Administrator\.codex\skills\save-mall-comments\scripts\prepare_ip_board_job.py `
  --name "春绢" `
  --identity "绒花技艺守护者・春日花信使" `
  --age "9岁" `
  --tags "温柔治愈、灵动活泼、文化自信、认真负责" `
  --slogan "以绒为花，以金藏春" `
  --description-file "C:\path\description.txt" `
  --reference-image "C:\path\reference.jpg" `
  --ip-image "C:\path\ip.jpg" `
  --output-root "C:\Users\Administrator\Desktop\展板制作工作流\output" `
  --total-candidates 2
```

2. Run each generated `chatgpt_job_版本*_*.json` with `chatgpt-generate-save-images.js`. By default there are only 2 jobs/images; do not generate 6 unless the user explicitly asks for more.
3. Save generated boards only to the Desktop `IP名字展板` folder. Keep source images, prompt files, and JSON configs in the project `output/IP名字_展板` folder.
4. Verify the Desktop folder contains only `展板候选_版本*_*.png`.
5. Show the user the Desktop folder path and candidate images for selection.

For detailed lessons from the IP 展板 workflow, read `references/ip-board-workflow.md`.

## Prompt Style For IP Posters

Keep prompts short. The best default is:

```text
参考上传图片，生成 1 张好看的中文竖版 IP 产品宣传海报。主体是{IP名称/角色描述}，保留可爱 3D 潮玩质感，画面干净高级、温暖治愈、有商品宣传感。文字只放：主标题“{标题}”，副标题“{副标题}”。请直接生成图片。
```

Only add more details when the user explicitly asks for a specific campaign style, sale point, layout, color, or size.

## Script Behavior

The bundled script supports both modes:

- `prompt` present: captures images before prompting, uploads `referenceImagePaths` if provided, sends the prompt, waits for new images, and exports the newest generated images.
- `prompt` absent: opens the conversation URL and exports existing large images already in the page.

It exports image pixels from `main img` elements through canvas, avoiding ChatGPT UI chrome, preview overlays, buttons, and page screenshots. When source image paths are provided, it filters out uploaded source images by exact dimensions so uploaded IP/reference images are not mistaken for generated results.

## Common Pitfalls

Read `references/pitfalls.md` when:

- the user insists the image was not saved;
- a relative path points to the wrong folder;
- the user wants the file from a specific ChatGPT conversation URL;
- ChatGPT generated an image but the script found no images;
- the saved image includes UI controls or is too small.

Read `references/split-board-workflow.md` when:

- the user asks for 分块图片, 展板分块, 横向分块, or 从上到下拆成4张;
- the user asks to split existing block images into 左半块 / 右半块, or generate 8 images from 4 block images;
- the user distinguishes GPT-generated saved images from local crops;
- the user wants already-generated split images saved from a ChatGPT conversation.
