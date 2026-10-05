# -*- coding: utf-8 -*-
"""
删除 PDF 里所有含 "百家有谱" (04e5094611b60cf7) 的文字。
"""
import sys
import re
import fitz  # PyMuPDF

TARGET_HEX = "04e5094611b60cf7"


def remove_baijia_youpu(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    total = 0

    # 编译正则：匹配 <04e5094611b60cf7>Tj
    # 允许 hex 内部有空格：<04e5 0946 11b6 0cf7>
    hex_pat = r"0\s*4\s*e\s*5\s*0\s*9\s*4\s*6\s*1\s*1\s*b\s*6\s*0\s*c\s*f\s*7"
    tj_pat = re.compile(r"<\s*" + hex_pat + r"\s*>\s*Tj\b", re.IGNORECASE)

    # 1) 遍历 PDF 里所有含流的对象
    n_objs = doc.xref_length()
    print(f"共 {n_objs} 个对象，开始扫描...")

    for xref in range(1, n_objs):
        try:
            raw = doc.xref_stream(xref)
        except Exception:
            continue
        if not raw:
            continue

        try:
            s = raw.decode("latin-1")
        except Exception:
            continue

        if TARGET_HEX not in s:
            continue

        # 命中！删掉所有 <hex>Tj
        new_s, n = tj_pat.subn("", s)
        if n:
            doc.update_stream(xref, new_s.encode("latin-1"))
            total += n
            print(f"  xref={xref}: 删除 {n} 处", flush=True)
        else:
            print(f"  xref={xref}: 含目标 hex 但正则没匹配到，检查格式", flush=True)

    print(f"\n合计删除 {total} 处")
    print(f"保存到 {output_pdf}")
    doc.save(output_pdf, garbage=4, deflate=True, clean=True)
    doc.close()
    print("完成")


if __name__ == "__main__":
    input_path  = "/Users/teacher/Desktop/百度网盘下载/001/黄坪营黄氏挂图_副本.pdf"
    output_path = input_path.replace(".pdf", "_去百家有谱.pdf")
    remove_baijia_youpu(input_path, output_path)