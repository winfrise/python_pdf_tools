import fitz  # PyMuPDF
import os
import time

def classify_pdf_pages(input_path, target_sizes, tolerance=5.0, default_output_dir=None):
    """
    基于页面内容占用宽高对 PDF 页面进行分类提取
    
    :param input_path: 原始 PDF 文件路径
    :param target_sizes: 目标宽高列表，格式为 [(width, height), ...]
    :param tolerance: 宽高容差（准确度区域），单位为 pt，默认 5.0
    :param default_output_dir: 默认输出目录
    """
    
    # 1. 参数校验与初始化
    if not isinstance(target_sizes, list):
        raise ValueError("target_sizes 必须是列表格式，例如 [(w, h)]")
        
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"找不到文件: {input_path}")

    # 处理输出目录
    if default_output_dir is None:
        default_output_dir = os.path.dirname(os.path.abspath(input_path))
    os.makedirs(default_output_dir, exist_ok=True)

    # 获取基础文件名（去除扩展名）
    base_name = os.path.splitext(os.path.basename(input_path))[0]

    try:
        doc = fitz.open(input_path)
        total_pages = len(doc)
        print(f"📄 开始处理: {os.path.basename(input_path)} (共 {total_pages} 页)")
        print(f"🎯 目标尺寸: {target_sizes}, 容差: ±{tolerance}")
        
        # 2. 初始化输出文档容器
        # matched_docs: 存储每个目标尺寸对应的 PDF 对象
        matched_docs = [fitz.open() for _ in target_sizes]
        remaining_doc = fitz.open()
        
        start_time = time.time()

        # 3. 遍历每一页进行分类
        for page_index in range(total_pages):
            page = doc[page_index]
            
            # --- 核心逻辑：计算页面内容实际占用的宽高 ---
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
            
            # 如果页面完全空白，content_bbox 会是空的，这里给个默认值防止报错
            if content_bbox.is_empty:
                actual_w, actual_h = 0, 0
            else:
                actual_w = content_bbox.width
                actual_h = content_bbox.height

            # --- 匹配逻辑 (互斥) ---
            matched = False
            for i, (target_w, target_h) in enumerate(target_sizes):
                # 判断宽高是否在容差范围内
                w_match = abs(actual_w - target_w) <= tolerance
                h_match = abs(actual_h - target_h) <= tolerance
                
                if w_match and h_match:
                    matched_docs[i].insert_pdf(doc, from_page=page_index, to_page=page_index)
                    matched = True
                    break # 匹配成功一个后跳出，不再匹配后续尺寸
            
            # 如果所有目标尺寸都没匹配上，放入剩余文档
            if not matched:
                remaining_doc.insert_pdf(doc, from_page=page_index, to_page=page_index)

            # --- 进度打印 ---
            if (page_index + 1) % 10 == 0 or (page_index + 1) == total_pages:
                elapsed = time.time() - start_time
                print(f"   ⏳ 进度: {page_index + 1}/{total_pages} | 耗时: {elapsed:.2f}s")

        doc.close()

        # 4. 保存文件 (按新命名规则)
        saved_count = 0
        
        # 保存匹配到的文件
        for i, out_doc in enumerate(matched_docs):
            if len(out_doc) > 0:
                t_w, t_h = target_sizes[i]
                # 格式化文件名：原文件名_【索引+1】_【范围宽X范围高】.pdf
                # 这里的宽高大取整数显示，看起来更整洁
                new_name = f"{base_name}_{i+1}_{int(t_w)}x{int(t_h)}.pdf"
                save_path = os.path.join(default_output_dir, new_name)
                out_doc.save(save_path)
                print(f"   ✅ 已导出匹配文件: {new_name} ({len(out_doc)}页)")
                saved_count += 1
            out_doc.close()

        # 保存剩余文件
        if len(remaining_doc) > 0:
            rem_name = f"{base_name}_remaining.pdf"
            save_path = os.path.join(default_output_dir, rem_name)
            remaining_doc.save(save_path)
            print(f"   ✅ 已导出剩余文件: {rem_name} ({len(remaining_doc)}页)")
            saved_count += 1
        remaining_doc.close()

        if saved_count == 0:
            print("⚠️ 警告: 没有生成任何文件，请检查目标尺寸或容差设置。")
        else:
            print(f"🎉 处理完成! 共生成 {saved_count} 个文件。")

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
    
    pdf_file = "/Users/teacher/Desktop/区域/Sevenbest Пена проф 45  D203.pdf"
    
    classify_pdf_pages(pdf_file, target_dims, tolerance=5.0)
