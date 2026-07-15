import os
import fitz
from utils import parse_page_range

def process_file_with_callback(input_file, output_file, page_range, callback_func, **extra_kwargs):
    print(f"正在打开文件: {input_file} -> {output_file}")

    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误：输入文件 '{input_file}' 不存在！")
        return False


    # 打开文件
    doc = fitz.open(input_file)
    total_pages = len(doc)

    # 获取页码
    target_pages = parse_page_range(page_range, total_pages)

    # 处理每一页
    for page_num in target_pages:
        print(f"正在处理第 {page_num} 页")
        page = doc[page_num]
        # 调用回调函数
        callback_func(page, page_num, **extra_kwargs)
    

    # 保存文件
    try:
        if not output_file:
            base_name, ext = os.path.splitext(input_file)
            output_file = f"{base_name}_output{ext}"

        # 2. 保存文件
        doc.save(output_file)
        doc.close()

        return True
    except Exception as e:
        print(f"保存失败：{e}")
        doc.close()
        return False