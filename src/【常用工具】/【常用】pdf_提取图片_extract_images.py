import fitz  # PyMuPDF
import os

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import process_file_with_callback, batch_process_file_with_callback
from PIL import Image
import io

def extract_images(input_file, page_range):
    output_dir = os.path.splitext(input_file)[0] + "__提取的图片"
    # 自动创建不存在的文件夹
    os.makedirs(output_dir, exist_ok=True) 

    def callback_func(page, page_num, doc):

        # 获取当前页面的所有图片列表
        image_list = page.get_images(full=True)

        # 6. 遍历当前页面的所有图片
        for img_index, img in enumerate(image_list):
        
            xref = img[0]  # 图片的引用ID (xref)
            
            # 根据 xref 提取图片的原始数据
            base_image = doc.extract_image(xref)
            image_bytes, image_ext = base_image["image"], base_image["ext"]
            
            # 7. 构造图片保存的文件名
            inner_name = img[7] # 文档流中的名字
            image_filename = f"page{page_num}_img{img_index + 1}_{inner_name}.{image_ext}"
            image_full_path = os.path.join(output_dir, image_filename)
    
            # 8. 将图片写入本地文件
            with open(image_full_path, "wb") as img_file:
                img_file.write(image_bytes)
            

            print(f"✅ 已保存: {image_filename}")

    process_file_with_callback(
        input_file=input_file, 
        output_file="NOT_SAVE", 
        page_range=page_range, 
        callback_func=callback_func,
    )



# ================= 使用示例 =================
if __name__ == "__main__":

    INPUT_FILE = "/Users/teacher/Desktop/百度网盘下载/学业质量测评语文4上.pdf" 
    PAGE_RANGE = "1-1000"

    if os.path.isfile(INPUT_FILE):
        extract_images(
            input_file = INPUT_FILE, 
            page_range = PAGE_RANGE, 
        )
    elif os.path.isdir(INPUT_FILE):
        def callback_func(input_file, output_file):
            extract_images(
                input_file=input_file,
                page_range = PAGE_RANGE,
            )
        input_dir = INPUT_FILE
        batch_process_file_with_callback(
            input_dir=input_dir, 
            output_dir="NO_SAVE",
            callback_func=callback_func    
        )
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {INPUT_FILE}")
