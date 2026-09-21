import fitz
from tools.find_img_by_size import find_img_by_size


pdf_path = "/Users/teacher/Downloads/百度网盘Download/森木磊石BP-让天下没有难做的电源.pdf"

def delete_images_by_object(input_pdf, output_path, target_sizes):
    image_list = find_img_by_size(
        input_pdf=input_pdf,
        target_sizes=target_sizes
    )

    if output_path is None:
        output_path = input_pdf.replace('.pdf', '_output_删除图片对象.pdf')

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
    INPUT_PDF = "/Users/teacher/Desktop/test/森木磊石BP-让天下没有难做的电源.pdf"
    TARGET_SIZES = ['1044x696']
    delete_images_by_object(
        input_pdf=INPUT_PDF,
        output_path = None,
        target_sizes=TARGET_SIZES
    )