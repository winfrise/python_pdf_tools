import fitz  # PyMuPDF
import os
import re


# 代码不够键合：input_file为多页的时候会有问题

from utils import process_file_with_callback, batch_process_file_with_callback

def background_overlay(input_file, background_config, page_range, output_file = None):
    if not output_file:
        output_file = input_file.replace(".pdf", "_output_overlay_background.pdf")

    def callback_func(page, page_num, doc):
        # 遍历配置列表，在同一页添加多张图片
 
        background_path = background_config.get('path')
        background_page_index = background_config.get('page_index', 0) # 默认为PDF图片的第0页
        rotate = background_config.get('rotate', 0)

        if not os.path.exists(background_path):
            print(f"⚠️ 警告：背景文件不存在 {background_path}")
            return

        try:
            # --- 关键修改部分 ---
            # 1. 打开图片PDF文件 (作为对象)
            background_doc = fitz.open(background_path)
            
            # 2. 获取源页面的矩形区域（用于获取原始宽高）
            background_page = background_doc.load_page(background_page_index)

            content_page_width = page.rect.width
            content_page_height = page.rect.height
            if rotate in [90, -90, 270, -270]:
                target_rect = fitz.Rect(0, 0, content_page_height, content_page_width)
            else:
                target_rect = fitz.Rect(0, 0, content_page_width, content_page_height)


            page_index = page_num - 1
            background_page.show_pdf_page(
                target_rect, 
                doc, 
                page_index, 
                rotate=rotate, 
                overlay=True
            )
            
            # 5. 关闭图片PDF对象以释放内存
            background_doc.save(output_file)
            background_doc.close()
            print(f"✅ 成功在 Page {page_num} 添加: {background_path}")

        except Exception as e:
            print(f"❌ 处理图片出错 {background_path}: {e}")


    process_file_with_callback(
        input_file = input_file,
        output_file = "NO_SAVE",
        page_range = page_range,
        callback_func=callback_func
    )



def batch_background_overlay(input_folder,background_config, page_range):
    def callback_func(input_file, output_file):
        background_overlay(
            input_file=input_file,
            output_file=output_file,
            page_range = page_range,
            background_config=background_config
        )

    output_folder = f"{input_folder}_output_background_overlay"
    batch_process_file_with_callback(
        input_dir=input_folder,
        output_dir=output_folder,
        callback_func=callback_func
    )



if __name__ == "__main__":
    input_path = "/Users/teacher/Desktop/图纸修改/未命名文件夹"
    page_range = "1-1000" # page_range 示例：1,3, 5-9

    background_config = {
        "path": "/Users/teacher/Desktop/图纸修改/sign.pdf", 
        "rotate": -90 
    }


    # 单个文件处理
    if os.path.isfile(input_path):
        background_overlay(
                input_file=input_path, 
                background_config=background_config, 
                page_range=page_range, 
        )
    elif os.path.isdir(input_path):
        batch_background_overlay(
            input_folder=input_path,
            background_config=background_config,
            page_range=page_range,
        )
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {input_path}")

