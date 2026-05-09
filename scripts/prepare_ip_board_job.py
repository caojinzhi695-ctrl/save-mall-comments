#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Prepare an IP board generation job for ChatGPT website automation.

This script does not call OpenAI APIs. It creates local copy/prompt artifacts
and JSON configs that can be consumed by the existing save-mall-comments
ChatGPT website automation script.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

KEYWORD_TAGS = [
    ("温柔治愈", ["温柔", "治愈", "陪伴", "温暖", "柔软", "柔和"]),
    ("元气满满", ["元气", "活力", "年轻", "阳光", "校园", "青春"]),
    ("亲和可爱", ["可爱", "亲和", "软萌", "童趣", "娃娃"]),
    ("认真负责", ["守护", "负责", "专业", "匠心", "传承"]),
    ("灵动活泼", ["灵动", "活泼", "俏皮", "传播", "社交"]),
    ("文化自信", ["文化", "非遗", "传统", "品牌", "历史"]),
]


def clean_text(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"[ \t]+", " ", value)
    return value.strip()


def clean_value(value: str) -> str:
    return clean_text(value).strip(" 　\t:：\"'“”")


def safe_folder_name(name: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\n\r\t]', "_", name).strip(" .")
    return cleaned or "未命名IP"


def ensure_unique_folder(output_root: Path, folder_name: str) -> Path:
    target = output_root / folder_name
    if not target.exists():
        return target
    index = 2
    while True:
        candidate = output_root / f"{folder_name}_{index}"
        if not candidate.exists():
            return candidate
        index += 1


def default_desktop_dir() -> Path:
    desktop = Path.home() / "Desktop"
    if desktop.exists():
        return desktop
    return Path.cwd()


def validate_image(path_text: str, label: str) -> Path:
    path = Path(path_text).expanduser()
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"{label}不存在：{path}")
    if path.suffix.lower() not in IMAGE_EXTENSIONS:
        allowed = "、".join(sorted(ext.lstrip(".") for ext in IMAGE_EXTENSIONS))
        raise ValueError(f"{label}格式不支持：{path.suffix}。请使用 {allowed}")
    return path.resolve()


def generate_tags(name: str, identity: str, description: str) -> str:
    source = f"{name} {identity} {description}"
    tags: list[str] = []
    for tag, cues in KEYWORD_TAGS:
        if any(cue in source for cue in cues) and tag not in tags:
            tags.append(tag)
    for fallback in ["亲和可爱", "元气满满", "温柔治愈", "认真负责", "富有感染力"]:
        if len(tags) >= 4:
            break
        if fallback not in tags:
            tags.append(fallback)
    return "、".join(tags[:5])


def generate_slogan(name: str, identity: str, description: str) -> str:
    source = f"{identity} {description}"
    if "棉" in source:
        return f"{name}相伴，把温暖带到身边"
    if "花" in source or "春" in source:
        return f"{name}相伴，让美好自然绽放"
    if "非遗" in source or "传承" in source:
        return f"{name}相伴，守护文化之美"
    if "品牌" in source:
        return f"和{name}一起传递品牌温度"
    return f"和{name}一起遇见美好"


def pick_theme(description: str) -> str:
    theme_rules = [
        ("品牌文化", ["品牌", "文化", "理念"]),
        ("非遗传承", ["非遗", "传承", "传统", "匠心"]),
        ("温暖陪伴", ["温暖", "陪伴", "治愈"]),
        ("年轻化传播", ["年轻", "社交", "传播", "校园"]),
        ("文创延展", ["文创", "衍生", "产品", "延展"]),
        ("视觉展示", ["展板", "视觉", "展示"]),
    ]
    hits = [name for name, cues in theme_rules if any(cue in description for cue in cues)]
    if not hits:
        hits = ["角色叙事", "视觉识别", "品牌传播"]
    return "、".join(hits[:3])


