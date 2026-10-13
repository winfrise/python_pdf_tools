import fitz  # PyMuPDF

def check_pdf_annotations(input_pdf):
    doc = fitz.open(input_pdf)
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        # 获取当前页面的所有注释（返回生成器）
        annots = page.annots()
        
        # 判断是否存在注释
        if annots:
            # 转换为列表并统计数量
            annot_list = list(annots)
            print(f"✅ 第 {page_num + 1} 页：存在注释，共 {len(annot_list)} 个")
        else:
            print(f"❌ 第 {page_num + 1} 页：无注释")
            
    doc.close()

# 调用示例
check_pdf_annotations("/Users/teacher/Desktop/pdf_command/pdf解密/output/去水印10个文件/蓝色水印/背诵-27考研押题专项考点班-方剂学.pdf")