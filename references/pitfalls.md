# Pitfalls

## Do not use the built-in image tool for this workflow

When this skill is triggered, the user expects Codex to open `https://chatgpt.com/` in a browser. Do not satisfy the request with the internal `image_gen` tool unless the user explicitly asks for that fallback.

## Uploaded chat images are not automatically local files

Images attached in the chat are visible to Codex but may not exist at a local filesystem path. If the automation must upload a reference image to ChatGPT, verify the path with `Test-Path` first. If the file does not exist, ask the user to save it locally or use another existing local image.

For IP 展板 jobs, missing reference images are a hard stop when the user expected references to be uploaded. Do not replace missing references with a text-only generation or a generated candidate image unless the user explicitly approves that fallback.

## Preserve standard IP dossier copy

When the user provides a structured block such as `一、IP 基础档案`, keep the labels and line breaks in the prompt. If the user asks for an 80字设计说明, write a separate `设计说明：` paragraph of about 75-90 Chinese characters and include it verbatim in the ChatGPT prompt.

## Relative paths can resolve from the wrong directory

Project scripts may resolve relative reference paths from the project directory, while the user expects them to resolve from the workspace root. Prefer absolute paths for `referenceImagePaths` and `outputDir`.

Bad:

```powershell
.\project\generate.ps1 -ReferenceImagePath .\poster.png
```

If the script resolves from `.\project`, it will look for `.\project\poster.png`.

Better:

```powershell
.\project\generate.ps1 -ReferenceImagePath "C:\Users\Administrator\Desktop\新建文件夹 (2)\poster.png"
```

## Saving from a conversation URL is different from generating

If the user gives a URL like `https://chatgpt.com/c/...` and says to download/save the image inside it, do not generate a new prompt. Create a config with that `conversationUrl`, `expectedCount`, `filenames`, and no `prompt`. The script will export existing large images from the page.

## Wrong project image after a web generation

If a newly saved PNG visibly belongs to a previous project, do not keep regenerating from the ChatGPT home page as the first fix. ChatGPT may have created the requested image in the new conversation, while the automation saved an older large image that was still present in the page state. Open the exact conversation URL recorded for that run, inspect the images in that conversation, and export from that URL with a no-`prompt` config.

Case to remember: the 云香灵 / 云白国际 IP board run on 2026-05-08 saved an 橙小递 image even though the correct web-generation conversation was `https://chatgpt.com/c/69fcd279-98f4-83ea-a546-334d60d65bb5`. For that project, reopen this URL and save from the conversation instead of treating the Desktop PNG as the final result.

## Save to the exact requested folder

Users often mean the root folder they named, not a project subfolder. After saving to a project output directory, copy the final PNG to the requested root folder if needed and verify with `Get-Item`.

## Filename visibility matters

If the user says they cannot find the file, copy another copy with a clear Chinese filename into the requested folder root, then list the root files sorted by `LastWriteTime`.

## Avoid screenshot saves

Do not use page screenshots for final generated images. Screenshots can include ChatGPT UI, clipped panels, or preview overlays. Export the actual image pixels from loaded `img` elements with canvas.

## Image count and dedupe

When generating, compare large images before and after prompting. Save only new images. Dedupe by `img.currentSrc || img.src`. For existing conversations, save the latest large image unless the user asks for multiple.

## Browser/profile issues

Always start with `playwright-cli close-all`. If profile lock errors remain, stop only browser processes whose command line contains `ms-playwright`; do not kill unrelated user browser windows.

## Chinese JSON and PowerShell

Windows PowerShell 5 can misread UTF-8 JSON with Chinese text through `Get-Content -Raw`. In project scripts, read JSON with:

```powershell
[System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)
```

When writing config JSON from PowerShell, use UTF-8 without BOM.