def about_short_board_copy(text: str, limit: int = 92) -> str:
    text = clean_text(text)
    if len(text) <= limit:
        return text
    cut = text[:limit]
    for mark in ("。", "；"):
        pos = cut.rfind(mark)
        if pos >= 65:
            return cut[: pos + 1]
    pos = cut.rfind("，")
    if pos >= 65:
        return cut[:pos].rstrip("，；、") + "。"
    return cut.rstrip("，；、") + "。"


def build_design_description(
    name: str,
    identity: str,
    age: str,
    tags: str,
    slogan: str,
    raw_description: str,
) -> str:
    theme = pick_theme(raw_description)
    if any(word in raw_description for word in ["棉", "柔软", "温暖"]):
        visual = "以柔软温暖的视觉语言强化识别"
    elif any(word in raw_description for word in ["花", "绒", "非遗", "传统"]):
        visual = "以文化符号与柔和色彩强化记忆"
    else:
        visual = "以鲜明轮廓和统一色彩建立记忆点"

    text = (
        f"{name}定位为{identity}，围绕{theme}展开塑造。"
        f"角色气质{tags}，{visual}。"
        f"形象亲和精致，适合展板展示、文创延展与社交传播。"
    )
    return about_short_board_copy(text)


def build_profile_block(profile: dict[str, str], design_description: str) -> str:
    return (
        "一、IP 基础档案\n\n"
        f"姓名 “{profile['name']}”\n\n"
        f"身份 “{profile['identity']}”\n\n"
        f"年龄 “{profile['age']}”\n\n"
        f"性格标签 “{profile['tags']}”\n\n"
        f"核心 Slogan “{profile['slogan']}”\n\n"
        "二、设计说明：\n\n"
        f"{design_description}\n"
    )


def build_prompt(
    profile_block: str,
    version: int,
    expected_count: int = 1,
    candidate_index: int = 0,
) -> str:
    endings = {
        1: "请生成第 1 个版本，整体尽量贴近图1的版式结构，保证信息完整清晰。",
        2: "请生成第 2 个版本，整体排版可以和第 1 个版本不同，但仍然参考图1的结构，画面要更有设计感。",
        3: "请生成第 3 个版本，整体排版可以更活泼、更适合年轻化传播，但仍然要保持图2 IP 人物风格一致。",
    }
    count_line = ""
    if expected_count > 1:
        count_line = f"这个版本后续需要生成 {expected_count} 张候选图，每张都必须是一张完整的 IP 展板。\n\n"
    candidate_line = ""
    if candidate_index:
        candidate_line = (
            f"这是版本 {version} 的第 {candidate_index} 张候选图，请保持该版本方向，"
            "但让构图细节、装饰节奏和画面层次与同版本其他候选图有自然差异。\n\n"
        )

    return (
        "请根据我上传的两张图片生成 IP 展板。\n\n"
        "请不要输出分析过程、说明文字或排版建议，直接生成图片。\n\n"
        "图1是参考展板，请参考图1的内容结构、信息层级、版式排版、标题区域、文字模块、装饰元素和整体布局。\n\n"
        "图2是 IP 人物形象，请以图2中的 IP 人物为主视觉，保持人物形象、颜色、服饰、五官、比例和风格一致，不要改变 IP 人物设定。\n\n"
        "请生成一张完整的 IP 展板，内容包含以下文案：\n\n"
        f"{profile_block}\n"
        "设计要求：\n"
        "1. 参考图1的内容和排版。\n"
        "2. 使用图2的 IP 人物作为核心视觉。\n"
        "3. 展板整体风格要和图2的 IP 人物风格一致。\n"
        "4. 保持画面干净、完整、精致。\n"
        "5. 字体清晰，排版有层次。\n"
        "6. 不要出现错别字。\n"
        "7. 不要随意更改 IP 人物形象。\n"
        "8. 不要生成多余人物。\n"
        "9. 不要遮挡 IP 主体。\n"
        "10. 展板适合用于 IP 形象展示、毕业设计展示、品牌视觉展示。\n\n"
        f"{count_line}"
        f"{candidate_line}"
        f"{endings[version]}\n"
    )


