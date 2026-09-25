import fitz
import re
import os, sys
from collections import Counter
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import parse_page_range

def analyze_pdf_colors(pdf_path, pages):
    """
    遍历 PDF 每一页，统计所有填充颜色的出现次数。
    """
    # 定义正则片段
    WS = r'[ \t\r\n]+'
    # 匹配数字：支持 0.5, .5, 1., 1, 0
    NUM = r'(?:\d+\.?\d*|\.\d+)' 
    NAME = r'/[A-Za-z0-9._-]+'

    # 编译正则列表 (只关注填充指令: rg, g, k, scn)
    patterns = [
        # 1. 设备空间简写
        re.compile(rf"({NUM}){WS}({NUM}){WS}({NUM}){WS}rg"),      # RGB
        re.compile(rf"({NUM}){WS}g"),                             # Gray
        re.compile(rf"({NUM}){WS}({NUM}){WS}({NUM}){WS}({NUM}){WS}k"), # CMYK
        
        # 2. 显式设备空间 scn
        re.compile(rf"/DeviceRGB{WS}cs{WS}({NUM}){WS}({NUM}){WS}({NUM}){WS}scn"),
        re.compile(rf"/DeviceGray{WS}cs{WS}({NUM}){WS}scn"),
        re.compile(rf"/DeviceCMYK{WS}cs{WS}({NUM}){WS}({NUM}){WS}({NUM}){WS}({NUM}){WS}scn"),
        
        # 3. 命名空间 scn (注意：这里只捕获数值，不捕获名字，因为名字无法直接转RGB)
        # 假设命名空间也是标准的 RGB/Gray/CMYK 分量数量
        re.compile(rf"{NAME}{WS}cs{WS}({NUM}){WS}({NUM}){WS}({NUM}){WS}scn"), # 3分量 (可能是RGB或Gray扩展)
        re.compile(rf"{NAME}{WS}cs{WS}({NUM}){WS}({NUM}){WS}({NUM}){WS}({NUM}){WS}scn") # 4分量 (CMYK)
    ]

    doc = fitz.open(pdf_path)

    total_pages = len(doc)
    target_pages = parse_page_range(pages, total_pages)

    for page_index in target_pages:
        print(f"正在分析第{page_index + 1}页")
        page = doc[page_index]

        raw_counter = Counter()
        try:
            # 获取原始内容流字节并解码
            content_bytes = page.read_contents()
            if not content_bytes: continue
            
            content_str = content_bytes.decode('latin-1')
            
            # 遍历所有正则进行匹配
            for pattern in patterns:
                # finditer 返回匹配对象
                for match in pattern.finditer(content_str):
                    # group(0) 是整个匹配到的字符串，即我们要的 Key
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

    doc.close()



# === 使用示例 ===
if __name__ == "__main__":
    pdf_file = "/Users/teacher/Desktop/百度网盘下载/1.【言语】理论刷题合集讲义&答案（全）-粉笔名师-讲义/1.【言语】理论刷题合集讲义&答案（全）-粉笔名师-讲义.pdf"  
    pages = "1-5"
    
    stats = analyze_pdf_colors(
        pdf_path = pdf_file, 
        pages = pages
    )
    
