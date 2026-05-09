# Split Board Workflow Notes

Use these notes when a user asks to generate or save horizontal block images from a complete board, especially Chinese requests like "分块图片", "从上到下拆成4张", "按原图分块", or "把 GPT 生成好的保存下来".

## What The User Usually Means

- They want ChatGPT/GPT website generation, not a deterministic local crop.
- They may still expect the four outputs to behave like crops: same visual order, same board content, and able to be stitched back together.
- If they say "保存下来", they usually mean save the generated images from the ChatGPT conversation page, not copy helper files from a local folder.

## Recommended Sequence

This workflow is complete only after three steps are done:

1. Stage 1 creates and prompt-less exports 4 GPT top-to-bottom block images.
2. Stage 2 uses those 4 GPT-exported images to create and prompt-less export 8 GPT left/right block images.
3. Stage 3 copies the final outputs into one clean user-facing archive folder and verifies counts.

Do not stop after Stage 1 unless the user explicitly asked for only top-to-bottom blocks.

Stage 1 sequence:

1. Verify the reference image path with `Test-Path`.
2. If boundaries matter, create temporary/helper local crops only as reference aids. Do not make them the final output.
3. Build a ChatGPT generation JSON with:
   - `conversationUrl: "https://chatgpt.com/"`
   - `expectedCount: 4`
   - clear Chinese filenames in top-to-bottom order
   - `referenceImagePaths` containing the full board first and helper crops afterward if used
   - a prompt saying "不是重新设计/不是四宫格/不是整图缩小/4张独立图片"
4. Run `scripts/chatgpt-generate-save-images.js`.
5. Read the recorded `last-conversation-url.txt`.
6. For final delivery, especially if the user emphasizes "GPT生成好的保存", run a second prompt-less export from that conversation into a folder named like `从GPT会话保存_4张分块图`.
7. Verify files with dimensions and sizes, then open the final folder with Explorer.
8. Check that every final file is landscape (`width > height`) and not a full-board render, four-panel grid, or wrong block. If any file fails this check, regenerate with a stricter prompt or keep a clearly labeled exact local backup, but still continue to Stage 2 with the GPT-exported files if they exist.
9. Continue immediately to Stage 2. Do not send a final response yet.

Stage 2 sequence:

1. Use the Stage 1 prompt-less GPT conversation-exported 4 PNGs as `referenceImagePaths`.
2. Create one ChatGPT job with `expectedCount: 8`.
3. Filename order must be: top-left, top-right, upper-middle-left, upper-middle-right, lower-middle-left, lower-middle-right, bottom-left, bottom-right.
4. Prompt must require 8 actual downloadable images and forbid text-only "already split" replies.
5. Run `chatgpt-generate-save-images.js`, read the recorded conversation URL, then run a prompt-less export into a final Stage 2 folder.
6. Verify the Stage 2 GPT folder contains exactly 8 PNGs. Create a temporary contact sheet when helpful; remove it from the final archive.
7. If ChatGPT returns only text or fewer than 8 images, retry or reopen the recorded conversation and export again. Do not proceed to final response without Stage 2 outputs unless the user approves a local-only fallback.

Stage 3 sequence:

1. Create the final archive folder as a new folder on the Desktop root (for example `C:\Users\Administrator\Desktop\敦煌神女图片分块_最终交付`). Do not leave the only user-facing delivery under the current workspace.
2. Copy Stage 1 GPT prompt-less export files into the Stage 1 subfolder.
3. Copy Stage 2 GPT prompt-less export files into the Stage 2 subfolder.
4. Optionally include exact local crop backup folders when GPT text/layout fidelity is suspect; label them as backups.
5. Verify PNG counts and dimensions.
6. Final response must include the Desktop final archive path and both ChatGPT conversation URLs.

## Final Archive Folder

After Stage 1 and Stage 2 are complete, organize both results into one user-facing archive folder. This is mandatory for a complete "分块图片" job.

Naming:

- Infer a short content name from the board title or main IP name, removing punctuation when reasonable.
- Name the archive folder `{展板内容名}图片分块_最终交付`, for example `绒娘春绾图片分块_最终交付`, and create it directly under `C:\Users\Administrator\Desktop` unless the user explicitly requested a different output folder.
- Inside it, create:
  - `第一次分块_上下4张_GPT会话保存`
  - `第二次分块_左右8张_GPT会话保存`
  - optional `备份_本地精确裁切_上下4张`
  - optional `备份_本地精确裁切_左右8张`

Rules:

- Copy the final Stage 1 GPT-conversation-exported files into `第一次分块_上下4张_GPT会话保存`.
- Copy the final Stage 2 GPT-conversation-exported/remapped files into `第二次分块_左右8张_GPT会话保存`.
- If local exact crops are created because GPT changed text/layout, copy them into backup folders only. Never name local backups as GPT outputs.
- Preserve `last-conversation-url.txt` and run records when present so the generated images can be traced back to ChatGPT.
- Do not include helper crops, temporary contact sheets, failed generations, or text-only response screenshots in the archive.
- Report the PNG counts: Stage 1 should have 4 PNGs, Stage 2 should have 8 PNGs. Backup folders, if present, should also have 4 and 8 PNGs.

