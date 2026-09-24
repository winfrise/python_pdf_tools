import fitz  # PyMuPDF
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import  batch_process_file_with_callback

def bypass_pdf_restrictions(input_pdf, output_pdf):
    try:
        # 1. 直接打开文件（无需密码）
        doc = fitz.open(input_pdf)
        
        # 2. 核心操作：将文件重新保存为无加密版本
        # garbage=4: 清理无用对象，减小文件体积
        # deflate=True: 压缩数据流
        # encryption=fitz.PDF_ENCRYPT_NONE: 明确指定不保留任何加密
        # doc.save(output_pdf, garbage=4, deflate=True, encryption=fitz.PDF_ENCRYPT_NONE)
        doc.save(output_pdf, garbage=4, deflate=True, clean=True, encryption=fitz.PDF_ENCRYPT_NONE)
        
        doc.close()
        print(f"✅ 限制解除成功！已保存至: {output_pdf}")
        
    except Exception as e:
        print(f"❌ 处理出错: {e}")


if __name__ == "__main__":
    input_pdf = "/Users/teacher/Downloads/百度网盘Download/未命名文件夹 2/0-中石油历年笔试真题（2014-2025年）⭐"

    # 单个文件处理
    if os.path.isfile(input_pdf):
        output_pdf = input_pdf.replace('.pdf', '_已解密.pdf')
        bypass_pdf_restrictions(
            input_pdf=input_pdf,
            output_pdf=output_pdf
        )
    elif os.path.isdir(input_pdf):
        input_dir = input_pdf
        output_dir = f"{input_dir}_outpout_已解密"

        batch_process_file_with_callback


        def callback_func(input_file, output_file):
            bypass_pdf_restrictions(
                input_pdf=input_file,
                output_pdf=output_file
            )

        batch_process_file_with_callback(
            input_dir = input_pdf,
            output_dir = output_dir,
            callback_func = callback_func
        )
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {input_pdf}")