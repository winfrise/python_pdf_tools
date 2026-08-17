import fitz  # PyMuPDF
import os

def merge_pdf_sliding_window(input_pdf_path, output_pdf_path, merge_count=3, overlap=2, spacing=50):
    """
    滑动窗口合并PDF，包含容错机制
    """
    if not os.path.exists(input_pdf_path):
        print(f"错误：找不到输入文件 {input_pdf_path}")
        return

    if not output_pdf_path:
        output_pdf_path = input_pdf_path.replace('.pdf', '_output_merge_page.pdf')

    doc = fitz.open(input_pdf_path)
    total_pages = len(doc)
    
    # 计算滑动步长
    step = merge_count - overlap
    if step <= 0:
        raise ValueError("交叉重叠页数(overlap)必须小于合并页数(merge_count)")
        
    new_doc = fitz.open()
    new_page_index = 0
    
    print(f"开始处理：共 {total_pages} 页，窗口大小 {merge_count}，重叠 {overlap}")
    print("-" * 40)

    start_idx = 0
    while start_idx < total_pages:
        # 确定当前窗口的结束索引
        end_idx = min(start_idx + merge_count, total_pages)
        current_window_pages = list(range(start_idx, end_idx))
        
        new_page_index += 1
        print(f"正在合并：第 {start_idx + 1} - {end_idx} 页  -->  生成新文档的第 {new_page_index} 页")

        try:
            # --- 1. 计算当前这一组页面的总高度 ---
            page_width = doc[0].rect.width
            current_group_height = 0
            valid_pages_info = [] # 存储 (page_obj, height, y_offset)

            temp_y = 0
            for p_idx in current_window_pages:
                try:
                    p = doc[p_idx]
                    h = p.rect.height
                    valid_pages_info.append((p, h, temp_y))
                    current_group_height += h + spacing
                    temp_y += h + spacing
                except Exception as e:
                    print(f"  [警告] 无法读取原文件第 {p_idx+1} 页的尺寸信息，已跳过该页。错误: {e}")

            if not valid_pages_info:
                print(f"  [错误] 第 {new_page_index} 组所有页面均无法读取，跳过生成。")
                start_idx += step
                continue

            current_group_height -= spacing # 减去最后多余的间距

            # --- 2. 创建新页面 ---
            new_page = new_doc.new_page(width=page_width, height=current_group_height)

            # --- 3. 绘制内容与文本层 ---
            for p_obj, p_height, y_offset in valid_pages_info:
                target_rect = fitz.Rect(0, y_offset, page_width, y_offset + p_height)
                
                # A. 绘制可视化内容 (图片/矢量)
                try:
                    new_page.show_pdf_page(target_rect, doc, p_obj.number)
                except Exception as draw_err:
                    print(f"  [警告] 绘制第 {p_obj.number+1} 页图像失败: {draw_err}")
                    # 如果图像绘制失败，画个红框提示
                    new_page.draw_rect(target_rect, color=(1, 0, 0), width=2)
                    new_page.insert_text((10, y_offset + 20), "Page Error", fontsize=20, color=(1, 0, 0))

                # B. 提取并写入文本层 (为了可复制)
                try:
                    text_dict = p_obj.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
                    for block in text_dict["blocks"]:
                        if block["type"] == 0: # 文本块
                            for line in block["lines"]:
                                for span in line["spans"]:
                                    text_content = span["text"]
                                    font_size = span["size"]
                                    # 简单的坐标映射
                                    origin_x = span["origin"][0]
                                    origin_y = span["origin"][1] + y_offset
                                    
                                    # 写入隐形文本 (颜色设为白色或透明，这里用白色防止被看见)
                                    # 注意：如果背景不是白色，可能需要调整策略，但通常白色最通用
                                    new_page.insert_text(
                                        (origin_x, origin_y), 
                                        text_content, 
                                        fontsize=font_size, 
                                        color=(1, 1, 1) # 白色文字，不可见但可选中
                                    )
                except Exception as text_err:
                    # 文本提取失败不影响大局，静默忽略或打印日志
                    pass 

        except Exception as e:
            print(f"  [严重错误] 处理第 {new_page_index} 组时发生未知错误: {e}")

        # 移动窗口
        start_idx += step

    print("-" * 40)
    print(f"处理完成！共生成 {len(new_doc)} 页。")
    new_doc.save(output_pdf_path)
    new_doc.close()
    doc.close()


# 使用示例
if __name__ == "__main__":
    input_pdf_path = "/Users/teacher/Desktop/排版/（已压缩）海连内部图册2025.9.2（原）_unencrypted_output.pdf"
    merge_count = 2
    overlap = 1
    spacing = 50
    merge_pdf_sliding_window(
        input_pdf_path=input_pdf_path,
        output_pdf_path=None,
        merge_count=merge_count,   # 每次合并3页
        overlap=overlap,       # 交叉2页
        spacing=spacing       # 页面间距
    )