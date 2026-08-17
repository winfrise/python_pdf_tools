import fitz

def diagnose_pdf_colors(pdf_path, max_pages=5):
    """
    诊断工具：扫描 PDF 前几页，列出所有检测到的形状颜色。
    这能帮你确认是否存在“叠加”或“颜色数值不对”的问题。
    """
    doc = fitz.open(pdf_path)
    
    print(f"--- 开始诊断文件: {pdf_path} ---")
    
    for page_num in range(min(max_pages, len(doc))):
        page = doc[page_num]
        drawings = page.get_drawings()
        
        if not drawings:
            continue
            
        print(f"\n[第 {page_num + 1} 页] 共发现 {len(drawings)} 个图形对象")
        
        # 用一个集合来去重，只看有哪些独特的颜色
        unique_fills = set()
        unique_strokes = set()
        
        for d in drawings:
            # 获取填充色和描边色
            fill = d.get("fill")
            stroke = d.get("stroke")
            
            # 简单的格式化函数，把长浮点数变成易读的 (R,G,B)
            def fmt(c):
                if not c: return None
                # 取前三位 RGB，四舍五入到小数点后2位，忽略透明度
                return (round(c[0], 2), round(c[1], 2), round(c[2], 2))
            
            f = fmt(fill)
            s = fmt(stroke)
            
            if f: unique_fills.add(f)
            if s: unique_strokes.add(s)
            
        # 打印这一页出现的所有颜色
        print(f"  -> 出现的填充色 (Fill): {sorted(unique_fills)[:10]}...") # 只显示前10种
        print(f"  -> 出现的描边色 (Stroke): {sorted(unique_strokes)[:10]}...")

    doc.close()

# 使用示例：
diagnose_pdf_colors("/Users/teacher/Desktop/未命名文件夹 2/提取自2026胡源 高二数学精讲精练.pdf")