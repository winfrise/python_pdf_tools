import os
import fitz  # PyMuPDF
from natsort import natsorted, ns

# 定义标准纸张尺寸 (单位: pt)
# A4: 21.0cm x 29.7cm -> ~595 x 842 pt
# A3: 29.7cm x 42.0cm -> ~842 x 1191 pt
PAPER_SIZES = {
    "a4_h": (841.89, 595.28),
    "a4_v": (595.28, 841.89),
    "a3_h": (1190.55, 841.89),
    "a3_v": (841.89, 1190.55),
}

def _cm_to_pt(cm):
    """将厘米转换为 pt (1cm ≈ 28.3465pt)"""
    return cm * 28.3465

def parse_page_size(size_arg, original_w, original_h):
    """
    解析页面尺寸参数。
    :param size_arg: 用户传入的参数
                     - None: 原始大小
                     - 'half': 原始的一半
                     - 'A4_v', 'A3_h' 等: 固定纸张大小
                     - 'A4_width', 'A3_width': 固定宽度，高度自适应
                     - 数字 (int/float): 视为厘米(cm)，等比缩放适应？(此处按你的需求，单数字通常指宽，但为了严谨，
                       如果是单数字且未指定模式，通常很难判断是宽还是高。
                       *但在本实现中，为了配合你的需求，如果传入纯数字，我们默认视为“指定宽度(cm)，高度自适应”或者你需要明确传元组)
                       *修正策略：为了兼容你之前的“只传宽或高”，这里假设传入单个数字代表“宽度(cm)”，高度自适应。
                       *如果你希望传入元组 (w, h) 代表强制拉伸/裁剪，也支持。
    :param original_w/h: 图片原始尺寸 (pt)
    :return: (width_pt, height_pt)
    """
    
    # 1. 什么都不传 -> 原始大小
    if size_arg is None:
        return original_w, original_h

    # 2. 传 "half" -> 原始的一半
    if isinstance(size_arg, str) and size_arg.lower() == "half":
        return original_w / 2, original_h / 2

    # 3. 字符串模式匹配 (A4_v, A4_width 等)
    if isinstance(size_arg, str):
        key = size_arg.lower().replace(" ", "")
        
        # 3.1 检查是否是 "固定宽度" 模式 (例如 A4_width)
        if key.endswith("_width"):
            base_key = key.replace("_width", "")
            if base_key in PAPER_SIZES:
                target_w_pt = PAPER_SIZES[base_key][0] # 获取该纸张的宽度
                # 计算缩放比例
                ratio = target_w_pt / original_w
                return target_w_pt, original_h * ratio
        
        # 3.2 检查是否是标准纸张 (例如 A4_v)
        if key in PAPER_SIZES:
            return PAPER_SIZES[key]

    # 4. 数值模式 (支持厘米单位)
    # 这里的逻辑：
    # - 如果传入元组 (w, h)，视为强制尺寸 (cm -> pt)
    # - 如果传入单个数字，视为“指定宽度 (cm)”，高度同比例缩放 (类似 A4_width 的逻辑)
    if isinstance(size_arg, (int, float)):
        target_w_cm = size_arg
        target_w_pt = _cm_to_pt(target_w_cm)
        ratio = target_w_pt / original_w
        return target_w_pt, original_h * ratio

    if isinstance(size_arg, tuple) and len(size_arg) == 2:
        w_cm, h_cm = size_arg
        return _cm_to_pt(w_cm), _cm_to_pt(h_cm)

    # 兜底：如果解析失败，返回原始大小并警告
    print(f"[Warning] 无法识别的尺寸参数: {size_arg}，将使用原始尺寸。")
    return original_w, original_h


