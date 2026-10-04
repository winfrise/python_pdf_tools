"""
PDF 图片 mask(SMask) 获取 + 黑底/黑白反转修复脚本
------------------------------------------------------------
在上一版"获取 mask"脚本基础上，重点修复【提取出来图片黑白反转】的问题。

黑白反转的根因：
  PDF 里图片的透明蒙版(SMask)有"极性"约定：白=不透明、黑=透明。
  但有两种情况会让这份极性反过来，而 fitz.Pixmap(doc, xref) /
  extract_image 都不会自动纠正：
    1) 蒙版带 /Decode [1 0] 反相数组（PDF 的采样值重映射）；
    2) 它是 1bit 的模板蒙版 /ImageMask true（stencil，1=上色，约定相反）；
    3) 少数导出器把 alpha 直接存成"黑实白透"(matte)。

本脚本的修复策略：
  A) mask_needs_invert(doc, xref)  : 自动读 Decode / ImageMask / BitsPerComponent
                                     判断这张蒙版要不要反相。
  B) composite_image_with_mask(...) : 合成 alpha 前按需反相蒙版，可选铺白底。
  C) extract_mask(...)              : 批量导出灰度 mask，同步应用反相并打印依据。
  D) render_image_via_page(...)     : 【最稳保底】让 PDF 渲染器处理 /Decode 与蒙版
                                     极性，clip 出该图，所见即所得，绝不再反转。

依赖：pip install pymupdf pillow
沿用原脚本的 utils 回调结构(process_file_with_callback / batch_process_file_with_callback)。
"""

import os
import sys
import io

import fitz  # PyMuPDF
from PIL import Image, ImageOps

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import process_file_with_callback, batch_process_file_with_callback


# ============================================================
# 工具：安全读取 xref 上的某个键
# ============================================================
def _xref_raw(doc, xref, key):
    """返回 (type, value) 元组，读不到返回 ('', 'null')。"""
    try:
        t, v = doc.xref_get_key(xref, key)
        return (t or ""), (v if v is not None else "null")
    except Exception:
        return "", "null"


def _is_truthy(v):
    return str(v).strip().lower() == "true"


def _decode_is_inverted(v):
    """
    解析 /Decode 数组判断是否反相。
    灰度/单通道正常为 [0 1] 或 null；出现 [1 0]（首值 > 尾值）即为反相。
    """
    s = str(v).strip().strip("[]")
    if not s or s.lower() == "null":
        return False
    try:
        nums = [float(x) for x in s.replace(",", " ").split()]
    except ValueError:
        return False
    # 单通道: [dmin dmax]; 多通道成对出现。任一对首值>尾值即反相。
    for i in range(0, len(nums) - 1, 2):
        if nums[i] > nums[i + 1]:
            return True
    return False


# ============================================================
# 核心1：判断某张蒙版要不要反相
# ============================================================
def mask_needs_invert(doc, smask_xref):
    """
    返回 (need_invert: bool, reason: str)。
    依据：/Decode 反相数组 或 1bit /ImageMask 模板蒙版。
    """
    if not smask_xref:
        return False, "无蒙版"

    _, decode_v = _xref_raw(doc, smask_xref, "Decode")
    if _decode_is_inverted(decode_v):
        return True, f"/Decode={decode_v} 反相"

    _, im_v = _xref_raw(doc, smask_xref, "ImageMask")
    _, bpc_v = _xref_raw(doc, smask_xref, "BitsPerComponent")
    if _is_truthy(im_v) and str(bpc_v).strip() == "1":
        return True, "/ImageMask=true 且 1bit(stencil 极性相反)"

    return False, "默认极性(白=不透明)"


# ============================================================
# 核心2：从一个图片 xref 拿 mask 信息
# ============================================================
def get_mask_info(doc, xref):
    """返回 (has_mask, smask_xref, mask_bytes, mask_ext)。"""
    base = doc.extract_image(xref)
    smask_xref = base.get("smask", 0)
    if not smask_xref:
        return False, 0, None, None
    mask_img = doc.extract_image(smask_xref)
    return True, smask_xref, mask_img["image"], mask_img["ext"]


def _load_mask_pil(doc, smask_xref, force_invert=None):
    """
    读取蒙版为 PIL 灰度图，并按需反相。
    force_invert=None -> 自动判断；True/False -> 强制。
    返回 (mask_pil, reason)。
    """
    mask = fitz.Pixmap(doc, smask_xref)
    if mask.colorspace and mask.colorspace.n > 1:
        mask = fitz.Pixmap(fitz.csGRAY, mask)
    mask_pil = Image.open(io.BytesIO(mask.tobytes("png"))).convert("L")

    auto, reason = mask_needs_invert(doc, smask_xref)
    need = auto if force_invert is None else bool(force_invert)
    if need:
        mask_pil = ImageOps.invert(mask_pil)
        reason += " -> 已反相"
    else:
        reason += " -> 保持原样"
    return mask_pil, reason


