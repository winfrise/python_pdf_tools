import fitz

def diagnose_pdf_colors(pdf_path, max_pages=5):
    doc = fitz.open(pdf_path)
    print(f"--- 开始诊断文件: {pdf_path} ---")
    for page_num in range(min(max_pages, len(doc))):
        page = doc[page_num]
        drawings = page.get_drawings()
        if not drawings:
            continue
        print(f"\n[第 {page_num + 1} 页] 共发现 {len(drawings)} 个图形对象")

        unique_fills = set()
        for d in drawings:
            fill = d.get("fill")
            if not fill or len(fill) < 3:
                continue

            rgb_float = (round(fill[0], 2), round(fill[1], 2), round(fill[2], 2))
            rgb_int = (int(fill[0] * 255), int(fill[1] * 255), int(fill[2] * 255))

            # 关键：读取透明度。None 表示未设置，等价于 1.0（完全不透明）
            fo = d.get("fill_opacity")     # 填充不透明度
            so = d.get("stroke_opacity")   # 描边不透明度
            fo = 1.0 if fo is None else round(fo, 2)

            unique_fills.add((rgb_float, rgb_int, fo))

        for rgb_f, rgb_i, fo in sorted(unique_fills):
            flag = "  <-- 疑似水印/底纹(低不透明)" if fo < 0.6 else ""
            print(f"  Float(0-1): {rgb_f} | Int(0-255): {rgb_i} | fill_opacity: {fo}{flag}")

    doc.close()

if __name__ == "__main__":
    # 请确保将路径替换为你自己的文件路径
    diagnose_pdf_colors("/Users/teacher/Desktop/百度网盘下载/test/信息技术笔记_已解密.pdf")