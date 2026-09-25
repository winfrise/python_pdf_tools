import fitz  # PyMuPDF

def mark_shapes(input_pdf, output_pdf, is_target_shape_func):
    """
    删除 PDF 中的形状，支持试运行模式。
    
    :param input_pdf: 输入 PDF 路径
    :param output_pdf: 输出 PDF 路径
    :param is_target_shape_func: 判断是否是目标形状
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
            shape.finish(fill=(0, 1, 0), fill_opacity=0.5, color=None)  # 仅填充绿色半透明，无边框
        shape.commit(overlay=True)

        if (len(rects_to_process) > 0):
            print(f"[Dry Run] 页面 {page_num + 1} 发现 {len(rects_to_process)} 个匹配的形状，已标记为绿色。")

    # garbage=4 用于清理冗余对象，deflate=True 用于压缩
    doc.save(output_pdf, garbage=4, deflate=True)
    doc.close()
    print(f"处理完成，文件已保存至: {output_pdf}")

# --- 使用示例 ---
if __name__ == "__main__":

    # 通过高度判断
    def check_target_shape_by_height(shape):
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
        if (height > 11.5 and height < 12.5 and rect[2] > 546):
            print(rect)
            return True

        return False

    # 通过填充颜色和透明度判断
    def check_target_shape_by_fill_opacity(shape):
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

    def check_target_shape_by_fill(shape):
        fill_color = shape.get("fill")

        if fill_color:
            target_color = (0.949, 0.949, 0.949)

            rounded_fill_color = tuple(round(c, 3) for c in fill_color)
            rounded_target_color = tuple(round(c, 3) for c in target_color)

            # 示例：如果指定了目标颜色，且形状颜色匹配，且透明度匹配，则判定为需要删除
            if rounded_fill_color == rounded_target_color:
                print("fill_color:", fill_color)

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



    input_pdf = "/Users/teacher/Desktop/百度网盘下载/未命名文件夹 2/背诵资料/美国文学考研资料.pdf"
    output_pdf = input_pdf.replace('.pdf', '_output_标记目标形状.pdf')
    is_target_shape_func = check_target_shape_by_fill

    mark_shapes(
        input_pdf=input_pdf, 
        output_pdf=output_pdf, 
        is_target_shape_func = is_target_shape_func
    )
