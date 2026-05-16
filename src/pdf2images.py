import fitz  # PyMuPDF
import os

def pdf_to_images(pdf_path, output_folder=None, dpi=300, img_format="jpg"):
    """
    将PDF的每一页转换为图片
    :param pdf_path: PDF文件路径
    :param output_folder: 输出文件夹路径（默认为PDF同级目录下的 'output_images'）
    :param dpi: 分辨率（DPI），数值越大图片越清晰，但文件越大（默认300）
    :param img_format: 图片格式，支持 'jpg', 'png', 'ppm' 等（默认 'jpg'）
    """
    # 1. 准备输出目录
    if output_folder is None:
        pdf_dir = os.path.dirname(pdf_path)
        output_folder = os.path.join(pdf_dir, "output_images")
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 2. 打开PDF
    doc = fitz.open(pdf_path)
    print(f"📄 开始转换：{os.path.basename(pdf_path)}，共 {len(doc)} 页...")

    # 3. 设置缩放矩阵（控制清晰度）
    # PDF 默认是 72 DPI，我们要转换成目标 DPI，需要计算缩放比例
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)

    # 4. 遍历每一页进行转换
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # 核心步骤：将页面渲染为像素图 (Pixmap)
        pix = page.get_pixmap(matrix=mat, alpha=False) # alpha=False 去除透明通道，对JPG很重要
        
        # 构造文件名：page_001.jpg
        filename = f"page_{page_num + 1:03d}.{img_format}"
        output_path = os.path.join(output_folder, filename)
        
        # 保存图片
        pix.save(output_path) # 导出的图片DPI与设置的不符
        
        print(f"✅ 第 {page_num + 1} 页已保存: {filename}")

    print(f"🎉 转换完成！图片保存在: {output_folder}")

# --- 使用示例 ---
if __name__ == "__main__":
    # 替换为你的PDF路径
    pdf_file = "/Users/teacher/Downloads/百度网盘下载/张正发茶餐厅招商手册(电子版1) 2026-5-11 81133 1.pdf" 
    pdf_to_images(pdf_file, dpi=300)