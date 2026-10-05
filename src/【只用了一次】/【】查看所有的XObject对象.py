# -*- coding: utf-8 -*-
"""
打印 PDF 中所有 XObject 对象的信息。

用法:
    python dump_xobjects.py input.pdf
    python dump_xobjects.py input.pdf 3        # 只看第 3 页
"""

import sys
import re
import fitz  # PyMuPDF


def dump_xobjects(pdf_path,):
    doc = fitz.open(pdf_path)
    print(f"PDF: {pdf_path}")
    print(f"总页数: {len(doc)}\n")

    # 已处理过的 xref，避免多页共用一个 XObject 时重复打印
    seen_xrefs = set()

    for page_num, page in enumerate(doc):
        print("=" * 70)
        print(f"页面 {page_num + 1}  (xref={page.xref})")
        print("=" * 70)

        xobjs = page.get_xobjects()
        if not xobjs:
            print("  (无 XObject)\n")
            continue

        for xo in xobjs:
            xref, name = xo[0], xo[1]
            # xo 结构: (xref, name, invoker, bbox)
            invoker = xo[2] if len(xo) > 2 else None
            bbox = xo[3] if len(xo) > 3 else None

            print(f"\n---- {name}  (xref={xref}) ----")
            if invoker is not None:
                print(f"  invoker xref: {invoker}")
            if bbox is not None:
                print(f"  bbox: {bbox}")

            # 对象字典
            try:
                obj = doc.xref_object(xref)
                print(f"  --- 对象定义 ---")
                # 只打印前 20 行，避免刷屏
                for i, line in enumerate(obj.splitlines()[:20]):
                    print(f"    {line}")
                if len(obj.splitlines()) > 20:
                    print(f"    ... (共 {len(obj.splitlines())} 行)")
            except Exception as e:
                print(f"  [!] 无法读取对象: {e}")

            # 内容流
            try:
                raw = doc.xref_stream(xref)
            except Exception as e:
                print(f"  [!] 无法读取流: {e}")
                raw = None

            if raw is None:
                print(f"  (无内容流)")
                continue

            s = raw.decode("latin-1")
            print(f"  --- 内容流 ---")
            print(f"  长度: {len(s)} 字节")

            # 内部调用了哪些 XObject
            inner = re.findall(r"/(\w+)\s+Do\b", s)
            if inner:
                from collections import Counter
                c = Counter(inner)
                inner_str = ", ".join(f"{n}×{cnt}" for n, cnt in c.items())
                print(f"  内部 Do 调用: {inner_str}")
            else:
                print(f"  内部 Do 调用: 无")

            # 统计颜色
            colors = re.findall(r"([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+rg\b", s)
            if colors:
                from collections import Counter
                c = Counter(colors)
                color_str = ", ".join(f"{col}×{cnt}" for col, cnt in c.most_common(5))
                print(f"  颜色 rg (前5): {color_str}")

            # 统计 <hex>Tj 个数
            n_tj = len(re.findall(r"<[0-9A-Fa-f\s]+>\s*Tj\b", s))
            if n_tj:
                print(f"  <hex>Tj 数量: {n_tj}")

            # 前 300 字符预览
            print(f"  --- 前 300 字符 ---")
            preview = s[:300].replace("\n", "\\n")
            print(f"  {preview}")

        print()

    doc.close()


if __name__ == "__main__":
    pg = None
    pdf = "/Users/teacher/Desktop/百度网盘下载/001/黄坪营黄氏挂图.pdf"
    dump_xobjects(pdf, pg)