import re

def parse_page_range(page_range, total_pages = 10000):
    page_indices = set() # 使用集合来存储页码，自动去重
    # 将输入的字符串按逗号分割
    parts = str(page_range).split(',')
    for part in parts:
        part = part.strip() # 去除空格
        if '-' in part:
            # 处理范围，例如 "1-3"
            range_match = re.match(r'^(\d+)-(\d+)$', part)
            if range_match:
                start = int(range_match.group(1))
                end = int(range_match.group(2))
                # 确保起始页不大于结束页，并限制在文档范围内
                if start <= end:
                    page_indices.update(range(max(1, start) - 1, min(total_pages, end)))
        else:
            # 处理单个页码，例如 "1" 或 "5"
            try:
                page_num = int(part)
                if 1 <= page_num <= total_pages:
                    page_indices.add(page_num - 1) # 转换为0基索引
            except ValueError:
                # 如果转换失败，忽略该部分
                print(f"❌ 警告：无法识别的页码格式 '{part}'，已跳过。")
    
    return sorted(page_indices)