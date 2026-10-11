from tools.generate_image_map import generate_image_map
from tools.replace_pdf_image_by_stream import replace_pdf_image_by_stream

if __name__ == "__main__":
    FOLDER_PATH = "/Users/teacher/Desktop/户卡博士/用所选项目新建的文件夹/新能源商用车--多合一__提取的图片"  # 你的图片文件夹路径

    # 1. 生成 map
    my_image_map = generate_image_map(FOLDER_PATH)

    # 2. 直接传给替换函数
    input_pdf = "/Users/teacher/Desktop/户卡博士/新能源商用车-小三电.pdf"
    output_pdf = input_pdf.replace('.pdf', '_替换图片.pdf')

    replace_pdf_image_by_stream(
        pdf_path=input_pdf,
        output_path= output_pdf,
        image_map = my_image_map
    )