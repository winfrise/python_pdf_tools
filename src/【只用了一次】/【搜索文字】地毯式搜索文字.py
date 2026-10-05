# -*- coding: utf-8 -*-
import fitz
import re
from collections import defaultdict

PDF = "/Users/teacher/Desktop/百度网盘下载/001/黄坪营黄氏挂图_副本.pdf"
doc = fitz.open(PDF)

HEX = "04e5094611b60cf7"

print("=" * 60)
print("1) 页面文本提取测试")
print("=" * 60)
for pno, page in enumerate(doc):
    txt = page.get_text()
    if "百家有谱" in txt:
        print(f"  page {pno+1}: get_text() 里含 '百家有谱'")

        # 统计
        span_stats = defaultdict(int)

        # 看它属于哪个 span
        d = page.get_text("dict")
        for block in d["blocks"]:
            for line in block.get("lines", []):


                for span in line["spans"]:
                    if "百家有谱" in span["text"]:
                        x0, y0, x1, y1 = span['bbox']
                        bbox_width = round(x1 - x0)
                        bbox_height = round(y1 - y0)
                        span_key = (span['font'], round(span['size'], 2), span['color'], bbox_width, bbox_height)
                        span_stats[span_key] += 1

        # 打印汇总报告
        if span_stats:
            print("\n=== 样式统计报告 ===")
            for span_item, count in span_stats.items():
                print(f"font: {span_item[0]}, font_size: {span_item[1]}, color: {span_item[2]:#08x}, width={span_item[3]}, height={span_item[4]} -> 共 {count} 个")
    
    else:
        print(f"  page {pno+1}: get_text() 里没有 '百家有谱'")

print()
print("=" * 60)
print("2) 按位置搜索")
print("=" * 60)

for pno, page in enumerate(doc):
    rects = page.search_for("百家有谱")
    if rects:
        print(f"  page {pno+1}: 找到 {len(rects)} 处")
    else:
        print(f"  page {pno+1}: 没找到")

print()
print("=" * 60)
print("3) 全对象搜索 hex 04e5094611b60cf7")
print("=" * 60)
for xref in range(1, doc.xref_length()):
    try:
        raw = doc.xref_stream(xref)
    except Exception:
        raw = None

    if not raw:
        # 也许是对象字典里直接含这个 hex（不太可能）
        try:
            obj = doc.xref_object(xref)
            if HEX in obj:
                print(f"  xref={xref} 对象字典里含 {HEX}")
        except Exception:
            pass
        continue

    s = raw.decode("latin-1", errors="ignore")
    if HEX in s:
        print(f"  xref={xref}: 流里含 {HEX} ({s.count(HEX)} 次)")

print()
print("=" * 60)
print("4) 全对象搜索明文 '百家有谱'")
print("=" * 60)
for xref in range(1, doc.xref_length()):
    try:
        raw = doc.xref_stream(xref)
    except Exception:
        raw = None
    if not raw:
        continue
    try:
        s = raw.decode("utf-8", errors="ignore")
    except Exception:
        continue
    if "百家有谱" in s:
        print(f"  xref={xref}: 流里含明文 '百家有谱'")

doc.close()
print()
print("搜索完成")