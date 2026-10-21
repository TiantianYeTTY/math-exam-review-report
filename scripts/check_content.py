# Designed by TiantianYe
# -*- coding: utf-8 -*-
"""【内容源自动质检】check_content.py review_content.md [images_dir]
       或【交付 docx 审计】check_content.py --docx 报告.docx
md 模式覆盖交付前质检清单的前半部分（Stage 4 手工项之外的自动化部分）：
  1. $ 配对：逐行 $ 数量为偶数
  2. 禁用字面 grep = 0（错误档案 #7 的字面表）
  3. TXX 残留 = 0（学生可见文本）
  4. 条目顺序：每个条目内第一张图片行必须位于第一行 **答案 之前（错误档案 #18）
  5. 引用的 images/xxx.png 文件真实存在
  6. 独立 --- 横线行 = 0
  7. 条目编号连续性：同一小节内 **（N）** 必须从 1 连续递增，重复/跳号/乱序即违例（错误档案 #21）
  8. 图先于题拦截：条目内第一张图片行之前必须存在题干文本行——任何情况下题目在图前，
     包括无答案/解析的条目（如 5.4 同模式真题题图集，错误档案 #22）
docx 模式（--docx）审计已生成的 Word：
  A. 图片尺寸 ≤ 上限（限高 IMG_MAX_H_CM 默认 5cm，宽度兜底 IMG_MAX_W_CM 默认 16cm，错误档案 #24）
  B. 每个条目头段之前有空段落（题目间换行 1 行，小节首条跳过，错误档案 #23）
  C. 图文同段且图在文字之前（pandoc implicit_figures 并段事故，错误档案 #22）
返回码：0 = 全部通过；1 = 存在违例（逐条打印条目名与行号）
"""
import io, os, re, sys

FORBIDDEN = ['版本：V', 'LaTeX 排版', '原始题图', '配套文件：逐题数据库', '附完整原题',
             '逐条附原题', '题干完整可引', '含题图', '无需回查原卷', '以下给出']
ENTRY_RE = re.compile(r'^\*\*（\d+）|^#### ')          # 3.2/3.3 条目头、变式头
IMG_RE = re.compile(r'^!\[.*\]\(([^)]+)\)')
ANS_RE = re.compile(r'\*\*答案[：:]')

def check_md(md_path):
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

    # 4) 条目内图片行先于答案行 + 图先于题 + 5) 图片文件存在
    md_dir = os.path.dirname(os.path.abspath(md_path))
    entry = '(文件开头)'
    first_answer = None
    has_question = False      # 距上一张图以来是否出现过题干（题干引用块或条目头）
    for i, ln in enumerate(lines, 1):
        # 条目/章节边界：3.2/3.3 条目头、变式头、各级 md 标题、加粗小节头（**压轴一…**、**同型题图集**…；答案行不重置）
        if ENTRY_RE.match(ln) or (re.match(r'^\*\*', ln) and not ANS_RE.search(ln)):
            entry = ln.strip()[:50]
            first_answer = None
            # 编号条目头（**（N）…**，按模板含题目简述）与典型原题头算题干；
            # 其他加粗行（小节头/变式头/解析引导）重置题干标记
            if re.match(r'^\*\*（\d+）', ln) or ln.startswith('**典型原题'):
                has_question = True
            else:
                has_question = False
        elif re.match(r'^#{1,6} ', ln):
            entry = ln.strip()[:50]
            first_answer = None
            has_question = False   # 章节标题不是题干：标题→图之间必须有条目头/题干引用块
        if ln.startswith('>'):
            has_question = True    # 题干引用块
        if ANS_RE.search(ln) and first_answer is None:
            first_answer = i
        m = IMG_RE.match(ln.strip())
        if m:
            img = m.group(1)
            if not has_question:
                problems.append(f'[L{i}] 条目「{entry}」图片前无题干（题干引用块或条目头必须在图前，图先于题）')
            else:
                has_question = False   # 每张图都要有自己的题干，下一张图重新检查
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
    print('全部通过：$ 配对 / 禁用字面 / TXX / 图片-答案顺序 / 图前有题干 / 图片存在 / 横线 / 编号连续')

def check_docx(docx_path):
    from docx import Document
    from docx.oxml.ns import qn
    from docx.shared import Cm
    problems = []
    doc = Document(docx_path)

    # A) 图片尺寸上限（错误档案 #24；限高为主默认 5cm，宽度仅防溢出兜底 16cm）
    max_w = Cm(float(os.environ.get('IMG_MAX_W_CM', '16')))
    max_h = Cm(float(os.environ.get('IMG_MAX_H_CM', '5')))
    for k, sh in enumerate(doc.inline_shapes, 1):
        w, h = sh.width or 0, sh.height or 0
        if w > max_w or h > max_h:
            problems.append(f'图片#{k} 尺寸超上限: {w/360000:.1f}x{h/360000:.1f}cm（上限 {max_w.cm:.0f}x{max_h.cm:.0f}cm）')

    # 条目头判定（与 style_docx.py 保持一致）
    head_re = re.compile(r'^（\d+）|^典型原题')
    def is_entry_head(p):
        if p.style is None or p.style.name in ('Block Text', 'Quote'):
            return False
        txt = p.text.strip()
        if not txt:
            return False
        first = next((r for r in p.runs if r.text.strip()), None)
        if first is None or not first.bold:
            return False
        return bool(head_re.match(txt)) or ('——代表题：' in txt or '——代表题:' in txt)

    # B) 条目头前空段（错误档案 #23）+ C) 图文同段且图在前（错误档案 #22）
    new_section = True
    paras = list(doc.paragraphs)
    for idx, p in enumerate(paras):
        sname = p.style.name if p.style is not None else ''
        if sname.startswith('Heading') or sname == 'Title':
            new_section = True
            continue
        drawing = p._p.find('.//' + qn('w:drawing'))
        if drawing is not None:
            # C) 图文同段（题图必须独立成段），并注明图在前/图在后（八年级 5.4 并段事故，错误档案 #22）
            if p.text.strip():
                first_run = next((r for r in p.runs if r.text.strip()), None)
                if first_run is not None:
                    dr_el = drawing.getparent() if drawing.getparent().tag == qn('w:r') else drawing
                    pos = '图在前' if list(p._p.iter()).index(dr_el) < list(p._p.iter()).index(first_run._element) else '图在后'
                    problems.append(f'段{idx}「{p.text.strip()[:30]}…」图文同段（{pos}）——题图必须独立成段，题目与图分开放')
            new_section = False if not is_entry_head(p) else new_section
            continue
        if is_entry_head(p):
            if not new_section:
                prev = paras[idx - 1] if idx else None
                if prev is None or prev.text.strip():
                    problems.append(f'条目「{p.text.strip()[:30]}…」前缺空段落（题目间必须换行 1 行）')
            new_section = False

    if problems:
        print(f'docx 审计共 {len(problems)} 处违例：')
        for p in problems:
            print(' ', p)
        sys.exit(1)
    print('docx 审计全部通过：图片尺寸上限 / 条目间空行 / 图文并段')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    if sys.argv[1] == '--docx':
        if len(sys.argv) < 3:
            print(__doc__)
            sys.exit(2)
        check_docx(sys.argv[2])
    else:
        check_md(sys.argv[1])
