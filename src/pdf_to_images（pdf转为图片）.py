import fitz  # PyMuPDF
import os
from utils import process_file_with_callback, batch_process_file_with_callback

INPUT_FILE = "/Users/teacher/Desktop/1503认证证书/未命名文件夹/ST-1503A  智能按摩梳  质检报告  S01A25090599P00101.pdf" 
DPI = 300
PAGE_RANGE = '1-1000'
IMG_FORMAT = 'jpg'

def pdf_to_images(input_file, page_range, dpi=72, img_format="jpg"):

    output_dir = os.path.splitext(input_file)[0] + "__OUTPUT_IMAGES"
    os.makedirs(output_dir, exist_ok=True) 

    def callback_func(page, page_num, doc):
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)

        # 核心步骤：将页面渲染为像素图 (Pixmap)
        pix = page.get_pixmap(matrix=mat, alpha=False) # alpha=False 去除透明通道，对JPG很重要
        
        # 构造文件名：page_001.jpg
        filename = f"page_{page_num:03d}.{img_format}"

        output_file = os.path.join(output_dir, filename)
        
        # 保存图片
        pix.save(output_file)


    process_file_with_callback(
        input_file=input_file, 
        output_file="NOT_SAVE", 
        page_range=page_range, 
        callback_func=callback_func,
    )


# --- 使用示例 ---
if __name__ == "__main__":
    pdf_to_images(
        input_file = INPUT_FILE,
        dpi = DPI,
        page_range = PAGE_RANGE,
        img_format = IMG_FORMAT
    )