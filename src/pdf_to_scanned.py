import os
import fitz  # PyMuPDF

def convert_to_scanned_pdf(input_pdf_path, output_pdf_path=None, dpi=300):
    """
    使用 PyMuPDF 将文字版 PDF 转换为扫描版（图片版）PDF
    :param input_pdf_path: 输入文件路径
    :param output_pdf_path: 输出文件路径（默认为None，即自动生成）
    :param dpi: 输出图片的分辨率 (默认 300，建议范围 150-300)
    """
    
    # 1. 自动处理输出路径
    if output_pdf_path is None:
        dir_name = os.path.dirname(input_pdf_path)
        base_name = os.path.splitext(os.path.basename(input_pdf_path))[0]
        output_pdf_path = os.path.join(dir_name, f"{base_name}_图片版.pdf")

    print(f"📄 输入文件: {input_pdf_path}")
    print(f"⚙️ 设置分辨率: {dpi} DPI")
    
    # 打开原始 PDF
    doc = fitz.open(input_pdf_path)
    
    # 创建一个新的空 PDF 用于写入
    new_doc = fitz.open()
    
    # 2. 计算缩放倍率 (PyMuPDF 基础分辨率为 72 DPI)
    # 例如：300 / 72 ≈ 4.16 倍
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)

    print(f"🔄 正在转换... (共 {doc.page_count} 页)")
    
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        
        # 1. 将页面渲染为图片 (Pixmap)
        pix = page.get_pixmap(matrix=mat, alpha=False) # alpha=False 避免透明通道导致的黑底问题
        
        # 2. 在新文档中插入一个与图片大小一致的空白页
        # pix.width 和 pix.height 是图片的像素尺寸
        new_page = new_doc.new_page(width=pix.width, height=pix.height)
        
        # 3. 将图片直接插入到这一页中
        # 这里使用 insert_image，传入的是 rect (矩形区域) 和 stream (字节流)
        new_page.insert_image(fitz.Rect(0, 0, pix.width, pix.height), stream=pix.tobytes("png"))
        
        # 释放 pixmap 内存
        pix = None

        if (page_num + 1) % 10 == 0 or (page_num + 1) == doc.page_count:
            print(f"   ...已处理 {page_num + 1}/{doc.page_count} 页")

    # 3. 保存新文件
    new_doc.save(output_pdf_path)
    new_doc.close()
    doc.close()

    print(f"✅ 转换完成！文件已保存至: {output_pdf_path}")

# --- 使用示例 ---
if __name__ == "__main__":
    # 这里填入你的 PDF 文件路径
    input_file = "/Users/teacher/Desktop/2026年4月/去公司名（交个朋友）/11.pdf" 
    
    # 调用函数，不传 output_pdf_path 则自动命名，dpi 默认 300
    convert_to_scanned_pdf(input_file, dpi=300)