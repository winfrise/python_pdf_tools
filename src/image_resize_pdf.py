import fitz  # PyMuPDF
import os

def resize_pdf_images_by_dimension(
    input_file: str,
    image_configs: list,
    use_pixel_units: bool = True  # 【新增开关】True=你填的是像素(px)，代码自动换算；False=你填的是PDF点(pt)
):
    """
    通过图片原始宽高匹配，批量调整 PDF 图片大小
    """
    if not os.path.exists(input_file):
        print(f"❌ 错误：找不到文件 {input_file}")
        return

    # 自动生成输出路径
    dir_name = os.path.dirname(input_file)
    base_name = os.path.basename(input_file)
    name_without_ext = os.path.splitext(base_name)[0]
    output_file = os.path.join(dir_name, f"{name_without_ext}_【已修改】.pdf")

    try:
        doc = fitz.open(input_file)
        total_pages = len(doc)
        print(f"📄 正在处理文件：{base_name} (共 {total_pages} 页)")

        for page_num in range(total_pages):
            page = doc[page_num]
            images = page.get_images()
            print(f"✅ 第 {page_num + 1} 页：开始修改")
            if not images:
                continue

            for config in image_configs:
                match_w = config.get("match_width")
                match_h = config.get("match_height")
                scale_width = config.get("scale_width", 1)
                scale_height = config.get("scale_height", 1)
                offset_x = config.get("offset_x", 0)
                offset_y = config.get("offset_y", 0)

                if match_w is None or match_h is None:
                    continue

                for img_item in images:
                    xref = img_item[0]
                    
                    img_info = doc.extract_image(xref)
                    if not img_info:
                        continue
                        
                    original_width = img_info["width"]
                    original_height = img_info["height"]

                    # 匹配原始像素宽高
                    if original_width == match_w and original_height == match_h:
                        old_rects = page.get_image_rects(xref)
                        if not old_rects:
                            continue
                            
                        old_rect = old_rects[0]
                        x0, y0, x1, y1 = old_rect
                        original_display_width = x1 - x0
                        original_display_height = y1 - y0

                        print(f"原始显示宽度: { original_display_width }, 原始显示高度: { original_display_height }")

                        # 计算新图片的矩形坐标
                        new_width = original_display_width * scale_width
                        new_height = original_display_height * scale_height
                        new_x0 = x0 + offset_x
                        new_y0 = y0 + offset_y 
                        new_x1 = new_x0  + new_width
                        new_y1 = new_y0 + new_height

                        new_rect = fitz.Rect(new_x0, new_y0, new_x1, new_y1)
                        # page.draw_rect(new_rect, color=None, fill=(0, 0, 1)) # 测试矩形
                        
                        # 1. 擦除原图
                        page.add_redact_annot(old_rect)
                        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE)
                        
                        # 2. 重新插入
                        img_bytes = img_info["image"]
                        page.insert_image(new_rect, stream=img_bytes)
                        
                        print(f"成功修改原始尺寸为 {original_width}x{original_height}px 的图片")

        doc.ez_save(output_file)
        print(f"🎉 全部处理完成！已保存至：{output_file}")
        
    except Exception as e:
        print(f"❌ 处理文件时发生错误：{e}")
    finally:
        if 'doc' in locals():
            doc.close()

# ================= 使用配置区 =================
if __name__ == "__main__":
    pdf_path = r"/Users/teacher/Desktop/产品标签批量修改/Test/测试.pdf" 
    
    my_image_configs = [
        {
            # 这里填写图片的【原始像素宽高】（可以通过右键图片属性查看，或者看运行代码时的打印日志）
            "match_width": 124,   
            "match_height": 124,  
            # 下面填写你期望的【新尺寸】
            "scale_width": 1.2,     # 这里需要看【真实的显示宽度】才能正确填写
            "scale_height": 1.2,    # 这里需要看【真实的显示高度】才能正确填写
            "offset_x": -3,       # 向右偏移 单位为(pt)
            "offset_y": 0        # 向下偏移 单位为(pt)
        },
        {
            "match_width": 869,   
            "match_height": 150,  
            "scale_width": 1.2,     # 这里需要看【真实的显示宽度】才能正确填写（pdf中的单位可能是pt）目标宽度 (pt)=像素宽度 (px)×72 / DPI
            "scale_height": 1,    # 这里需要看【真实的显示高度】才能正确填写
            "offset_x": 0,       # 向右偏移 单位为(pt)
            "offset_y": 0        # 向下偏移 单位为(pt)
        }
    ]

    # 【注意】use_pixel_units=True 表示上面填的都是像素(px)，代码会自动帮你换算！
    resize_pdf_images_by_dimension(pdf_path, my_image_configs, use_pixel_units=True)