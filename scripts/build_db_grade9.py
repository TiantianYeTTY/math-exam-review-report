# Designed by TiantianYe
# 【参考实现·九年级】EXCLUDED 剔除机制 + 子代理落盘合并（load_agent_files）+ 考点编码 S1-S9。用法见文件头。
# -*- coding: utf-8 -*-
"""九年级 2026-2027 上学期期中试卷逐题数据库与统计（沪教版五四制新教材）
考试范围口径（按卷面声明与内容判定）：
GROUP_FULL  第27~29章=二次函数+相似三角形+锐角三角比：T02 T04 T06（卷面明示）
GROUP_BASE  第27~28章=二次函数+相似三角形：T01 T03 T05 T07 T08 T09 T10 T11 T12 T13 T14
（T07-T12 卷面未声明，按内容判定，若发现三角比题在 note 标 S8 并入 FULL 复核）

考点编码:
S1 比例线段与相似基础(比例性质/比例中项/平行线分线段成比例/黄金分割/相似多边形/位似)
S2 相似三角形的判定与性质(判定/A字X字模型/面积比/折叠剪切相似/证明)
S3 相似的应用(坐标系相似/投影影子/实际测量)
S4 二次函数概念与表达式(定义/待定系数/顶点式交点式)
S5 二次函数图象与性质(开口/对称轴/顶点/增减性/系数符号/平移/图象上点大小比较)
S6 二次函数与方程不等式(与x轴交点/图象法解不等式/恒成立/判别式/公共点个数)
S7 二次函数综合与应用(实际应用/存在性/动点/面积/几何结合压轴)
S8 锐角三角比与解直角三角形
S9 其他拓展(新定义/规律/计数/阅读理解)
难度: 1基础 2较易 3中等 4较难 5压轴
题型: X选择 T填空 J解答 Z综合压轴
"""
import json, csv, os

DB = []
X = "X"; T = "T"; J = "J"; Z = "Z"

def infer_code(text, typ):
    """code 缺失时按关键词推断主考点"""
    t = text
    if any(k in t for k in ["抛物线", "二次函数"]) and typ in ("Z", "J"):
        return "S7"
    if any(k in t for k in ["旋转相似", "手拉手", "相似三角"]):
        return "S2"
    if "新定义" in t:
        return "S9"
    return "S7" if typ == "Z" else "S2"

def add(paper, rows):
    for r in rows:
        qno, typ, score, grp, code, sub, diff, note = r
        DB.append(dict(paper=paper, qno=qno, typ=typ, score=score, grp=grp,
                       code=code, sub=sub, diff=diff, note=note))

