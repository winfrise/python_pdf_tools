import fitz  # PyMuPDF
import os

def merge_pdfs(base_path, overlay_path, output_path, offset_x=0, offset_y=0):
    """
    将 overlay_path 的内容叠加到 base_path 的对应页面上
    :param base_path: 底层 PDF 路径 (被覆盖的)
    :param overlay_path: 覆盖层 PDF 路径 (浮在上面的)
    :param output_path: 输出文件路径
    """
    # 检查文件是否存在
    if not os.path.exists(base_path) or not os.path.exists(overlay_path):
        print("错误：找不到输入的 PDF 文件，请检查路径。")
        return

    if not output_path:
        output_path = base_path.replace('.pdf', '_output_text_overlay.pdf')

    # 打开文档
    base_doc = fitz.open(base_path)
    overlay_doc = fitz.open(overlay_path)

    # 获取两个文档的最小页数，防止页数不一致导致索引越界
    page_count = min(len(base_doc), len(overlay_doc))
    
    print(f"正在处理：底层共 {len(base_doc)} 页，覆盖层共 {len(overlay_doc)} 页。")
    print(f"将叠加前 {page_count} 页...")

    for page_num in range(page_count):
        # 获取底层页面
        base_page = base_doc[page_num]
        
        page_rect = base_page.rect
        
        # 2. 创建一个新的矩形，应用偏移量
        # fitz.Rect(left, top, right, bottom)
        # 正数 offset_x 会让 left/right 变大（向右移）
        # 正数 offset_y 会让 top/bottom 变大（向下移）
        dest_rect = fitz.Rect(
            page_rect.x0 + offset_x, 
            page_rect.y0 + offset_y, 
            page_rect.x1 + offset_x, 
            page_rect.y1 + offset_y
        )
        
        # 3. 将覆盖层页面绘制到这个偏移后的矩形区域中
        # 注意：如果偏移量过大导致 dest_rect 超出页面范围，内容可能会被裁剪
        base_page.show_pdf_page(dest_rect, overlay_doc, page_num)

    # 保存结果
    base_doc.save(output_path, garbage=4, clean=True, deflate=True )
    base_doc.close()
    overlay_doc.close()
    print(f"成功！已保存至：{output_path}")

# --- 主程序入口 ---
if __name__ == "__main__":
    # 请在这里修改你的实际文件路径
    # 注意：为了避免报错，函数名叫 merge_pdfs，不要和变量名搞混
    
    base_path = "/Users/teacher/Desktop/未命名文件夹/01/1.pdf"      # 底层文件
    overlay_path = "/Users/teacher/Desktop/未命名文件夹/01/overlay.pdf" # 要叠上去的文件
    output_path = None  # 输出文件
    offset_x = 0 # 单位为pt，1 厘米 (cm) ≈ 28.35 pt
    offset_y = 0

    # 执行合并
    merge_pdfs(
        base_path = base_path, 
        overlay_path = overlay_path,
        output_path = output_path,
        offset_x = offset_x,
        offset_y = offset_y,
    )