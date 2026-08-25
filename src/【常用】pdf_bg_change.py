import fitz  # 需安装 pymupdf：pip install pymupdf


def parse_page_range(page_range_str: str, total_pages: int) -> set:
    """解析页码范围字符串，返回需要插入背景的页码集合（1-based）"""
    target_pages = set()
    if not page_range_str.strip():
        return target_pages

    parts = page_range_str.split(",")
    for part in parts:
        part = part.strip()
        if "-" in part:
            start_str, end_str = part.split("-", 1)
            try:
                start = int(start_str)
                end = int(end_str)
                # 确保页码在有效范围内（1 到 total_pages）
                start = max(1, min(start, total_pages))
                end = max(1, min(end, total_pages))
                if start <= end:
                    target_pages.update(range(start, end + 1))
            except ValueError:
                continue  # 跳过格式错误的部分
        else:
            try:
                page_num = int(part)
                if 1 <= page_num <= total_pages:
                    target_pages.add(page_num)
            except ValueError:
                continue  # 跳过非数字的部分
    return target_pages


def process_pdf(input_path: str, page_range: str, background_config: dict):
    """处理 PDF 文件，生成带背景的新 PDF"""
    bg_path = background_config["path"]

    # 打开输入 PDF 和背景 PDF
    doc_input = fitz.open(input_path)
    doc_bg = fitz.open(bg_path)
    if len(doc_bg) == 0:
        raise ValueError(f"背景 PDF {bg_path} 无页面")
    bg_page = doc_bg[0]  # 取背景 PDF 的第 1 页（索引 0）

    # 解析目标页码（1-based）
    total_pages = len(doc_input)
    target_pages = parse_page_range(page_range, total_pages)

    # 创建新 PDF 文档
    new_doc = fitz.open()

    # 遍历输入 PDF 的每一页（索引从 0 开始，对应页码为 index+1）
    for idx in range(total_pages):
        page_num = idx + 1  # 转为 1-based 页码
        input_page = doc_input[idx]

        if page_num in target_pages:

            new_doc.insert_pdf(doc_bg, from_page=0, to_page=0)
            new_page = new_doc[-1]

            new_page.show_pdf_page(input_page.rect, doc_input, idx)

        else:
            # 直接复制原页到新文档
            new_doc.insert_pdf(doc_input, from_page=idx, to_page=idx)

    # 保存新 PDF（路径可根据需求修改）
    output_path = input_path.replace(".pdf", "_processed.pdf")
    new_doc.save(output_path)
    print(f"处理完成，输出文件：{output_path}")

    # 关闭所有文档，释放资源
    doc_input.close()
    doc_bg.close()
    new_doc.close()


if __name__ == "__main__":
    # 入参配置（根据实际路径修改）
    input_path = "/Users/teacher/Desktop/去红印/合同ZC20260820001_f6716ffcd36d4e84bd13642b85f9a175.pdf"
    page_range = "1-3"  # 示例格式：1,3,5-9,10-20
    background_config = {
        "path": "/Users/teacher/Desktop/去红印/bg2.pdf",
    }

    process_pdf(input_path, page_range, background_config)