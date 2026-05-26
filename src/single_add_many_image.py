import os
import fitz # PyMuPDF

def add_images_to_pdf(input_file, image_configs, start_page=0, end_page=None):
    """
    向PDF添加图片，支持控制页码范围
    :param start_page: 开始页码 (从0开始计数，包含)
    :param end_page: 结束页码 (从0开始计数，不包含)。如果为None，则处理到文档末尾。
    """
    dir_name = os.path.dirname(input_file)
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(dir_name, f"{base_name}_edit.pdf")
    
    doc = fitz.open(input_file)
    
    # --- 核心修改：控制页码范围 ---
    # 如果未指定结束页，则默认为文档总页数（即处理到最后一页）
    if end_page is None:
        end_page = doc.page_count
    
    # 确保页码在有效范围内
    start_page = max(0, start_page)
    end_page = min(doc.page_count, end_page)
    
    print(f"正在处理第 {start_page+1} 页 到 第 {end_page} 页...")

    for page_num in range(start_page, end_page):
        page = doc.load_page(page_num)
        
        # 获取当前页面的实际尺寸
        page_width = page.rect.width
        page_height = page.rect.height

        for config in image_configs:
            img_path = config['path']
            target_width = config.get('width')
            target_height = config.get('height')
            position = config.get('position', (0, 0))
            
            # 1. 获取图片原始尺寸并计算缩放后的宽高
            try:
                img_doc = fitz.open(img_path)
                img_page = img_doc[0]
                original_width = img_page.rect.width
                original_height = img_page.rect.height
                img_doc.close()
            except Exception as e:
                print(f"无法打开图片 {img_path}: {e}")
                continue
                
            scale = 1.0
            if target_width and target_height:
                scale = min(target_width / original_width, target_height / original_height)
            elif target_width:
                scale = target_width / original_width
            elif target_height:
                scale = target_height / original_height
                
            new_width = original_width * scale
            new_height = original_height * scale
            
            # 2. 处理位置坐标
            x, y = position
            
            # 如果 x 为负数，则从页面右侧往左算
            if x < 0:
                x = page_width + x - new_width
                
            # 如果 y 为负数，则从页面底部往上算
            if y < 0:
                y = page_height + y - new_height 

            # 3. 定义插入矩形并插入图片
            rect = fitz.Rect(x, y, x + new_width, y + new_height)
            try:
                page.insert_image(rect, filename=img_path)
            except Exception as e:
                print(f"无法在第 {page_num+1} 页插入图片 {img_path}: {e}")

    # 使用推荐的保存选项
    doc.save(output_file, garbage=4, deflate=True)
    doc.close()
    print(f"文件已保存为: {output_file}")

# ================= 配置区域 =================
INPUT_FILE = r"/Users/teacher/Desktop/未命名文件夹/xxx.pdf"
START_PAGE = 0
END_PAGE = None


IMAGE_CONFIGS = [ 
    { 
        "path": r"/Users/teacher/Desktop/图纸/logo_white-assets/11.png", 
        "width": 60, 
        "position": (10, 60) 
    } 
]

if __name__ == "__main__":
    # --- 修改这里来控制页码 ---
    # 例子1：只处理第1页 (Python索引从0开始，所以是0)
    # add_images_to_pdf(INPUT_FILE, IMAGE_CONFIGS, start_page=0, end_page=1)
    
    # 例子2：处理第2页到第5页
    # add_images_to_pdf(INPUT_FILE, IMAGE_CONFIGS, start_page=1, end_page=5)
    
    # 例子3：处理第3页到文档末尾
    # add_images_to_pdf(INPUT_FILE, IMAGE_CONFIGS, start_page=2, end_page=None)
    
    # 默认：处理全部页面
    add_images_to_pdf(INPUT_FILE, IMAGE_CONFIGS, START_PAGE, END_PAGE)
    
    print("所有文件处理完成！")