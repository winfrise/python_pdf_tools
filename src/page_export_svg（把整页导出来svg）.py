import fitz  # pymupdf
import os

def extract_pdf_shapes_to_svg(input_file):
    """
    将 PDF 中的矢量形状提取为 SVG 文件，并保存在与输入文件同级目录下的 '文件夹名_svg' 文件夹中。
    
    参数:
        input_file (str): PDF 文件的路径。
    """
    # 1. 获取输入文件所在的绝对路径和文件名（不含后缀）
    file_dir = os.path.dirname(os.path.abspath(input_file))
    file_name = os.path.splitext(os.path.basename(input_file))[0]
    
    # 2. 拼接并创建目标文件夹路径（例如：原文件名为 test.pdf，则文件夹为 test_svg）
    output_folder_name = f"{file_name}_svg"
    output_dir = os.path.join(file_dir, output_folder_name)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"✅ 成功创建文件夹: {output_dir}")
    else:
        print(f"📂 目标文件夹已存在: {output_dir}")
    
    # 3. 读取 PDF 并逐页提取 SVG
    try:
        doc = fitz.open(input_file)
        total_pages = len(doc)
        print(f"📄 开始提取，共 {total_pages} 页...")
        
        for i in range(total_pages):
            page = doc[i]
            # 提取当前页的矢量内容为 SVG
            svg_content = page.get_svg_image()
            
            # 构建输出文件路径（例如：page_1.svg, page_2.svg）
            svg_file_path = os.path.join(output_dir, f"page_{i+1}.svg")
            
            # 写入 SVG 文件
            with open(svg_file_path, "w", encoding="utf-8") as f:
                f.write(svg_content)
                
        print(f"🎉 提取完成！所有 SVG 文件已保存至: {output_dir}")
        
    except Exception as e:
        print(f"❌ 提取过程中发生错误: {e}")
    finally:
        doc.close()

# --- 使用示例 ---
input_file = "/Users/teacher/Downloads/百度网盘Download/WDFCGBF32172406.pdf"
extract_pdf_shapes_to_svg(
    input_file = input_file
)