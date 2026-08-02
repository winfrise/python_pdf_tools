import fitz  # PyMuPDF
import os
from utils import process_file_with_callback, batch_process_file_with_callback

def mm_to_pt(*args):
    factor = 2.83465
    # 处理传入元组的情况: mm_to_pt((10, 20, 30, 40))
    if len(args) == 1 and isinstance(args[0], (tuple, list)):
        return tuple(x * factor for x in args[0])
    # 处理传入多个参数的情况: mm_to_pt(10, 20, 30, 40)
    elif len(args) > 1:
        return tuple(x * factor for x in args)
    # 处理单个数值
    return args[0] * factor

def mask_pdf_areas(input_file, page_range, mask_regions, mask_color=(0, 0, 0)):
    """
    彻底遮挡PDF中的指定区域
    :param input_pdf: 输入的PDF文件路径
    :param mask_regions: 遮挡区域列表，格式为 [(x, y, width, height), ...]
    """
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

       # 遍历当前页需要遮挡的所有区域
        for x, y, width, height in mask_regions:
            # 构建遮挡矩形区域 (x0, y0, x1, y1)
            rect = fitz.Rect(x, y, x + width, y + height)
        
            
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
    input_file = "/Users/teacher/Downloads/百度网盘Download/111.pdf" 
    mask_color = (0, 0, 0) # 黑色；(0, 0, 0) 白色：（1, 1, 1,）
    page_range = "5"
    
    # 参数2：撤档的区域列表 (x, y, width, height)
    # 你可以添加多个区域，例如：[(50, 100, 200, 30), (300, 400, 150, 50)]
    regions = [
        mm_to_pt(0, 234.7, 210, 10),  # 第1个遮挡区域
        # mm_to_pt(104, 239, 160, 11),  # 第2个遮挡区域
    ]
    
    mask_pdf_areas(
        input_file = input_file, 
        page_range = page_range,
        mask_regions = regions, 
        mask_color = mask_color
    )