def build_readme(
    profile: dict[str, str],
    total_candidates: int,
    board_output_dir: Path,
) -> str:
    return (
        "IP 展板 ChatGPT 网页端生成操作说明\n\n"
        f"IP 名称：{profile['name']}\n"
        f"默认候选图数量：{total_candidates} 张\n\n"
        f"展板图片单独保存位置：{board_output_dir.resolve()}\n"
        "该桌面文件夹只保存最终展板候选图，不放文案、原图或配置文件。\n\n"
        "文件说明：\n"
        "1. 01_IP基础档案与设计说明.txt 是整理后的展板文案。\n"
        "2. 02-04 是三个可复制到 ChatGPT 生图工具的展板提示词。\n"
        "3. 图1_参考展板_原图 是参考版式图片。\n"
        "4. 图2_IP人物_原图 是 IP 人物主视觉图片。\n"
        "5. chatgpt_job_版本*.json 是 Codex 调用 ChatGPT 网页端时使用的任务配置。\n\n"
        "正式生成时：Codex 会打开 https://chatgpt.com/，上传图1和图2，发送提示词，"
        "并将生成的候选展板图保存回本文件夹。若网页要求登录、验证码或权限确认，请先手动完成。\n"
    )


def copy_image(source: Path, output_dir: Path, target_stem: str) -> Path:
    target = output_dir / f"{target_stem}{source.suffix.lower()}"
    shutil.copy2(source, target)
    return target.resolve()


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8", newline="\n")