PowerShell pattern:

```powershell
$root = "C:\Users\Administrator\Desktop\{展板内容名}图片分块"
$firstDst = Join-Path $root "第一次分块_上下4张"
$secondDst = Join-Path $root "第二次分块_左右8张"
New-Item -ItemType Directory -Force -Path $firstDst, $secondDst | Out-Null
Get-ChildItem -LiteralPath $stage1Final -File | ForEach-Object {
  Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $firstDst $_.Name) -Force
}
Get-ChildItem -LiteralPath $stage2Final -File | ForEach-Object {
  Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $secondDst $_.Name) -Force
}
```

## Stage 1 Config Template

Use this template for the first pass from one complete board to 4 GPT-generated top-to-bottom blocks. Add helper crop paths only if they are clearly marked as references and are not final outputs.

```json
{
  "conversationUrl": "https://chatgpt.com/",
  "outputDir": "C:/Users/Administrator/Desktop/GPT分块生成_初次导出",
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
  "prompt": "请使用 ChatGPT 的图像生成能力直接生成图片文件。请严格参考我上传的完整展板，生成 4 张独立高清横向长条图片。任务不是重新设计，不是重新排版，不是四宫格，也不是把完整展板缩小放进去。请按原展板从上到下拆成 4 张：1 顶部区域，2 上中区域，3 下中区域，4 底部区域。每张图片只展示对应横向分块内容，4 张图上下拼接后应能完整还原原展板。严格保留原图文字、版式、模块位置、装饰、边框、色彩、IP人物形象、表情、服饰、比例和姿态。不要新增、删除、改字、改顺序、改版式。请直接输出 4 张实际图片，不要只回复文字。"
}
```

Then run a prompt-less export from the recorded conversation:

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

## Known Pitfalls

- Do not satisfy the request with local slicing only. Local slicing is useful for boundary references but fails the "go to GPT and generate" requirement.
- Do not stop after the first 4-image split. A complete "分块图片" delivery also includes the second left/right split and a final archive folder.
- Do not present copied helper crops as GPT output. Keep helper-crop folder names separate from final GPT-conversation export folder names.
- The script's prompt mode can save images, but user trust is higher when final files are exported from the recorded conversation URL without a prompt. This also recovers cases where ChatGPT finished generation after the initial script export.
- A prompt-less export saves large images already in the conversation. Use the exact conversation URL from `last-conversation-url.txt` or `chatgpt-conversations.jsonl`.
- ChatGPT may output images with different dimensions. Report the dimensions instead of silently resizing. Only resize/post-process if the user asks.
- ChatGPT may output one block as a portrait image or reorder the generated images. Detect this by checking dimensions and visual order after export; if the shape or order is wrong, resubmit or resave the correct conversation images.
- ChatGPT may create Stage 1 blocks that are aesthetically good but not stitch-accurate. Continue the required GPT Stage 2 from the GPT-exported blocks, and also create exact local backup splits so the user has a precise fallback.
- ChatGPT may not preserve Chinese text perfectly. The prompt must explicitly prioritize text clarity and no changed/missing words, but still warn internally that model image text is less deterministic than local cropping.
- If fewer than four images export, inspect `generation-status.txt` and the conversation page before reprompting. Avoid sending another prompt if the user only asked to save existing generated images.
- ChatGPT may answer with text such as "已裁切为 2 张 PNG 图片：左半块、右半块" while showing no actual images. Treat this as failure. Reprompt with "请使用 ChatGPT 的图像生成能力直接生成图片文件；不要只回复文字；本次回复中必须实际出现可下载的生成图片."
- ChatGPT may generate all requested images but output them in a different order than requested. Make a temporary contact sheet, visually map each generated image to its real content, and copy/rename the generated files into a final folder. Remove the temporary contact sheet before delivery.

## Second-Pass Left/Right Split

Use this when the user already has 4 GPT-generated horizontal block images and asks to split each one into left/right halves, producing 8 images.

Preferred sequence:

1. Use the GPT-conversation-exported 4 block images as inputs, not local helper crops.
2. If the user says all 4 can be uploaded together, create one ChatGPT job with `expectedCount: 8`.
3. Filename order must be:
   - `01-1 ... 顶部区域_左半块`
   - `01-2 ... 顶部区域_右半块`
   - `02-1 ... 上中区域_左半块`
   - `02-2 ... 上中区域_右半块`
   - `03-1 ... 下中区域_左半块`
   - `03-2 ... 下中区域_右半块`
   - `04-1 ... 底部区域_左半块`
   - `04-2 ... 底部区域_右半块`
4. After prompt-mode generation, always run a prompt-less export from the recorded conversation URL into a final folder such as `第二步_从GPT会话保存_8张左右分块图`.
5. Make a quick contact sheet or visual check if needed, but remove temporary review images from the final folder before delivery.

Stage 2 config template:

