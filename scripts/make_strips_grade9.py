# Designed by TiantianYe
# 【参考实现·九年级】逐题图片条带生成器：按题切分 md、每题图片拼带标签条带（WMF 先 wmf2gd 渲染、透明图白底合成）。
# 路径为九年级工作区硬编码，复用时改 MD_DIR/MEDIA_DIR/OUT_DIR 三个常量。
# -*- coding: utf-8 -*-
"""九年级逐题图片条带生成器
把每道题引用的媒体（wmf 渲染 png + 原生 png）垂直拼成一张带标签条带，
供读图转写公式与题图。产出 strips_grade9/{paper}_q{n}.png + manifest.json
"""
import os, re, json, glob
from PIL import Image, ImageDraw, ImageFont

MD_DIR = "/Users/tiantianye/Documents/初中数学上半学期期中考试梳理/.workbuddy/analysis/extracted_grade9"
MEDIA_DIR = "/Users/tiantianye/Documents/初中数学上半学期期中考试梳理/.workbuddy/analysis/media_extract/grade9"
OUT_DIR = "/Users/tiantianye/Documents/初中数学上半学期期中考试梳理/.workbuddy/analysis/strips_grade9"
os.makedirs(OUT_DIR, exist_ok=True)

FONT = None
for p in ["/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/HelveticaNeue.ttc"]:
    if os.path.exists(p):
        FONT = ImageFont.truetype(p, 18)
        break

IMG_RE = re.compile(r'!\[[^\]]*\]\((T\w+/media/[^)\s]+)\)')

def find_paper_file(pid):
    """优先原卷版(_y，题干完整)，否则解析版"""
    if os.path.exists(os.path.join(MD_DIR, f"{pid}_y.md")):
        return os.path.join(MD_DIR, f"{pid}_y.md"), "_y"
    if os.path.exists(os.path.join(MD_DIR, f"{pid}.md")):
        return os.path.join(MD_DIR, f"{pid}.md"), ""
    return None, None

def split_questions(md_text):
    """按行首题号切分：支持 '**1．C**' '1．' '1\\.' '1．（本题4分）' '    1．如图' 等"""
    lines = md_text.split("\n")
    qstarts = []
    for i, ln in enumerate(lines):
        m = re.match(r'^\s*>?\s*\**\(?((?:2[0-9]|1[0-9]|[1-9]))\\?[．\.、]\s*(（本题|（\d+分）|\(|【)?', ln)
        if m and not re.match(r'^\s*\**\d+\\?[．\.、]\s*本试卷', ln):
            qstarts.append(i)
    # 同号取最后一次出现（注意事项1/2/3在真实题目前，真实题号优先）
    last = {}
    order = []
    for i in qstarts:
        m = re.match(r'^\s*>?\s*\**\(?(\d{1,2})', lines[i])
        n = int(m.group(1))
        if n not in last:
            order.append(n)
        last[n] = i
    qs = []
    for idx, i in enumerate(qstarts):
        m = re.match(r'^\s*>?\s*\**\(?(\d{1,2})', lines[i])
        n = int(m.group(1))
        if last[n] != i:
            continue  # 非最后一次出现，丢弃（其内容并入下一块边界之外的注意事项块）
        end = qstarts[idx+1] if idx+1 < len(qstarts) else len(lines)
        qs.append((n, "\n".join(lines[i:end])))
    qs.sort(key=lambda x: x[0])
    return qs

def build_strip(pid, qno, texts, media_base, out_path):
    """texts: list of md fragments (question + its images); 拼接全部图片"""
    cells = []
    for frag in texts:
        for m in IMG_RE.finditer(frag):
            rel = m.group(1)
            path = None
            for cand in [rel + ".png", rel]:  # wmf->wmf.png 优先
                fp = os.path.join(MEDIA_DIR, cand)
                if os.path.exists(fp) and os.path.getsize(fp) > 100:
                    path = fp
                    break
            if not path:
                continue
            tag = os.path.basename(rel).replace(".wmf", "").replace(".png", "")
            cells.append((path, tag))
    if not cells:
        return 0
    W = 900
    imgs = []
    total_h = 0
    for path, tag in cells:
        try:
            im = Image.open(path)
            if im.mode in ("RGBA", "LA", "P"):
                im = im.convert("RGBA")
                bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
                im = Image.alpha_composite(bg, im)
            im = im.convert("RGB")
        except Exception:
            continue
        # 放大小图
        if im.width < 700:
            scale = min(2.0, 760 / max(im.width, 1))
            im = im.resize((max(1, int(im.width*scale)), max(1, int(im.height*scale))), Image.LANCZOS)
        if im.width > 860:
            scale = 860 / im.width
            im = im.resize((860, int(im.height*scale)), Image.LANCZOS)
        label_h = 22
        cell = Image.new("RGB", (W, im.height + label_h + 6), "white")
        d = ImageDraw.Draw(cell)
        d.rectangle([0, 0, 6, cell.height], fill=(200, 30, 30))
        if FONT:
            d.text((12, 2), f"{tag}", fill=(180, 0, 0), font=FONT)
        cell.paste(im, (10, label_h))
        imgs.append(cell)
        total_h += cell.height + 8
    if not imgs:
        return 0
    sheet = Image.new("RGB", (W, total_h), "white")
    y = 0
    for c in imgs:
        sheet.paste(c, (0, y))
        y += c.height + 8
    sheet.save(out_path)
    return len(imgs)

def process(pid):
    md_path, suf = find_paper_file(pid)
    if not md_path:
        print(f"{pid}: md 不存在")
        return
    text = open(md_path, encoding="utf-8").read()
    qs = split_questions(text)
    manifest = {}
    for qno, qtext in qs:
        strip_path = os.path.join(OUT_DIR, f"{pid}_q{qno}.png")
        n = build_strip(pid, qno, [qtext], MEDIA_DIR, strip_path)
        manifest[str(qno)] = dict(
            text=qtext[:4000], n_images=n,
            strip=os.path.basename(strip_path) if n else None,
        )
    with open(os.path.join(OUT_DIR, f"{pid}_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    n_with = sum(1 for v in manifest.values() if v["n_images"])
    print(f"{pid}: {len(qs)} 题, 有图题 {n_with}")

if __name__ == "__main__":
    import sys
    for pid in sys.argv[1:]:
        process(pid)