def images_to_pdf(folder_path, pdf_path, page_size=None):
    """
    将图片转换为 PDF
    :param folder_path: 图片文件夹路径
    :param pdf_path: 输出 PDF 路径
    :param page_size: 页面尺寸控制参数
                      - None: 原始大小
                      - 'A4_v', 'A4_h', 'A3_v', 'A3_h': 标准纸张
                      - 'A4_width', 'A3_width': 固定宽度，高度自适应
                      - 'half': 原始尺寸的一半
                      - 21.0 (float): 视为宽度 21cm，高度自适应
                      - (21.0, 29.7) (tuple): 强制设为该尺寸 (cm)
    """
    supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')
    
    # 1. 获取文件列表
    try:
        all_files = os.listdir(folder_path)
    except FileNotFoundError:
        print(f"错误：找不到文件夹 {folder_path}")
        return

    image_files = [
        os.path.join(folder_path, f) 
        for f in all_files 
        if f.lower().endswith(supported_formats)
    ]
    
    if not image_files:
        print("该文件夹下没有找到任何支持的图片文件！")
        return

    # 2. 自然排序
    sorted_images = natsorted(image_files, alg=ns.IGNORECASE)
    
    # 3. 开始转换
    doc = fitz.open()
    
    for img_path in sorted_images:
        try:
            # 打开图片获取原始尺寸 (pt)
            img_doc = fitz.open(img_path)
            img_page = img_doc[0]
            rect = img_page.rect
            original_w = rect.width
            original_h = rect.height
            
            # 计算目标尺寸
            target_w, target_h = parse_page_size(page_size, original_w, original_h)
            
            # 创建新页面
            # 注意：fitz.open() 创建新 PDF 时，insert_page 需要指定尺寸
            # 这里我们先创建一个临时页，或者直接 insert_page
            
            # 方法：插入一个空白页，然后插入图片
            # 或者是直接利用 fitz 的特性：
            # doc.insert_page(-1, width=target_w, height=target_h)
            
            doc.insert_page(-1, width=target_w, height=target_h)
            
            # 在新页面上绘制图片
            # 获取最后一页的指针
            page = doc[-1]
            
            # 定义放置图片的矩形区域 (填满整个页面)
            target_rect = fitz.Rect(0, 0, target_w, target_h)
            
            # 插入图片
            page.insert_image(target_rect, stream=open(img_path, "rb").read())
            
            img_doc.close()
            
        except Exception as e:
            print(f"处理图片 {img_path} 时出错: {e}")

    # 4. 保存
    doc.save(pdf_path)
    doc.close()
    print(f"成功生成 PDF: {pdf_path}")


# --- 测试调用示例 ---
if __name__ == "__main__":
    input_dir = "/Users/teacher/Desktop/20260830/去水印001-110元/图片"      # 替换为你的图片文件夹路径
    output_pdf = f"{input_dir}/output_图片合并.pdf"
    # 示例 1: 使用 A4 宽度，高度自动伸缩 (适合长图)
    print("正在生成 A4 宽度自适应高度的 PDF...")
    images_to_pdf(input_dir, output_pdf, page_size="A4_width")
    
    # ==========================================
    # page_size 参数调用示例大全
    # 单位说明：数字默认单位为 厘米(cm)
    # ==========================================

    # 示例 1：使用原始尺寸 (不缩放)
    # images_to_pdf(input_dir, output_pdf, page_size=None)

    # 示例 2：缩小为原始尺寸的一半
    # images_to_pdf(input_dir, output_pdf, page_size="half")

    # --- 预设纸张模式 (强制适应页面) ---

    # 示例 3：A4 纵向 (默认标准)
    # images_to_pdf(input_dir, output_pdf, page_size="A4") 
    # 或者写全称: page_size="A4_v"

    # 示例 4：A4 横向
    # images_to_pdf(input_dir, output_pdf, page_size="A4_h")

    # 示例 5：A3 纵向
    # images_to_pdf(input_dir, output_pdf, page_size="A3_v")

    # 示例 6：A3 横向
    # images_to_pdf(input_dir, output_pdf, page_size="A3_h")

    # --- 固定宽度模式 (高度按比例自动计算) ---

    # 示例 7：锁定宽度为 A4 宽 (21cm)，高度自适应
    # images_to_pdf(input_dir, output_pdf, page_size="A4_width")

    # 示例 8：锁定宽度为 A3 宽 (29.7cm)，高度自适应
    # images_to_pdf(input_dir, output_pdf, page_size="A3_width")

    # --- 自定义尺寸模式 (单位: cm) ---

    # 示例 9：自定义宽度 25cm，高度同比例自适应
    # images_to_pdf(input_dir, output_pdf, page_size=25)

    # 示例 10：自定义宽度 15.5cm，高度同比例自适应
    # images_to_pdf(input_dir, output_pdf, page_size=15.5)

    # 示例 11：强制指定宽高 (宽20cm, 高30cm)，图片会拉伸或压缩以填满页面
    # images_to_pdf(input_dir, output_pdf, page_size=(20, 30))

