import fitz  # PyMuPDF
import os
import re

from utils import process_file_with_callback, batch_process_file_with_callback

def add_shape_to_pdf(input_file, output_file, image_configs, page_range):
    if not output_file:
        output_file = input_file.replace(".pdf", "_output_add_shape.pdf")

    def callback_func(page, page_num, doc):
        # 遍历配置列表，在同一页添加多张图片
        for config in image_configs:
            img_path = config.get('path')
            pos = config.get('pos', (0, 0))
            size = config.get('size', None) # 默认为None，表示原始尺寸
            src_page_index = config.get('page_index', 0) # 默认为PDF图片的第0页
            rotate = config.get('rotate', 0)

            if not os.path.exists(img_path):
                print(f"⚠️ 警告：图片文件不存在 {img_path}")
                continue

            try:
                # --- 关键修改部分 ---
                # 1. 打开图片PDF文件 (作为对象)
                img_doc = fitz.open(img_path)
                
                # 2. 获取源页面的矩形区域（用于获取原始宽高）
                src_page = img_doc.load_page(src_page_index)
                src_rect = src_page.rect # 获取原始尺寸 rect(x0, y0, x1, y1)
                original_width = src_rect.width
                original_height = src_rect.height
                
                # 3. 计算插入区域
                x, y = pos
                if size is None:
                    # 如果size为None，使用原始尺寸
                    w, h = original_width, original_height
                elif size == 'fullscreen':
                    w, h = page.rect.width, page.rect.height
                else:
                    w, h = size
                
                # 定义目标矩形：(左上x, 左上y, 右下x, 右下y)
                # target_rect = fitz.Rect(x, y, x + w, y + h)

                rect_width = x + w
                rect_height = y + h

                if rotate in [90, -90, 270, -270]:
                    target_rect = fitz.Rect(y, x, rect_height, rect_width)
                else:
                    target_rect = fitz.Rect(x, y, rect_width, rect_height)

                # 4. 执行嵌入 (传入 img_doc 对象，而不是路径字符串)
                # 注意：show_pdf_page 的参数顺序是 (rect, pdf_document, page_number)
                page.show_pdf_page(target_rect, img_doc, src_page_index, rotate=rotate, overlay=True)
                
                # 5. 关闭图片PDF对象以释放内存
                img_doc.close()
                
                print(f"✅ 成功在 Page {page_num} 添加: {img_path}")

            except Exception as e:
                print(f"❌ 处理图片出错 {img_path}: {e}")


    process_file_with_callback(
        input_file = input_file,
        output_file = output_file,
        page_range = page_range,
        callback_func=callback_func
    )



def batch_add_shape(input_folder,image_configs, page_range, output_folder):
    def callback_func(input_file, output_file):
        add_shape_to_pdf(
            input_file=input_file,
            output_file=output_file,
            page_range = page_range,
            image_configs=image_configs
        )

    batch_process_file_with_callback(
        input_dir=input_folder,
        output_dir=output_folder,
        callback_func=callback_func
    )



if __name__ == "__main__":
    input_path = "/Users/teacher/Desktop/图纸修改/sign.pdf"
    output_path = "" # 单文件时为空，批量处理时为输入文件夹

    page_range = "1-1000" # page_range 示例：1,3, 5-9

    my_images = [
        {
            "path": "/Users/teacher/Desktop/图纸修改/look_bold.pdf",      # 你的SVG转成的PDF
            "pos": (0, 0),         # 距离左边50，距离底部50 (坐标系原点在左下角)
            "size": None,      # None：表示原尺寸添加；(200, 200)：表示宽200，高200 fullscreen:表示全屏添加
            "page_index": 0,          # 取该PDF的第0页
            "rotate": -90,  # 新增：设置为True以旋转90度
        },
        # {
        #     "path": "/Users/teacher/Downloads/百度网盘下载/mask2.pdf",      # 你的SVG转成的PDF
        #     "pos": (0, 0),         # 距离左边50，距离底部50 (坐标系原点在左下角)
        #     "size": None,      # None：表示原尺寸添加；(200, 200)：表示宽200，高200 fullscreen:表示全屏添加
        #     "page_index": 0          # 取该PDF的第0页
        # },
        # 可以继续添加更多图片配置...
    ]

    # 单个文件处理
    if os.path.isfile(input_path):
        add_shape_to_pdf(
                input_file=input_path, 
                image_configs=my_images, 
                page_range=page_range, 
                output_file = None,
        )
    elif os.path.isdir(input_path):
        batch_add_shape(
            input_folder=input_path,
            image_configs=my_images,
            page_range=page_range,
            output_folder=output_path
        )
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {input_path}")

