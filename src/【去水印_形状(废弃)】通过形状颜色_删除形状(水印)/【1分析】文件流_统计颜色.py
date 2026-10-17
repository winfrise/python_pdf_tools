import fitz
import re
import os, sys
from collections import Counter
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import parse_page_range

# ---------- ANSI 颜色工具 ----------
RESET = "\033[0m"

def rgb_block(r, g, b, text="  "):
    """用 ANSI 真彩色背景显示一个色块"""
    r = max(0, min(255, int(round(r))))
    g = max(0, min(255, int(round(g))))
    b = max(0, min(255, int(round(b))))
    return f"\033[48;2;{r};{g};{b}m{text}{RESET}"

def clamp01(v):
    return max(0.0, min(1.0, v))

def cmyk_to_rgb(c, m, y, k):
    c, m, y, k = map(clamp01, (c, m, y, k))
    r = (1 - c) * (1 - k)
    g = (1 - m) * (1 - k)
    b = (1 - y) * (1 - k)
    return r * 255, g * 255, b * 255

# ---------- 颜色指令解析 ----------
def parse_color_cmd(cmd_text):
    """
    把一个颜色指令字符串解析成 (类型, 分量列表)
    返回 None 表示无法解析。
    """
    s = cmd_text.strip()
    # 去掉可能的换行
    s = re.sub(r'\s+', ' ', s)

    # 1. rg / g / k 简写
    m = re.match(r'^([\d.]+) ([\d.]+) ([\d.]+) rg$', s)
    if m:
        return ('rgb', [float(x) for x in m.groups()])
    m = re.match(r'^([\d.]+) g$', s)
    if m:
        return ('gray', [float(m.group(1))])
    m = re.match(r'^([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) k$', s)
    if m:
        return ('cmyk', [float(x) for x in m.groups()])

    # 2. 显式设备空间 scn
    m = re.match(r'^/DeviceRGB cs ([\d.]+) ([\d.]+) ([\d.]+) scn$', s)
    if m:
        return ('rgb', [float(x) for x in m.groups()])
    m = re.match(r'^/DeviceGray cs ([\d.]+) scn$', s)
    if m:
        return ('gray', [float(m.group(1))])
    m = re.match(r'^/DeviceCMYK cs ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) scn$', s)
    if m:
        return ('cmyk', [float(x) for x in m.groups()])

    # 3. 命名空间 scn
    m = re.match(r'^/\S+ cs ([\d.]+) scn$', s)
    if m:
        return ('gray', [float(m.group(1))])
    m = re.match(r'^/\S+ cs ([\d.]+) ([\d.]+) ([\d.]+) scn$', s)
    if m:
        return ('rgb', [float(x) for x in m.groups()])
    m = re.match(r'^/\S+ cs ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) scn$', s)
    if m:
        return ('cmyk', [float(x) for x in m.groups()])

    return None

def color_to_rgb(parsed):
    """把解析结果转成 (R, G, B) 0-255"""
    if parsed is None:
        return None
    kind, vals = parsed
    if kind == 'rgb':
        r, g, b = vals
        return clamp01(r)*255, clamp01(g)*255, clamp01(b)*255
    if kind == 'gray':
        v = clamp01(vals[0]) * 255
        return v, v, v
    if kind == 'cmyk':
        return cmyk_to_rgb(*vals)
    return None

# ---------- 主函数 ----------
def analyze_pdf_colors(pdf_path, pages):
    WS = r'[ \t\r\n]+'
    NUM = r'(?:\d+\.?\d*|\.\d+)'
    NAME = r'/[A-Za-z0-9._-]+'

    patterns = [
        re.compile(rf"({NUM}){WS}({NUM}){WS}({NUM}){WS}rg\b"),
        re.compile(rf"({NUM}){WS}g\b"),
        re.compile(rf"({NUM}){WS}({NUM}){WS}({NUM}){WS}({NUM}){WS}k\b"),
        re.compile(rf"/DeviceRGB{WS}cs{WS}({NUM}){WS}({NUM}){WS}({NUM}){WS}scn\b"),
        re.compile(rf"/DeviceGray{WS}cs{WS}({NUM}){WS}scn\b"),
        re.compile(rf"/DeviceCMYK{WS}cs{WS}({NUM}){WS}({NUM}){WS}({NUM}){WS}({NUM}){WS}scn\b"),
        re.compile(rf"{NAME}{WS}cs{WS}({NUM}){WS}({NUM}){WS}({NUM}){WS}scn\b"),
        re.compile(rf"{NAME}{WS}cs{WS}({NUM}){WS}({NUM}){WS}({NUM}){WS}({NUM}){WS}scn\b")
    ]

    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    target_pages = parse_page_range(pages, total_pages)

    for page_index in target_pages:
        print(f"正在分析第{page_index + 1}页")
        page = doc[page_index]
        raw_counter = Counter()
        try:
            content_bytes = page.read_contents()
            if not content_bytes:
                continue
            content_str = content_bytes.decode('latin-1')
            for pattern in patterns:
                for match in pattern.finditer(content_str):
                    raw_counter[match.group(0)] += 1
        except Exception as e:
            print(f"处理第 {page_index+1} 页时出错: {e}")

        print()
        print("-" * 100)
        print(f"第{page_index + 1}页，共发现 {len(raw_counter)} 种填充颜色：")
        header = f"{'排名':<5} {'色块':<8} {'RGB(0-255)':<16} {'颜色指令':<60} {'次数':>6}"
        print(header)
        print("-" * 100)

        for rank, (cmd_text, count) in enumerate(raw_counter.most_common(), 1):
            parsed = parse_color_cmd(cmd_text)
            rgb = color_to_rgb(parsed)

            if rgb is not None:
                block = rgb_block(*rgb)
                rgb_str = f"({int(rgb[0])},{int(rgb[1])},{int(rgb[2])})"
            else:
                # 无法解析的，显示问号块
                block = "\033[48;2;128;128;128m??\033[0m"
                rgb_str = "未知"

            # 用两个块更好看
            block = block * 2 if rgb is not None else block
            # 清理指令里的换行，保证单行显示
            cmd_display = re.sub(r'\s+', ' ', cmd_text)
            print(f"{rank:<5} {block:<10} {rgb_str:<16} {cmd_display:<60} {count:>6}")

    doc.close()


if __name__ == "__main__":
    pdf_file = "/Users/teacher/Desktop/百度网盘下载/口腔医学中心/002/1.pdf"
    pages = "1-5"
    analyze_pdf_colors(pdf_path=pdf_file, pages=pages)