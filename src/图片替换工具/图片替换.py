from tools.generate_image_map import generate_image_map
from tools.replace_pdf_image_by_stream import replace_pdf_image_by_stream

if __name__ == "__main__":
    FOLDER_PATH = "/Users/teacher/Desktop/百度网盘下载/凯斯丽亚/3__提取的图片/用所选项目新建的文件夹"  # 你的图片文件夹路径

    # 1. 生成 map
    my_image_map = generate_image_map(FOLDER_PATH)

    # 2. 直接传给替换函数
    input_pdf = "/Users/teacher/Desktop/百度网盘下载/凯斯丽亚/3_output_删除图片对象.pdf"
    output_pdf = input_pdf.replace('.pdf', '_output_替换图片.pdf')

    replace_pdf_image_by_stream(
        pdf_path=input_pdf,
        output_path= output_pdf,
        image_map = my_image_map
    )