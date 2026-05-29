import fitz  # PyMuPDF
import os

def add_images_to_pdf(input_pdf_path, image_configs, page_range='all'):
    """
    向PDF中添加图片（支持PDF矢量图，自动处理原始尺寸）
    """
    
    # 1. 检查原文件是否存在
    if not os.path.exists(input_pdf_path):
        print(f"❌ 错误：找不到文件 {input_pdf_path}")
        return

    # 2. 生成输出文件路径
    base_name, ext = os.path.splitext(input_pdf_path)
    output_pdf_path = f"{base_name}_【已修改】{ext}"

    # 3. 打开目标PDF
    try:
        doc = fitz.open(input_pdf_path)
    except Exception as e:
        print(f"❌ 错误：无法打开PDF文件: {e}")
        return

    # 4. 确定页面范围
    total_pages = doc.page_count
    if page_range == 'all':
        page_indices = range(total_pages)
    elif isinstance(page_range, tuple) and len(page_range) == 2:
        start, end = page_range
        start = max(0, start)
        end = min(total_pages - 1, end)
        page_indices = range(start, end + 1)
    else:
        print("❌ 错误：page_range 格式不正确，应为 'all' 或 (start, end)")
        doc.close()
        return

    # 5. 遍历每一页进行添加
    for page_num in page_indices:
        page = doc[page_num]
        
        # 遍历配置列表，在同一页添加多张图片
        for config in image_configs:
            img_path = config.get('path')
            pos = config.get('pos', (0, 0))
            size = config.get('size', None) # 默认为None，表示原始尺寸
            src_page_index = config.get('page_index', 0) # 默认为PDF图片的第0页

            if not os.path.exists(img_path):
                print(f"⚠️ 警告：图片文件不存在 {img_path}")
                continue

            try:
                # --- 关键修改部分 ---
                # 1. 打开图片PDF文件 (作为对象)
                img_doc = fitz.open(img_path)
                
                # 2. 获取源页面的矩形区域（用于获取原始宽高）
                src_page = img_doc.load_page(src_page_index)
                src_rect = src_page.rect # 获取原始尺寸 rect(x0, y0, x1, y1)
                original_width = src_rect.width
                original_height = src_rect.height
                
                # 3. 计算插入区域
                x, y = pos
                if size is None:
                    # 如果size为None，使用原始尺寸
                    w, h = original_width, original_height
                else:
                    w, h = size
                
                # 定义目标矩形：(左上x, 左上y, 右下x, 右下y)
                target_rect = fitz.Rect(x, y, x + w, y + h)

                # 4. 执行嵌入 (传入 img_doc 对象，而不是路径字符串)
                # 注意：show_pdf_page 的参数顺序是 (rect, pdf_document, page_number)
                page.show_pdf_page(target_rect, img_doc, src_page_index,  overlay=True)
                
                # 5. 关闭图片PDF对象以释放内存
                img_doc.close()
                
                print(f"✅ 成功在 Page {page_num+1} 添加: {img_path}")

            except Exception as e:
                print(f"❌ 处理图片出错 {img_path}: {e}")

    # 6. 保存并关闭
    try:
        doc.save(output_pdf_path)
        doc.close()
        print(f"🎉 处理完成！文件已保存为: {output_pdf_path}")
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")


# ==========================================
# 使用示例
# ==========================================

if __name__ == "__main__":
    # 1. 输入PDF路径
    input_file = "/Users/teacher/Desktop/未命名文件夹 2/xxx.pdf"
    page_range = (4,100)
    # 2. 配置图片列表 (注意：这里的path现在指向你的PDF格式图片)
    my_images = [
        {
            "path": "/Users/teacher/Desktop/未命名文件夹 2/提取xxx.pdf",      # 你的SVG转成的PDF
            "pos": (0, 0),         # 距离左边50，距离底部50 (坐标系原点在左下角)
            "size": None,      # None：表示原尺寸添加；(200, 200)：表示宽200，高200
            "page_index": 0          # 取该PDF的第0页
        },
        # 可以继续添加更多图片配置...
    ]

    # 3. 执行函数
    # 示例1: 全部页面添加
    add_images_to_pdf(input_file, my_images, page_range)
    
    # 示例2: 仅在第1页到第3页添加 (页码从0开始，即 0, 1, 2)
    # add_images_to_pdf(input_file, my_images, page_range=(0, 2))