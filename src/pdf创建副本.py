import fitz  # PyMuPDF

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import parse_page_range, batch_process_file_with_callback

# 取消签名，签名变普通内容
def generate_new_pdf(input_path, output_path):
    doc = fitz.open(input_path)
    doc.bake(annots=True, widgets=True)  # 关键：将注释和表单字段转为静态内容
    doc.save(output_path)
    doc.close()


if __name__ == "__main__":

    INPUT_FILE = "/Volumes/西数4T外置/百度网盘默认下载/检索证明/001" 
    if os.path.isfile(INPUT_FILE):
        input_path = INPUT_FILE
        output_path = input_path.replace('.pdf', '_副本.pdf')
        generate_new_pdf(
            input_path = input_path, 
            output_path = output_path, 
        )
    elif os.path.isdir(INPUT_FILE):
        def callback_func(input_file, output_file):
            generate_new_pdf(
                input_path = input_file, 
                output_path = output_file, 
            )
        input_dir = INPUT_FILE
        output_dir = f"{input_dir}_副本"
        batch_process_file_with_callback(
            input_dir=input_dir, 
            output_dir=output_dir,
            callback_func=callback_func    
        )
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {INPUT_FILE}")



