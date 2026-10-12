import fitz  # PyMuPDF

def scale_pdf_by_width_cm(input_path, output_path, new_width_cm):
    """
    按指定新宽度(单位: 厘米)同比缩放PDF的所有页面
    """
    # 1. 将厘米转换为 PyMuPDF 使用的“点”
    new_width_pt = new_width_cm * 28.346 
    
    doc = fitz.open(input_path)
    new_doc = fitz.open()
    
    for page in doc:
        # 2. 计算缩放比例
        scale_factor = new_width_pt / page.rect.width
        
        # 3. 计算新的高度（保持同比）
        new_height_pt = page.rect.height * scale_factor
        
        # 4. 创建新页面并映射内容
        new_page = new_doc.new_page(width=new_width_pt, height=new_height_pt)
        new_page.show_pdf_page(
            new_page.rect,  # 目标区域
            doc,            # 源文档
            page.number,    # 源页码
            keep_proportion=True 
        )
        
    new_doc.save(output_path)
    doc.close()
    new_doc.close()
    print(f"缩放完成，新宽度为: {new_width_cm} 厘米")

# 使用示例：将PDF缩放为宽度 400 点
input_path = "/Users/teacher/Desktop/未命名文件夹/组合 1.pdf"
new_width_cm = 15
output_path = input_path.replace('.pdf', f"_width_{new_width_cm}.pdf")

scale_pdf_by_width_cm(
    input_path = input_path, 
    output_path = output_path, 
    new_width_cm = new_width_cm
)