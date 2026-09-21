import fitz  # PyMuPDF
import os
from collections import defaultdict
import sys
from tools.find_img_by_size import find_img_by_size

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 计算父级目录（假设utils在src目录下，即当前目录的上一级）
parent_dir = os.path.dirname(current_dir)
# 将父级目录加入模块搜索路径
sys.path.append(parent_dir)
from utils import batch_process_file_with_callback



def remove_pdf_images(input_pdf, target_sizes, output_path=None):

    target_image_list = find_img_by_size(
        input_pdf=input_pdf,
        target_sizes=target_sizes
    )


    if output_path is None:
        output_path = input_pdf.replace('.pdf', '_output_删除图片.pdf')

    doc = fitz.open(input_pdf)


    # 3. 删除功能 - 支持多尺寸批量删除
    try:
        removed_count = 0

        # 遍历记录，删除匹配的图片
        for target_img in target_image_list:
            page = doc[target_img['page']]
            page.delete_image(target_img['xref'])
            removed_count += 1

        print(f"合计删除图片: {removed_count} 张")

        doc.save(output_path, garbage=4, deflate=True)
        print(f"文件已保存至: {output_path}")

        doc.close()
    except Exception as e:
        print(f"处理出错: {e}")


if __name__ == "__main__":
    # 替换为你的 PDF 路径
    pdf_file = "/Users/teacher/Desktop/test/森木磊石BP-让天下没有难做的电源.pdf"
    
    # target_sizes 改为数组，可以同时指定多个尺寸
    target_sizes = ["1044x696"]

    if os.path.isfile(pdf_file):
        remove_pdf_images(
            input_pdf=pdf_file, 
            target_sizes=target_sizes
        )
    elif os.path.isdir(pdf_file):
        def callback_func(input_file, output_file):
            remove_pdf_images(
                input_pdf=input_file, 
                output_path = output_file,
                target_sizes=target_sizes
            )
        input_dir = pdf_file
        output_dir = f"{input_dir}_output_去水印"
        batch_process_file_with_callback(
            input_dir=input_dir, 
            output_dir=output_dir,
            callback_func=callback_func    
        )
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {pdf_file}")