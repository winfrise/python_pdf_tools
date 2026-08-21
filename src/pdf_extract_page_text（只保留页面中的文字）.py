import fitz  # PyMuPDF
import sys 

def recreate_pdf_with_text(input_pdf, output_pdf = None, local_font_path = None):
    if not output_pdf:
        output_pdf = input_pdf.replace('.pdf', '_output_text.pdf')
    # 1. 打开原始 PDF
    doc = fitz.open(input_pdf)
    # 创建一个全新的 PDF 用于写入
    new_doc = fitz.open()

    # 2. 遍历原始 PDF 的每一页
    for page in doc:
        # 创建与原页面尺寸相同的新页面
        new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
        
        # 3. 提取当前页面的文本字典（包含位置、字体、颜色等详细信息）
        text_dict = page.get_text("dict")
        
        # 4. 遍历所有的文本块(block) -> 行(line) -> 文本段(span)
        for block in text_dict["blocks"]:
            # 过滤掉图片块，只处理文本块 (type=0 为文本)
            if block["type"] != 0:
                continue
                
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"]
                    if not text.strip():  # 跳过空白文本
                        continue
                        
                    # 提取样式信息
                    bbox = span["bbox"]       # 边界框 (x0, y0, x1, y1)
                    font_name = span["font"]  # 字体名称
                    font_size = span["size"]  # 字体大小
                    color_int = span["color"] # 颜色 (整数格式)
                    
                    # 将整数颜色转换为 RGB 元组 (0-1 之间)
                    r = ((color_int >> 16) & 255) / 255.0
                    g = ((color_int >> 8) & 255) / 255.0
                    b = (color_int & 255) / 255.0
                    
                    # 5. 在新页面的原坐标位置插入文字
                    # 使用 bbox 的左下角 (x0, y1) 作为插入点
                    insert_point = (bbox[0], bbox[1] + font_size) 
                    
                    # 尝试使用原字体，如果系统中没有则回退到默认字体
                    try:
                        print(f'font_name:{font_name}')
                        # 注册并使用原始字体
                        new_page.insert_font(fontname=font_name)
                        new_page.insert_text(
                            insert_point,
                            text,
                            fontname=font_name,
                            fontsize=font_size,
                            color=(r, g, b)
                        )
                    except Exception as e:
                        if local_font_path:
                            print("使用本地字体")
                            # 如果传入了本地字体，使用自定义的 fontname 注册并插入
                            custom_font_name = 'custom_font_song'
                            new_page.insert_font(fontname=custom_font_name, fontfile=local_font_path)
                            new_page.insert_text(
                                insert_point,
                                text,
                                fontname=custom_font_name,
                                fontsize=font_size,
                                color=(r, g, b)
                            )
                        else:
                            # 1. 打印自定义提示
                            print(f"严重错误：字体处理失败 ({font_name})，程序即将停止。")

                            

                            sys.exit(1) 
                        # 字体缺失时的降级处理
                        # new_page.insert_text(
                        #     insert_point,
                        #     text,
                        #     fontname="helv",
                        #     fontsize=font_size,
                        #     color=(r, g, b)
                        # )

    # 6. 保存新 PDF
    new_doc.save(output_pdf)
    doc.close()
    new_doc.close()
    print(f"PDF 重新创建成功，已保存至: {output_pdf}")

# 使用示例
if __name__ == "__main__":
    input_pdf = "/Users/teacher/Desktop/未命名文件夹/01/1.pdf"
    local_font_path = "/Users/teacher/Library/Fonts/simsun_0.ttc"
    recreate_pdf_with_text(
        input_pdf,
        local_font_path=local_font_path
    )