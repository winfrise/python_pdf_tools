import fitz  # PyMuPDF
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import process_file_with_callback, batch_process_file_with_callback

def add_shape_to_pdf(input_file, output_file,  page_range, exclude_pages, mask_pdf_path ):
    if not output_file:
        output_file = input_file.replace(".pdf", "_output_遮挡.pdf")

    def callback_func(page, page_num, doc):
        if page_num in exclude_pages:
            return

        mask_path = mask_pdf_path
        if callable(mask_path):
            mask_path = mask_path(page_num)


            if not mask_path or not os.path.exists(mask_path):
                print(f"⚠️ 警告: Mask文件不存在 {mask_path}")
                return

            try:
                # --- 关键修改部分 ---
                # 1. 打开图片PDF文件 (作为对象)
                mask_doc = fitz.open(mask_path)
                
                mask_page = mask_doc.load_page(0)
                mask_page_width = mask_page.rect.width
                mask_page_height = mask_page.rect.height
            

                # 定义目标矩形：(左上x, 左上y, 右下x, 右下y)
                target_rect = fitz.Rect(0, 0, mask_page_width, mask_page_height)


                # 4. 执行嵌入 (传入 img_doc 对象，而不是路径字符串)
                # 注意：show_pdf_page 的参数顺序是 (rect, pdf_document, page_number)
                page.show_pdf_page(
                    target_rect, mask_doc, 0, 
                    keep_proportion=True,
                    rotate=0, 
                    overlay=True
                )
                
                # 5. 关闭图片PDF对象以释放内存
                mask_doc.close()
                
                print(f"✅ 成功在 Page {page_num} 添加: {mask_path}")

            except Exception as e:
                print(f"❌ 处理出错 {mask_path}: {e}")


    process_file_with_callback(
        input_file = input_file,
        output_file = output_file,
        page_range = page_range,
        callback_func=callback_func
    )



if __name__ == "__main__":
    input_path = "/Users/teacher/Desktop/百度网盘下载/20260928不要删/去水印-初二下合/初二下合_output_删除图片_output_遮挡左右.pdf"

    # page_range 示例：1,3, 5-9
    page_range = "1-999"
    exclude_pages = {}
    # exclude_pages = {1, 13, 27}

    def get_mask_path (page_num):
        return "/Users/teacher/Desktop/百度网盘下载/20260928不要删/去水印-初二下合/mask2.pdf"

    mask_pdf_path = get_mask_path

    # 单个文件处理
    if os.path.isfile(input_path):
        add_shape_to_pdf(
                input_file=input_path, 
                mask_pdf_path=mask_pdf_path, 
                page_range=page_range, 
                output_file = None,
                exclude_pages = exclude_pages,
        )
    elif os.path.isdir(input_path):
        def callback_func(input_file, output_file):
            add_shape_to_pdf(
                input_file=input_file,
                output_file=output_file,
                page_range = page_range,
                mask_pdf_path = mask_pdf_path, 
                exclude_pages = exclude_pages,
            )
        input_dir = input_path
        output_dir = f"{input_dir}_output_遮挡"
        batch_process_file_with_callback(
            input_dir=input_dir,
            output_dir=output_dir,
            callback_func=callback_func
        )
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {input_path}")

