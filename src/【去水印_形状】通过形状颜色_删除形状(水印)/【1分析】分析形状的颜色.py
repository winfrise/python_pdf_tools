import fitz

def diagnose_pdf_colors(pdf_path, max_pages=5):
    doc = fitz.open(pdf_path)
    print(f"--- 开始诊断文件: {pdf_path} ---")
    for page_num in range(min(max_pages, len(doc))):
        print(page_num)
        page = doc[page_num]
        drawings = page.get_drawings()
        if not drawings:
            continue
        print(f"\n[第 {page_num + 1} 页] 共发现 {len(drawings)} 个图形对象")

        unique_fills = set()
        for d in drawings:
            fill = d.get("fill")

            if fill is None:
                continue

            # 判断颜色类型
            fill_color_type = ''
            n = len(fill)
            if n == 1:
                fill_color_type =  "灰度(Gray)"
            elif n == 3:
                fill_color_type = "RGB"
            elif n == 4:
                fill_color_type = "CMYK"
            else:
                fill_color_type =  "未知"

            fill_rgb_float = (round(fill[0], 20), round(fill[1], 20), round(fill[2], 20))
            fill_rgb_int = (int(fill[0] * 255), int(fill[1] * 255), int(fill[2] * 255))

            # 关键：读取透明度。None 表示未设置，等价于 1.0（完全不透明）
            fill_opacity = d.get("fill_opacity")     # 填充不透明度
            stroke_opacity = d.get("stroke_opacity")   # 描边不透明度

            unique_fills.add((
                fill_color_type, 
                fill_rgb_float, 
                fill_rgb_int, 
                fill_opacity
            ))

        for fill_color_type, fill_rgb_float, fill_rgb_int, fill_opacity in sorted(unique_fills):
            opacity_flag = "  <-- 疑似水印/底纹(低不透明)" if fill_opacity < 0.6 else ""
            print(f"Color Type: {fill_color_type}  Float(0-1): {fill_rgb_float} | Int(0-255): {fill_rgb_int} | fill_opacity: {fill_opacity}{opacity_flag}")

    doc.close()

if __name__ == "__main__":
    # 请确保将路径替换为你自己的文件路径
    diagnose_pdf_colors("/Users/teacher/Desktop/百度网盘下载/1.【言语】理论刷题合集讲义&答案（全）-粉笔名师-讲义/1.【言语】理论刷题合集讲义&答案（全）-粉笔名师-讲义.pdf")