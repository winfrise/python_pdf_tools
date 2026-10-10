import fitz  # PyMuPDF
from PIL import Image
import io
import os
import numpy as np


def apply_levels(pil_img, black=0, white=235, gamma=1.0):
    """
    模拟 Photoshop「色阶(Levels)」中的「设置白场」。

    映射公式（单通道，0-255）:
        x = (v - black) / (white - black)      # 输入区间 [black, white] 归一化到 [0,1]
        x = clip(x, 0, 1)                       # 超出部分截断
        x = x ** (1 / gamma)                    # 中间调(灰系数)
        v' = x * 255

    - white(白场): 阈值及以上的像素被映射为纯白 255。
      这正是「白场吸管」的效果 —— 把接近白色的浅色水印连同背景一起推成纯白，从而去除。
    - black(黑场): 默认 0，一般无需改动；设大于 0 可同时压暗暗部。
    - gamma(中间调): 默认 1.0(线性)。>1 提亮中间调，<1 压暗中间调。
    """
    rgb = pil_img.convert('RGB')
    arr = np.asarray(rgb).astype(np.float32)

    black = float(black)
    white = float(white)
    if white <= black:
        # 防止除零 / 反向，退化为不处理白场
        white = 255.0

    x = (arr - black) / (white - black)
    x = np.clip(x, 0.0, 1.0)
    if gamma and gamma != 1.0:
        x = np.power(x, 1.0 / float(gamma))

    out = np.clip(x * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(out, 'RGB')


def image_to_png_bytes(pil_img):
    """无损保存为 PNG 字节流（不执行体积压缩）。"""
    buf = io.BytesIO()
    pil_img.save(buf, format='PNG', optimize=False)
    return buf.getvalue()


def process_pdf_by_levels(
    input_path,
    output_path,
    black=0,
    white=235,
    gamma=1.0,
    rebuild_pdf=True,
):
    """
    对 PDF 中每张图片执行「色阶-设置白场」去水印，然后用处理后的图片替换原图。
    不再做任何体积压缩 / 二分质量 / 缩放逻辑。
    """
    if rebuild_pdf:
        new_doc = fitz.open()               # 全新空文档：把处理后的图按原位置重排
    else:
        new_doc = fitz.open(input_path)     # 原文档副本：原地替换图片流

    doc = fitz.open(input_path)
    total_pages = len(doc)

    if total_pages == 0:
        print("PDF 没有页面！")
        doc.close()
        return

    print(f"色阶参数 -> 黑场:{black} 白场:{white} 中间调:{gamma} | 总页数: {total_pages}")

    for page_num in range(total_pages):
        page = doc[page_num]
        image_list = page.get_images(full=True)

        if not image_list:
            print(f"[页 {page_num+1}] 无图片，跳过")
            continue

        for img_idx, img_info in enumerate(image_list):
            xref = img_info[0]

            try:
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]

                # 1. 执行色阶白场处理（替代原压缩逻辑）
                pil_img = Image.open(io.BytesIO(image_bytes))
                processed = apply_levels(pil_img, black=black, white=white, gamma=gamma)
                new_image_bytes = image_to_png_bytes(processed)

                # 2. 替换回 PDF（不再判断"是否变小"，处理后的图一律替换）
                if rebuild_pdf:
                    if page_num >= len(new_doc):
                        new_doc.new_page(width=page.rect.width, height=page.rect.height)
                    new_page = new_doc[page_num]

                    rects = page.get_image_rects(xref)
                    place_rect = rects[0] if rects else new_page.rect
                    new_page.insert_image(place_rect, stream=new_image_bytes)
                else:
                    target_page = new_doc[page_num]
                    target_page.replace_image(xref, stream=new_image_bytes)

                print(f"[页 {page_num+1}_{img_idx}] 色阶白场处理完成并替换 (白场={white})")

            except Exception as e:
                print(f"[页 {page_num+1}_{img_idx}] 处理失败: {e}")
                continue

    # 保存。去水印后背景多为纯白，用 deflate 对 PNG 仍有良好收纳，不影响画质
    new_doc.save(output_path, garbage=4, deflate=True, clean=True)
    new_doc.close()
    doc.close()

    final_size = os.path.getsize(output_path) / 1024
    print(f"\n色阶去水印完成! 输出: {output_path} 大小: {final_size:.1f} KB")


if __name__ == "__main__":
    input_path = "/Users/teacher/Desktop/百度网盘下载/2M/（已压缩）郑州市课题_扫描版__提取的图片"
    output_path = input_path.replace('.pdf', '_色阶去水印.pdf')

    # ==== 色阶参数（PS「设置白场」等价控制）====
    black = 100        # 黑场，一般保持 0
    white = 178      # 白场：阈值越低，越多浅色像素被推成纯白(去水印更狠)；越高越保守
    gamma = 1.0      # 中间调：1.0 线性，>1 提亮中间调，<1 压暗
    rebuild_pdf = False   # True=按原位置重建；False=原文档原地替换图片流

    process_pdf_by_levels(
        input_path=input_path,
        output_path=output_path,
        black=black,
        white=white,
        gamma=gamma,
        rebuild_pdf=rebuild_pdf,
    )