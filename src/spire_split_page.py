from spire.pdf import *

def split_pdf_spire(input_pdf_path, output_path=None):

    # 自动处理输出路径
    if output_path is None:
        dir_name = os.path.dirname(input_pdf_path)
        output_path = os.path.join(dir_name, "split_pages/page-{0}.pdf")

    doc = PdfDocument()
    doc.LoadFromFile(input_pdf_path)
    
    # 核心代码：一行搞定拆分单页，{0} 会自动替换为页码
    doc.Split(output_path, 1)
    
    doc.Close()
    print("拆分完成！")

# 使用示例 (注意：需提前确保 split_pages 文件夹存在)
split_pdf_spire("/Users/teacher/Desktop/未命名文件夹 2/章程.pdf")