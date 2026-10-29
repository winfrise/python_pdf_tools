import fitz
import re
import os, sys
from collections import Counter
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import parse_page_range

def render_color(color_str):
    """
    解析 PDF/PS 格式的颜色字符串并在控制台渲染色块
    支持格式: '0 g', '1 g', '0.212 0.373 0.569 rg'
    """
    parts = color_str.strip().split()
    r, g, b = 0, 0, 0
    
    try:
        if parts[-1] == 'g':
            # 灰度模式: 只有一个数值，R=G=B
            val = int(float(parts[0]) * 255)
            r, g, b = val, val, val
        elif parts[-1] == 'rg':
            # RGB模式: 有三个数值
            r = int(float(parts[0]) * 255)
            g = int(float(parts[1]) * 255)
            b = int(float(parts[2]) * 255)
        else:
            return f"未知格式: {color_str}"
            
        # 使用 ANSI 24位真彩色转义序列渲染背景色块
        # \033[48;2;R;G;Bm 设置背景色
        # "   " 是显示的色块内容（空格）
        # \033[0m 重置颜色
        return f"\033[48;2;{r};{g};{b}m      \033[0m RGB({r},{g},{b}) {color_str}"
        
    except (ValueError, IndexError):
        return f"解析错误: {color_str}"

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
            if not content_bytes: continue
            content_str = content_bytes.decode('latin-1')
            for pattern in patterns:
                for match in pattern.finditer(content_str):
                    cmd_text = match.group(0)
                    raw_counter[cmd_text] += 1
        except Exception as e:
            print(f"处理第 {page_index+1} 页时出错: {e}")

        print(f"\n")
        print("-" * 80)
        print(f"第{page_index + 1}页，共发现 {len(raw_counter)} 种填充颜色：")
        print(f"{'排名':<6}{'颜色 (RGB)':<80}{'出现次数':<40}")
        for rank, (color, count) in enumerate(raw_counter.most_common(), 1):
            print(f"{rank:<6}{str(color):<80}| {count:<40}")
            print(render_color(color))
            print()

    doc.close()

if __name__ == "__main__":
    pdf_file = "/Volumes/西数4T外置/百度网盘默认下载/AKA红猪 资料分析·全考点全考法·考前冲刺·抄袭必究(1)/AKA红猪 资料分析·全考点全考法·考前冲刺·抄袭必究(1).pdf"  
    pages = "1-2"
    stats = analyze_pdf_colors(pdf_path=pdf_file, pages=pages)