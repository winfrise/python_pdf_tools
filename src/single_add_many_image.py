import os
import fitz  # PyMuPDF


def add_images_to_pdf(input_file, image_configs):
    """
    向单个PDF添加图片，支持负数坐标从右/底部对齐
    """

    dir_name = os.path.dirname(input_file)
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(dir_name, f"{base_name}_edit.pdf")

    doc = fitz.open(input_file)
    
    # 默认添加到第一页
    page = doc[0]
    # 获取页面的宽度和高度，用于计算负数坐标
    page_width = page.rect.width
    page_height = page.rect.height
    
    for config in image_configs:
        img_path = config['path']
        target_width = config.get('width')
        target_height = config.get('height')
        position = config.get('position', (0, 0))
        
        # 1. 获取图片原始尺寸并计算缩放后的宽高
        img_doc = fitz.open(img_path)
        img_page = img_doc[0]
        original_width = img_page.rect.width
        original_height = img_page.rect.height
        img_doc.close()
        
        scale = 1.0
        if target_width and target_height:
            scale = min(target_width / original_width, target_height / original_height)
        elif target_width:
            scale = target_width / original_width
        elif target_height:
            scale = target_height / original_height
            
        new_width = original_width * scale
        new_height = original_height * scale
        
        # 2. 处理位置坐标 (核心修改部分)
        x, y = position
        
        # 如果 x 为负数，则从页面右侧往左算 (例如 -50 代表距离右边 50 点)
        if x < 0:
            x = page_width + x - new_width
        # 如果 y 为负数，则从页面底部往上算 (例如 -50 代表距离底部 50 点)
        if y < 0:
            y = page_height + y - new_height
            
        # 3. 定义插入矩形并插入图片
        rect = fitz.Rect(x, y, x + new_width, y + new_height)
        page.insert_image(rect, filename=img_path)
        
    doc.save(output_file)
    doc.close()

# ================= 配置区域 =================

INPUT_FILE = r"/Users/teacher/Desktop/图纸/104MP201GM-机舱主甲板下分段管系制作图(104)-B.pdf" 

IMAGE_CONFIGS = [
    # {
    #     "path": r"./images/logo.png",
    #     "width": 600,
    #     "position": (-120, 50)  # 距离右边 120点，距离顶部 50点
    # },
    {
        "path": r"/Users/teacher/Desktop/图纸/logo_white.png", 
        "width": 60,
        "position": (10, 60)  # 距离右边 210点，距离底部 60点 (右下角附近)
    }
]

if __name__ == "__main__":
    add_images_to_pdf(INPUT_FILE, IMAGE_CONFIGS)
    print("所有文件处理完成！")