# -*- coding: utf-8 -*-
"""
清空指定的 Form XObject（可传单个名字或名字列表），使其不再绘制任何内容。
用法:
    python F2删除.py input.pdf output.pdf
"""

import sys
import fitz  # PyMuPDF


def _normalize_names(target_name):
    """把字符串 / 列表 / 元组 / 集合 统一成 set[str]。"""
    if isinstance(target_name, str):
        return {target_name}
    elif isinstance(target_name, (list, tuple, set, frozenset)):
        return {str(n) for n in target_name}
    else:
        raise TypeError(f"target_name 类型不支持: {type(target_name)!r}，"
                        f"请传入 str 或 list/tuple/set[str]")


def blank_fm2(input_pdf: str, output_pdf: str, target_name="Fm3", try_run=True):
    target_names = _normalize_names(target_name)
    if not target_names:
        print("target_name 为空，未做任何处理")
        return

    name_desc = ", ".join(sorted(target_names))
    doc = fitz.open(input_pdf)
    found = 0

    for pno, page in enumerate(doc):
        # get_xobjects() 返回 (xref, name, ...) 的列表
        for xo in page.get_xobjects():
            xref, name = xo[0], xo[1]
            if name not in target_names:
                continue

            if try_run:
                rect_tuple = xo[3]
                xobject_rect = fitz.Rect(rect_tuple)
                page.draw_rect(
                    xobject_rect,
                    color=(0, 1, 0),  # 绿色边框
                    fill=(0, 1, 0),   # 绿色填充
                    width=2
                )
            else:
                print(f"page {pno+1}: 找到 {name} (xref={xref})，清空其内容流", flush=True)
                # 用一个空流替换，变成什么都不画
                doc.update_stream(xref, b" ")

            found += 1

    if found == 0:
        print(f"未找到 [{name_desc}]，请检查名字是否正确")
        doc.close()
        return

    print(f"共处理 {found} 个 XObject（目标: [{name_desc}]），开始保存 -> {output_pdf}")
    doc.save(output_pdf, garbage=4, deflate=True)
    doc.close()
    print("完成")


if __name__ == "__main__":
    input_path = "/Volumes/西数4T外置/Chrome下载目录/英国文学2026笔记自己整理.pdf"
    target_name = ["KSPX1", "KSPX2", "KSPX3", "KSPX4"]  # 现在也支持单个字符串 "KSPX3"
    try_run = False

    output_suffix = "标记" if try_run else "去水印"
    # 生成输出文件名时把列表拼起来，避免出现非法字符
    name_tag = target_name if isinstance(target_name, str) else "_".join(map(str, target_name))
    output_path = input_path.replace('.pdf', f'_去水印_{output_suffix}_{name_tag}.pdf')
    blank_fm2(input_path, output_path, target_name, try_run=try_run)