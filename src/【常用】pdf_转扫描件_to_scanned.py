import os
import fitz  # PyMuPDF
from utils import process_file_with_callback, batch_process_file_with_callback

INPUT_FILE = "/Volumes/西数4T外置/Pdf修改资料/2026年8月/完成/试卷去水印ing/2026胡源 高二数学精讲精练·配套习题(1).pdf" 
DPI = 300

def convert_to_scanned_pdf(input_file, dpi=300):
    
    output_file = input_file.replace(".pdf", "_转图片版.pdf")

    print(f"📄 输入文件: {input_file}")
    print(f"⚙️ 设置分辨率: {dpi} DPI")
    

    # 创建一个新的空 PDF 用于写入
    new_doc = fitz.open()

    # 打开原始 PDF
    doc = fitz.open(input_file)
    
    # 2. 计算缩放倍率 (PyMuPDF 基础分辨率为 72 DPI)
    # 例如：300 / 72 ≈ 4.16 倍
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)

    print(f"🔄 正在转换... (共 {doc.page_count} 页)")
    
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)

        # 获取页面尺寸（宽高）
        page_width = page.rect.width
        page_height = page.rect.height
        
        # 将页面渲染为图片 (Pixmap)
        pix = page.get_pixmap(matrix=mat, alpha=False) # alpha=False 避免透明通道导致的黑底问题
        
        # 创建新的页面，和原来的页面大小一样
        new_page = new_doc.new_page(width=page_width, height=page_height)

        # 将图片直接插入页面，传入的是 rect (矩形区域) 和 stream (字节流)
        new_page.insert_image(fitz.Rect(0, 0, page_width, page_height), stream=pix.tobytes("png"))
        
        # 释放 pixmap 内存
        pix = None

        print(f"   ...已处理 {page_num + 1}/{doc.page_count} 页")

    # 3. 保存新文件
    new_doc.save(output_file)
    new_doc.close()
    doc.close()

    print(f"✅ 转换完成！文件已保存至: {output_file}")

# --- 使用示例 ---
if __name__ == "__main__":
    convert_to_scanned_pdf(
        input_file = INPUT_FILE,
        dpi = DPI,
    )