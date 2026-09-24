import fitz  # PyMuPDF

def remove_shapes_from_pdf(input_pdf, output_pdf, is_target_shape_func):
    """
    删除 PDF 中的形状，支持试运行模式。
    
    :param input_pdf: 输入 PDF 路径
    :param output_pdf: 输出 PDF 路径
    :param dry_run: 试运行模式，若为 True 则不删除，仅将匹配的形状变为绿色
    :param shape_filter_kwargs: 传递给 is_shape_to_delete 的参数
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
        
        # 将匹配的形状绘制为绿色（不删除原形状，仅覆盖显示）
        shape = page.new_shape()
        for rect in rects_to_process:
            shape.draw_rect(rect)
            shape.finish(color=(0, 1, 0), fill=(0, 1, 0), width=2, fill_opacity=0.5) # 绿色半透明覆盖
        shape.commit(overlay=True)
        print(f"[Dry Run] 页面 {page_num + 1} 发现 {len(rects_to_process)} 个匹配的形状，已标记为绿色。")

    # garbage=4 用于清理冗余对象，deflate=True 用于压缩
    doc.save(output_pdf, garbage=4, deflate=True)
    doc.close()
    print(f"处理完成，文件已保存至: {output_pdf}")

# --- 使用示例 ---
if __name__ == "__main__":
    input_pdf = "/Users/teacher/Desktop/百度网盘下载/去水印-四上阅读/四上阅读理解与答题模板.pdf"
    output_pdf = input_pdf.replace('.pdf', '_output_删形状.pdf')


    def check_target_shape_func(shape):
        """
        默认的形状判断逻辑：根据形状颜色（包括透明度）和尺寸来判断是否删除。
        你可以在此基础上修改判断条件。
        """
        # 1. 获取形状的边界框 (x0, y0, x1, y1)
        rect = shape.get("rect")
        if not rect:
            return False
        
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        
        # 2. 尺寸判断
        # if width < min_width or height < min_height:
        #     return False
            
        # 3. 颜色与透明度判断
        # 注意：PyMuPDF 中 stroke_color 和 fill_color 可能为 None
        stroke_color = shape.get("stroke_color")

        fill_color = shape.get("fill")
        fill_opacity = shape.get("fill_opacity", 1.0)

        if fill_color and fill_opacity:
            target_color = (0.95, 0.95, 0.95)
            target_fill_opacity = 0.32

            rounded_fill_color = tuple(round(c, 2) for c in fill_color) # 保留2位小数
            rounded_fill_opacity = round(fill_opacity, 2)
            # 示例：如果指定了目标颜色，且形状颜色匹配，且透明度匹配，则判定为需要删除
            if rounded_fill_color == target_color and rounded_fill_opacity == target_fill_opacity:
                print("fill_color:", fill_color)
                print("fill_opacity:", fill_opacity)

                # 判断谍有类型
                n = len(fill_color)
                if n == 3:
                    kind = "RGB/灰度"
                elif n == 4:
                    kind = "CMYK"
                elif n == 1:
                    kind = "灰度"
                print("颜色类型：", kind)

                return True
            
        return False


    remove_shapes_from_pdf(
        input_pdf=input_pdf, 
        output_pdf=output_pdf, 
        is_target_shape_func = check_target_shape_func
    )
    
    # 2. 正式删除
    # remove_shapes_from_pdf(
    #     input_pdf="input.pdf", 
    #     output_pdf="cleaned_output.pdf", 
    #     dry_run=False, 
    #     target_color=(1.0, 0.0, 0.0), 
    #     min_width=20, 
    #     min_height=20
    # )