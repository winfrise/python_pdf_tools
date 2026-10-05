# -*- coding: utf-8 -*-
"""
清空 Fm2（大杂烩 Form XObject），使其不再绘制任何内容。
用法:
    python F2删除.py input.pdf output.pdf
"""

import sys
import fitz  # PyMuPDF


def blank_fm2(input_pdf: str, output_pdf: str, target_name: str = "Fm3"):
    doc = fitz.open(input_pdf)
    found = 0

    for pno, page in enumerate(doc):
        # get_xobjects() 返回 (xref, name, ...) 的列表
        for xo in page.get_xobjects():
            xref, name = xo[0], xo[1]
            if name != target_name:
                continue

            print(f"page {pno+1}: 找到 {name} (xref={xref})，清空其内容流", flush=True)
            # 用一个空流替换，Fm2 变成什么都不画
            doc.update_stream(xref, b" ")
            found += 1

    if found == 0:
        print(f"未找到 {target_name}，请检查名字是否正确")
        doc.close()
        return

    print(f"共处理 {found} 个 {target_name}，开始保存 -> {output_pdf}")
    doc.save(output_pdf, garbage=4, deflate=True)
    doc.close()
    print("完成")


if __name__ == "__main__":
    input_path = "/Users/teacher/Desktop/百度网盘下载/001/黄坪营黄氏挂图_副本_去百家有谱.pdf"
    target_name = "Fm3"
    output_path = input_path.replace('.pdf', f'_去水印_{target_name}.pdf')
    blank_fm2(input_path, output_path, target_name)