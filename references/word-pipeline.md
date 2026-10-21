# Word 生成管线详解

## 管线总览

```
review_content.md（内容源，Markdown+LaTeX）
    │  pandoc -f markdown+pipe_tables-implicit_figures -t docx --wrap=none
    ▼
out.docx（公式=OMML，图片=普通 inline 段落，表格=原生表）
    │  scripts/style_docx.py（python-docx 后处理）
    ▼
交付 docx（页眉/字体/标题色/空段落间隔/图片限宽/WJ/表格样式）
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
| 题目条目间隔 | 每个条目头段（加粗 `**（N）…**` / `**典型原题…**` / 含"——代表题："的加粗段；引用块内、标题、答案行不算）前插 1 个空段落，小节首条跳过——**所有有题目的地方，每题结束换行 1 行**（硬规则 #17） | 与 H4 变式同款逻辑 |
| 图片限高 | 遍历 inline_shapes：超限图片等比缩小。**以限高为主**（长条形题图不因限宽被压小） | 默认限高 5cm（IMG_MAX_H_CM），宽度仅防溢出兜底 16cm（IMG_MAX_W_CM），硬规则 #18 |
| 图注样式 | 图片行下的全斜体"…题图…"行 → 9pt 灰色 #5A6472、居中、行距 1.2 | 内容源约定见硬规则 #19；不加 keepNext |
| 页边距 | 上 2.3 / 下 2.0 / 左 2.2 / 右 2.2 cm | |
| 表格 | 全边框 single 4 #E0E0E0；表头底纹 #F5F7FA 加粗着色；表内 9.5pt、行距 1.4 | |
| 引用块 | Block Text 样式：10.5pt、左缩进 0.5cm、右 0.3cm、行距 1.5；**无底纹** | 用于原题引用块 |
| 公式后标点 | 遍历 `m:oMath` 的紧邻下一个 `w:r`，若首个 `w:t` 以 。，、；：）开头则前置 U+2060 词连接符 | 防止句号/逗号出现在行首 |
| 输出 | 覆盖保存原文件并打印统计（表格数/段落数/空段落数/WJ 数/缩图数） | |

## Markdown 内容源约定（决定 pandoc 输出质量）

- 行内公式 `$...$`；重点推导独立成行用 `$$...$$`（每条保持单行）。
- 选择题选项写成 `A\. xxx`（转义句点）并空行分段，防 pandoc fancy_lists 把连续选项行变成编号列表。
- 原题引用块用 `>`，块内含多个小问时用 `>` 空行 + `> 续行` 保持同一引用块。
- 图片：`![alt](images/xxx.png)`，alt 写"卷名 第 X 题题图"（进图片替代文字，不显示）；**pandoc 必须禁用 implicit_figures（`-implicit_figures`）**——图片以普通段落插入、可自由剪切移动，不生成"图+图注"的 CaptionedFigure/ImageCaption 结构（用户反馈图注样式与标题相似、图片不便移动）；图片文件先放 stage2/images/。
- 表格用 pipe table；表头行必填。
- `# 第一部分` 为 H1、`## 2.1` 为 H2、`#### 变式 N` 为 H4——style 脚本按此识别插空段。

## 生成命令（在工作目录 stage2/ 下）

```bash
pandoc review_content.md -f markdown+pipe_tables-implicit_figures -t docx --wrap=none -o ../stage3/报告.docx
python3 <skill>/scripts/style_docx.py ../stage3/报告.docx
cp ../stage3/报告.docx "<交付文件夹>/报告.docx"
```

## 交付前质检清单（全部通过才交付）

