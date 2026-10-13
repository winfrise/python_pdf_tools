import fitz  # PyMuPDF

input_path = "/Volumes/西数4T外置/百度网盘默认下载/RT-2026-4186_i_21584.pdf"
output_path = input_path.replace('.pdf', '_转静态.pdf')

doc = fitz.open(input_path)
doc.bake(annots=True, widgets=True)  # 关键：将注释和表单字段转为静态内容
doc.save(output_path)
doc.close()