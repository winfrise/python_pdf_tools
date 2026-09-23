import fitz  # PyMuPDF

def pdf_to_gray_pymupdf(input_path, output_path):
    doc = fitz.open(input_path)
    new_doc = fitz.open()
    
    for page in doc:
        # 将页面渲染为高分辨率位图 (DPI=150)
        zoom = 150 / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        # 转换为灰度图像 ('L' 模式)
        gray_pix = fitz.Pixmap(fitz.csGRAY, pix)
        
        # 将灰度图插入新文档
        rect = page.rect
        new_page = new_doc.new_page(width=rect.width, height=rect.height)
        new_page.insert_image(rect, pixmap=gray_pix)
        
        pix = None  # 及时释放内存，防止大文件爆内存
        
    new_doc.save(output_path, garbage=4, deflate=True)
    print("✅ PyMuPDF 灰度转换完成！")

pdf_to_gray_pymupdf("/Users/teacher/Desktop/魏阳光原始病历最后版(1) (1) (1).pdf", '11.pdf')