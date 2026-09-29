import fitz
import re
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import  batch_process_file_with_callback



def make_watermark_invisible(pdf_path, out_path, target_color="0.949"):
    doc = fitz.open(pdf_path)
    for page in doc:
        xref = page.get_contents()[0]          # 取该页内容流 xref
        stream = doc.xref_stream(xref).decode("latin-1")

        # 构建search_str
        search_str = ''
        # 1. 根据颜色长度自动判断类型并构建查找字符串
        if isinstance(target_color, (int, float)):
            # 灰度 (Gray) -> 操作符 'g'
            color_tuple = (float(target_color),)
            search_str = f"{target_color} g"
            color_type = "Gray"
        elif len(target_color) == 3:
            # RGB -> 操作符 'rg'
            color_tuple = tuple(float(x) for x in target_color)
            search_str = f"{' '.join(f'{x}' for x in color_tuple)} rg"
            color_type = "RGB"
        elif len(target_color) == 4:
            # CMYK -> 操作符 'k'
            color_tuple = tuple(float(x) for x in target_color)
            search_str = f"{' '.join(f'{x}' for x in color_tuple)} k"
            color_type = "CMYK"
        else:
            raise ValueError("target_color 必须是数值(灰度)、3元组(RGB)或4元组(CMYK)")

        # 1. 定位水印块：从 '0.949 g' 开始，到第一个正文文本块 'BT' 之前
        start = stream.find(search_str)
        if start == -1:
            continue
        end = stream.find("BT", start)
        if end == -1:
            end = len(stream)
        head, wm, tail = stream[:start], stream[start:end], stream[end:]

        # 2. 只在水印块内，把填充符 f/f* 换成 n（结束路径但不绘制）
        wm = re.sub(r"\bf\*?\b", "n", wm)
        # 水印变为红色
        # wm = wm.replace(f"{gray} g", "1 0 0 rg") 

        # 3. 写回
        doc.update_stream(xref, (head + wm + tail).encode("latin-1"))

    doc.save(out_path, garbage=4, deflate=True)
    doc.close()
    print("处理完成")

if __name__ == "__main__":
    input_pdf = "/Users/teacher/Desktop/002/111"
    target_color = (0.753) # 支持 灰度："0.949" rgb:(0.949, 0.949,0.949) cmyk: (0.949, 0.949, 0.949, 0.949)


    if os.path.isfile(input_pdf):
        output_pdf = input_pdf.replace('.pdf', '_output_透明.pdf')
        make_watermark_invisible(
            pdf_path = input_pdf, 
            out_path = output_pdf,
            target_color = target_color
        )
    elif os.path.isdir(input_pdf):
        input_dir = input_pdf
        output_dir = f"{input_dir}_outpout_去水印形状"

        batch_process_file_with_callback


        def callback_func(input_file, output_file):
            make_watermark_invisible(
                pdf_path = input_file, 
                out_path = output_file,
                target_color = target_color
            )

        batch_process_file_with_callback(
            input_dir = input_dir,
            output_dir = output_dir,
            callback_func = callback_func
        )
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {input_pdf}")