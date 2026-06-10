import fitz
import os
import sys


def parse_page_range(page_str):
    """解析页码字符串，例如 "1,3-5,7" -> [0, 2, 3, 4, 6] (转换为0-based索引)"""
    pages = set()
    if not page_str:
        return []

    parts = page_str.split(",")
    for part in parts:
        part = part.strip()
        if "-" in part:
            try:
                start, end = map(int, part.split("-"))
                for i in range(start - 1, end):
                    pages.add(i)
            except ValueError:
                print(f"警告：无法解析页码区间 '{part}'，已跳过。")
        else:
            try:
                pages.add(int(part) - 1)
            except ValueError:
                print(f"警告：无法解析页码 '{part}'，已跳过。")

    return sorted(pages)


def redact_pdf(input_path, page_range_str, text_list):
    """
    :param input_path: 输入PDF文件路径
    :param page_range_str: 页码范围字符串，如 "1,3-5,7"
    :param text_list: 需要遮挡的文字列表，如 ['上海中远海运重工', 'NO. 24 SERIES']
    """
    # 1. 检查输入文件是否存在
    if not os.path.exists(input_path):
        print(f"错误：输入文件 '{input_path}' 不存在！")
        return False

    # 2. 创建备份文件
    backup_path = input_path.replace('.pdf', '_备份.pdf')
    try:
        os.rename(input_path, backup_path)
        print(f"原文件已备份为：{backup_path}")
    except Exception as e:
        print(f"备份失败：{e}")
        return False

    # 3. 打开备份文件进行处理
    doc = fitz.open(backup_path)
    target_pages = parse_page_range(page_range_str)

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
        doc.save(input_path)
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
    file_path = "/Users/teacher/Desktop/二次修改/【08-2表】分项工程预算表.pdf"  # 你的PDF文件路径
    pages = "1-1000"         # 页码范围 1,3-5,7
    words = ["xxx", "xx1"]  # 要遮挡的文字列表

    # 运行函数
    redact_pdf(file_path, pages, words)