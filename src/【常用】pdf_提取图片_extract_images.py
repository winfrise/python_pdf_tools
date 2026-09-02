import fitz  # PyMuPDF
import os
from utils import process_file_with_callback, batch_process_file_with_callback
from PIL import Image
import io


INPUT_FILE = "/Users/teacher/Desktop/20260830/改公司名称100元/11.pdf" 
PAGE_RANGE = "1-1000"
IS_FLAT_OUTPUT = True
ROTATION_ANGLE = 0 # 正数：逆时针旋转，负数：顺时针旋转

def extract_images(input_file, page_range, is_flat_output=True, rotation_angle=0):
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
            image_filename = f"page{page_num}_img{img_index + 1}.{image_ext}"
            image_full_path = os.path.join(output_dir, image_filename)

            # 1. 确定当前页的输出目录
            if not is_flat_output:
                # 非扁平化：创建 "page_页码" 子文件夹（页码从1开始）
                current_page_dir = os.path.join(output_dir, f"page_{page_num}")
                os.makedirs(current_page_dir, exist_ok=True)  # 自动创建不存在的文件夹
                image_full_path = os.path.join(current_page_dir, image_filename)


            if rotation_angle != 0:
                # 将图片字节数据加载到内存中
                image_stream = io.BytesIO(image_bytes)
                # 使用 Pillow 打开图片
                pil_image = Image.open(image_stream)
                # 旋转图片。expand=True 会自动调整画布大小以容纳整个旋转后的图片
                rotated_image = pil_image.rotate(rotation_angle, expand=True)
                
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

def batch_extract_images(input_dir, page_range):
    def callback_func(input_file, output_file):
        extract_images(
            input_file=input_file,
            page_range = page_range,
            is_flat_output = IS_FLAT_OUTPUT,
            rotation_angle = ROTATION_ANGLE,

        )

    batch_process_file_with_callback(
        input_dir=input_dir, 
        output_dir="NOT_SAVE",
        callback_func=callback_func    
    )




# ================= 使用示例 =================
if __name__ == "__main__":

    if os.path.isfile(INPUT_FILE):
        extract_images(
            input_file = INPUT_FILE, 
            page_range = PAGE_RANGE, 
            is_flat_output = IS_FLAT_OUTPUT,
            rotation_angle = ROTATION_ANGLE,
        )
    elif os.path.isdir(INPUT_FILE):
        batch_extract_images(INPUT_FILE,PAGE_RANGE, IS_FLAT_OUTPUT)
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {INPUT_FILE}")
