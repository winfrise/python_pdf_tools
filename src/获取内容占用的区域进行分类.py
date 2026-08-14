import fitz  # PyMuPDF
import os
import time

def classify_pdf_pages(input_path, target_sizes, tolerance=5.0, default_output_dir=None):
    """
    基于页面内容占用宽高对 PDF 页面进行分类提取
    
    :param input_path: 原始 PDF 文件路径
    :param target_sizes: 目标宽高列表，格式为 [(width, height), ...]
                         例如：[(595, 842)] 或 [(595, 842), (300, 400)]
    :param tolerance: 宽高容差（准确度区域），单位为 pt，默认 5.0
    :param default_output_dir: 默认输出目录（如果不传，则使用 PDF 所在目录）
    """
    
    # 1. 参数校验与初始化
    if not isinstance(target_sizes, list):
        raise ValueError("target_sizes 必须是列表格式，例如 [(w, h)]")
        
    if default_output_dir is None:
        default_output_dir = os.path.dirname(os.path.abspath(input_path))
    os.makedirs(default_output_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    
    try:
        doc = fitz.open(input_path)
        total_pages = len(doc)
        print(f"🚀 开始处理: {os.path.basename(input_path)} (共 {total_pages} 页)")
        print(f"🎯 目标尺寸: {target_sizes}, 容差: ±{tolerance}")
        
        # 2. 初始化输出文档容器
        # matched_docs[i] 对应 target_sizes[i]
        matched_docs = [fitz.open() for _ in range(len(target_sizes))]
        remaining_doc = fitz.open()
        
        start_time = time.time()

        for page_index in range(total_pages):
            page = doc[page_index]
            
            # --- 计算当前页面的内容边界 ---
            content_bbox = fitz.Rect()
            
            # 获取文本边界
            blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
            for block in blocks:
                if block["type"] == 0: 
                    for line in block["lines"]:
                        for span in line["spans"]:
                            content_bbox.include_rect(fitz.Rect(span["bbox"]))
            
            # 获取图片/绘图边界
            for img in page.get_images(full=True):
                try:
                    img_rect = page.get_image_bbox(img)
                    if not img_rect.is_empty: content_bbox.include_rect(img_rect)
                except: pass
            
            for drawing in page.get_drawings():
                 content_bbox.include_rect(drawing["rect"])

            # 如果页面完全空白，跳过或归入 remaining (这里选择归入 remaining)
            if content_bbox.is_empty:
                remaining_doc.insert_pdf(doc, from_page=page_index, to_page=page_index)
                continue

            # --- 核心判断逻辑 ---
            current_w = content_bbox.width
            current_h = content_bbox.height
            is_matched = False

            # 遍历所有目标尺寸进行匹配
            for idx, (t_w, t_h) in enumerate(target_sizes):
                # 判断宽高是否在容差范围内 (支持横竖屏互换检测，可选)
                w_match = abs(current_w - t_w) <= tolerance
                h_match = abs(current_h - t_h) <= tolerance
                
                # 增加反向匹配支持 (防止页面旋转90度导致漏判)
                w_match_rev = abs(current_w - t_h) <= tolerance
                h_match_rev = abs(current_h - t_w) <= tolerance

                if (w_match and h_match) or (w_match_rev and h_match_rev):
                    matched_docs[idx].insert_pdf(doc, from_page=page_index, to_page=page_index)
                    is_matched = True
                    break # 命中一个即停止，避免重复导出

            # 如果所有目标都没命中，放入剩余文档
            if not is_matched:
                remaining_doc.insert_pdf(doc, from_page=page_index, to_page=page_index)

            # --- 进度打印 ---
            if (page_index + 1) % 10 == 0 or page_index == total_pages - 1:
                elapsed = time.time() - start_time
                print(f"   ⏳ 进度: {page_index + 1}/{total_pages} | 耗时: {elapsed:.2f}s")

        # 3. 保存文件 (仅当文档有页面时才保存)
        saved_count = 0
        
        # 保存匹配的文件
        for idx, m_doc in enumerate(matched_docs):
            if len(m_doc) > 0:
                out_name = f"{base_name}_{idx}.pdf"
                out_path = os.path.join(default_output_dir, out_name)
                m_doc.save(out_path)
                print(f"✅ 已生成匹配文件: {out_name} ({len(m_doc)} 页)")
                saved_count += 1
            m_doc.close()

        # 保存剩余文件
        if len(remaining_doc) > 0:
            out_name = f"{base_name}_remaining.pdf"
            out_path = os.path.join(default_output_dir, out_name)
            remaining_doc.save(out_path)
            print(f"✅ 已生成剩余文件: {out_name} ({len(remaining_doc)} 页)")
            saved_count += 1
        remaining_doc.close()
        
        if saved_count == 0:
            print("⚠️ 警告: 未生成任何文件，请检查目标尺寸或容差设置。")
            
        doc.close()
        print(f"🏁 处理完成! 共生成 {saved_count} 个文件。")

    except Exception as e:
        print(f"❌ 处理出错: {e}")
        import traceback
        traceback.print_exc()

# ================= 调用示例 =================
if __name__ == "__main__":
    # 假设你要找 A4 大小 (595x842) 的页面
    # 这里的 target_sizes 是一个列表，即使只有一个也要用 [] 包起来
    target_dims = [
        (171, 71),
        (171, 104)
    ] 
    
    pdf_file = "/Users/teacher/Desktop/区域/Sevenbest Пена проф 75  D206.pdf"
    
    classify_pdf_pages(pdf_file, target_dims, tolerance=5.0)
