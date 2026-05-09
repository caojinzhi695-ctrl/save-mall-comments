const fs = require("fs");
const os = require("os");
const path = require("path");

const playwrightCore = "C:/Users/Administrator/AppData/Roaming/npm/node_modules/@playwright/cli/node_modules/playwright-core";
const { chromium } = require(playwrightCore);
const DEFAULT_CHATGPT_PROFILE = "C:/Users/Administrator/AppData/Local/ms-playwright/daemon/541ca920c10645c5/ud-default-chrome";

function readConfig() {
  const configPath = process.argv[2];
  if (!configPath) {
    throw new Error("Usage: node chatgpt-generate-save-images.js <config.json>");
  }
  const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
  config.__configPath = path.resolve(configPath);
  config.__configDir = path.dirname(config.__configPath);
  return config;
}

function newestSessionProfile() {
  const base = path.join(process.env.LOCALAPPDATA || "", "ms-playwright", "daemon");
  const candidates = [];
  if (!fs.existsSync(base)) return undefined;

  for (const daemon of fs.readdirSync(base)) {
    const dir = path.join(base, daemon);
    if (!fs.statSync(dir).isDirectory()) continue;
    for (const file of fs.readdirSync(dir)) {
      if (!file.endsWith(".session")) continue;
      try {
        const session = JSON.parse(fs.readFileSync(path.join(dir, file), "utf8"));
        const userDataDir = session.browser && session.browser.userDataDir;
        if (session.cli && session.cli.persistent && userDataDir && fs.existsSync(userDataDir)) {
          candidates.push({
            userDataDir,
            timestamp: session.timestamp || fs.statSync(path.join(dir, file)).mtimeMs,
          });
        }
      } catch {
        // Ignore stale or partial session files.
      }
    }
  }

  candidates.sort((a, b) => b.timestamp - a.timestamp);
  return candidates[0] && candidates[0].userDataDir;
}

function resolveProfileDir(config) {
  const candidates = [
    config.profileDir,
    process.env.PLAYWRIGHT_CHATGPT_PROFILE,
    fs.existsSync(DEFAULT_CHATGPT_PROFILE) ? DEFAULT_CHATGPT_PROFILE : undefined,
    newestSessionProfile(),
  ].filter(Boolean);
  return candidates[0] && path.resolve(candidates[0]);
}

function lockPathForProfile(profileDir) {
  const key = Buffer.from(path.resolve(profileDir).toLowerCase()).toString("base64url");
  return path.join(os.tmpdir(), `chatgpt-profile-${key}.lock`);
}

