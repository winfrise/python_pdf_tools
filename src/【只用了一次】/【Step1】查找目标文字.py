# -*- coding: utf-8 -*-
"""
不靠推断，直接程序定位 "百家有谱" 对应的内容流 hex。
"""
import sys
import re
import fitz  # PyMuPDF


def find_hex_by_text(pdf_path, target="百家有谱"):
    doc = fitz.open(pdf_path)

    print(f"目标文本: {target}\n")

    for pno, page in enumerate(doc):
        # ---------- 1. 找到文字在页面上的位置 ----------
        rects = page.search_for(target)
        if not rects:
            continue
        print(f"page {pno+1}: 找到 {len(rects)} 处，前 3 个 bbox:")
        for r in rects[:3]:
            print(f"  {r}")

        # ---------- 2. 拿到所有内容流（页面流 + XObject 流） ----------
        streams = []
        for xref in page.get_contents():
            streams.append(("page", xref))
        for xo in page.get_xobjects():
            xref, name = xo[0], xo[1]
            if doc.xref_stream(xref):
                streams.append((name, xref))

        # ---------- 3. 遍历每个流，找落在 rects 里的 <hex>Tj ----------
        found_hexes = set()
        for label, xref in streams:
            raw = doc.xref_stream(xref)
            if not raw:
                continue
            s = raw.decode("latin-1")

            # 粗匹配：BT ... ET 块里，有 <hex>Tj 和 Tm
            # Tm 结构: a b c d e f Tm  → e, f 是平移
            # 简化：按 "Tm ... <hex>Tj" 成对匹配
            for m in re.finditer(
                r"([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\s+"
                r"([\d.\-]+)\s+([\d.\-]+)\s+Tm\s*"
                r"<\s*([0-9A-Fa-f\s]+)\s*>\s*Tj",
                s
            ):
                e = float(m.group(5))   # Tm 平移 x
                f = float(m.group(6))   # Tm 平移 y
                hex_str = re.sub(r"\s+", "", m.group(7)).lower()

                # PDF 坐标系原点在左下，PyMuPDF 的 bbox 原点在左上
                # 需要把 e, f 和 rects 做坐标对齐后再判断
                # 简单做法：把 e, f 视作 (x, y_pdf)，转成 PyMuPDF 的 y
                ph = page.rect.height
                pt = fitz.Point(e, ph - f)

                for r in rects:
                    if r.contains(pt):
                        found_hexes.add((hex_str, label, xref))
                        break

        # ---------- 4. 打印结果 ----------
        if found_hexes:
            print(f"  命中 hex:")
            for h, label, xref in sorted(found_hexes):
                print(f"    <{h}>  ← {label} (xref={xref})")
        else:
            print("  未在内容流中定位到对应 hex（可能在嵌套 XObject 或图形路径里）")
        print()

    doc.close()


if __name__ == "__main__":
    input_path = "/Users/teacher/Desktop/百度网盘下载/001/黄坪营黄氏挂图_副本.pdf"
    find_hex_by_text(input_path, "百家有谱")