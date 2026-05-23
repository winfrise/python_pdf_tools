import os
import fitz  # PyMuPDF

def process_pdfs_with_images(input_dir, output_dir, image_configs):
    """
    批量处理PDF并添加图片，保留目录结构
    
    :param input_dir: 输入目录路径
    :param output_dir: 输出目录路径
    :param image_configs: 图片配置列表，每个元素是一个字典
                          格式: {'path': 图片路径, 'width': 宽度(可选), 'height': 高度(可选), 'position': (x, y)元组}
    """
    # 遍历输入目录，找出所有PDF文件
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                # 获取输入PDF的绝对路径
                input_pdf_path = os.path.join(root, file)
                
                # 计算相对于输入目录的相对路径 (保留目录结构的关键)
                relative_path = os.path.relpath(input_pdf_path, input_dir)
                
                # 构建输出PDF的绝对路径
                output_pdf_path = os.path.join(output_dir, relative_path)
                
                # 确保输出目录存在
                output_pdf_dir = os.path.dirname(output_pdf_path)
                os.makedirs(output_pdf_dir, exist_ok=True)
                
                print(f"正在处理: {relative_path}")
                
                # 处理单个PDF
                add_images_to_pdf(input_pdf_path, output_pdf_path, image_configs)

def add_images_to_pdf(input_path, output_path, image_configs):
    """
    向单个PDF添加图片
    """
    # 打开PDF
    doc = fitz.open(input_path)
    
    # 默认添加到第一页 (索引为0)，你可以根据需求修改逻辑
    page = doc[0]
    
    for config in image_configs:
        img_path = config['path']
        target_width = config.get('width')
        target_height = config.get('height')
        position = config.get('position', (0, 0)) # 默认左上角 (0,0)
        
        # 获取图片的原始尺寸
        # 注意：这里我们创建一个临时矩形来获取图片信息，或者直接用 fitz.open 读取图片
        img_doc = fitz.open(img_path)
        img_page = img_doc[0]
        original_width = img_page.rect.width
        original_height = img_page.rect.height
        img_doc.close()
        
        # 计算缩放比例 (保持宽高比)
        scale = 1.0
        if target_width and target_height:
            # 如果同时指定了宽高，取较小的缩放比例以确保图片完全容纳在指定区域内
            scale = min(target_width / original_width, target_height / original_height)
        elif target_width:
            scale = target_width / original_width
        elif target_height:
            scale = target_height / original_height
            
        # 计算缩放后的宽高
        new_width = original_width * scale
        new_height = original_height * scale
        
        # 定义图片在PDF页面上的插入矩形 (x0, y0, x1, y1)
        x, y = position
        rect = fitz.Rect(x, y, x + new_width, y + new_height)
        
        # 插入图片
        page.insert_image(rect, filename=img_path)
        
    # 保存PDF
    doc.save(output_path)
    doc.close()

# ================= 配置区域 =================

# 1. 输入目录 (包含嵌套子文件夹)
INPUT_DIRECTORY = r"/Users/teacher/Desktop/" 

# 2. 输出目录
OUTPUT_DIRECTORY = r"/Users/teacher/Desktop/"

# 3. 图片配置列表
# 支持配置多张图片，每张图片可以指定宽度或高度（会自动等比缩放），以及插入位置(x, y)
IMAGE_CONFIGS = [
    {
        "path": r"/Users/teacher/Desktop/图纸修改/素材/印章.png",   # 图片路径
        "width": 200,                   # 指定宽度为100点 (PDF单位)，高度自动等比
        # "height": 50,                 # 或者指定高度 (如果宽高都指定，会取较小比例缩放)
        "position": (50, 50)            # 插入位置，距离页面左边50点，顶部50点
    },
    {
        "path": r"/Users/teacher/Desktop/图纸修改/素材/印章2.png", 
        "width": 200,                   
        "position": (500, 400)          
    }
]

# ================= 执行 =================
if __name__ == "__main__":
    if not os.path.exists(INPUT_DIRECTORY):
        print(f"错误: 输入目录 '{INPUT_DIRECTORY}' 不存在！")
    else:
        process_pdfs_with_images(INPUT_DIRECTORY, OUTPUT_DIRECTORY, IMAGE_CONFIGS)
        print("所有文件处理完成！")