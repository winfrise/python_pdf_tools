import fitz  # PyMuPDF

def split_double_page_pdf(input_path, output_path):
    # 1. 打开原始文档 (这是源)
    src_doc = fitz.open(input_path)
    # 2. 创建新文档 (这是目标)
    new_doc = fitz.open()

    print(f"正在处理: {input_path}")

    for page_num in range(len(src_doc)):
        # 获取当前页面的尺寸信息
        src_page = src_doc[page_num]
        width = src_page.rect.width
        height = src_page.rect.height

        # 定义左右两半的裁剪区域
        left_rect = fitz.Rect(0, 0, width / 2, height)
        right_rect = fitz.Rect(width / 2, 0, width, height)

        # --- 处理左半页 ---
        # 在新文档中插入一页，尺寸与原页一致
        new_page_left = new_doc.new_page(width=width/2, height=height)
        
        # 【关键点】第二个参数传 src_doc (文档对象)，第三个参数传 page_num (整数)
        new_page_left.show_pdf_page(
            new_page_left.rect,   # 目标区域：新页面的全貌
            src_doc,              # 源文档：必须是 Document 对象
            page_num,             # 源页码：整数
            clip=left_rect        # 裁剪区域：只取左半边
        )

        # --- 处理右半页 ---
        new_page_right = new_doc.new_page(width=width/2, height=height)
        
        # 同上，注意参数顺序
        new_page_right.show_pdf_page(
            new_page_right.rect, 
            src_doc,              # 源文档
            page_num,             # 源页码
            clip=right_rect       # 裁剪区域：只取右半边
        )
        
        print(f"已拆分第 {page_num + 1} 页")

    # 保存结果
    new_doc.save(output_path)
    new_doc.close()
    src_doc.close()
    print(f"完成！文件已保存至: {output_path}")

# 使用示例
if __name__ == "__main__":
    input_file = "/Users/teacher/Downloads/百度网盘Download/2027.pdf"
    output_file = "/Users/teacher/Downloads/百度网盘Download/2027_split.pdf"
    
    try:
        split_double_page_pdf(input_file, output_file)
    except Exception as e:
        print(f"发生错误: {e}")

