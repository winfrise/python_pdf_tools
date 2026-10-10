import fitz  # PyMuPDF
import os
import time
from collections import defaultdict

def pt_to_mm(pt_value):
    """
    将 pt（磅）转换为 mm（毫米）
    :param pt_value: pt 数值
    :return: mm 数值
    """
    return pt_value * (25.4 / 72)

def mm_to_pt(mm_value):
    """
    将 mm（毫米）转换为 pt（磅）
    :param mm_value: mm 数值
    :return: pt 数值
    """
    return mm_value * (72 / 25.4)

def classify_pdf_pages(input_path):
    """
    基于页面内容占用宽高对 PDF 页面进行分类提取
    :param input_path: 原始 PDF 文件路径
    :param target_sizes: 目标宽高列表，格式为 [(width, height), ...]
    :param tolerance: 宽高容差（准确度区域），单位为 pt，默认 5.0
    :param default_output_dir: 默认输出目录（如果不传，则使用 PDF 所在目录）
    """


    try:
        doc = fitz.open(input_path)
        total_pages = len(doc)
        
        
        # 3. 记录开始时间
        start_time = time.time()
        print(f"🚀 开始处理: {input_path} (共 {total_pages} 页)")

        size_count = defaultdict(int)      # 记录尺寸 (宽, 高) 出现的次数
        for page in doc:
            # --- 进度打印 ---
            current_page = page.number + 1
            elapsed = time.time() - start_time
            print(f"⏳ 正在处理: {current_page}/{total_pages} 页 | 耗时: {elapsed:.2f}s")
            
            # 4. 计算当前页面的实际内容占用区域
            content_bbox = fitz.Rect()
            
            # 收集文本块边界
            for block in page.get_text("dict")["blocks"]:
                if block["type"] == 0:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            content_bbox.include_rect(fitz.Rect(span["bbox"]))
            
            # 收集矢量图形边界
            for drawing in page.get_drawings():
                content_bbox.include_rect(drawing["rect"])
                
            # 收集图片边界
            for img in page.get_images(full=True):
                try:
                    img_bbox = page.get_image_bbox(img)
                    if not (img_bbox.is_infinite or img_bbox.is_empty):
                        content_bbox.include_rect(img_bbox)
                except Exception:
                    continue
            
            # 5. 获取实际内容的宽高
            actual_w = content_bbox.width
            actual_h = content_bbox.height
            page_width = page.rect.width
            page_height = page.rect.height

            print(
                f"{pt_to_mm(page_width):.2f}",
                f"{pt_to_mm(page_height):.2f}",
                f"{pt_to_mm(actual_w):.2f}",
                f"{pt_to_mm(actual_h):.2f}"
            )

            size_count[(page_width, page_height, actual_w, actual_h)] += 1
            

        print("\n")
        for size, count in size_count.items():
            # size 是一个元组 (width, height)，所以需要分别取值
            field_page_width = f"page_width: {size[0]}"  
            field_page_height = f"page_height: {size[1]}" 
            field_actual_width = f"page_width: {size[2]}"  
            field_actual_height = f"page_height: {size[3]}" 
            field_count = f"共 {count} 张"                            # 字段3：数量
            print(f" {field_page_width:<15} {field_page_height:<10} {field_actual_width:<10} {field_actual_height:<10} {field_count}")

    except Exception as e:
        print(f"❌ 处理出错: {e}")
    finally:
        doc.close()
        total_time = time.time() - start_time
        print(f"🏁 处理完成！总耗时: {total_time:.2f}s")

# ================= 用法示例 =================
if __name__ == "__main__":
    pdf_file = "/Users/teacher/Desktop/001/test/Beebot - GR 15 D White - 50 - PT Bersama Bangun Tim - QR Code V2(1).pdf"
    

    classify_pdf_pages(pdf_file)