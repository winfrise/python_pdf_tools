import fitz  # PyMuPDF
import os
from collections import defaultdict

def remove_pdf_images(pdf_path, target_sizes, output_path=None):
    if output_path is None:
        pdf_dir = os.path.dirname(pdf_path)
        pdf_name = os.path.basename(pdf_path).replace('.pdf', '')
        output_path = os.path.join(pdf_dir, f"{pdf_name}_processed.pdf")

    doc = fitz.open(pdf_path)
    
    # 用于统计的字典
    size_count = defaultdict(int)      # 记录尺寸 (宽, 高) 出现的次数
    image_details = []                 # 记录每张图片的详细信息 (页码, xref, 宽, 高, 宽高比)

    print("正在扫描 PDF 中的图片信息...\n")

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
    print(f"统计完成！该 PDF 共有 {len(image_details)} 张图片。")

    # 3. 删除功能 - 支持多尺寸批量删除
    try:
        # 将所有目标尺寸解析为 (宽, 高) 元组列表
        target_pairs = []
        for ts in target_sizes:
            w, h = map(int, ts.split('x'))
            target_pairs.append((w, h))
        
        removed = 0
        removed_details = []  # 记录每次删除的尺寸和数量

        # 遍历记录，删除匹配的图片
        for img in image_details:
            for w, h in target_pairs:
                if img['width'] == w and img['height'] == h:
                    page = doc[img['page']]
                    page.delete_image(img['xref'])
                    removed += 1
                    # 记录该尺寸已删除，避免重复打印
                    if (w, h) not in [(t[0], t[1]) for t in removed_details]:
                        removed_details.append((w, h, 1))
                    else:
                        for i, (tw, th, cnt) in enumerate(removed_details):
                            if tw == w and th == h:
                                removed_details[i] = (tw, th, cnt + 1)
                    break  # 已匹配到目标尺寸，跳过后续判断

        # 打印删除结果
        for w, h, cnt in removed_details:
            print(f"已删除尺寸为 {w}x{h} 的图片共 {cnt} 张。")
        print(f"合计删除图片: {removed} 张")

        doc.save(output_path, garbage=4, deflate=True)
        print(f"文件已保存至: {output_path}")

        doc.close()
    except Exception as e:
        print(f"处理出错: {e}")


if __name__ == "__main__":
    # 替换为你的 PDF 路径
    pdf_file = "/Users/teacher/Desktop/pdf_command/pdf解密/output/沪教5上语法讲义与练习题（8.12）_已解密.pdf"
    
    # target_sizes 改为数组，可以同时指定多个尺寸
    target_sizes = ["1276x756", "461x154"]
    
    remove_pdf_images(
        pdf_path=pdf_file, 
        target_sizes=target_sizes
    )