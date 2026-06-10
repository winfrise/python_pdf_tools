import fitz  # PyMuPDF
import os

def extract_images_from_pdf(pdf_path, output_dir_name="extracted_images"):
    """
    从指定的PDF文件中提取所有图片，并保存到 PDF 文件所在的同级目录中
    :param pdf_path: PDF文件的路径
    :param output_dir_name: 保存图片的文件夹名称（默认为 extracted_images）
    """
    # 1. 获取 PDF 文件所在的目录路径
    pdf_dir = os.path.dirname(pdf_path)
    
    # 2. 拼接出完整的输出文件夹路径
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_dir = os.path.join(pdf_dir, f"{base_name}_{output_dir_name}")

    # 3. 如果文件夹不存在，则创建它
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 4. 打开PDF文件
    doc = fitz.open(pdf_path)
    img_count = 0  # 用于统计总共提取的图片数量

    print(f"📄 开始处理文件：{pdf_path}")

    # 5. 遍历PDF的每一页
    for page_num in range(len(doc)):
        page = doc[page_num]
        # 获取当前页面的所有图片列表
        image_list = page.get_images(full=True)

        # 6. 遍历当前页面的所有图片
        for img_index, img in enumerate(image_list):

            xref = img[0]  # 图片的引用ID (xref)
            
            # 根据 xref 提取图片的原始数据
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]  # 图片的二进制数据
            image_ext = base_image["ext"]      # 图片的原始扩展名 (如 jpg, png)
            
            # 7. 构造图片保存的文件名
            img_filename = f"page{page_num + 1}_img{img_index + 1}.{image_ext}"
            # 将文件名拼接到输出文件夹路径中
            img_path = os.path.join(output_dir, img_filename)
            
            # 8. 将图片写入本地文件
            with open(img_path, "wb") as img_file:
                img_file.write(image_bytes)
            
            img_count += 1
            print(f"✅ 已保存: {img_filename}")

    doc.close()
    print("-" * 30)
    print(f"🎉 提取完成！共从 PDF 中提取了 {img_count} 张图片。")
    print(f"📂 图片已保存在：{output_dir}")

# ================= 使用示例 =================
if __name__ == "__main__":
    # 替换成你本地的 PDF 文件路径（可以是相对路径，也可以是绝对路径）
    pdf_file = "/Users/teacher/Desktop/《临床基础检验技术》复习要点/《临床基础检验技术》复习要点.pdf" 
    
    extract_images_from_pdf(pdf_file)