1. 公式完整性（两道关）：a) md 阶段——开 `$` 后不能紧跟空白、闭 `$` 前不能是空白（pandoc 规则，违反即整段变字面文本，如 `$n = $`）；b) **docx 阶段（权威）**——解包后全文 w:t/m:t 文本中 `$` = 0、`^` = 0、反斜杠命令（`\frac` 等）= 0。`$` 配对数检查查不出相邻空格类错误，docx 扫描是硬闸门。
2. 禁用字面 grep = 0：`版本：V`、`LaTeX 排版`、`原始题图`、`配套文件：逐题数据库`、`附完整原题`、`逐条附原题`、`题干完整可引`、`含题图`、`无需回查原卷`。
3. 学生可见文本 TXX 残留 = 0（图片内部路径与内部追踪除外）。
4. 独立 `---` 行 = 0；document.xml 中 `<w:pBdr>` = 0。
5. 关键内容抽查（转 docx 后合并 w:t+m:t 提取，注意 pandoc 的 OMML 用 U+2212 减号，匹配前把 − 归一成 -）：七个部分标题、每部分首条代表性内容、每道选择题四选项齐全、引用块条目数符合预期。
6. 图片数 = 预期题图数（unzip 后 ls word/media/）。
7. oMath 数量与 md 公式数量级一致（明显偏少说明有公式未转换）。
8. 页眉：word/header*.xml 含"Oli教室专用"且 document.xml 有 headerReference。
9. styles.xml：Heading1 `w:before="0"`、BlockText 无 shd。
10. 每道引用真题三查留痕：题号 grep 过、选项/题干读图转写过、答案重算过。
11. 条目顺序（任何情况下 = 题目 → 题图 → 答案 → 解析）：每个条目内 a) **每张**图片行之前必须有题干引用块（`>`）或编号条目头/典型原题头（小节标题、小节引言、普通正文不算题干；图后标记重置，下一张图重新检查）；b) 图片行位于答案行之前；c) 题图独立成段、不与题干文字并段（scripts/check_content.py 自动检查，违例输出条目名与行号）。
12. 对账：参与统计卷数 = 源目录卷数 − EXCLUDED 数；questions.csv 行数 = 各卷题数之和；正文所有"N 份/M 题"与数据库一致。
13. 条目间空行：所有题目条目之间有空段落（题目间换行 1 行）——`check_content.py --docx 交付.docx` 自动审计（小节首条跳过为正常）。
14. 图片尺寸：docx 内所有图片高 ≤ 上限（默认 5cm，宽度兜底 16cm）——`check_content.py --docx 交付.docx` 自动审计；带图条的条目图行下有斜体图注行（样式由 style_docx.py 统一处理）。

## 常见坑（都是踩过的）

- **pandoc fancy_lists**：未转义的 `A. xxx` 独立成段会被解析为字母编号列表 → 必须写 `A\. xxx`。
- **pandoc 数学定界符**：闭 `$` 前有空格（如 `$n = $`）则整段变字面文本且不跨段配对 → 定界符内不留边缘空格，空格写到定界符外（`$n$ = ______`）。
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
- **答案与题图顺序**：内容源条目骨架为"题干→题图→答案→解析"，任何情况下题目都在图前（含无答案/解析的题图集条目），写完用 scripts/check_content.py 复查（九年级曾出现答案先于题图、八年级 5.4 曾出现图先于题，用户均明确返工）。
- **pandoc implicit_figures 已禁用**：pandoc 命令一律 `-f markdown+pipe_tables-implicit_figures`——否则 `![alt](img)` 独立成段会生成 CaptionedFigure + ImageCaption 结构，图注样式与标题相似、图片不便移动（用户 2026-10-21 反馈，错误档案 #25）。禁用后图片=普通 inline 段落，图注由图片行下的**斜体独立段**提供（style_docx.py 样式化为 9pt 灰色居中）；但**图行之后紧跟非图注文字行（中间无空行）仍会并段且图在前**——图先于题风险不因此消失，check_content.py 第 8 项与 --docx 审计照常拦截。
- **图片尺寸**：pandoc 按像素 96dpi 原生尺寸插图，原卷截图常达 9cm 宽——由 style_docx.py **限高**（默认 5cm，IMG_MAX_H_CM 可调；长条形图保持原宽不被压小，宽度仅防溢出兜底 16cm），交付前用 --docx 审计兜底。**注意审计与 style 的默认值必须同步**（曾出现 style 已改限高 5cm 而审计仍按 6×6 报违例的不一致）。
- **图片段落 keepNext 黑点（错误档案 #26）**：style_docx.py 禁止给含图段落设置 keep_with_next——Word 会在段落左侧显示黑色小方点，与标题的标记相同，用户会以为图片变成了"标题格式"（成品报告旧脚本无此标记）。图片限宽 6cm 后孤图概率低，图片与答案跨页分离可接受。诊断口诀：Word 段落左侧黑点 = keepNext/keepLines 标记，不是列表符号，查 XML 的 `<w:keepNext/>`。
- **交付 docx 覆盖保护（用户可能在 Word 里改过）**：**修改交付 docx 的唯一默认路径 = 精修（XML 手术增量修改），只动用户点名的部分，整卷重建/覆盖重写默认禁止**（即使"源↔交付全文等价校验"通过也不允许，除非用户明确同意；用户已改过的内容为基准；归一化对比：去 $/^/_/花括号/引号形态差异/表格线后 difflib）。动手前仍须：①查目录下 ~$ 锁文件（有则提醒用户先关闭）；②将现有文件复制到 `.workbuddy/backups/<时间戳>/` 快照；③将现有文件转纯文本与手中基线 diff，发现用户改动 → 停下报告并询问合并方式，绝不直接覆盖；④XML 手术（unzip→lxml 改 document.xml→rezip，保留用户已存改动）。
- **XML 手术三件套**：克隆段落内现有 run 保 rPr 字体；分数用 `<m:f><m:num>…</m:num><m:den>…</m:den></m:f>` 构造并核对命名空间；锚点用"唯一文本+邻段内容"双重校验防误替换。pandoc plain 输出中复杂公式显示为 $...$ 是正常回退渲染，不是错误。
