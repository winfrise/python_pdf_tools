import fitz  # PyMuPDF
import os
from utils import process_file_with_callback, batch_process_file_with_callback



INPUT_FILE = "/Users/teacher/Desktop/未命名文件夹 2/23-4砖砌块合格证明.pdf" 
PAGE_RANGE = "5-6"
DPI = 300


def pdf_to_images(input_file, page_range, dpi=300):
    output_dir = os.path.splitext(input_file)[0] + "__合成的图片"

    # 自动创建不存在的文件夹
    os.makedirs(output_dir, exist_ok=True) 


    def callback_func(page, page_num, doc):
        # 设置缩放矩阵以控制清晰度 (DPI)
        # PDF 默认 DPI 为 72，通过 zoom 因子调整到目标 DPI
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)
        
        # 将页面渲染为像素图 (Pixmap)
        pix = page.get_pixmap(matrix=mat)
        
        # 构造输出图片的文件名 (例如: 文件名_第1页.png)
        img_filename = f"page_{page_num}.png"
        img_path = os.path.join(output_dir, img_filename)
        
        # 保存图片
        pix.save(img_path)
        print(f"✅ 已保存第 {page_num} 页：{img_filename}")

    process_file_with_callback(
        input_file=input_file, 
        output_file="NOT_SAVE", 
        page_range=page_range, 
        callback_func=callback_func,
    )




# ================= 使用示例 =================
if __name__ == "__main__":

    if os.path.isfile(INPUT_FILE):
        pdf_to_images(
            input_file = INPUT_FILE, 
            page_range = PAGE_RANGE, 
            dpi = DPI
        )
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {INPUT_FILE}")
