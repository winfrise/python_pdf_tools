# -*- coding: utf-8 -*-
"""
合并脚本：分析 PDF 的填充颜色。

两个原始脚本的取色视角被合并为两种「模式」，公共部分（打开文档、
计算页范围、逐页循环、关闭文档）统一为同一套骨架：
    - mode="stream"   : 读取原始内容流字节，用正则统计填充指令出现次数（原「文件流_统计颜色.py」）
    - mode="drawings" : 用 get_drawings() 收集矢量图形的填充色并去重，带透明度（原「分析形状的颜色.py」）
    - mode="both"     : 两种模式都跑

页范围统一使用 parse_page_range(pages, total)（已内联，无需外部 utils 依赖）。
"""
import os
import sys
import re
import fitz
from collections import Counter
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import parse_page_range


# ============ 模式一：内容流统计填充指令出现次数（原文件 A） ============
def _count_by_stream(page):
    """读取页面原始内容流，正则匹配填充指令，返回 Counter(指令字符串 -> 次数)。"""
    WS = r'[ \t\r\n]+'
    NUM = r'(?:\d+\.?\d*|\.\d+)'
    NAME = r'/[A-Za-z0-9._-]+'

    patterns = [
        re.compile(rf"({NUM}){WS}({NUM}){WS}({NUM}){WS}rg"),                       # RGB
        re.compile(rf"({NUM}){WS}g"),                                               # Gray
        re.compile(rf"({NUM}){WS}({NUM}){WS}({NUM}){WS}({NUM}){WS}k"),              # CMYK
        re.compile(rf"/DeviceRGB{WS}cs{WS}({NUM}){WS}({NUM}){WS}({NUM}){WS}scn"),   # 显式设备空间 scn
        re.compile(rf"/DeviceGray{WS}cs{WS}({NUM}){WS}scn"),
        re.compile(rf"/DeviceCMYK{WS}cs{WS}({NUM}){WS}({NUM}){WS}({NUM}){WS}({NUM}){WS}scn"),
        re.compile(rf"{NAME}{WS}cs{WS}({NUM}){WS}({NUM}){WS}({NUM}){WS}scn"),       # 命名空间 3 分量
        re.compile(rf"{NAME}{WS}cs{WS}({NUM}){WS}({NUM}){WS}({NUM}){WS}({NUM}){WS}scn"),  # 命名空间 4 分量
    ]

    raw_counter = Counter()
    try:
        content_bytes = page.read_contents()
        if content_bytes:
            content_str = content_bytes.decode('latin-1')
            for pattern in patterns:
                for match in pattern.finditer(content_str):
                    raw_counter[match.group(0)] += 1     # group(0) 即整条填充指令，作为统计 Key
    except Exception as e:
        print(f"处理内容流时出错: {e}")
    return raw_counter


# ============ 模式二：矢量图形填充色去重（原文件 B） ============
def _list_by_drawings(page):
    """读取矢量图形对象填充色，去重返回 list[(类型, float元组, int元组, 填充不透明度)]。"""
    drawings = page.get_drawings()
    unique_fills = set()
    for d in drawings:
        fill = d.get("fill")
        if fill is None:
            continue

        n = len(fill)
        if n == 1:
            fill_color_type = "灰度(Gray)"
        elif n == 3:
            fill_color_type = "RGB"
        elif n == 4:
            fill_color_type = "CMYK"
        else:
            fill_color_type = "未知"

        # 灰度只有 1 个分量，补齐到 3 通道，避免下面索引越界
        if n == 1:
            fill = (fill[0], fill[0], fill[0]) + tuple(fill[1:])

        fill_rgb_float = (round(fill[0], 20), round(fill[1], 20), round(fill[2], 20))
        fill_rgb_int = (int(fill[0] * 255), int(fill[1] * 255), int(fill[2] * 255))

        fill_opacity = d.get("fill_opacity")     # None 表示未设置，等价于 1.0
        unique_fills.add((fill_color_type, fill_rgb_float, fill_rgb_int, fill_opacity))
    return sorted(unique_fills)


# ============ 统一入口：一个页范围骨架 + 两种统计模式 ============
def analyze_pdf_colors(pdf_path, pages=None, mode="both"):
    """
    遍历 PDF 指定页范围，按 mode 输出填充颜色分析结果。
        mode: "stream" | "drawings" | "both"
    """
    if mode not in ("stream", "drawings", "both"):
        raise ValueError("mode 只能是 'stream' / 'drawings' / 'both'")

    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    target_pages = parse_page_range(pages, total_pages)

    for page_index in target_pages:
        page = doc[page_index]
        print(f"\n{'=' * 80}")
        print(f"正在分析第 {page_index + 1} 页")
        print('=' * 80)

        # ---- 模式一：内容流填充指令统计 ----
        if mode in ("stream", "both"):
            raw_counter = _count_by_stream(page)
            print(f"\n[内容流模式] 第 {page_index + 1} 页，共发现 {len(raw_counter)} 种填充颜色指令：")
            print(f"{'排名':<6}{'颜色 (原始填充指令)':<70}{'出现次数':<10}")
            for rank, (cmd_text, count) in enumerate(raw_counter.most_common(), 1):
                print(f"{rank:<6}{str(cmd_text):<70}| {count}")

        # ---- 模式二：矢量图形填充色去重 ----
        if mode in ("drawings", "both"):
            unique_fills = _list_by_drawings(page)
            if not unique_fills:
                print(f"\n[图形模式] 第 {page_index + 1} 页：没有发现带填充的图形对象")
                continue
            print(f"\n[图形模式] 第 {page_index + 1} 页，去重后填充色清单：")
            for fill_color_type, fill_rgb_float, fill_rgb_int, fill_opacity in unique_fills:
                opacity = fill_opacity if fill_opacity is not None else 1.0
                opacity_flag = "  <-- 疑似水印/底纹(低不透明)" if opacity < 0.6 else ""
                print(f"Color Type: {fill_color_type}  Float(0-1): {fill_rgb_float} | "
                      f"Int(0-255): {fill_rgb_int} | fill_opacity: {fill_opacity}{opacity_flag}")

    doc.close()


# === 使用示例 ===
if __name__ == "__main__":
    pdf_file = "/Users/teacher/Desktop/百度网盘下载/20260928不要删/去水印-初二下合/初二下合.pdf"
    pages = "1-5"          # 页范围统一由 parse_page_range 解析，支持 "1-5" / "1,3,5-8" / None(全部)
    mode = "both"          # "stream" | "drawings" | "both"

    analyze_pdf_colors(pdf_path=pdf_file, pages=pages, mode=mode)