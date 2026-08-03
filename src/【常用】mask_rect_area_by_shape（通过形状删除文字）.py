import fitz  # PyMuPDF
import os
from utils import process_file_with_callback, batch_process_file_with_callback


def get_selected_shape(drawings):
    target_fill_color = (0, 0, 0) # 黑色
    target_stroke_color = (1, 0, 0) # 红色

    selected_shapes = []
    
    # 2. 遍历所有图形，根据颜色进行筛选
    for drawing in drawings:
        # drawing 是一个字典，包含了图形的各项属性
        # 'color' 是描边（边框）颜色，'fill' 是填充颜色
        stroke_color = drawing.get("color")
        fill_color = drawing.get("fill")
        
        # 判断描边颜色或填充颜色是否匹配目标颜色
        # 注意：颜色值通常是 0 到 1 之间的浮点数元组，如 (1.0, 0.0, 0.0)
        if stroke_color == target_stroke_color or fill_color == target_fill_color:
            selected_shapes.append(drawing)
    return selected_shapes

def mask_pdf_areas(input_file, page_range, mask_color):

    if not os.path.exists(input_file):
        print(f"错误：找不到文件 {input_file}")
        return

    # 1. 生成输出文件名：原文件名_mask_output.pdf
    dir_name, file_name = os.path.split(input_file)
    name, ext = os.path.splitext(file_name)
    output_pdf = os.path.join(dir_name, f"{name}_mask_output{ext}")

    def callback_func(page, page_num, doc):
        page_width = page.rect.width
        page_height = page.rect.height

        drawings = page.get_drawings()
        selected_shapes = get_selected_shape(drawings)

        print(f"共找到 {len(selected_shapes)} 个目标形状")
        
       # 遍历当前页需要遮挡的所有区域
        for shape in selected_shapes:
            rect = shape["rect"] 
            
            # 添加红注标记（默认填充为白色）
            page.add_redact_annot(rect, fill=mask_color)
        
        # 应用红注：彻底删除该区域的底层文本和图像数据
        # images=fitz.PDF_REDACT_IMAGE_REMOVE 确保图片也被物理移除
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE)

    process_file_with_callback(
        input_file=input_file, 
        output_file=output_pdf, 
        page_range=page_range, 
        callback_func=callback_func,
    )



# --- 使用示例 ---
if __name__ == "__main__":
    # 假设输入文件在当前目录
    input_file = "/Users/teacher/Downloads/百度网盘Download/111_副本.pdf" 
    page_range = "5"
    mask_color = (1, 1, 1) # 白色
    selected_fill_color = (1, 0, 0) # 红色
    selected_stroke_color = (0, 0, 0) # 黑色
    
    
    mask_pdf_areas(
        input_file = input_file, 
        page_range = page_range,
        mask_color = mask_color,
        selected_fill_color = selected_fill_color,
        selected_stroke_color = selected_stroke_color
    )