# ============================================================
# 用途1：把 mask 合成回主图 alpha(修复黑底/黑白反转)
# ============================================================
def composite_image_with_mask(doc, xref, force_invert=None, flatten_white=False):
    """
    返回 PIL.Image。
      - 有蒙版：合成正确的 alpha(RGBA)；flatten_white=True 时透明区铺白底(转 RGB)。
      - 无蒙版：返回普通 RGB 图。
    force_invert: None=自动判断极性, True/False=强制反相/不反相。
    """
    pix = fitz.Pixmap(doc, xref)
    if pix.colorspace and pix.colorspace.n > 3:
        pix = fitz.Pixmap(fitz.csRGB, pix)

    _, smask_xref, _, _ = get_mask_info(doc, xref)
    if smask_xref:
        # 用反相后的蒙版重建 alpha 通道：走 PIL 通道替换，最直观可控
        mask_pil, _reason = _load_mask_pil(doc, smask_xref, force_invert)

        base_pil = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
        if mask_pil.size != base_pil.size:
            mask_pil = mask_pil.resize(base_pil.size)
        rgba = base_pil.convert("RGBA")
        rgba.putalpha(mask_pil)

        if flatten_white:
            bg = Image.new("RGB", rgba.size, (255, 255, 255))
            bg.paste(rgba, mask=rgba.split()[3])
            return bg
        return rgba

    return Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")


# ============================================================
# 用途2：批量导出 PDF 内所有图片的 mask(灰度 PNG，自动反相)
# ============================================================
def extract_mask(input_file, page_range, is_flat_output=True,
                 target_img_index=-1, force_invert=None):
    output_dir = os.path.splitext(input_file)[0] + "__提取的mask"
    os.makedirs(output_dir, exist_ok=True)

    def callback_func(page, page_num, doc):
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            if (target_img_index >= 0) and (img_index != target_img_index):
                continue

            xref = img[0]
            has_mask, smask_xref, _, _ = get_mask_info(doc, xref)
            if not has_mask:
                print(f"[跳过] page{page_num}_img{img_index + 1} 无 SMask(本身不带透明蒙版)")
                continue

            # 按极性自动(或强制)反相后再保存
            mask_pil, reason = _load_mask_pil(doc, smask_xref, force_invert)

            mask_filename = f"page{page_num}_img{img_index + 1}_mask.png"
            mask_full_path = os.path.join(output_dir, mask_filename)
            if not is_flat_output:
                current_page_dir = os.path.join(output_dir, f"page_{page_num}")
                os.makedirs(current_page_dir, exist_ok=True)
                mask_full_path = os.path.join(current_page_dir, mask_filename)

            mask_pil.save(mask_full_path, format="PNG")
            print(f"已保存 mask: {mask_filename}  (smask_xref={smask_xref}) 极性: {reason}")

    process_file_with_callback(
        input_file=input_file,
        output_file="NOT_SAVE",
        page_range=page_range,
        callback_func=callback_func,
    )


# ============================================================
# 用途3(最稳保底)：用页面渲染裁剪出该图，彻底规避黑白反转
#   渲染器会自动应用 /Decode 与正确的蒙版极性，所见即所得。
# ============================================================
def render_image_via_page(page, xref, zoom=3.0, alpha=True):
    """
    返回 PIL.Image。适合 Pixmap 手动合成仍不对时直接改用此法。
    注意：图若被裁剪/旋转/多实例复用，get_image_rects 可能返回多个矩形，
    这里取面积最大的一个。
    """
    rects = page.get_image_rects(xref)
    if not rects:
        return None
    rect = max(rects, key=lambda r: r.width * r.height)
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, clip=rect, alpha=alpha)
    mode = "RGBA" if alpha else "RGB"
    return Image.frombytes(mode, (pix.width, pix.height), pix.samples)


# ================= 使用示例 =================
if __name__ == "__main__":
    INPUT_FILE = "/Users/teacher/Desktop/百度网盘下载/未命名文件夹/卞氏3 - 0928.pdf"
    PAGE_RANGE = "1-5"
    IS_FLAT_OUTPUT = True
    TARGET_IMG_INDEX = -1
    FORCE_INVERT = None      # None=自动判断极性; True/False=强制
    FLATTEN_WHITE = True     # 存 JPG 或想彻底消黑底时设 True

    if os.path.isfile(INPUT_FILE):
        # 方式A：只导出所有图片的 mask(灰度图，自动修正极性)
        extract_mask(
            input_file=INPUT_FILE,
            page_range=PAGE_RANGE,
            is_flat_output=IS_FLAT_OUTPUT,
            target_img_index=TARGET_IMG_INDEX,
            force_invert=FORCE_INVERT,
        )

        # 方式B：把某张图修复后存成 PNG(合成 alpha / 铺白底)
        # doc = fitz.open(INPUT_FILE)
        # page = doc[0]
        # img = page.get_images(full=True)[0]
        # out = composite_image_with_mask(doc, img[0],
        #                                 force_invert=FORCE_INVERT,
        #                                 flatten_white=FLATTEN_WHITE)
        # out.save("/tmp/fixed.png")
        #
        # 方式C(最稳)：渲染裁剪法，绕开一切极性问题
        # out = render_image_via_page(page, img[0], zoom=3.0, alpha=False)
        # out.save("/tmp/fixed_render.png")

    elif os.path.isdir(INPUT_FILE):
        def dir_callback(input_file, output_file):
            extract_mask(
                input_file=input_file,
                page_range=PAGE_RANGE,
                is_flat_output=IS_FLAT_OUTPUT,
                target_img_index=TARGET_IMG_INDEX,
                force_invert=FORCE_INVERT,
            )
        batch_process_file_with_callback(
            input_dir=INPUT_FILE,
            output_dir="NO_SAVE",
            callback_func=dir_callback,
        )
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {INPUT_FILE}")