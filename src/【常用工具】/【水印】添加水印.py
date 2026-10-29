import fitz  # PyMuPDF
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import process_file_with_callback, batch_process_file_with_callback

def add_watermark_pdf(
        input_pdf_path, 
        output_pdf_path, 
        watermark_pdf_path, 
        overlay=True,
        oc_index = None
    ):
    """
    给PDF添加水印，自动计算缩放比例保证水印完整居中显示。
    
    :param input_pdf_path: 原始PDF路径
    :param output_pdf_path: 输出PDF路径
    :param watermark_pdf_path: 水印PDF路径（仅使用第一页）
    :param overlay: True为覆盖在文字上方，False为置于文字下方
    """
    # 1. 打开源文档和水印文档
    doc = fitz.open(input_pdf_path)
    watermark_doc = fitz.open(watermark_pdf_path)
    
    # 获取水印的第一页作为模板
    watermark_page = watermark_doc[0]
    wm_rect = watermark_page.rect  # 水印页面的原始尺寸 (x0, y0, x1, y1)
    wm_width, wm_height = wm_rect.width, wm_rect.height
    
    # 2. 遍历目标文档的每一页
    for page in doc:
        page_rect = page.rect
        page_width, page_height = page_rect.width, page_rect.height
        
        # 3. 【核心】计算等比例缩放因子 (Fit Contain)
        # 分别计算宽度和高度方向能放下的最大缩放比例，取较小值，保证不超出边界
        scale_x = page_width / wm_width
        scale_y = page_height / wm_height
        scale = min(scale_x, scale_y)
        
        # 4. 计算缩放后的水印尺寸
        new_wm_width = wm_width * scale
        new_wm_height = wm_height * scale
        
        # 5. 计算居中偏移量，确保水印在页面正中间
        x_offset = (page_width - new_wm_width) / 2
        y_offset = (page_height - new_wm_height) / 2
        
        # 6. 构建水印在目标页面上的最终矩形区域
        target_rect = fitz.Rect(
            x_offset, 
            y_offset, 
            x_offset + new_wm_width, 
            y_offset + new_wm_height
        )
        
        # 7. 将水印叠加到目标页面
        page.show_pdf_page(
            target_rect,      # 目标位置
            watermark_doc,    # 水印文档对象
            0,                # 水印页码（这里固定用第0页）
            overlay=overlay,  # 是否覆盖在原文字上方
            # oc=oc_index,      # 可选内容组，配合下面的透明度设置
        )

    # 9. 保存并清理资源
    doc.save(output_pdf_path, garbage=4, deflate=True)
    doc.close()
    watermark_doc.close()
    print(f"✅ 水印添加完成，已保存至: {output_pdf_path}")

# ================= 使用示例 =================
if __name__ == "__main__":
    input_pdf_path = "/Volumes/西数4T外置/百度网盘默认下载/0001/11/未命名文件夹"
    watermark_pdf_path = "/Volumes/西数4T外置/百度网盘默认下载/0001/11/watermark.pdf"

    overlay = True  #True为覆盖在文字上方，False为置于文字下方
    oc_index = None # 层级


    if os.path.isfile(input_pdf_path):
        output_pdf_path = input_pdf_path.replace('.pdf', '_加水印.pdf')
        add_watermark_pdf(
            input_pdf_path=input_pdf_path,
            output_pdf_path=output_pdf_path,
            watermark_pdf_path=watermark_pdf_path,
            overlay=overlay,
            oc_index=oc_index
        )
    elif os.path.isdir(input_pdf_path):
        def callback_func(input_file, output_file):
            add_watermark_pdf(
                input_pdf_path=input_file,
                output_pdf_path=output_file,
                watermark_pdf_path=watermark_pdf_path,
                overlay=overlay,
                oc_index=oc_index
            )
        input_dir = input_pdf_path
        output_dir = f"{input_dir}_加水印"
        batch_process_file_with_callback(
            input_dir=input_dir,
            output_dir=output_dir,
            callback_func=callback_func
        )
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {input_pdf_path}")