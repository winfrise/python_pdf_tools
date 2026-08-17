import fitz

def diagnose_pdf_colors(pdf_path, max_pages=5):
    """
    诊断工具：扫描 PDF 前几页，列出所有检测到的形状颜色。
    现在会同时打印出 (0-1) 和 (0-255) 两种格式。
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

            # 修改后的格式化函数，同时返回两种格式
            def fmt(c):
                if not c or len(c) < 3:
                    return None
                # 1. RGB 浮点数格式 (0.0 - 1.0)，保留两位小数
                rgb_float = (round(c[0], 2), round(c[1], 2), round(c[2], 2))
                # 2. RGB 整数格式 (0 - 255)
                rgb_int = (int(c[0] * 255), int(c[1] * 255), int(c[2] * 255))
                return (rgb_float, rgb_int)

            f = fmt(fill)
            s = fmt(stroke)

            if f:
                unique_fills.add(f)
            if s:
                unique_strokes.add(s)

        # 打印这一页出现的所有颜色
        # 注意：这里对集合进行排序时，会根据元组的第一个元素（即rgb_float）来排序
        sorted_fills = sorted(unique_fills)
        sorted_strokes = sorted(unique_strokes)

        print(f" -> 出现的填充色 (Fill):")
        for rgb_f, rgb_i in sorted_fills[:10]: # 只显示前10种
            print(f"    Float(0-1): {rgb_f}  |  Int(0-255): {rgb_i}")
        if len(sorted_fills) > 10: print("    ...")

        print(f" -> 出现的描边色 (Stroke):")
        for rgb_f, rgb_i in sorted_strokes[:10]: # 只显示前10种
            print(f"    Float(0-1): {rgb_f}  |  Int(0-255): {rgb_i}")
        if len(sorted_strokes) > 10: print("    ...")

    doc.close()

# 使用示例：
# 请确保将路径替换为你自己的文件路径
diagnose_pdf_colors("/Users/teacher/Desktop/未命名文件夹 2/提取自2026胡源 高二数学精讲精练.pdf")