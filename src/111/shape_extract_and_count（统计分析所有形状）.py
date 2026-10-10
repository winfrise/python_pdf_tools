import fitz  # PyMuPDF
import os
from collections import Counter

def extract_and_export_shapes(pdf_path):
    """
    获取PDF页面中所有形状的信息（宽、高、位置、颜色），根据宽高和颜色进行统计，
    并将所有形状信息导出为txt文件。
    """
    doc = fitz.open(pdf_path)
    all_shapes_info = []
    # 统计的键现在增加了颜色信息
    size_counter = Counter()

    # 遍历所有页面提取形状信息
    for page_num in range(len(doc)):
        page = doc[page_num]
        drawings = page.get_drawings()
        
        for drawing in drawings:
            bbox = drawing["rect"]
            x0, y0, x1, y1 = bbox
            
            # 计算宽和高，并保留两位小数
            width = round(x1 - x0, 2)
            height = round(y1 - y0, 2)
            
            # 提取描边颜色(color)和填充颜色(fill)
            # 颜色值为(r, g, b)元组，范围0-1，这里转换为0-255的整数
            stroke_color = drawing.get("color")
            fill_color = drawing.get("fill")
            
            # 将颜色元组转换为 (R, G, B) 字符串格式，如果为None则标记为"无"
            if stroke_color:
                stroke_rgb = tuple(int(c * 255) for c in stroke_color)
                stroke_color_str = str(stroke_rgb)
            else:
                stroke_color_str = "无"
                
            if fill_color:
                fill_rgb = tuple(int(c * 255) for c in fill_color)
                fill_color_str = str(fill_rgb)
            else:
                fill_color_str = "无"

            shape_info = {
                "page": page_num + 1,
                "position": (round(x0, 2), round(y0, 2)),
                "width": width,
                "height": height,
                "stroke_color": stroke_color_str,
                "fill_color": fill_color_str
            }
            all_shapes_info.append(shape_info)
            
            # 统计时，将颜色信息也作为键的一部分
            # 这里我们统计 (宽, 高, 描边色, 填充色) 的组合
            size_counter[(width, height, stroke_color_str, fill_color_str)] += 1

    doc.close()

    # 导出为 TXT 文件
    output_filename = pdf_path.replace('.pdf', '_shape_info.txt')
    
    with open(output_filename, "w", encoding="utf-8") as f:
        # 写入文件表头
        f.write(f"PDF文件: {pdf_path}\n")
        f.write(f"提取形状总数: {len(all_shapes_info)}\n")
        f.write("-" * 80 + "\n")
        # 增加颜色列
        f.write(f"{'页码':<6} | {'位置(X, Y)':<15} | {'宽度':<8} | {'高度':<8} | {'描边色':<12} | {'填充色':<12}\n")
        f.write("-" * 80 + "\n")
        
        # 逐行写入形状信息
        for info in all_shapes_info:
            line = f"{info['page']:<6} | {str(info['position']):<15} | {info['width']:<8} | {info['height']:<8} | {info['stroke_color']:<12} | {info['fill_color']:<12}\n"
            f.write(line)
            
    print(f"✅ 形状信息已成功导出至: {output_filename}")
    return all_shapes_info, size_counter

# --- 使用示例 ---
if __name__ == "__main__":
    pdf_file = "/Users/teacher/Desktop/未命名文件夹 2/提取自2026胡源 高二数学精讲精练.pdf"  # 替换为你的PDF文件路径
    
    try:
        shapes_info, size_stats = extract_and_export_shapes(pdf_file)
        
        # 打印宽高和颜色统计结果
        print("\n📊 根据宽高和颜色统计结果 (宽 x 高 | 描边色 | 填充色 : 出现次数)：")
        for (w, h, sc, fc), count in size_stats.most_common():
            print(f"  {w} x {h} | 描边:{sc} | 填充:{fc} : {count} 次")
            
    except Exception as e:
        print(f"处理PDF时发生错误: {e}")