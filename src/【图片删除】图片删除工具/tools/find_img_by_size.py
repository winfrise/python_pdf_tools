import fitz  # PyMuPDF
from collections import defaultdict

def find_img_by_size(input_pdf, target_sizes):
    # 将所有目标尺寸解析为 (宽, 高) 元组列表
    target_pairs = []
    for ts in target_sizes:
        w, h = map(int, ts.split('x'))
        target_pairs.append((w, h))

    doc = fitz.open(input_pdf) 

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
            try:
                img_info = doc.extract_image(xref)
            except Exception as e:
                print(f"警告: 无法提取页面 {page_num} 中 xref={xref} 的图片: {e}")
                continue

            img_w = img_info['width']
            img_h = img_info['height']


            for target_w, target_h in target_pairs:
                if img_w == target_w and img_h == target_h:

                    ratio = round(w / h, 2)  # 宽高比保留两位小数
                    
                    size_count[(w, h)] += 1
                    image_details.append({
                        'page': page_num,
                        'xref': xref,
                        'width': w,
                        'height': h,
                        'ratio': ratio,
                        'name': img[7]
                    })

    # 2. 打印统计结果
    print(f"统计完成！该 PDF 共有 {len(image_details)} 张【符合要求】的图片。")

    return image_details