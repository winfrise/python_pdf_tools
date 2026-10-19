import fitz
import os, sys
from tools.find_img_by_size import find_img_by_size
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import batch_process_file_with_callback

def delete_images_by_object(input_pdf, output_path, target_sizes):
    image_list = find_img_by_size(
        input_pdf=input_pdf,
        target_sizes=target_sizes
    )

    if output_path is None:
        output_path = input_pdf.replace('.pdf', '_output_删除图片.pdf')

    doc = fitz.open(input_pdf)
    removed_count = 0

    for image_item in image_list:
        xref = image_item['xref']
        doc._deleteObject(xref)
        removed_count += 1

    doc.save(output_path, garbage=4, deflate=True)

    print(f"文件已保存至: {output_path}")
    print(f"合计删除图片: {removed_count} 张")

    doc.close()


    
if __name__ == "__main__":
    INPUT_PDF = "/Volumes/西数4T外置/百度网盘默认下载/未命名文件夹/思维导图_watermarked.pdf"
    
    def target_sizes_func (img_info):
        img_w = img_info['width']
        img_h = img_info['height']
        if img_w >= 650 and img_h >= 1000:
            return True

        return False

    # TARGET_SIZES = target_sizes_func
    TARGET_SIZES = ["351x108", "584x92"]

    if os.path.isfile(INPUT_PDF):
        delete_images_by_object(
            input_pdf=INPUT_PDF,
            output_path = None,
            target_sizes=TARGET_SIZES
        )
    elif os.path.isdir(INPUT_PDF):
        def callback_func(input_file, output_file):
            delete_images_by_object(
                input_pdf=input_file,
                output_path = output_file,
                target_sizes=TARGET_SIZES
            )
        input_dir = INPUT_PDF
        output_dir = f"{input_dir}_删除图片"
        batch_process_file_with_callback(
            input_dir=input_dir, 
            output_dir=output_dir,
            callback_func=callback_func    
        )
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {INPUT_PDF}")