from tools.generate_image_map import generate_image_map
from tools.replace_pdf_image_by_stream import replace_pdf_image_by_stream

if __name__ == "__main__":
    FOLDER_PATH = "/Users/teacher/Downloads/百度网盘Download/制度改公司名称/汗克尔标准化制度牌2024__提取的图片"  # 你的图片文件夹路径

    # 1. 生成 map
    my_image_map = generate_image_map(FOLDER_PATH)

    # 2. 打印结果预览
    # import json
    # print(json.dumps(my_image_map, indent=2, ensure_ascii=False))



    # 3. 直接传给替换函数
    input_pdf = "/Users/teacher/Downloads/百度网盘Download/制度改公司名称/汗克尔标准化制度牌2024.pdf"
    output_pdf = input_pdf.replace('.pdf', '_output_替换图片.pdf')

    replace_pdf_image_by_stream(
        pdf_path=input_pdf,
        output_path= output_pdf,
        image_map = my_image_map
    )