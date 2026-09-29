"""
PDF 图片 mask(SMask) 获取脚本
------------------------------------------------------------
背景：PDF 里带透明边的图片，"透明度信息"并不在主图里，
而是单独存成一张灰度蒙版(软掩膜 SMask)，主图通过 /SMask 引用它。
 只返回主图，需要顺着它字典里的  键
(即蒙版对象的 xref) 再取一次，才能拿到 mask。

本脚本提供三个能力：
  1) get_mask_bytes(doc, xref)        : 只取某张图的 mask 原始字节(灰度)，无 mask 返回 None
  2) extract_mask(...)                : 批量把 PDF 里所有图片的 mask 单独导出成灰度 PNG
  3) composite_image_with_mask(...)   : 把 mask 合成回主图的 alpha 通道(消除黑底用)

依赖：pip install pymupdf pillow
沿用原脚本的 utils 回调结构(process_file_with_callback / batch_process_file_with_callback)。
"""

import os
import sys
import io

import fitz  # PyMuPDF
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import process_file_with_callback, batch_process_file_with_callback


# ============================================================
# 核心：从一个图片 xref 拿到 mask 相关信息
# ============================================================
def get_mask_info(doc, xref):
    """
    返回 (has_mask: bool, smask_xref: int, mask_bytes: bytes|None, mask_ext: str|None)

    - doc.extract_image(xref) 返回的字典里，smask 键就是蒙版对象的 xref；
      没有透明蒙版时该值为 0。
    - 拿到 smask_xref 后，再 extract_image 一次即可得到蒙版(单通道灰度)的原始字节。
    """
    base = doc.extract_image(xref)
    smask_xref = base.get("smask", 0)
    if not smask_xref:
        return False, 0, None, None

    mask_img = doc.extract_image(smask_xref)
    return True, smask_xref, mask_img["image"], mask_img["ext"]


def get_mask_pixmap(doc, xref):
    """
    以 Pixmap 方式拿到 mask 的灰度位图(便于直接读像素/尺寸)。
    无 mask 返回 None。
    """
    _, smask_xref, _, _ = get_mask_info(doc, xref)
    if not smask_xref:
        return None
    return fitz.Pixmap(doc, smask_xref)


# ============================================================
# 用途1：把 mask 合成回主图 alpha(修复黑底的关键一步)
# ============================================================
def composite_image_with_mask(doc, xref):
    """
    返回带 alpha 通道的 PIL.Image(RGBA)，透明区已正确还原。
    若该图本身没有 mask，则返回不带 alpha 的普通 RGB 图。
    """
    pix = fitz.Pixmap(doc, xref)
    # CMYK 等 >3 通道先转 RGB
    if pix.colorspace and pix.colorspace.n > 3:
        pix = fitz.Pixmap(fitz.csRGB, pix)

    _, smask_xref, _, _ = get_mask_info(doc, xref)
    if smask_xref:
        mask = fitz.Pixmap(doc, smask_xref)
        # 把灰度蒙版作为 alpha 贴回主图
        pix = fitz.Pixmap(pix, mask)

    img = Image.open(io.BytesIO(pix.tobytes("png")))
    return img


# ============================================================
# 用途2：批量导出 PDF 内所有图片的 mask(灰度 PNG)
# ============================================================
def extract_mask(input_file, page_range, is_flat_output=True, target_img_index=-1):
    output_dir = os.path.splitext(input_file)[0] + "__提取的mask"
    os.makedirs(output_dir, exist_ok=True)

    def callback_func(page, page_num, doc):
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            if (target_img_index >= 0) and (img_index != target_img_index):
                continue

            xref = img[0]

            has_mask, smask_xref, mask_bytes, mask_ext = get_mask_info(doc, xref)
            if not has_mask:
                print(f"[跳过] page{page_num}_img{img_index + 1} 无 SMask(该图本身不带透明蒙版)")
                continue

            # 蒙版字节存成灰度 PNG
            mask_stream = io.BytesIO(mask_bytes)
            mask_pil = Image.open(mask_stream).convert("L")

            mask_filename = f"page{page_num}_img{img_index + 1}_mask.png"
            mask_full_path = os.path.join(output_dir, mask_filename)
            if not is_flat_output:
                current_page_dir = os.path.join(output_dir, f"page_{page_num}")
                os.makedirs(current_page_dir, exist_ok=True)
                mask_full_path = os.path.join(current_page_dir, mask_filename)

            mask_pil.save(mask_full_path, format="PNG")
            print(f"已保存 mask: {mask_filename}  (smask_xref={smask_xref})")

    process_file_with_callback(
        input_file=input_file,
        output_file="NOT_SAVE",
        page_range=page_range,
        callback_func=callback_func,
    )


# ================= 使用示例 =================
if __name__ == "__main__":
    INPUT_FILE = "/Users/teacher/Desktop/百度网盘下载/未命名文件夹/卞氏3 - 0928.pdf"
    PAGE_RANGE = "1-5"
    IS_FLAT_OUTPUT = True
    TARGET_IMG_INDEX = -1

    if os.path.isfile(INPUT_FILE):
        # 方式A：只导出所有图片的 mask(灰度图)
        extract_mask(
            input_file=INPUT_FILE,
            page_range=PAGE_RANGE,
            is_flat_output=IS_FLAT_OUTPUT,
            target_img_index=TARGET_IMG_INDEX,
        )

        # 方式B：只想看某一张图有没有 mask、mask 是哪个对象
        # doc = fitz.open(INPUT_FILE)
        # page = doc[0]
        # img = page.get_images(full=True)[0]
        # has, sxref, mbytes, ext = get_mask_info(doc, img[0])
        # print("是否有mask:", has, "smask_xref:", sxref, "字节数:", None if mbytes is None else len(mbytes))

    elif os.path.isdir(INPUT_FILE):
        def dir_callback(input_file, output_file):
            extract_mask(
                input_file=input_file,
                page_range=PAGE_RANGE,
                is_flat_output=IS_FLAT_OUTPUT,
                target_img_index=TARGET_IMG_INDEX,
            )
        batch_process_file_with_callback(
            input_dir=INPUT_FILE,
            output_dir="NO_SAVE",
            callback_func=dir_callback,
        )
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {INPUT_FILE}")