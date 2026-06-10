import fitz  # PyMuPDF
import os
import re

from utils import rename_backup_file

def add_images_to_pdf(input_pdf_path, image_configs, page_range='all', output_path = None):
    """
    向PDF中添加图片（支持PDF矢量图，自动处理原始尺寸）
    """
    
    # 1. 检查原文件是否存在
    if not os.path.exists(input_pdf_path):
        print(f"❌ 错误：找不到文件 {input_pdf_path}")
        return

    # 3. 打开目标PDF
    try:
        doc = fitz.open(input_pdf_path)
    except Exception as e:
        print(f"❌ 错误：无法打开PDF文件: {e}")
        return

    # 4. 确定页面范围
    total_pages = doc.page_count
    page_indices = set() # 使用集合来存储页码，自动去重

    if page_range == 'all':
        # 如果是 'all'，选择所有页面
        page_indices = set(range(total_pages))
    else:
        # 将输入的字符串按逗号分割
        parts = str(page_range).split(',')
        for part in parts:
            part = part.strip() # 去除空格
            if '-' in part:
                # 处理范围，例如 "1-3"
                range_match = re.match(r'^(\d+)-(\d+)$', part)
                if range_match:
                    start = int(range_match.group(1))
                    end = int(range_match.group(2))
                    # 确保起始页不大于结束页，并限制在文档范围内
                    if start <= end:
                        page_indices.update(range(max(1, start) - 1, min(total_pages, end)))
            else:
                # 处理单个页码，例如 "1" 或 "5"
                try:
                    page_num = int(part)
                    if 1 <= page_num <= total_pages:
                        page_indices.add(page_num - 1) # 转换为0基索引
                except ValueError:
                    # 如果转换失败，忽略该部分
                    print(f"❌ 警告：无法识别的页码格式 '{part}'，已跳过。")

    # 将集合转换为排序后的列表，便于后续处理
    page_indices = sorted(page_indices)

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
                elif size == 'fullscreen':
                    w, h = page.rect.width, page.rect.height
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

    # 6. 保存文件逻辑修改
    try:
        if output_path == None:
            # 1. 定义备份路径和临时路径
            base_name, ext = os.path.splitext(input_file)
            output_path = f"{base_name}_output{ext}"

        # 2. 保存文件
        doc.save(output_path)
        print(f"生成文件：{output_path}")
        doc.close()  # 必须关闭文档，释放对原文件的占用

        # 3. 备份原文件
        # rename_backup_file(input_file)

        # 4. 将临时文件重命名为原文件名
        # os.rename(output_path, input_file)
        # print(f"新文件重命名为: {input_file}")

    except Exception as e:
        print(f"保存文件时出错: {e}")


# ==========================================
# 使用示例
# ==========================================

if __name__ == "__main__":

    try:
        is_batch = False

        # page_range 示例：1,3, 5-9
        page_range = "1-1000"
        my_images = [
            {
                "path": "/Users/teacher/Desktop/未命名文件夹/mask.pdf",      # 你的SVG转成的PDF
                "pos": (0, 0),         # 距离左边50，距离底部50 (坐标系原点在左下角)
                "size": None,      # None：表示原尺寸添加；(200, 200)：表示宽200，高200 fullscreen:表示全屏添加
                "page_index": 0          # 取该PDF的第0页
            },
            # 可以继续添加更多图片配置...
        ]

        if not is_batch:
            # 1. 输入PDF路径
            input_file = "/Users/teacher/Desktop/未命名文件夹/1.离心泵.pdf"

            # 3. 执行函数
            # 示例1: 全部页面添加
            add_images_to_pdf(input_file, my_images, page_range)
        else:
            input_folder = "/Users/teacher/Desktop/图纸修改/4-1需要修改"
            output_folder = "/Users/teacher/Desktop/图纸修改/4-2修改后"

            for root, dirs, files in os.walk(input_folder):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        input_file = os.path.join(root, file)
                        relative_input_pdf = os.path.relpath(input_file, input_folder)
                        output_file = os.path.join(output_folder, relative_input_pdf)
                        
                        # 确保输出目录存在
                        output_pdf_dir = os.path.dirname(output_file)
                        os.makedirs(output_pdf_dir, exist_ok=True)
                        
                        print(f"正在处理: {relative_input_pdf}")
     
                        add_images_to_pdf(input_file, my_images, page_range = "all", output_path = output_file)

    except FileNotFoundError:
        print(f"错误: 找不到文件 '{input_file}'，请确认文件名和路径。")


