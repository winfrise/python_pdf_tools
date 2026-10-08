import fitz

def get_color_block(r, g, b, width=5):
    """
    在控制台输出指定 RGB 颜色的正方形块
    :param r: 红色通道 (0-255)
    :param g: 绿色通道 (0-255)
    :param b: 蓝色通道 (0-255)
    :param width: 块的宽度 (字符数)
    :param height: 块的高度 (行数)
    """
    # 24位真彩色 ANSI 转义序列
    color_code = f"\033[38;2;{r};{g};{b}m"
    reset_code = "\033[0m"
    
    # 生成一行由全块字符组成的字符串
    line = "█" * width
    
    # 按指定高度循环输出
    return (f"{color_code}{line}{reset_code}")

def diagnose_pdf_colors(input_path, max_pages=5):
    doc = fitz.open(input_path)
    print(f"--- 开始诊断文件: {input_path} ---")

    for page_num in range(min(max_pages, len(doc))):
        page = doc[page_num]

        # 获取页面中所有形状
        drawings = page.get_drawings()
        if not drawings:
            print(f"\n[第 {page_num + 1} 页] 没有发现图形对象")
            continue

        print(f"\n[第 {page_num + 1} 页] 共发现 {len(drawings)} 个图形对象")

        unique_fills = set()
        for shape in drawings:
            fill_color = shape.get("fill")
            fill_opacity = shape.get("fill_opacity")     # 填充不透明度
            stroke_opacity = shape.get("stroke_opacity")   # 描边不透明度

            if fill_color is None:
                continue

            # 判断颜色类型
            fill_color_type = {
                1: "灰度(Gray)", 
                3: "RGB", 
                4: "CMYK"
            }.get(len(fill_color), "未知")

            # 1. 浮点数保留3位小数
            fill_rgb_float = tuple(map(lambda x: round(x, 3), fill_color))

            # 2. 转换为 0-255 整数
            fill_rgb_int = tuple(map(lambda x: int(x * 255), fill_color))


            unique_fills.add((
                fill_color_type, 
                fill_rgb_float, 
                fill_rgb_int, 
                fill_opacity
            ))

        for fill_color_type, fill_rgb_float, fill_rgb_int, fill_opacity in sorted(unique_fills):
            r, g, b = fill_rgb_int
            color_block = get_color_block(r, g, b)

            opacity_flag = " <-- 疑似水印/底纹(低不透明)" if fill_opacity < 0.6 else ""

            # 使用圆括号 () 包裹，允许在内部自由换行
            print(
                f"{color_block} Color Type: {fill_color_type}  "
                f"Float(0-1): {fill_rgb_float} | "
                f"Int(0-255): {fill_rgb_int} | "
                f"fill_opacity: {fill_opacity}{opacity_flag}"
            )

    doc.close()

if __name__ == "__main__":
    input_path = "/Users/teacher/Desktop/百度网盘下载/未命名文件夹/Lesson 1.pdf"
    diagnose_pdf_colors(
        input_path = input_path
    )