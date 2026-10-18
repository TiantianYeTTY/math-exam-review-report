# Designed by TiantianYe
# -*- coding: utf-8 -*-
"""【内容源自动质检】check_content.py review_content.md [images_dir]
覆盖交付前质检清单的前半部分（Stage 4 手工项之外的自动化部分）：
  1. $ 配对：逐行 $ 数量为偶数
  2. 禁用字面 grep = 0（错误档案 #7 的字面表）
  3. TXX 残留 = 0（学生可见文本）
  4. 条目顺序：每个条目内第一张图片行必须位于第一行 **答案 之前（错误档案 #18）
  5. 引用的 images/xxx.png 文件真实存在
  6. 独立 --- 横线行 = 0
  7. 条目编号连续性：同一小节内 **（N）** 必须从 1 连续递增，重复/跳号/乱序即违例（错误档案 #21）
用法：python3 check_content.py review_content.md
返回码：0 = 全部通过；1 = 存在违例（逐条打印条目名与行号）
"""
import io, os, re, sys

FORBIDDEN = ['版本：V', 'LaTeX 排版', '原始题图', '配套文件：逐题数据库', '附完整原题',
             '逐条附原题', '题干完整可引', '含题图', '无需回查原卷', '以下给出']
ENTRY_RE = re.compile(r'^\*\*（\d+）|^#### ')          # 3.2/3.3 条目头、变式头
IMG_RE = re.compile(r'^!\[.*\]\(([^)]+)\)')
ANS_RE = re.compile(r'\*\*答案[：:]')

def main(md_path):
    lines = io.open(md_path, encoding='utf-8').read().split('\n')
    problems = []

    # 1) $ 配对
    for i, ln in enumerate(lines, 1):
        if ln.count('$') % 2:
            problems.append(f'[L{i}] $ 配对异常: {ln[:60]}')

    # 2) 禁用字面
    joined = '\n'.join(lines)
    for w in FORBIDDEN:
        if w in joined:
            for i, ln in enumerate(lines, 1):
                if w in ln:
                    problems.append(f'[L{i}] 禁用字面 "{w}"')
                    break

    # 3) TXX 残留（排除图片路径 Txx/media）
    for i, ln in enumerate(lines, 1):
        s = re.sub(r'\(T\w+/media/[^)]*\)', '', ln)
        if re.search(r'\bT\d{2}\b', s):
            problems.append(f'[L{i}] TXX 残留: {ln[:60]}')

    # 4) 条目内图片行先于答案行 + 5) 图片文件存在
    md_dir = os.path.dirname(os.path.abspath(md_path))
    entry = '(文件开头)'
    first_answer = None
    for i, ln in enumerate(lines, 1):
        # 条目/章节边界：3.2/3.3 条目头、变式头、各级 md 标题、加粗小节头（**压轴一…**、**同型题图集**…；答案行不重置）
        if ENTRY_RE.match(ln) or re.match(r'^#{1,6} ', ln) or (re.match(r'^\*\*', ln) and not ANS_RE.search(ln)):
            entry = ln.strip()[:50]
            first_answer = None
        if ANS_RE.search(ln) and first_answer is None:
            first_answer = i
        m = IMG_RE.match(ln.strip())
        if m:
            img = m.group(1)
            if first_answer is not None:
                problems.append(f'[L{i}] 条目「{entry}」图片出现在答案行(L{first_answer})之后')
            if img.startswith('images/'):
                p = os.path.join(md_dir, img)
                if not os.path.exists(p):
                    problems.append(f'[L{i}] 图片不存在: {img}')

    # 6) 独立横线行
    for i, ln in enumerate(lines, 1):
        if re.match(r'^-{3,}\s*$', ln):
            problems.append(f'[L{i}] 独立 --- 横线行')

    # 7) 条目编号连续性：**（N）** 在同一小节内必须 1,2,3,… 连续（错误档案 #21）
    prev_n = None
    run_line = None
    for i, ln in enumerate(lines, 1):
        m = re.match(r'^\*\*（(\d+)）', ln)
        if m:
            n = int(m.group(1))
            if prev_n is not None and n != prev_n + 1:
                problems.append(f'[L{i}] 条目编号不连续：前一「（{prev_n}）」(L{run_line})，此处「（{n}）」')
            if prev_n is None:
                run_line = i
            prev_n = n
        elif re.match(r'^#{1,6} ', ln) or (re.match(r'^\*\*', ln) and not ANS_RE.search(ln)):
            # 小节边界（标题/非答案加粗行）重置编号序列
            prev_n = None
            run_line = None

    if problems:
        print(f'共 {len(problems)} 处违例：')
        for p in problems:
            print(' ', p)
        sys.exit(1)
    print('全部通过：$ 配对 / 禁用字面 / TXX / 图片-答案顺序 / 图片存在 / 横线 / 编号连续')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1])