function processExists(pid) {
  if (!pid) return false;
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

function readLock(lockPath) {
  try {
    return JSON.parse(fs.readFileSync(lockPath, "utf8"));
  } catch {
    return undefined;
  }
}

async function sleep(ms) {
  await new Promise(resolve => setTimeout(resolve, ms));
}

async function acquireProfileLock(profileDir, config) {
  if (config.profileLock === false) {
    return { release() {} };
  }

  const lockPath = lockPathForProfile(profileDir);
  const startedAt = Date.now();
  const waitMs = config.lockWaitMs || 2 * 60 * 60 * 1000;
  const staleMs = config.lockStaleMs || 3 * 60 * 60 * 1000;
  const payload = {
    pid: process.pid,
    profileDir,
    configPath: config.__configPath,
    outputDir: config.outputDir,
    conversationUrl: config.conversationUrl,
    startedAt: new Date().toISOString(),
  };

  while (Date.now() - startedAt < waitMs) {
    try {
      const fd = fs.openSync(lockPath, "wx");
      fs.writeFileSync(fd, JSON.stringify(payload, null, 2), "utf8");
      fs.closeSync(fd);
      return {
        release() {
          const current = readLock(lockPath);
          if (current && current.pid === process.pid) {
            fs.rmSync(lockPath, { force: true });
          }
        },
      };
    } catch (error) {
      if (error.code !== "EEXIST") throw error;
      const current = readLock(lockPath);
      const lockAgeMs = current && current.startedAt ? Date.now() - Date.parse(current.startedAt) : staleMs + 1;
      if (!current || !processExists(current.pid) || lockAgeMs > staleMs) {
        fs.rmSync(lockPath, { force: true });
        continue;
      }
      console.log(`Waiting for ChatGPT profile lock held by pid=${current.pid}: ${lockPath}`);
      await sleep(config.lockPollMs || 5000);
    }
  }

  throw new Error(`Timed out waiting for ChatGPT profile lock: ${lockPath}`);
}

async function largeImages(page) {
  return await page.locator("main img").evaluateAll(imgs => {
    const bySrc = new Map();
    for (const img of imgs) {
      const src = img.currentSrc || img.src;
      const rect = img.getBoundingClientRect();
      const item = {
        src,
        width: img.naturalWidth,
        height: img.naturalHeight,
        boxArea: rect.width * rect.height,
      };
      if (!src || item.width < 300 || item.height < 300) continue;
      const existing = bySrc.get(src);
      if (!existing || item.boxArea > existing.boxArea) bySrc.set(src, item);
    }
    return [...bySrc.values()];
  });
}

async function submitPrompt(page, prompt) {
  const roleBox = page.getByRole("textbox", { name: "与 ChatGPT 聊天" });
  const fallback = page.locator("#prompt-textarea.ProseMirror, div[role='textbox'][contenteditable='true']").last();
  const editor = await roleBox.count().then(count => count ? roleBox : fallback);
  await editor.waitFor({ state: "visible", timeout: 60000 });
  await editor.click();
  await page.keyboard.insertText(prompt);

  const send = page.locator("button[data-testid='send-button'], button[aria-label*='发送'], button[aria-label*='Send']").last();
  if (await send.count()) {
    await send.click();
  } else {
    await page.keyboard.press("Enter");
  }

  await page.waitForFunction(text => document.body.innerText.includes(text), prompt.slice(0, 40), { timeout: 30000 });
}

async function waitForConversationUrl(page, timeoutMs = 90000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const url = page.url();
    if (/^https:\/\/chatgpt\.com\/c\//.test(url)) return url;
    await page.waitForTimeout(2000);
  }
  return page.url();
}

function resolveReferenceImagePaths(config) {
  const rawPaths = config.referenceImagePaths || config.referenceImages || [];
  const paths = Array.isArray(rawPaths) ? rawPaths : [rawPaths];
  return paths
    .filter(Boolean)
    .map(item => path.isAbsolute(item) ? item : path.resolve(config.__configDir || process.cwd(), item));
}

function imageDimensionsFromFile(imagePath) {
  const buffer = fs.readFileSync(imagePath);
  const ext = path.extname(imagePath).toLowerCase();

  if (ext === ".png" && buffer.toString("ascii", 1, 4) === "PNG") {
    return {
      width: buffer.readUInt32BE(16),
      height: buffer.readUInt32BE(20),
    };
  }

  if ((ext === ".jpg" || ext === ".jpeg") && buffer[0] === 0xff && buffer[1] === 0xd8) {
    let offset = 2;
    while (offset < buffer.length) {
      if (buffer[offset] !== 0xff) break;
      const marker = buffer[offset + 1];
      const length = buffer.readUInt16BE(offset + 2);
      if (
        marker === 0xc0 ||
        marker === 0xc1 ||
        marker === 0xc2 ||
        marker === 0xc3 ||
        marker === 0xc5 ||
        marker === 0xc6 ||
        marker === 0xc7 ||
        marker === 0xc9 ||
        marker === 0xca ||
        marker === 0xcb ||
        marker === 0xcd ||
        marker === 0xce ||
        marker === 0xcf
      ) {
        return {
          height: buffer.readUInt16BE(offset + 5),
          width: buffer.readUInt16BE(offset + 7),
        };
      }
      offset += 2 + length;
    }
  }

  if (ext === ".webp" && buffer.toString("ascii", 0, 4) === "RIFF" && buffer.toString("ascii", 8, 12) === "WEBP") {
    const chunk = buffer.toString("ascii", 12, 16);
    if (chunk === "VP8X") {
      return {
        width: 1 + buffer.readUIntLE(24, 3),
        height: 1 + buffer.readUIntLE(27, 3),
      };
    }
    if (chunk === "VP8 ") {
      return {
        width: buffer.readUInt16LE(26) & 0x3fff,
        height: buffer.readUInt16LE(28) & 0x3fff,
      };
    }
    if (chunk === "VP8L") {
      const bits = buffer.readUInt32LE(21);
      return {
        width: 1 + (bits & 0x3fff),
        height: 1 + ((bits >> 14) & 0x3fff),
      };
    }
  }

  return undefined;
}

function filterUploadedSourceImages(images, referenceImagePaths) {
  const sourceDimensions = referenceImagePaths
    .map(imagePath => {
      try {
        return imageDimensionsFromFile(imagePath);
      } catch {
        return undefined;
      }
    })
    .filter(Boolean);

  if (!sourceDimensions.length) return images;
  return images.filter(item => !sourceDimensions.some(dim => dim.width === item.width && dim.height === item.height));
}

async function uploadReferenceImages(page, imagePaths) {
  if (!imagePaths.length) return;

  for (const imagePath of imagePaths) {
    if (!fs.existsSync(imagePath)) {
      throw new Error(`Reference image does not exist: ${imagePath}`);
    }
  }

  let fileInput = page.locator("input[type='file']").last();
  if (!await fileInput.count()) {
    const attachButton = page.locator([
      "button[aria-label*='Attach']",
      "button[aria-label*='Upload']",
      "button[aria-label*='上传']",
      "button[aria-label*='附件']",
      "button[data-testid*='attach']",
      "button[data-testid*='upload']",
    ].join(", ")).last();

    if (await attachButton.count()) {
      await attachButton.click();
      await page.waitForTimeout(1000);
      fileInput = page.locator("input[type='file']").last();
    }
  }

  if (!await fileInput.count()) {
    throw new Error("Could not find ChatGPT file upload input.");
  }

  await fileInput.setInputFiles(imagePaths);
  await page.waitForTimeout(8000);
}

async function exportImageBySrc(page, src, outputPath) {
  const dataUrl = await page.evaluate(async targetSrc => {
    const img = [...document.querySelectorAll("main img")]
      .find(candidate => (candidate.currentSrc || candidate.src) === targetSrc);
    if (!img) throw new Error("Image element disappeared before export");
    if (!img.complete) await img.decode();
    const canvas = document.createElement("canvas");
    canvas.width = img.naturalWidth;
    canvas.height = img.naturalHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0);
    return canvas.toDataURL("image/png");
  }, src);

  const base64 = dataUrl.replace(/^data:image\/png;base64,/, "");
  fs.writeFileSync(outputPath, Buffer.from(base64, "base64"));
}

