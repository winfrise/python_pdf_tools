import fitz  # PyMuPDF
import os

def extract_images(input_file, is_flat_output = False):
    # 1. 获取 PDF 文件所在的目录路径
    input_file_dir = os.path.dirname(input_file)
    
    # 2. 拼接出完整的输出文件夹路径
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = os.path.join(input_file_dir, f"{base_name}_提取的图片")

    # 4. 打开PDF文件
    doc = fitz.open(input_file)
    img_count = 0  # 用于统计总共提取的图片数量

    print(f"📄 开始处理文件：{input_file}")

    # 5. 遍历PDF的每一页
    for page_num in range(len(doc)):
        page = doc[page_num]

        # 1. 确定当前页的输出目录
        if is_flat_output:
            current_page_dir = output_dir  # 扁平化：直接用总输出目录
            os.makedirs(current_page_dir, exist_ok=True)  # 自动创建不存在的文件夹
        else:
            # 非扁平化：创建 "page_页码" 子文件夹（页码从1开始）
            current_page_dir = os.path.join(output_dir, f"page_{page_num + 1}")
            os.makedirs(current_page_dir, exist_ok=True)  # 自动创建不存在的文件夹

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
            img_path = os.path.join(current_page_dir, img_filename)
            
            # 8. 将图片写入本地文件
            with open(img_path, "wb") as img_file:
                img_file.write(image_bytes)
            
            img_count += 1
            print(f"✅ 已保存: {img_filename}")

    doc.close()
    print("-" * 30)
    print(f"🎉 提取完成！共从 PDF 中提取了 {img_count} 张图片。")
    print(f"📂 图片已保存在：{output_dir}")


def batch_extract_images(input_dir, is_flat_output):
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                input_file = os.path.join(root, file)
                extract_images(input_file, is_flat_output)


# ================= 使用示例 =================
if __name__ == "__main__":
    # 替换成你本地的 PDF 文件路径（可以是相对路径，也可以是绝对路径）
    input_path = "/Users/teacher/Desktop/未命名文件夹 2/2.5氟碳漆铝单板-金奥维.pdf" 
    is_flat_output = True
    
    if os.path.isfile(input_path):
        extract_images(input_path, is_flat_output)
    elif os.path.isdir(input_path):
        batch_extract_images(input_path, is_flat_output)
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {input_path}")
