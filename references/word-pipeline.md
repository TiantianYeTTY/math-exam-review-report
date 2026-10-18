# Word 生成管线详解

## 管线总览

```
review_content.md（内容源，Markdown+LaTeX）
    │  pandoc -f markdown+pipe_tables -t docx --wrap=none
    ▼
out.docx（公式=OMML，图片=嵌入，表格=原生表）
    │  scripts/style_docx.py（python-docx 后处理）
    ▼
交付 docx（页眉/字体/标题色/空段落间隔/WJ/表格样式）
    │  cp 到交付文件夹
    ▼
质检清单（本文末）
```

环境依赖：/opt/homebrew/bin/pandoc；python-docx（/Users/tiantianye/.venv-html-to-docx/bin/python 已含）。

## style_docx.py 做了什么（逐段说明）

| 步骤 | 内容 | 关键参数 |
|---|---|---|
| 正文样式 | Normal：微软雅黑 10.5pt、行距 1.6、段后 4pt | |
| 标题样式 | Heading 1-4 / Title：微软雅黑加粗、H1/H2 色 #1A237E、H3/H4 色 #212121；**段前距全部为 0**（间隔由空段落负责） | H1 17pt、H2 13pt、H3 11.5pt、H4 11pt |
| 页眉 | 每个 section 的 header 加"Oli教室专用"，9pt #8B97A8 居中，run 级设置 rFonts eastAsia | 每一页都显示 |
| 章节间隔 | 遍历段落：H1/H2 跳过文档第一个标题；每个 Heading 1 前插 2 个空 `<w:p/>`、Heading 2 前插 1 个、Heading 4（变式标题）前插 1 个（H4 跳过首道变式）（addprevious） | 空段落高度 = Normal 行高，即"回车空行" |
| 页边距 | 上 2.3 / 下 2.0 / 左 2.2 / 右 2.2 cm | |
| 表格 | 全边框 single 4 #E0E0E0；表头底纹 #F5F7FA 加粗着色；表内 9.5pt、行距 1.4 | |
| 引用块 | Block Text 样式：10.5pt、左缩进 0.5cm、右 0.3cm、行距 1.5；**无底纹** | 用于原题引用块 |
| 公式后标点 | 遍历 `m:oMath` 的紧邻下一个 `w:r`，若首个 `w:t` 以 。，、；：）开头则前置 U+2060 词连接符 | 防止句号/逗号出现在行首 |
| 输出 | 覆盖保存原文件并打印统计（表格数/段落数/空段落数/WJ 数） | |

## Markdown 内容源约定（决定 pandoc 输出质量）

- 行内公式 `$...$`；重点推导独立成行用 `$$...$$`（每条保持单行）。
- 选择题选项写成 `A\. xxx`（转义句点）并空行分段，防 pandoc fancy_lists 把连续选项行变成编号列表。
- 原题引用块用 `>`，块内含多个小问时用 `>` 空行 + `> 续行` 保持同一引用块。
- 图片：`![alt](images/xxx.png)`，alt 写"卷名 第 X 题题图"；图片文件先放 stage2/images/。
- 表格用 pipe table；表头行必填。
- `# 第一部分` 为 H1、`## 2.1` 为 H2、`#### 变式 N` 为 H4——style 脚本按此识别插空段。

## 生成命令（在工作目录 stage2/ 下）

```bash
pandoc review_content.md -f markdown+pipe_tables -t docx --wrap=none -o ../stage3/报告.docx
python3 <skill>/scripts/style_docx.py ../stage3/报告.docx
cp ../stage3/报告.docx "<交付文件夹>/报告.docx"
```

## 交付前质检清单（全部通过才交付）

1. `$` 配对：逐行 count('$') % 2 == 0 的行数为 0。
2. 禁用字面 grep = 0：`版本：V`、`LaTeX 排版`、`原始题图`、`配套文件：逐题数据库`、`附完整原题`、`逐条附原题`、`题干完整可引`、`含题图`、`无需回查原卷`。
3. 学生可见文本 TXX 残留 = 0（图片内部路径与内部追踪除外）。
4. 独立 `---` 行 = 0；document.xml 中 `<w:pBdr>` = 0。
5. 关键内容抽查（转 docx 后合并 w:t+m:t 提取，注意 pandoc 的 OMML 用 U+2212 减号，匹配前把 − 归一成 -）：七个部分标题、每部分首条代表性内容、每道选择题四选项齐全、引用块条目数符合预期。
6. 图片数 = 预期题图数（unzip 后 ls word/media/）。
7. oMath 数量与 md 公式数量级一致（明显偏少说明有公式未转换）。
8. 页眉：word/header*.xml 含"Oli教室专用"且 document.xml 有 headerReference。
9. styles.xml：Heading1 `w:before="0"`、BlockText 无 shd。
10. 每道引用真题三查留痕：题号 grep 过、选项/题干读图转写过、答案重算过。
11. 条目顺序：每个条目内图片行位于答案行之前（scripts/check_content.py 自动检查，违例输出条目名与行号）。
12. 对账：参与统计卷数 = 源目录卷数 − EXCLUDED 数；questions.csv 行数 = 各卷题数之和；正文所有"N 份/M 题"与数据库一致。

