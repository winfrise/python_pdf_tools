import fitz  # PyMuPDF
import os

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import process_file_with_callback, batch_process_file_with_callback
from PIL import Image
import io

def extract_images(input_file, page_range, is_flat_output=True, rotate_angle=0, target_img_index = -1):
    output_dir = os.path.splitext(input_file)[0] + "__提取的图片"
    # 自动创建不存在的文件夹
    os.makedirs(output_dir, exist_ok=True) 

    def callback_func(page, page_num, doc):

        # 获取当前页面的所有图片列表
        image_list = page.get_images(full=True)

        # 6. 遍历当前页面的所有图片
        for img_index, img in enumerate(image_list):

            if (target_img_index >= 0) & (img_index != target_img_index):
                continue
            
            xref = img[0]  # 图片的引用ID (xref)
            
            # 根据 xref 提取图片的原始数据
            base_image = doc.extract_image(xref)
            image_bytes, image_ext = base_image["image"], base_image["ext"]
            
            # 7. 构造图片保存的文件名
            inner_name = img[7]
            image_filename = f"page{page_num}_img{img_index + 1}_{inner_name}.{image_ext}"
            image_full_path = os.path.join(output_dir, image_filename)

            # 1. 确定当前页的输出目录
            if not is_flat_output:
                # 非扁平化：创建 "page_页码" 子文件夹（页码从1开始）
                current_page_dir = os.path.join(output_dir, f"page_{page_num}")
                os.makedirs(current_page_dir, exist_ok=True)  # 自动创建不存在的文件夹
                image_full_path = os.path.join(current_page_dir, image_filename)

            current_rotate = rotate_angle
            if callable(current_rotate):
                width = img[2]  # 图片宽度（像素）
                height = img[3]  # 图片高度（像素）
                current_rotate = current_rotate(
                    page, 
                    {'width': width, 'height':height}
                )

            if current_rotate != 0:
                # 将图片字节数据加载到内存中
                image_stream = io.BytesIO(image_bytes)
                # 使用 Pillow 打开图片
                pil_image = Image.open(image_stream)
                # 旋转图片。expand=True 会自动调整画布大小以容纳整个旋转后的图片
                rotated_image = pil_image.rotate(current_rotate, expand=True)
                
                # 将旋转后的图片保存到另一个内存流中
                output_stream = io.BytesIO()
                # 保存时指定格式，例如 'JPEG' 或 'PNG'。Pillow 可以根据扩展名自动推断，但显式指定更稳妥
                rotated_image.save(output_stream, format=pil_image.format)
                # 获取旋转后的图片字节数据
                image_bytes = output_stream.getvalue()
    
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
    def rotate_angele_func (page, img_info):
        # width = img_info['width']
        # height = img_info['height']

        # if width > height:
        #     return -90
        # 正数：逆时针旋转，负数：顺时针旋转
        return 0

    INPUT_FILE = "/Users/teacher/Desktop/百度网盘下载/高中英语人教版课本单词表总汇(1).pdf" 
    PAGE_RANGE = "1-1000"
    IS_FLAT_OUTPUT = True
    ROTATE_ANGLE = rotate_angele_func
    TARGET_IMG_INDEX = -1

    if os.path.isfile(INPUT_FILE):
        extract_images(
            input_file = INPUT_FILE, 
            page_range = PAGE_RANGE, 
            is_flat_output = IS_FLAT_OUTPUT,
            rotate_angle = ROTATE_ANGLE,
            target_img_index=TARGET_IMG_INDEX,
        )
    elif os.path.isdir(INPUT_FILE):
        def callback_func(input_file, output_file):
            extract_images(
                input_file=input_file,
                page_range = PAGE_RANGE,
                is_flat_output = IS_FLAT_OUTPUT,
                rotate_angle = ROTATE_ANGLE,
                target_img_index=TARGET_IMG_INDEX,
            )
        input_dir = INPUT_FILE
        batch_process_file_with_callback(
            input_dir=input_dir, 
            output_dir="NO_SAVE",
            callback_func=callback_func    
        )
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {INPUT_FILE}")