# ============ T05 检测卷（满分150, 建议100分钟, 范围: 九上第一二章=相似+二次函数）============
# 结构: 选择5×4=20(Q1-5) 填空11×4=44(Q6-16) 解答8题86分(Q17-19各8分, Q20-23各12分, Q24=14分)
# 注: 原卷题组标题有笔误, 按总分150反推: 填空实为Q6-16共11题44分, 解答Q17-Q24共8题86分
add("T05", [
 (1,X,4,20,"S1","平行线分线段成比例判断(DE=6,DF=9)",2,""),
 (2,X,4,20,"S4","二次函数识别(一次/反比例/根式)",1,"答案C y=3x²+1"),
 (3,X,4,20,"S2","AB∥CD∥EF交于O型比例判断(CE=6,EO=4,BE=9)",3,""),
 (4,X,4,20,"S4","二次函数定义求参 y=(m-2)x^(m²-2)+2x-7",2,"答案C m=-2"),
 (5,X,4,20,"S6","抛物线与x轴交点+点B在直线下方判断说法",4,"答案A 顶点不可能在第四象限"),
 (6,T,4,44,"S1","相似四边形(梯形内截EF∥BC)求AE/EB",3,"答案√2/2"),
 (7,T,4,44,"S1","相似矩形对应边成比例",1,"答案16/3"),
 (8,T,4,44,"S1","AD∥BE∥CF求AC(AB=4.8,DE=3.6,EF=1.2)",1,"答案6.4"),
 (9,T,4,44,"S1","比例尺1:5000000求图上距离",1,"答案2厘米"),
 (10,T,4,44,"S6","抛物线恒在一次函数上方(y₁≥y₂)求m",4,"答案m=0"),
 (11,T,4,44,"S1","黄金分割点(AP-BP=2)求AB",2,"答案4+2√5"),
 (12,T,4,44,"S2","四边形∠BAD+∠ACB=180°证相似求DO/OB",5,"答案10/9"),
 (13,T,4,44,"S1","黄金分割BP(AP>BP,AB=10)",1,"答案15-5√5"),
 (14,T,4,44,"S1","双黄金分割点CD=1求AB",2,"答案2+√5"),
 (15,T,4,44,"S1","平行四边形剪两菱形后与原图相似求边比",4,"解析匹配,双解"),
 (16,T,4,44,"S9","1~20取3数组成(a,b,c)使b²=ac计数",5,"自解22(三数互异)"),
 (17,J,8,86,"S2","等腰直角三角形折叠求OD/OE",4,"自解2/5(OD/OE)"),
 (18,J,8,86,"S4","待定系数求解析式+顶点在y=2ax上证b=2a",3,"解析匹配 y=x²+2x-1"),
 (19,J,8,86,"S4","二次函数定义求k+求值",2,"自解k=2,y(3)=14"),
 (20,J,12,86,"S1","相似四边形求角(120°)+求周长(42)",2,"自解"),
 (21,J,12,86,"S2","矩形△ADE∽△BEF证明+求BF=25/6;等腰分类",4,"①②自解,②等腰分类解析匹配"),
 (22,J,12,86,"S1","正方形折纸证黄金分割点+折30°角",5,""),
 (23,J,12,86,"S7","抛物线A(-8,0),tan∠CAO=2/3综合(角关系存在性+面积比)",5,""),
 (24,J,14,86,"S7","抛物线y=ax²+2ax+c顶点纵坐标4;tan∠ACB=2;∠AFC=∠DAB求CF",5,"自解 y=-x²-2x+3,tan=2,CF=6√10/5"),
])

PAPERS = {
 "T01": dict(name="自编测试卷1", short="自编测试1", full=None, time=None, extra="沪教版五四制期中自编测试"),
 "T02": dict(name="期中模拟卷(新题型)", short="模拟卷A", full=150, time=120, extra="2027中考新题型结构"),
 "T03": dict(name="自编测试卷", short="自编测试", full=None, time=None, extra="沪教版五四制期中自编测试"),
 "T04": dict(name="期中仿真卷(新题型)", short="仿真卷", full=150, time=120, extra="2027中考新题型结构"),
 "T05": dict(name="期中检测卷", short="检测卷", full=150, time=100, extra="范围九上第一二章"),
 "T06": dict(name="期中模拟卷(新题型)", short="模拟卷B", full=150, time=120, extra="2027中考新题型结构"),
 "T07": dict(name="期中考试自测卷", short="自测卷1", full=None, time=None, extra=""),
 "T08": dict(name="期中检测卷", short="检测卷B", full=None, time=None, extra=""),
 "T09": dict(name="期中模拟卷2", short="模拟卷2", full=None, time=None, extra=""),
 "T10": dict(name="期中模拟卷3", short="模拟卷3", full=None, time=None, extra=""),
 "T11": dict(name="期中模拟卷4", short="模拟卷4", full=None, time=None, extra=""),
 "T12": dict(name="期中自测卷", short="自测卷2", full=None, time=None, extra=""),
 "T13": dict(name="巩固培优卷", short="培优卷", full=None, time=None, extra="二次函数+相似三角形"),
 "T14": dict(name="学易金卷", short="学易金卷", full=None, time=None, extra="第27~28章"),
}

GROUP_FULL = ["T02","T04","T06"]
GROUP_BASE = ["T01","T03","T05","T07","T08","T09","T10","T11","T12","T13","T14"]

