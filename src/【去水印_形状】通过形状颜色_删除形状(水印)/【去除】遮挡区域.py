import fitz  # PyMuPDF
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import process_file_with_callback, batch_process_file_with_callback


def mask_pdf_areas(input_file, page_range, mask_color, is_target_shape, output_pdf = None):

    if not os.path.exists(input_file):
        print(f"错误：找不到文件 {input_file}")
        return

    # 1. 生成输出文件名：原文件名_mask_output.pdf
    dir_name, file_name = os.path.split(input_file)
    name, ext = os.path.splitext(file_name)
    if not output_pdf:
        output_pdf = os.path.join(dir_name, f"{name}_mask_output{ext}")

    def callback_func(page, page_num, doc):

        selected_shapes = []

        drawings = page.get_drawings()
        for drawing in drawings:
            if is_target_shape(drawing):
                selected_shapes.append(drawing)

        print(f"第{page_num}页，共找到 {len(selected_shapes)} 个目标形状")
        
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

    def IS_TARGET_SHAPE(shape):
        # TARGET_STROKE_COLOR = (0, 1, 0) # 红色
        # TARGET_FILL_COLOR = (0, 1, 0) # 黑色

        TARGET_STROKE_COLOR=(0, 1, 0)
        TARGET_FILL_COLOR=(0, 1, 0)

        stroke_color = shape.get("color")
        fill_color = shape.get("fill")

        if stroke_color == TARGET_STROKE_COLOR or fill_color == TARGET_FILL_COLOR:
            return True

        return False

    # 假设输入文件在当前目录
    input_file = "/Users/teacher/Desktop/百度网盘下载/去水印-初二下合/初二下合_output_删除图片_output_遮挡_output_标记目标形状.pdf" 
    output_file = input_file.replace('.pdf', '_output_Mask遮住.pdf')
    page_range = "1-1000"
    mask_color = (1, 1, 1) # 白色
    
    mask_pdf_areas(
        input_file = input_file, 
        output_pdf = output_file,
        page_range = page_range,
        mask_color = mask_color,
        is_target_shape=IS_TARGET_SHAPE
    )