import fitz  # PyMuPDF
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import process_file_with_callback, batch_process_file_with_callback

def pdf_to_images(input_file,  page_range, dpi=72, img_format="jpg"):

    base_name, ext = os.path.splitext(input_file)
    output_dir = f"{base_name}__合成的图片_DPI_{dpi}"
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

    INPUT_PDF = "/Volumes/西数4T外置/百度网盘默认下载/去水印/001_output_删除图片_Object/用所选项目新建的文件夹" 
    DPI = 300
    PAGE_RANGE = '1-1000'
    IMG_FORMAT = 'jpg'



    if os.path.isfile(INPUT_PDF):
        pdf_to_images(
            input_file = INPUT_PDF,
            dpi = DPI,
            page_range = PAGE_RANGE,
            img_format = IMG_FORMAT
        )
    elif os.path.isdir(INPUT_PDF):
        def callback_func(input_file, output_file):
            pdf_to_images(
                input_file = input_file,
                dpi = DPI,
                page_range = PAGE_RANGE,
                img_format = IMG_FORMAT
            )
        input_dir = INPUT_PDF
        batch_process_file_with_callback(
            input_dir=input_dir, 
            output_dir="NOT_SAVE",
            callback_func=callback_func    
        )
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {INPUT_PDF}")