## 常见坑（都是踩过的）

- **pandoc fancy_lists**：未转义的 `A. xxx` 独立成段会被解析为字母编号列表 → 必须写 `A\. xxx`。
- **$$ 与 $ 混排**：内容源生成脚本里对公式做占位保护时，正则要先匹配 `$$...$$` 再匹配 `$...$`（替换是精确子串回填，旧写法也能存活，但显式先 $$ 更安全）。
- **pandoc OMML 减号**：文本提取时是 U+2212（−）不是 ASCII '-'；做内容校验先归一。
- **块级公式 `$$...$$`**：pandoc 转 oMathPara 居中显示；不要在 `$$` 内写中文。
- **~$ 锁文件**：Word/PPT 开着时文件夹里会有 `~$xxx.docx`；重命名/移动文件夹前提醒用户先关闭文件，否则保存错位。
- **python-docx 页眉**：`sec.header.paragraphs[0]` 默认存在；清空旧 run 后 add_run，中文字体必须同时设 rFonts 的 eastAsia。
- **空段落插入**：`<w:p/>` 无 run 即为空行，高度继承 Normal；用 `para._p.addprevious(blank)` 插入。
- **不要在生成链路里重写前言**：前言与所有正文只存在于 review_content.md；任何"重新生成"都从同一份内容源出发，防止把已删元信息带回来。
- **WMF 公式图**：菁优网系 docx 的公式常为 MathType→WMF（单卷可达 500+ 处）。无 LibreOffice 时 `brew install libwmf`，再 `wmf2gd --maxwidth=1600 -t png -o "x.wmf.png" "x.wmf"`（xargs -P 8 并行，约 4700 个 1 分钟内完成）；渲染质量足够读图转写。
- **透明 PNG 全黑**：菁优网题图与公式图多为 RGBA 透明底，读图/拼条带/嵌入前必须 `Image.alpha_composite` 合成白底；PIL 打开 .wmf 会抛 "cannot find loader"，应读 wmf 渲染后的 .wmf.png。EMF 无法用 libwmf 渲染，按上下文推断并标注。
- **pandoc 图片路径漂移**：图片必须真实位于 stage2/images/（拷贝脚本里写绝对路径，防 cwd 漂移把文件拷去别处），pandoc 在 stage2/ 内执行；否则整批 "Could not fetch resource"，图片被替换为 alt 文本且**不报错中断**——生成后必须核对 word/media/ 数量。
- **逐题图片条带**：读题干公式/题图用 scripts/make_strips_grade9.py 的思路——按题切分 md、每题全部图片拼一张带标签条带；题号正则须容忍 `**` 前缀、引用块、缩进，且同号取最后一次出现（注意事项 1/2/3 在真实题目前）。解析版另做一套 j 条带用于答案对质。
- **答案与题图顺序**：内容源条目骨架为"题干→题图→答案→解析"，写完用 scripts/check_content.py 复查（九年级曾出现答案先于题图，用户明确返工）。
- **交付 docx 覆盖保护（用户可能在 Word 里改过）**：任何覆盖/替换交付 docx 的操作前，①查目录下 ~$ 锁文件（有则提醒用户先关闭）；②将现有文件复制到 `.workbuddy/backups/<时间戳>/` 快照；③将现有文件转纯文本与手中基线 diff，发现用户改动 → 停下报告并询问合并方式；④修改优先用 XML 手术（unzip→lxml 改 document.xml→rezip，保留用户已存改动），整卷重建必须以"源↔交付全文等价校验通过"为前提（归一化：去 $/^/_/花括号/引号形态差异/表格线后 difflib）。
- **XML 手术三件套**：克隆段落内现有 run 保 rPr 字体；分数用 `<m:f><m:num>…</m:num><m:den>…</m:den></m:f>` 构造并核对命名空间；锚点用"唯一文本+邻段内容"双重校验防误替换。pandoc plain 输出中复杂公式显示为 $...$ 是正常回退渲染，不是错误。