function appendRunRecord(outputDir, record) {
  fs.mkdirSync(outputDir, { recursive: true });
  const enriched = {
    timestamp: new Date().toISOString(),
    ...record,
  };
  fs.appendFileSync(
    path.join(outputDir, "chatgpt-conversations.jsonl"),
    `${JSON.stringify(enriched, null, 0)}\n`,
    "utf8"
  );
  if (record.conversationUrl) {
    fs.writeFileSync(path.join(outputDir, "last-conversation-url.txt"), `${record.conversationUrl}\n`, "utf8");
  }
}

async function main() {
  const config = readConfig();
  const outputDir = path.resolve(config.outputDir || "generated-posters");
  const filenames = config.filenames || ["poster-1.png", "poster-2.png"];
  const expectedCount = config.expectedCount || filenames.length;
  const profileDir = resolveProfileDir(config);
  if (!profileDir) throw new Error("No persistent Playwright profile found. Run playwright-cli open <url> --headed --persistent first.");

  fs.mkdirSync(outputDir, { recursive: true });
  const profileLock = await acquireProfileLock(profileDir, config);
  let context;
  let page;
  let conversationUrl = config.conversationUrl;

  try {
    context = await chromium.launchPersistentContext(profileDir, {
      channel: config.channel || "chrome",
      headless: false,
      viewport: config.viewport || { width: 1440, height: 1000 },
      args: ["--disable-blink-features=AutomationControlled"],
    });

    page = context.pages()[0] || await context.newPage();
    page.setDefaultTimeout(60000);
    await page.goto(config.conversationUrl || "https://chatgpt.com/", { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(config.initialWaitMs || 8000);

    const before = await largeImages(page);
    const referenceImagePaths = resolveReferenceImagePaths(config);
    if (referenceImagePaths.length) {
      await uploadReferenceImages(page, referenceImagePaths);
    }
    const beforePrompt = await largeImages(page);

    if (config.prompt) {
      await submitPrompt(page, config.prompt);
      conversationUrl = await waitForConversationUrl(page, config.conversationUrlWaitMs || 90000);
      appendRunRecord(outputDir, {
        status: "submitted",
        configPath: config.__configPath,
        profileDir,
        conversationUrl,
        filenames,
      });
    } else {
      conversationUrl = page.url();
    }

    const deadline = Date.now() + (config.maxWaitMs || 8 * 60 * 1000);
    let images = [];
    while (Date.now() < deadline) {
      await page.waitForTimeout(config.pollMs || 10000);
      images = await largeImages(page);
      const newImages = images.filter(item => !beforePrompt.some(old => old.src === item.src));
      if ((config.prompt ? newImages : images).length >= expectedCount) break;
    }

    const sourcePool = config.prompt
      ? filterUploadedSourceImages(
          images.filter(item => !beforePrompt.some(old => old.src === item.src)),
          referenceImagePaths
        )
      : images;
    const selected = sourcePool.slice(-expectedCount);
    if (selected.length < expectedCount) {
      const statusPath = path.join(outputDir, "generation-status.txt");
      fs.writeFileSync(statusPath, await page.locator("body").innerText(), "utf8");
      appendRunRecord(outputDir, {
        status: "image-not-found",
        configPath: config.__configPath,
        profileDir,
        conversationUrl,
        expectedCount,
        foundCount: selected.length,
        statusPath,
        filenames,
      });
      throw new Error(`Found ${selected.length}/${expectedCount} unique images. Saved page text to ${statusPath}`);
    }

    const saved = [];
    for (let i = 0; i < expectedCount; i++) {
      const name = filenames[i] || `poster-${i + 1}.png`;
      const outputPath = path.join(outputDir, name);
      await exportImageBySrc(page, selected[i].src, outputPath);
      saved.push(outputPath);
    }

    const dimensions = selected.map(({ width, height }) => ({ width, height }));
    appendRunRecord(outputDir, {
      status: "saved",
      configPath: config.__configPath,
      profileDir,
      conversationUrl,
      saved,
      dimensions,
    });

    console.log(JSON.stringify({
      saved,
      dimensions,
      conversationUrl,
      profileDir,
    }, null, 2));
  } finally {
    if (context) await context.close().catch(() => {});
    profileLock.release();
  }
}

main().catch(error => {
  console.error(error.stack || error.message);
  process.exit(1);
});
