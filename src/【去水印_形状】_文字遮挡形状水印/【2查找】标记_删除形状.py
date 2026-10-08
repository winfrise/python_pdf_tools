import fitz  # PyMuPDF

def mark_shapes(input_pdf, output_pdf, is_target_shape_func, dry_run=True):
    """
    删除 PDF 中的形状，支持试运行模式。
    
    :param input_pdf: 输入 PDF 路径
    :param output_pdf: 输出 PDF 路径
    :param is_target_shape_func: 判断是否是目标形状
    :param dry_run: True=仅标记绿色不删除；False=彻底删除形状
    """
    doc = fitz.open(input_pdf)
    
    for page_num in range(doc.page_count):
        page = doc[page_num]
        paths = page.get_drawings()
        
        # 记录需要处理的形状矩形
        rects_to_process = []
        
        for path in paths:
            if is_target_shape_func(path):
                rects_to_process.append(path["rect"])
        
        if len(rects_to_process) == 0:
            continue

        if dry_run:
            # 试运行模式：将匹配的形状绘制为绿色半透明（仅覆盖显示，不删除）
            shape = page.new_shape()
            for rect in rects_to_process:
                shape.draw_rect(rect)
                shape.finish(fill=(0, 1, 0), fill_opacity=0.5, color=None)
            shape.commit(overlay=True)
            print(f"[Dry Run] 页面 {page_num + 1} 发现 {len(rects_to_process)} 个匹配的形状，已标记为绿色。")
        else:
            # 彻底删除模式：添加 Redaction 并应用
            for rect in rects_to_process:
                # 略微扩大矩形，避免描边残留导致"删不干净"
                expand = 1.0
                padded = fitz.Rect(
                    rect.x0 - expand, rect.y0 - expand,
                    rect.x1 + expand, rect.y1 + expand
                )
                page.add_redact_annot(padded)
            
            # 关键参数：
            #   images=0  忽略图像（不误删）
            #   graphics=2 删除所有与矩形"重叠"的矢量图形（解决遮挡/部分重叠问题）
            #   text=1    保留文本（不误删文字）
            page.apply_redactions(images=0, graphics=2, text=1)
            print(f"[删除] 页面 {page_num + 1} 已删除 {len(rects_to_process)} 个匹配的形状。")

    # garbage=4 清理冗余对象，deflate=True 压缩
    doc.save(output_pdf, garbage=4, deflate=True)
    doc.close()
    print(f"处理完成，文件已保存至: {output_pdf}")


# --- 使用示例 ---
if __name__ == "__main__":

    def check_target_shape(shape):
        fill_color = shape.get("fill")
        fill_opacity = shape.get("fill_opacity", 1.0)

        rect = shape.get("rect")
        shape_width = rect[2] - rect[0]
        shape_height = rect[3] - rect[1]


        CHECK_MODE = "fill_color"

        # 通过透明度判断
        if CHECK_MODE == 'opacity':
            target_fill_opacity = 0.2
            if fill_opacity and (round(fill_opacity, 2) == round(target_fill_opacity, 2)):
                return True
        # 通过填充色判断
        elif CHECK_MODE == 'fill_color':
            if fill_color:
                target_color = (0.75, 0.75, 0.75)
                rounded_fill_color = tuple(round(c, 2) for c in fill_color)
                rounded_target_color = tuple(round(c, 2) for c in target_color)
                if rounded_fill_color == rounded_target_color:
                    return True
                
        return False

    input_pdf = "/Users/teacher/Desktop/百度网盘下载/未命名文件夹/Lesson 1.pdf"
    output_pdf = input_pdf.replace('.pdf', '_output_标记目标形状.pdf')
    is_target_shape_func = check_target_shape
    dry_run = True

    # 建议流程：先 dry_run=True 确认命中准确，再改 False 正式删除
    mark_shapes(
        input_pdf=input_pdf,
        output_pdf=output_pdf,
        is_target_shape_func=is_target_shape_func,
        dry_run=dry_run,  
    )