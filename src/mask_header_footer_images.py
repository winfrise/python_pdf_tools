import fitz  # PyMuPDF
import os

def add_header_footer_images(pdf_path, output_path=None, header_img_path=None, footer_img_path=None):
    """
    给PDF的页头和页脚添加图片并遮挡原有内容
    """
    # 自动处理输出路径：如果为空，则设置为同目录下的 文件名_1.pdf
    if not output_path:
        # 获取文件所在的目录
        dir_name = os.path.dirname(pdf_path) 
        # 获取不带后缀的文件名
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        # 拼接成新的路径
        output_path = os.path.join(dir_name, f"{base_name}_1.pdf")

    # 打开PDF文档
    doc = fitz.open(pdf_path)

    # 遍历每一页
    for page_num in range(len(doc)):
        page = doc[page_num]
        # 获取页面的尺寸
        page_width = page.rect.width
        page_height = page.rect.height
        
        # --- 1. 处理页头 ---
        if header_img_path:
            # 加载页头图片
            header_img = fitz.Pixmap(header_img_path)
            img_w, img_h = header_img.width, header_img.height
            
            # 计算高度：如果没指定高度，则按页面宽度等比缩放
  
            aspect_ratio = img_w / img_h
            header_height = page_width / aspect_ratio
            
            # 定义页头的矩形区域
            header_rect = fitz.Rect(0, 0, page_width, header_height)
            # 绘制白色实心矩形遮挡原有内容
            page.draw_rect(header_rect, color=None, fill=(1, 1, 1))
            # 在页头区域插入图片
            page.insert_image(header_rect, pixmap=header_img)
            # 释放图片内存
            header_img = None
        
        # --- 2. 处理页脚 ---
        if footer_img_path:
            # 加载页脚图片
            footer_img = fitz.Pixmap(footer_img_path)
            img_w, img_h = footer_img.width, footer_img.height
            
            # 计算高度：如果没指定高度，则按页面宽度等比缩放
            aspect_ratio = img_w / img_h
            footer_height = page_width / aspect_ratio
            
            # 定义页脚的矩形区域
            footer_rect = fitz.Rect(0, page_height - footer_height, page_width, page_height)
            # 绘制白色实心矩形遮挡原有内容
            page.draw_rect(footer_rect, color=None, fill=(1, 1, 1))
            # 在页脚区域插入图片
            page.insert_image(footer_rect, pixmap=footer_img)
            # 释放图片内存
            footer_img = None

        print(f"✅ 第 {page_num + 1} 页已处理完成")
    # 保存并关闭文档
    doc.save(output_path)
    doc.close()
    print(f"✅ 页头页脚处理完成，已保存至：{output_path}")

# ================= 变量定义区 =================
input_pdf = "/Users/teacher/Desktop/2026年4月/test/111.pdf"          
output_pdf = ""                     # 留空表示，程序会自动生成 文件名_1.pdf

# 测试场景：只加页头，页头高度自动计算；不加页脚
my_header_img = "/Users/teacher/Desktop/2026年4月/test/header_img.png"        
my_footer_img = None       # None: 表示不加页脚             

# ================= 调用函数 =================
add_header_footer_images(
    pdf_path=input_pdf, 
    output_path=output_pdf, 
    header_img_path=my_header_img, 
    footer_img_path=my_footer_img
)