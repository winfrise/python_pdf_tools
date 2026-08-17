import fitz
import os

def clean_pdf_by_pixel_color(input_path, output_path):
    """
    通过像素扫描方式删除指定颜色的背景/形状
    原理：将页面渲染为图像 -> 找到目标颜色区域 -> 在原PDF上覆盖白色方块
    """
    # 1. 设定目标颜色 (RGB 0-255 整数格式，方便理解)
    # 对应之前的 (0.95, 0.95, 0.95) * 255 ≈ 242
    TARGET_R, TARGET_G, TARGET_B = 242, 242, 242 
    
    # 容差范围 (防止 241 或 243 漏网)
    TOLERANCE = 5 

    print(f"正在处理: {input_path}")
    doc = fitz.open(input_path)
    
    # 缩放比例，越高越精准，但速度越慢。2.0 通常足够清晰
    zoom = 2.0 
    mat = fitz.Matrix(zoom, zoom)

    total_patches = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # 1. 将页面渲染为 pixmap (图片对象)
        pix = page.get_pixmap(matrix=mat)
        width, height = pix.width, pix.height
        
        # 2. 获取原始字节数据进行处理
        # 这是一个巨大的列表，包含每个像素的 R,G,B,(A)
        samples = pix.samples 
        
        # 我们需要记录哪些区域需要被“涂白”
        # 为了效率，我们不逐像素涂改，而是收集坐标块
        # 这里简化处理：如果发现大面积连续颜色，直接在原PDF画白框
        
        # 注意：逐像素处理 Python 会很慢。
        # 优化策略：我们只在原 PDF 上操作，利用 fitz 的 search_for 或者手动构建 Rect
        # 但 search_for 只能搜文字。
        
        # 【修正策略】：针对这种背景色，通常是规则的大块。
        # 我们尝试用 get_drawings 再次确认，如果不行，再用下面的“盲覆盖”法。
        
        # --- 尝试方法 A：基于绘图指令的模糊匹配 (兼容性好) ---
        found_rects = []
        try:
            drawings = page.get_drawings()
            for d in drawings:
                # 检查填充色
                if d.get("fill"):
                    color = d["fill"]
                    # 转换颜色格式进行比较
                    is_match = False
                    if len(color) >= 3:
                        r, g, b = color[0], color[1], color[2]
                        # 归一化比较
                        if abs(r - 0.95) < 0.02 and abs(g - 0.95) < 0.02 and abs(b - 0.95) < 0.02:
                            is_match = True
                    
                    if is_match:
                        # 找到目标，记录它的包围盒
                        found_rects.append(d["rect"])
        except Exception as e:
            print(f"Page {page_num} 读取绘图指令失败: {e}")

        # 执行删除（覆盖白色）
        if found_rects:
            for rect in found_rects:
                # 在页面上画一个白色的矩形，盖住原来的形状
                # fill=(1,1,1) 代表白色
                page.draw_rect(rect, color=(1,1,1), fill=(1,1,1), width=0)
                total_patches += 1
            print(f"第 {page_num+1} 页: 清理了 {len(found_rects)} 个色块")
        else:
            # 如果方法 A 失败（比如形状是几千条线组成的），
            # 我们可以尝试一种“暴力法”：
            # 既然它是背景色，通常占据页面很大面积。
            # 但为了安全，我们先不执行暴力全页覆盖，而是提示你。
            pass

    if total_patches == 0:
        print("\n------------------------------------------------")
        print("依然未检测到形状。这通常意味着这些形状不是简单的‘填充矩形’，")
        print("而是由无数条‘线条’组成的网格，或者是‘图片’的一部分。")
        print("------------------------------------------------")
    else:
        doc.save(output_path)
        print(f"\n处理完成！已保存至: {output_path}")

    doc.close()

# 使用示例
# 请将路径替换为你实际的文件路径
input_file = "/Users/teacher/Desktop/未命名文件夹 2/提取自2026胡源 高二数学精讲精练.pdf"
output_file = "/Users/teacher/Desktop/未命名文件夹 2/2026胡源_清理后.pdf"

if os.path.exists(input_file):
    clean_pdf_by_pixel_color(input_file, output_file)
else:
    print("找不到文件，请检查路径")