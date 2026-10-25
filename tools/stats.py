# -*- coding: utf-8 -*-
"""内容体量体检：统计每页正文汉字数、幕数、每幕均字、各块指令用量。
用法：python tools/stats.py
"""
import glob, os, re, io, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")


def strip_code(t):
    parts = re.split(r"^---\s*$", t, maxsplit=2, flags=re.M)
    return parts[2] if len(parts) >= 3 else t


def analyze(path):
    t = open(path, encoding="utf-8").read()
    body = strip_code(t)
    fences = re.findall(r"^:::+\s*(\w+)(?:[^\n]*)\n(.*?)\n:::", body, flags=re.S | re.M)
    # pbtns / personas / sources 是导航或索引，不算叙事正文；分析块要计入。
    content_fences = {"scene", "deep", "insight", "arc", "reveal", "note"}
    fence_prose = 0
    for kind, content in fences:
        if kind in content_fences:
            prose = re.sub(r"^\s*### .*$", "", content, flags=re.M)
            prose = re.sub(r"^\s*\[[^]]+\|\d+(?:-\d+)?\]\s*$", "", prose, flags=re.M)
            fence_prose += len(re.findall(r"[\u4e00-\u9fff]", prose))
    nob = re.sub(r"^:::+\s*\w+[^\n]*\n.*?\n:::", "", body, flags=re.S | re.M)
    nob = re.sub(r"^#{2,3} .*$", "", nob, flags=re.M)
    nob = re.sub(r"^[-*] .*$", "", nob, flags=re.M)
    prose_cn = len(re.findall(r"[\u4e00-\u9fff]", nob)) + fence_prose
    total_cn = len(re.findall(r"[\u4e00-\u9fff]", body))
    acts = re.findall(r"^### (.+?)\s*\{act,([^}]*)\}", body, flags=re.M)
    wordcounts = []
    # 逐幕切分；每幕中的场景与分析同样算正文。
    chunks = re.split(r"^### .*?\{act[^}]*\}", body, flags=re.M)[1:]
    for c in chunks:
        c = re.split(r"^## ", c, maxsplit=1, flags=re.M)[0]
        c = re.sub(r"^:::+\s*(?:pbtns|personas|sources)[^\n]*\n.*?\n:::", "", c, flags=re.S | re.M)
        c = re.sub(r"^:::+\s*\w+[^\n]*$|^:::+\s*$|^\s*### .*$", "", c, flags=re.M)
        c = re.sub(r"^\s*\[[^]]+\|\d+(?:-\d+)?\]\s*$", "", c, flags=re.M)
        wordcounts.append(len(re.findall(r"[\u4e00-\u9fff]", c)))
    return {
        "total_cn": total_cn,
        "prose_cn": prose_cn,
        "acts": len(acts),
        "act_wc": wordcounts,
        "fence_kinds": [k for k, _ in fences],
    }


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    rows = []
    for f in sorted(glob.glob(os.path.join(CONTENT, "*.md"))):
        if os.path.basename(f).startswith("_"):
            continue
        d = analyze(f)
        d["name"] = os.path.basename(f)[:-3]
        rows.append(d)

    print(f'{"页面":26}{"正文汉字":>8}{"幕数":>5}{"每幕均字":>9}  {"最短幕":>6}{"最长幕":>6}')
    print("-" * 68)
    tot = 0
    totacts = 0
    for d in rows:
        avg = int(sum(d["act_wc"]) / len(d["act_wc"])) if d["act_wc"] else 0
        mn = min(d["act_wc"]) if d["act_wc"] else 0
        mx = max(d["act_wc"]) if d["act_wc"] else 0
        print(f'{d["name"]:26}{d["prose_cn"]:8}{d["acts"]:5}{avg:9}  {mn:6}{mx:6}')
        tot += d["prose_cn"]
        totacts += d["acts"]
    print("-" * 68)
    print(f'{"合计":26}{tot:8}{totacts:5}{tot // totacts if totacts else 0:9}')
    print()

    # 全局分布
    allwc = [w for d in rows for w in d["act_wc"]]
    if allwc:
        allwc.sort()
        n = len(allwc)
        print(f"全站共 {n} 幕；每幕正文汉字分布：")
        print(f"  最小 {allwc[0]} / 25分位 {allwc[n//4]} / 中位 {allwc[n//2]} / 75分位 {allwc[n*3//4]} / 最大 {allwc[-1]}")
        short = sum(1 for w in allwc if w < 300)
        mid = sum(1 for w in allwc if 300 <= w < 800)
        long_ = sum(1 for w in allwc if w >= 800)
        print(f"  <300字（偏薄）: {short} 幕 ({short*100//n}%)")
        print(f"  300-800字（合格）: {mid} 幕 ({mid*100//n}%)")
        print(f"  >=800字（深入）: {long_} 幕 ({long_*100//n}%)")
    print()
    # 指令用量
    from collections import Counter
    c = Counter()
    for d in rows:
        c.update(d["fence_kinds"])
    print("块指令用量：", dict(c))


if __name__ == "__main__":
    main()
