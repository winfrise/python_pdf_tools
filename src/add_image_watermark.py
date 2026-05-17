import fitz  # PyMuPDF
import os

def add_image_watermark(pdf_path, output_path, watermark_img, 
                        offset_x=0, offset_y=0, scale=0.5, 
                        position="center"):
    """
    给PDF添加图片水印
    :param pdf_path: 原始PDF路径
    :param output_path: 输出PDF路径
    :param watermark_img: 水印图片路径
    :param offset_x: X轴偏移量 (正数向右，负数向左)
    :param offset_y: Y轴偏移量 (正数向下，负数向上)
    :param scale: 水印宽度占页面宽度的比例 (例如 0.5 表示水印宽度是页面的一半)
    :param position: 位置字符串: 
                     'center', 'top', 'bottom', 
                     'top-left', 'top-right', 'bottom-left', 'bottom-right'
    """
    # 1. 自动处理输出路径
    if not output_path:
        dir_name = os.path.dirname(pdf_path)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = os.path.join(dir_name, f"{base_name}_watermark.pdf")

    # 2. 打开文档
    doc = fitz.open(pdf_path)

    # 3. 遍历每一页
    for page_num in range(len(doc)):
        print(f"正在处理第 {page_num + 1} 页")
        page = doc[page_num]
        page_rect = page.rect # 获取页面矩形 (包含宽高信息)
        page_width = page_rect.width
        page_height = page_rect.height

        # 4. 计算水印图片的目标尺寸
        # 这里我们设定水印宽度为页面宽度的 scale 比例，高度等比缩放
        # 如果你希望固定高度，可以修改这里的逻辑
        target_width = page_width * scale
        
        # 为了计算高度，我们需要先获取图片信息
        # 注意：这里为了性能，其实可以在循环外获取一次图片宽高比，但为了代码清晰写在循环内演示
        try:
            # 只是获取图片信息，不加载像素数据
            img_info = fitz.open(watermark_img)
            img_page = img_info[0]
            img_rect = img_page.rect
            img_ratio = img_rect.height / img_rect.width
            img_info.close()
            
            target_height = target_width * img_ratio
        except Exception as e:
            print(f"无法读取水印图片信息: {e}")
            return

        # 5. 根据 position 计算基础坐标 (x, y)
        # PDF坐标系：左下角是 (0,0)，y轴向上
        base_x = 0
        base_y = 0

        if position == "center":
            base_x = (page_width - target_width) / 2
            base_y = (page_height - target_height) / 2
            
        elif position == "top":
            base_x = (page_width - target_width) / 2
            base_y = page_height - target_height
            
        elif position == "bottom":
            base_x = (page_width - target_width) / 2
            base_y = 0
            
        elif position == "top-left":
            base_x = 0
            base_y = page_height - target_height
            
        elif position == "top-right":
            base_x = page_width - target_width
            base_y = page_height - target_height
            
        elif position == "bottom-left":
            base_x = 0
            base_y = 0
            
        elif position == "bottom-right":
            base_x = page_width - target_width
            base_y = 0
            
        else:
            print(f"未知的位置参数: {position}，默认使用居中")
            base_x = (page_width - target_width) / 2
            base_y = (page_height - target_height) / 2

        # 6. 应用 offset 偏移量
        final_x = base_x + offset_x
        final_y = base_y + offset_y

        # 7. 定义矩形并插入图片
        # 注意：y轴是向下的，所以矩形是 (x1, y1, x2, y2)
        rect = fitz.Rect(final_x, final_y, final_x + target_width, final_y + target_height)
        
        # 插入图片
        page.insert_image(
            rect, 
            filename=watermark_img, 
            keep_proportion=True, # 保持比例
            overlay=True         # 设为True表示浮在文字上方（水印通常这样），False则是在文字下方
        )

    # 8. 保存文件
    doc.save(output_path)
    doc.close()
    print(f"水印添加完成，已保存至: {output_path}")

# --- 使用示例 ---
if __name__ == "__main__":
    input_pdf = "/Users/teacher/Desktop/2026年4月/test/111.pdf" # 你的PDF文件
    watermark_img = "/Users/teacher/Desktop/2026年4月/test/水印.png" # 你的水印图片
    output_path=None # None表示自动命名
    position="center"
    offset_x=0
    offset_y=0
    
    
    # 示例:
    add_image_watermark(
        pdf_path=input_pdf,
        output_path=None, # 自动命名
        watermark_img=watermark_img,
        position=position,
        offset_x=0, 
        offset_y=0, 
        scale=1
    )