# 用户 2026-10-18 指定：解析版与原卷版对不上的试卷剔除，不参与统计。
# T05 期中检测卷 / T08 期中检测卷二：两卷解析版互相串卷+同池混拼，无法可信对位；
# T09 期中模拟卷二：解析 Q3 起与原卷错位（原卷 Q3 表格题 vs 解析待定系数题）。
# 数据行仍保留在 db_grade9/*.txt 供追溯，但不写入 questions.csv / stats.json / 报告。
EXCLUDED = ["T05", "T08", "T09"]

# ============ 从 db_grade9/*.txt 读取子代理产出并合并 ============
def load_agent_files():
    """读取 db_grade9/TXX.txt（STRUCT 行 + 逐题行 + 同题/易错行）"""
    base = os.path.dirname(os.path.abspath(__file__))
    d = os.path.join(base, "db_grade9")
    extras = {"same": [], "hard": [], "struct": {}}
    if not os.path.isdir(d):
        return extras
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".txt"):
            continue
        pid = fn[:-4]
        if pid not in PAPERS:
            continue
        rows = []
        for ln in open(os.path.join(d, fn), encoding="utf-8"):
            ln = ln.strip()
            if not ln:
                continue
            if ln.startswith("STRUCT|"):
                extras["struct"][pid] = ln
                continue
            if ln.startswith("同题:"):
                extras["same"].append(f"{pid} {ln[3:].strip()}")
                continue
            if ln.startswith("易错:"):
                extras["hard"].append(f"{pid} {ln[3:].strip()}")
                continue
            parts = ln.split("|")
            if len(parts) >= 8 and parts[0] == pid:
                try:
                    qno = int(parts[1])
                except ValueError:
                    continue
                score = None
                if parts[3] not in ("", "None"):
                    try: score = float(parts[3])
                    except ValueError: pass
                f4 = parts[4]
                grp, code, sub, diff, note, ans = None, None, None, None, "", ""
                if f4[:1] == "S":
                    # 无grp: paper|qno|typ|score|code|sub|diff|note... 或 code|sub1|sub2|diff|note...
                    code = f4
                    try:
                        diff = int(parts[6])
                        sub = parts[5]
                        note = "|".join(parts[7:])
                    except ValueError:
                        if len(parts) >= 9:
                            sub = parts[5] + "|" + parts[6]
                            try:
                                diff = int(parts[7])
                            except ValueError:
                                continue
                            note = "|".join(parts[8:])
                        else:
                            continue
                elif f4 in ("X", "T", "J", "Z"):
                    # 无code: paper|qno|typ|score|Z|sub1|sub2|diff|note...
                    sub = parts[5] + (("|" + parts[6]) if len(parts) > 8 else "")
                    code = infer_code(sub, parts[2])
                    try: diff = int(parts[7] if len(parts) > 8 else parts[6])
                    except ValueError: continue
                    note = "|".join(parts[8:] if len(parts) > 8 else parts[7:])
                elif len(f4) == 1 and f4 in "ABCD":
                    # 带答案字母: paper|qno|typ|score|ans|code|sub|diff|note...
                    ans = f4
                    code, sub = parts[5], parts[6]
                    try: diff = int(parts[7])
                    except ValueError: continue
                    note = "|".join(parts[8:])
                else:
                    # 可能是 grp（规范格式）或冗余数字：数值>=10 视为 grp，否则忽略
                    code, sub = parts[5], parts[6]
                    try:
                        v = float(f4)
                        grp = v if v >= 10 else None
                    except ValueError:
                        continue
                    try: diff = int(parts[7])
                    except ValueError: continue
                    note = "|".join(parts[8:])
                if ans:
                    note = f"答{ans}；" + note
                rows.append(dict(paper=pid, qno=qno, typ=parts[2], score=score, grp=grp,
                                 code=code, sub=sub, diff=diff, note=note))
                rows.append(dict(paper=pid, qno=qno, typ=parts[2], score=score, grp=grp,
                                 code=code, sub=sub, diff=diff, note=note))
        # 覆盖同名卷已录行（T05 由主控录入, 子文件无 T05）
        global DB
        DB = [r for r in DB if r["paper"] != pid] + rows
    return extras