```json
{
  "conversationUrl": "https://chatgpt.com/",
  "outputDir": "C:/Users/Administrator/Desktop/第二步_GPT强制生图左右分块_初次导出",
  "expectedCount": 8,
  "filenames": [
    "01-1_GPT强制生图_顶部区域_左半块.png",
    "01-2_GPT强制生图_顶部区域_右半块.png",
    "02-1_GPT强制生图_上中区域_左半块.png",
    "02-2_GPT强制生图_上中区域_右半块.png",
    "03-1_GPT强制生图_下中区域_左半块.png",
    "03-2_GPT强制生图_下中区域_右半块.png",
    "04-1_GPT强制生图_底部区域_左半块.png",
    "04-2_GPT强制生图_底部区域_右半块.png"
  ],
  "referenceImagePaths": [
    "C:/path/to/01_GPT会话生成图_顶部区域.png",
    "C:/path/to/02_GPT会话生成图_上中区域.png",
    "C:/path/to/03_GPT会话生成图_下中区域.png",
    "C:/path/to/04_GPT会话生成图_底部区域.png"
  ],
  "maxWaitMs": 1800000,
  "pollMs": 10000,
  "initialWaitMs": 8000,
  "conversationUrlWaitMs": 90000,
  "prompt": "请使用 ChatGPT 的图像生成能力直接生成图片文件。不要只回复文字，不要只列出“左半块/右半块”，不要说“已裁切”但不显示图片；本次回复中必须实际出现 8 张可下载的生成图片。参考我上传的这些图片。上传的 4 张图按顺序分别是：第1张顶部区域、第2张上中区域、第3张下中区域、第4张底部区域。请把每一张上传图片都按左右方向分成 2 张重新生成图片：每张的第 1 张是左半块，第 2 张是右半块。任务不是重新设计，不是重新排版，不是生成不同风格，也不是把整张图缩小放进去。每张生成图只展示对应图片的左右半边内容，左右两张拼接后应能还原对应上传图片。严格保留原图文字、排版、模块位置、装饰、边框、色彩、人物形象、比例和相对位置。不要新增、删除、改字、改顺序、改版式。请一次性直接输出 8 张独立图片，顺序必须是：1 顶部区域左半块，2 顶部区域右半块，3 上中区域左半块，4 上中区域右半块，5 下中区域左半块，6 下中区域右半块，7 底部区域左半块，8 底部区域右半块。不要输出解释文字。"
}
```

Prompt-less export template:

```json
{
  "conversationUrl": "https://chatgpt.com/c/CONVERSATION_ID",
  "outputDir": "C:/Users/Administrator/Desktop/第二步_从GPT会话保存_8张左右分块图",
  "expectedCount": 8,
  "filenames": [
    "01-1_GPT会话保存_顶部区域_左半块.png",
    "01-2_GPT会话保存_顶部区域_右半块.png",
    "02-1_GPT会话保存_上中区域_左半块.png",
    "02-2_GPT会话保存_上中区域_右半块.png",
    "03-1_GPT会话保存_下中区域_左半块.png",
    "03-2_GPT会话保存_下中区域_右半块.png",
    "04-1_GPT会话保存_底部区域_左半块.png",
    "04-2_GPT会话保存_底部区域_右半块.png"
  ],
  "maxWaitMs": 600000,
  "pollMs": 5000,
  "initialWaitMs": 10000
}
```

Prompt skeleton:

```text
请使用 ChatGPT 的图像生成能力直接生成图片文件。不要只回复文字，不要只列出“左半块/右半块”，不要说“已裁切”但不显示图片；本次回复中必须实际出现 8 张可下载的生成图片。
参考我上传的这些图片。上传的 4 张图按顺序分别是：第1张顶部区域、第2张上中区域、第3张下中区域、第4张底部区域。
请把每一张上传图片都按左右方向分成 2 张重新生成图片：每张的第 1 张是左半块，第 2 张是右半块。
任务不是重新设计，不是重新排版，不是生成不同风格，也不是把整张图缩小放进去。
每张生成图只展示对应图片的左右半边内容，左右两张拼接后应能还原对应上传图片。
严格保留原图文字、排版、模块位置、装饰、边框、色彩、人物形象、比例和相对位置。
不要新增、删除、改字、改顺序、改版式。
请一次性直接输出 8 张独立图片，顺序必须是：1 顶部区域左半块，2 顶部区域右半块，3 上中区域左半块，4 上中区域右半块，5 下中区域左半块，6 下中区域右半块，7 底部区域左半块，8 底部区域右半块。不要输出解释文字。
```

## Prompt Skeleton

```text
请严格参考我上传的完整展板，生成 4 张独立高清横向长条图片。
任务不是重新设计，不是重新排版，不是四宫格，也不是把完整展板缩小放进去。
请按原展板从上到下拆成 4 张：1 顶部区域，2 上中区域，3 下中区域，4 底部区域。
每张图片只展示对应横向分块内容，4 张图上下拼接后应能完整还原原展板。
严格保留原图文字内容、排版结构、模块位置、装饰元素、边框、色彩、IP人物形象、表情、配色、服饰、比例和姿态。
不要新增内容，不要删除内容，不要改字，不要改变模块顺序，不要改变版式逻辑。
请直接输出 4 张图片，不要输出解释文字。
```
