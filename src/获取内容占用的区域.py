import fitz  # PyMuPDF
import os
import time

def classify_pdf_pages(input_path, target_sizes, tolerance=5.0, default_output_dir=None):
    """
    基于页面内容占用宽高对 PDF 页面进行分类提取
    :param input_path: 原始 PDF 文件路径
    :param target_sizes: 目标宽高列表，格式为 [(width, height), ...]
    :param tolerance: 宽高容差（准确度区域），单位为 pt，默认 5.0
    :param default_output_dir: 默认输出目录（如果不传，则使用 PDF 所在目录）
    """
    # 1. 处理默认输出目录
    if default_output_dir is None:
        default_output_dir = os.path.dirname(input_path)
    os.makedirs(default_output_dir, exist_ok=True)

    try:
        doc = fitz.open(input_path)
        total_pages = len(doc)
        
        # 2. 初始化输出文档：索引0为"命中尺寸"，索引1为"剩余页面"
        output_docs = [fitz.open(), fitz.open()]
        output_names = ["matched_pages.pdf", "remaining_pages.pdf"]
        
        # 3. 记录开始时间
        start_time = time.time()
        print(f"🚀 开始处理: {input_path} (共 {total_pages} 页)")

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
            
            # 6. 判断实际宽高是否在目标尺寸 + 容差范围内
            is_matched = False
            for (target_w, target_h) in target_sizes:
                w_match = abs(actual_w - target_w) <= tolerance
                h_match = abs(actual_h - target_h) <= tolerance
                if w_match and h_match:
                    is_matched = True
                    break  # 命中一个即可跳出循环
            
            # 7. 将页面插入到对应的输出文档中
            doc_index = 0 if is_matched else 1
            output_docs[doc_index].insert_pdf(doc, from_page=page.number, to_page=page.number)

        # 8. 保存生成的 PDF 文件
        for i, out_doc in enumerate(output_docs):
            if out_doc.page_count > 0:
                output_path = os.path.join(default_output_dir, output_names[i])
                out_doc.save(output_path)
                print(f"✅ 已生成: {output_path} (共 {out_doc.page_count} 页)")
            else:
                print(f"⚠️ 未生成 {output_names[i]} (无符合条件的页面)")
            out_doc.close()

    except Exception as e:
        print(f"❌ 处理出错: {e}")
    finally:
        doc.close()
        total_time = time.time() - start_time
        print(f"🏁 处理完成！总耗时: {total_time:.2f}s")

# ================= 用法示例 =================
if __name__ == "__main__":
    pdf_file = "/Users/teacher/Desktop/区域/提取自Sevenbest Пена проф 75  D206.pdf"
    
    # 定义多个目标宽高 (width, height)
    sizes = [
        # (451.0, 742.0),  # 尺寸1
        # (300.0, 400.0)   # 尺寸2
        ()
    ]
    
    # 设置容差为 10 pt（约 3.5 毫米），允许在这个范围内浮动
    classify_pdf_pages(pdf_file, sizes, tolerance=10.0)