X = "X"; T = "T"; J = "J"; Z = "Z"

if __name__ == "__main__":
    extras = load_agent_files()
    # 剔除解析版与原卷版对不上的卷
    DB = [r for r in DB if r["paper"] not in EXCLUDED]
    out_dir = os.path.dirname(os.path.abspath(__file__))
    # 去重（同卷同题号保留最后一条）
    seen = {}
    for r in DB:
        seen[(r["paper"], r["qno"])] = r
    DB = sorted(seen.values(), key=lambda r: (r["paper"], r["qno"]))

    with open(os.path.join(out_dir, "questions_grade9.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["paper","qno","typ","score","grp","code","sub","diff","note"])
        w.writeheader()
        for r in DB: w.writerow(r)

    DIFF_NAME = {1:"基础",2:"较易",3:"中等",4:"较难",5:"压轴"}
    TYPE_NAME = {"X":"选择题","T":"填空题","J":"解答题","Z":"综合/压轴题"}
    CODE_NAME = {"S1":"比例线段与相似基础","S2":"相似三角形的判定与性质","S3":"相似的应用",
                 "S4":"二次函数概念与表达式","S5":"二次函数图象与性质","S6":"二次函数与方程不等式",
                 "S7":"二次函数综合与应用","S8":"锐角三角比与解直角三角形","S9":"其他拓展"}

    stats = {}
    for grp_name, group in [("BASE", GROUP_BASE), ("FULL", GROUP_FULL)]:
        rows = [r for r in DB if r["paper"] in group]
        cs = {}
        for r in rows:
            d = cs.setdefault(r["code"], {"q":0,"papers":set(),"diff":{}})
            d["q"] += 1; d["papers"].add(r["paper"])
            d["diff"][DIFF_NAME[r["diff"]]] = d["diff"].get(DIFF_NAME[r["diff"]],0)+1
        stats[grp_name] = {c: dict(q=v["q"], papers=sorted(v["papers"]), diff=v["diff"]) for c,v in cs.items()}

    result = dict(
        total_questions=len(DB),
        total_papers=len({r["paper"] for r in DB}),
        excluded_papers=EXCLUDED,
        group_full=[p for p in GROUP_FULL if p not in EXCLUDED],
        group_base=[p for p in GROUP_BASE if p not in EXCLUDED],
        struct=extras["struct"], same_candidates=extras["same"], hard_candidates=extras["hard"],
        code_stats=stats,
        yatou=[(r["paper"], r["qno"], r["sub"]) for r in DB if r["diff"]==5],
        hard_fills=[(r["paper"], r["qno"], r["sub"]) for r in DB if r["typ"]=="T" and r["diff"]>=4],
    )
    with open(os.path.join(out_dir, "stats_grade9.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1, default=str)

    print("=== 逐题总数:", len(DB), " 卷数:", len({r["paper"] for r in DB}), "===")
    for pid in sorted(PAPERS):
        n = sum(1 for r in DB if r["paper"]==pid)
        codes = {}
        for r in DB:
            if r["paper"]==pid: codes[r["code"]] = codes.get(r["code"],0)+1
        print(f"{pid}: {n}题  {codes}")
    print("\n--- BASE 组(11卷) 考点分布 ---")
    for c, v in sorted(stats.get("BASE",{}).items(), key=lambda kv:-kv[1]["q"]):
        print(f"{c} {CODE_NAME.get(c,c):<14} {v['q']:>4}题 覆盖{len(v['papers'])}卷 {v['diff']}")
    print("\n--- FULL 组(3卷) 考点分布 ---")
    for c, v in sorted(stats.get("FULL",{}).items(), key=lambda kv:-kv[1]["q"]):
        print(f"{c} {CODE_NAME.get(c,c):<14} {v['q']:>4}题 覆盖{len(v['papers'])}卷")
    print("\n--- 压轴(diff=5) ---")
    for p,q,s in result["yatou"]: print(f"{p}-Q{q}: {s}")
