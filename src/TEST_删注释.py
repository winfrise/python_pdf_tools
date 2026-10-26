import fitz  # PyMuPDF

def delete_all_annotations(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    # 遍历文档中的每一页
    for page in doc:
        # 获取当前页的所有注释
        annots = page.annots()
        # 如果存在注释，则逐一删除
        if annots:
            for annot in annots:
                page.delete_annot(annot)
    # 保存修改后的新文件
    doc.save(output_pdf)
    print(f"注释已全部删除，文件已保存为: {output_pdf}")

input_pdf = "/Users/teacher/Downloads/《高等数学(上)》精讲课-配套电子讲义1+2.pdf"
output_pdf = input_pdf.replace('.pdf', '_删除注释.pdf')
delete_all_annotations(input_pdf, output_pdf)

