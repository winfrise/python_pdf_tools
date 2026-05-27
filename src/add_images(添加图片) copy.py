import fitz  # PyMuPDF
import os

def add_images_to_pdf(input_pdf_path, image_configs, page_range='all'):
    """
    向PDF中添加图片

    参数:
    input_pdf_path (str): 输入的PDF文件路径
    image_configs (list): 图片配置列表，列表中的每个元素是一个字典
    page_range (str or tuple): 页面范围 ('all' 或 (start, end))
    """

    # 1. 检查原文件是否存在
    if not os.path.exists(input_pdf_path):
        print(f"❌ 错误：找不到文件 {input_pdf_path}")
        return

    # 2. 生成输出文件路径
    base_name, ext = os.path.splitext(input_pdf_path)
    output_pdf_path = f"{base_name}_【已修改】{ext}"

    # 3. 打开PDF
    try:
        doc = fitz.open(input_pdf_path)
    except Exception as e:
        print(f"❌ 打开PDF失败: {e}")
        return

    # 4. 确定页面范围
    total_pages = len(doc)
    target_pages = []

    if page_range == 'all':
        target_pages = range(total_pages)
    elif isinstance(page_range, tuple) or isinstance(page_range, list):
        start, end = page_range
        # 确保范围不越界
        start = max(0, start)
        end = min(total_pages - 1, end)
        if start > end:
            print("⚠️ 警告：起始页码大于结束页码，已跳过处理。")
            target_pages = []
        else:
            target_pages = range(start, end + 1)
    else:
        print("⚠️ 警告：page_range 格式不正确，应为 'all' 或 (start, end) 元组。")
        target_pages = []

    # 5. 遍历页面并添加图片
    print(f"ℹ️ 正在处理页面: {list(target_pages)} ...")
    for page_num in target_pages:
        page = doc[page_num]

        # 遍历配置列表，在同一页添加多张图片
        for config in image_configs:
            img_path = config['image']
            x = config.get('pos', (0, 0))[0]
            y = config.get('pos', (0, 0))[1]
            width = config.get('size', (0, 0))[0]
            height = config.get('size', (0, 0))[1]

            if not os.path.exists(img_path):
                print(f"⚠️ 警告：图片文件不存在 {img_path}，已跳过。")
                continue

            # --- 核心修正部分 ---
            # insert_image 需要一个矩形 rect=(x0, y0, x1, y1)
            # x1 = x + width, y1 = y + height
            rect = fitz.Rect(x, y, x + width, y + height)

            try:
                page.insert_image(rect, filename=img_path)
            except Exception as e:
                print(f"❌ 插入图片失败 {img_path}: {e}")

    # 6. 保存并关闭
    try:
        doc.save(output_pdf_path)
        doc.close()
        print(f"✅ 成功！文件已保存至: {output_pdf_path}")
    except Exception as e:
        print(f"❌ 保存失败: {e}")

# ==========================================
# 使用示例
# ==========================================

if __name__ == "__main__":
    input_file = "/Volumes/西数4T外置/Pdf修改资料/大连图纸修改/图纸TianMsup/743-SEALING_AIR_FUNNEL_C.pdf"
    page_range = (1,5)    # all 或 区间(0, 2)代表前3页
    my_images = [
        # {
        #     'image': 'logo.png',       # 图片路径
        #     'pos': (50, 50),          # 距离页面左上角 x=50, y=50 的位置
        #     'size': (100, 100)        # 强制缩放为 宽100, 高100
        # },
        {
            'image': '/Volumes/西数4T外置/Pdf修改资料/大连图纸修改/图纸TianMsup/Logo.jpg',  # 第二张图片
            'pos': (1, 5),        # 放在页面偏下的位置
            # 不填 'size' 则按原图大小显示
        }
    ]

    # 调用函数
    # 示例1：在所有页面添加
    add_images_to_pdf(input_file, my_images, page_range='all')
    
    # 示例2：只在第1页到第3页添加（注意：页码从0开始，所以0,2代表前3页）
    # add_images_to_pdf('test.pdf', my_images, page_range=(0, 2))