def create_chatgpt_config(
    output_dir: Path,
    board_output_dir: Path,
    version: int,
    candidate_index: int,
    prompt: str,
    reference_copy: Path,
    ip_copy: Path,
    expected_count: int,
) -> Path:
    filenames = [f"展板候选_版本{version}_{candidate_index:02d}.png"]
    config = {
        "conversationUrl": "https://chatgpt.com/",
        "outputDir": str(board_output_dir.resolve()),
        "expectedCount": expected_count,
        "filenames": filenames,
        "referenceImagePaths": [str(reference_copy), str(ip_copy)],
        "prompt": prompt,
        "maxWaitMs": 15 * 60 * 1000,
        "pollMs": 15000,
    }
    config_path = output_dir / f"chatgpt_job_版本{version}_{candidate_index:02d}.json"
    config_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    return config_path.resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare local artifacts for the IP board ChatGPT website workflow."
    )
    parser.add_argument("--name", required=True, help="IP 名称")
    parser.add_argument("--identity", required=True, help="IP 身份")
    parser.add_argument("--age", default="", help="IP 年龄，默认 8岁")
    parser.add_argument("--tags", default="", help="性格标签，使用顿号分隔")
    parser.add_argument("--slogan", default="", help="核心 Slogan")
    parser.add_argument("--description", default="", help="原始设计说明")
    parser.add_argument("--description-file", default="", help="原始设计说明 txt 路径")
    parser.add_argument("--reference-image", required=True, help="图1参考展板图片路径")
    parser.add_argument("--ip-image", required=True, help="图2 IP 人物图片路径")
    parser.add_argument(
        "--allow-same-image",
        action="store_true",
        help="允许图1和图2使用同一张图片；默认禁止，避免误把参考展板当成 IP 人物图上传",
    )
    parser.add_argument("--output-root", default="output", help="输出根目录，默认 output")
    parser.add_argument(
        "--board-output-root",
        default="",
        help="展板图片单独保存根目录，默认当前用户桌面",
    )
    parser.add_argument(
        "--expected-per-version",
        type=int,
        default=0,
        help="兼容旧流程：每个版本生成几张候选图；默认 0，表示不用旧的三版本批量模式",
    )
    parser.add_argument(
        "--total-candidates",
        type=int,
        default=2,
        help="总共生成几张候选展板图，默认 2",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.expected_per_version < 0:
        print("错误：--expected-per-version 必须大于等于 0", file=sys.stderr)
        return 2
    if args.total_candidates < 1:
        print("错误：--total-candidates 必须大于等于 1", file=sys.stderr)
        return 2

    try:
        raw_description = args.description
        if args.description_file:
            raw_description = Path(args.description_file).read_text(encoding="utf-8")
        raw_description = clean_text(raw_description)
        if not raw_description:
            raise ValueError("原始设计说明不能为空")

        reference_image = validate_image(args.reference_image, "图1参考展板图片")
        ip_image = validate_image(args.ip_image, "图2 IP人物图片")
        if reference_image == ip_image and not args.allow_same_image:
            raise ValueError(
                "图1参考展板图片和图2 IP人物图片不能是同一个文件。"
                "请分别提供参考展板图和独立 IP 人物图；如确实要复用同一张图，请显式添加 --allow-same-image。"
            )

        name = clean_value(args.name)
        identity = clean_value(args.identity)
        age = clean_value(args.age) or "8岁"
        if not age.endswith("岁") and re.fullmatch(r"\d+", age):
            age = f"{age}岁"
        tags = clean_value(args.tags) or generate_tags(name, identity, raw_description)
        slogan = clean_value(args.slogan) or generate_slogan(name, identity, raw_description)

        profile = {
            "name": name,
            "identity": identity,
            "age": age,
            "tags": tags,
            "slogan": slogan,
        }

        output_root = Path(args.output_root).expanduser().resolve()
        output_root.mkdir(parents=True, exist_ok=True)
        output_dir = ensure_unique_folder(output_root, f"{safe_folder_name(name)}_展板")
        output_dir.mkdir(parents=True, exist_ok=False)

        board_output_root = (
            Path(args.board_output_root).expanduser().resolve()
            if args.board_output_root
            else default_desktop_dir().resolve()
        )
        board_output_root.mkdir(parents=True, exist_ok=True)
        board_output_dir = ensure_unique_folder(board_output_root, f"{safe_folder_name(name)}展板")
        board_output_dir.mkdir(parents=True, exist_ok=False)

        reference_copy = copy_image(reference_image, output_dir, "图1_参考展板_原图")
        ip_copy = copy_image(ip_image, output_dir, "图2_IP人物_原图")

        design_description = build_design_description(
            name=name,
            identity=identity,
            age=age,
            tags=tags,
            slogan=slogan,
            raw_description=raw_description,
        )
        profile_block = build_profile_block(profile, design_description)

        prompt_paths: list[str] = []
        config_paths: list[str] = []
        if args.expected_per_version > 0:
            job_plan = [
                (version, candidate_index)
                for version in (1, 2, 3)
                for candidate_index in range(1, args.expected_per_version + 1)
            ]
        else:
            per_version_counts = {1: 0, 2: 0, 3: 0}
            job_plan = []
            for index in range(args.total_candidates):
                version = (index % 3) + 1
                per_version_counts[version] += 1
                job_plan.append((version, per_version_counts[version]))
        total_candidates = len(job_plan)

        write_text(output_dir / "01_IP基础档案与设计说明.txt", profile_block)
        for version in (1, 2, 3):
            prompt = build_prompt(profile_block, version, 1)
            prompt_path = output_dir / f"{version + 1:02d}_展板生成提示词_版本{version}.txt"
            write_text(prompt_path, prompt)
            prompt_paths.append(str(prompt_path.resolve()))
        for version, candidate_index in job_plan:
            config_prompt = build_prompt(
                profile_block,
                version,
                expected_count=1,
                candidate_index=candidate_index,
            )
            config_path = create_chatgpt_config(
                output_dir=output_dir,
                board_output_dir=board_output_dir,
                version=version,
                candidate_index=candidate_index,
                prompt=config_prompt,
                reference_copy=reference_copy,
                ip_copy=ip_copy,
                expected_count=1,
            )
            config_paths.append(str(config_path))

        write_text(
            output_dir / "README_操作说明.txt",
            build_readme(profile, total_candidates, board_output_dir),
        )

        manifest = {
            "ok": True,
            "outputDir": str(output_dir.resolve()),
            "profile": profile,
            "designDescription": design_description,
            "referenceImage": str(reference_copy),
            "ipImage": str(ip_copy),
            "boardOutputDir": str(board_output_dir.resolve()),
            "promptFiles": prompt_paths,
            "chatgptJobFiles": config_paths,
            "expectedImages": total_candidates,
        }
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
