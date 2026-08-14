import fitz  # PyMuPDF
import os
import time

def classify_pdf_pages(input_path, target_sizes, tolerance=5.0, default_output_dir=None):
    """
    基于页面内容占用宽高对 PDF 页面进行分类提取
    :param input_path: 原始 PDF 文件路径
    :param target_sizes: 目标宽高列表，格式必须为 [(width, height), ...]
                         例如：[(500, 700), (300, 400)]
    :param tolerance: 宽高容差（准确度区域），单位为 pt，默认 5.0
    :param default_output_dir: 默认输出目录
    """
    
    # --- 新增：参数格式校验 ---
    if not isinstance(target_sizes, list):
        raise ValueError(f"target_sizes 必须是列表格式，例如 [(w, h)]。当前传入的是: {type(target_sizes)}")
    
    # 1. 处理默认输出目录
    if default_output_dir is None:
        default_output_dir = os.path.dirname(os.path.abspath(input_path))
    
    if not os.path.exists(default_output_dir):
        os.makedirs(default_output_dir)

    print(f"🚀 开始处理: {os.path.basename(input_path)}")
    print(f"🎯 目标尺寸: {target_sizes} (容差: ±{tolerance})")

    try:
        doc = fitz.open(input_path)
        total_pages = len(doc)
        
        # 2. 初始化输出文档
        # output_docs[0]: 命中目标的页面
        # output_docs[1]: 剩余的其他页面
        output_docs = [fitz.open(), fitz.open()]
        output_names = ["matched_pages.pdf", "remaining_pages.pdf"]
        
        start_time = time.time()

        for page_num in range(total_pages):
            page = doc[page_num]
            
            # --- 核心逻辑：获取内容占用区域 ---
            content_bbox = fitz.Rect()
            
            # 收集文本
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block["type"] == 0: 
                    for line in block["lines"]:
                        for span in line["spans"]:
                            content_bbox.include_rect(fitz.Rect(span["bbox"]))
            
            # 收集绘图/矢量图
            drawings = page.get_drawings()
            for d in drawings:
                content_bbox.include_rect(d["rect"])
                
            # 收集图片
            images = page.get_images(full=True)
            for img in images:
                try:
                    img_rect = page.get_image_bbox(img)
                    if not (img_rect.is_infinite or img_rect.is_empty):
                        content_bbox.include_rect(img_rect)
                except:
                    pass
            
            # 计算实际内容的宽和高
            content_w = content_bbox.width
            content_h = content_bbox.height
            
            # --- 判断逻辑 ---
            is_matched = False
            
            # 遍历所有设定的目标尺寸
            for t_w, t_h in target_sizes:
                # 判断是否在容差范围内 (绝对值差小于 tolerance)
                w_match = abs(content_w - t_w) <= tolerance
                h_match = abs(content_h - t_h) <= tolerance
                
                if w_match and h_match:
                    is_matched = True
                    break # 只要匹配到一个目标尺寸即可
            
            # 插入到对应的文档
            if is_matched:
                output_docs[0].insert_pdf(doc, from_page=page_num, to_page=page_num)
            else:
                output_docs[1].insert_pdf(doc, from_page=page_num, to_page=page_num)

            # --- 进度打印 ---
            if (page_num + 1) % 10 == 0 or (page_num + 1) == total_pages:
                elapsed = time.time() - start_time
                print(f"   进度: {page_num + 1}/{total_pages} 页 | "
                      f"当前页内容尺寸: {content_w:.1f} x {content_h:.1f} | "
                      f"耗时: {elapsed:.2f}s")

        # 3. 保存结果
        for i, out_doc in enumerate(output_docs):
            if len(out_doc) > 0:
                save_path = os.path.join(default_output_dir, output_names[i])
                out_doc.save(save_path)
                print(f"✅ 已生成: {save_path} (共 {len(out_doc)} 页)")
            else:
                print(f"⚠️ {output_names[i]} 为空，未生成文件。")
                
        doc.close()
        for d in output_docs: d.close()

    except Exception as e:
        print(f"❌ 处理出错: {e}")

# ==========================================
# 如何正确调用 (解决你的报错)
# ==========================================
if __name__ == "__main__":
    pdf_file = "/Users/teacher/Desktop/区域/Sevenbest Пена проф 75  D206.pdf"
    
    # 注意：第二个参数必须是列表 [(w, h)]，不能只传数字
    # 假设你要找宽约 595，高约 842 (A4) 的内容区域
    target_dimensions = [
        (171, 104),
        # (171, 71),
    ] 
    
    classify_pdf_pages(
        input_path=pdf_file, 
        target_sizes=target_dimensions, # 传入列表
        tolerance=5.0                  # 允许 10pt 的误差
    )
