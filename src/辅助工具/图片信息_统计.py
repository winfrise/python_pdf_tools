import fitz  # PyMuPDF
import os
from collections import defaultdict

def analyze_images(pdf_path, output_path=None):
    if output_path is None:
        pdf_dir = os.path.dirname(pdf_path)
        pdf_name = os.path.basename(pdf_path).replace('.pdf', '')
        output_path = os.path.join(pdf_dir, f"{pdf_name}_processed.pdf")

    doc = fitz.open(pdf_path)
    
    # 用于统计的字典
    size_count = defaultdict(int)      # 记录尺寸 (宽, 高) 出现的次数
    image_details = []                 # 记录每张图片的详细信息 (页码, xref, 宽, 高, 宽高比)

    print("🔍 正在扫描 PDF 中的图片信息...\n")

    # 1. 遍历所有页面，提取图片信息并统计
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)
        
        for img in image_list:
            xref = img[0]
            # 提取图片的原始像素尺寸
            img_info = doc.extract_image(xref)
            w, h = img_info['width'], img_info['height']
            ratio = round(w / h, 2)  # 宽高比保留两位小数
            
            size_count[(w, h)] += 1
            image_details.append({
                'page': page_num,
                'xref': xref,
                'width': w,
                'height': h,
                'ratio': ratio
            })

    # 2. 打印统计结果
    print(f"📊 统计完成！该 PDF 共有 {len(image_details)} 张图片。")
    
    print("\n--- 📏 相同尺寸 (宽x高) 统计 ---")
    # key=lambda x: x[1] 表示按照“数量”倒序排列，这样数量最多的排在最前面
    for size, count in sorted(size_count.items(), key=lambda x: x[1], reverse=True):
        # size 是一个元组 (width, height)，所以需要分别取值
        print(f"尺寸 {size[0]}x{size[1]} 像素: 共 {count} 张")


if __name__ == "__main__":
    # 替换为你的 PDF 路径
    pdf_file = "/Users/teacher/Desktop/去水印0903/001_output_去水印/6上语法+习题/Unit3语法  .pdf"
    analyze_images(pdf_file)