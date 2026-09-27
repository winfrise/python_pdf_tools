import fitz
import os
import sys
from utils import parse_page_range
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import  batch_process_file_with_callback


def redact_pdf(input_path,  pages, text_list, output_path=None):
    """
    :param input_path: 输入PDF文件路径
    :param pages: 页码范围字符串，如 "1,3-5,7"
    :param text_list: 需要遮挡的文字列表，如 ['上海中远海运重工', 'NO. 24 SERIES']
    """
    # 1. 检查输入文件是否存在
    if not os.path.exists(input_path):
        print(f"错误：输入文件 '{input_path}' 不存在！")
        return False

    if not output_path:
        output_path = input_path.replace('.pdf', '_output_替换文字.pdf')

    # 3. 打开备份文件进行处理
    doc = fitz.open(input_path)
    total_pages = len(doc)

    target_pages = parse_page_range(pages, total_pages)

    # --- 初始化统计字典 ---
    occurrence_count = {text: 0 for text in text_list}

    print(f"目标页码 (0-based): {target_pages}")
    print(f"待遮挡文字: {text_list}")

    # 4. 遍历指定页面并应用红印
    for page_num in target_pages:
        if page_num >= len(doc):
            print(f"警告：页码 {page_num + 1} 超出文档总页数，已跳过。")
            continue

        page = doc[page_num]
        for text_to_hide in text_list:
            instances = page.search_for(text_to_hide)
            if instances:
                # --- 统计找到的数量 ---
                occurrence_count[text_to_hide] += len(instances)
                print(f"在第 {page_num + 1} 页找到 {len(instances)} 处 '{text_to_hide}'")
                for inst in instances:
                    page.add_redact_annot(inst, fill=(1, 1, 1))  # 白色填充
            else:
                print(f"在第 {page_num + 1} 页未找到 '{text_to_hide}'")

        # 对当前页应用红印，而非整个文档
        page.apply_redactions()

    # 5. 保存修改后的文件（覆盖原文件名）
    try:
        # 2. 保存文件
        doc.save(output_path)
        doc.close()

        # --- 新增：打印最终统计结果 ---
        print("\n" + "="*30)
        print("🔍 替换统计结果：")
        for text, count in occurrence_count.items():
            print(f"  '{text}' : 共 {count} 处")
        print("="*30)

        print(f"处理完成！新文件已保存为：{input_path}")
        return True
    except Exception as e:
        print(f"保存失败：{e}")
        doc.close()
        return False


# --- 使用示例 ---
if __name__ == "__main__":
    # 配置参数
    input_path = "/Users/teacher/Downloads/百度网盘Download/去水印/0-中石油历年笔试真题（2014-2025年）⭐"  # 你的PDF文件路径
    pages = "1-1000"         # 页码范围 1,3-5,7
    words = ["专业助考 品质保证各类国企央企银行证券笔试代做包过微信：deoffer","各类国企央企银行证券笔试代做包过微信：deoffer", "各类国企央企银行证券笔试代做包过微信：offertop"]  # 要遮挡的文字列表

    if os.path.isfile(input_path):
        redact_pdf(
            input_path = input_path, 
            pages = pages, 
            text_list = words
        )
    elif os.path.isdir(input_path):
        input_dir = input_path
        output_dir = f"{input_dir}_outpout_已解密"

        batch_process_file_with_callback


        def callback_func(input_file, output_file):
            redact_pdf(
                input_path=input_file,
                output_path=output_file,
                pages = pages, 
                text_list = words
            )

        batch_process_file_with_callback(
            input_dir = input_dir,
            output_dir = output_dir,
            callback_func = callback_func
        )
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {input_path}")

