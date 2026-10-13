import fitz  # PyMuPDF
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import parse_page_range, batch_process_file_with_callback

def merge_two_pages_to_one(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)

    if len(doc) != 2:
        raise ValueError("输入 PDF 必须是 2 页！")

    a4_width = 595
    a4_height = 842

    new_doc = fitz.open()
    new_page = new_doc.new_page(width=a4_height, height=a4_width)  # 横版

    page1 = doc[0]
    page2 = doc[1]

    scale = a4_width / page1.rect.height          # 595/842 ≈ 0.706
    scaled_width = page1.rect.width * scale       # 原页缩放后的宽度

    left_rect  = fitz.Rect(0, 0, scaled_width, a4_width)
    right_rect = fitz.Rect(scaled_width, 0, 2 * scaled_width, a4_width)

    # 1. 复制两页正文（不含注释）
    new_page.show_pdf_page(left_rect,  doc, page1.number)
    new_page.show_pdf_page(right_rect, doc, page2.number)

    # 2. 把每页的注释（印章等）渲染成位图，再贴回去
    def paste_annots(src_page, dst_rect, dst_page):
        for annot in src_page.annots():
            r = annot.rect  # 注释在源页上的矩形（PDF 坐标）

            # 渲染该注释区域（annots=True 才会把注释画进去）
            pix = src_page.get_pixmap(clip=r, dpi=300, annots=True)
            if pix.width == 0 or pix.height == 0:
                continue

            # 坐标换算：源页坐标 → 目标页坐标
            # 源页 (x0,y0) 缩放到 dst_rect 里的对应位置
            def map_pt(x, y):
                new_x = dst_rect.x0 + (x - src_page.rect.x0) * scale
                new_y = dst_rect.y0 + (y - src_page.rect.y0) * scale
                return new_x, new_y

            x0, y0 = map_pt(r.x0, r.y0)
            x1, y1 = map_pt(r.x1, r.y1)
            target = fitz.Rect(x0, y0, x1, y1)

            dst_page.insert_image(target, pixmap=pix)

    paste_annots(page1, left_rect,  new_page)
    paste_annots(page2, right_rect, new_page)

    new_doc.save(output_pdf)
    new_doc.close()
    doc.close()
    print(f"合并完成！输出文件：{output_pdf}")

if __name__ == "__main__":

    INPUT_FILE = "/Volumes/西数4T外置/百度网盘默认下载/检索证明/001_副本"   # 输入的 2 页 PDF

    if os.path.isfile(INPUT_FILE):
        input_path = INPUT_FILE
        output_path = input_path.replace('.pdf', '_合并.pdf')
        merge_two_pages_to_one(
            input_pdf = input_path, 
            output_pdf = output_path, 
        )
    elif os.path.isdir(INPUT_FILE):
        def callback_func(input_file, output_file):
            merge_two_pages_to_one(
                input_pdf = input_file, 
                output_pdf = output_file, 
            )
        input_dir = INPUT_FILE
        output_dir = f"{input_dir}_merge"
        batch_process_file_with_callback(
            input_dir=input_dir, 
            output_dir=output_dir,
            callback_func=callback_func    
        )
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {INPUT_FILE}")


