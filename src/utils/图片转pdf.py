import os
import fitz  # PyMuPDF
from natsort import natsorted, ns  # 建议直接导入 ns，更规范

def images_to_pdf(folder_path, pdf_path, page_width=None, page_height=None):
    """
    将指定文件夹下的图片按自然排序合并为 PDF
    :param folder_path: 图片所在的文件夹路径
    :param pdf_path: 输出的 PDF 路径
    :param page_width: (可选) 指定页面宽度 (单位: pt)。若不填则使用图片原始宽度。
    :param page_height: (可选) 指定页面高度 (单位: pt)。若不填则使用图片原始高度。
    """
    # 1. 获取并排序图片
    supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')
    image_files = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith(supported_formats)
    ]
    
    if not image_files:
        print("该文件夹下没有找到任何支持的图片文件！")
        return

    # 使用 ns.IGNORECASE 实现忽略大小写的自然排序
    sorted_images = natsorted(image_files, alg=ns.IGNORECASE)
    
    # 2. 创建一个新的空白 PDF 文档
    doc = fitz.open()

    print(f"正在处理 {len(sorted_images)} 张图片...")

    for img_name in sorted_images:
        img_path = os.path.join(folder_path, img_name)
        
        try:
            # 打开单张图片作为临时文档
            img_doc = fitz.open(img_path)
            
            # 获取图片原始尺寸
            img_rect = img_doc[0].rect
            original_w = img_rect.width
            original_h = img_rect.height
            
            # --- 核心逻辑：确定最终页面尺寸 ---
            if page_width and page_height:
                # 如果指定了宽高，则使用指定尺寸（相当于强制拉伸/缩放画布）
                final_w = page_width
                final_h = page_height
            else:
                # 如果未指定，则保持图片原始尺寸
                final_w = original_w
                final_h = original_h
            
            # 插入一个新页面，尺寸为 final_w x final_h
            # fitz.PaperSize 接受 (width, height)
            doc.new_page(width=final_w, height=final_h)
            
            # 获取刚才插入的最后一页
            last_page = doc[-1]
            
            # 定义图片在 PDF 页面上的放置区域 (Rect)
            # 这里设置为 (0, 0, 页面宽, 页面高)，即填满整个页面
            target_rect = fitz.Rect(0, 0, final_w, final_h)
            
            # 将图片内容插入到目标区域
            # 如果 original_w != final_w，PyMuPDF 会自动缩放图片以适应 target_rect
            last_page.insert_image(target_rect, stream=open(img_path, "rb").read())
            
            img_doc.close()
            print(f"已添加: {img_name}")
            
        except Exception as e:
            print(f"处理图片 {img_name} 时出错: {e}")

    # 3. 保存 PDF
    doc.save(pdf_path)
    doc.close()
    print(f"转换成功！已保存至: {pdf_path}")

# --- 使用示例 ---
if __name__ == "__main__":
    input_dir = "/Users/teacher/Desktop/20260830/去水印001-110元/图片"      # 替换为你的图片文件夹路径
    output_path = f"{input_dir}/output_图片合并.pdf"
    
    # 示例 1: 不传宽高，保持原图大小
    # images_to_pdf(input_dir, output_pdf)

    # 示例 2: 强制指定为 A4 大小 (宽595pt, 高842pt)
    # 注意：这可能会导致非 A4 比例的图片被拉伸变形
    images_to_pdf(input_dir, output_path, page_width=595, page_height=842)
