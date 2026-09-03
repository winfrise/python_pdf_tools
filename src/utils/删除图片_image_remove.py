import fitz  # PyMuPDF
import os
from collections import defaultdict

def remove_pdf_images(pdf_path, target_size, output_path=None):
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

    # 3. 删除功能

    try:
        w, h = map(int, target_size.split('x'))
        removed = 0
        # 遍历记录，删除匹配的图片
        for img in image_details:
            if img['width'] == w and img['height'] == h:
                page = doc[img['page']]
                page.delete_image(img['xref'])
                removed += 1
        print(f"✅ 已删除尺寸为 {w}x{h} 的图片共 {removed} 张。")

        doc.save(output_path, garbage=4, deflate=True)
        print(f"💾 文件已保存至: {output_path}")

        doc.close()
    except:
        print("❌ 输入格式错误，请确保格式为 宽x高 (如 500x300)")


if __name__ == "__main__":
    # 替换为你的 PDF 路径
    pdf_file = "/Users/teacher/Desktop/pdf_command/pdf解密/output/沪教5上语法讲义与练习题（8.12）_已解密.pdf"
    target_size = "1276x756 "
    remove_pdf_images(
        pdf_path = pdf_file, 
        target_size = target_size
    )