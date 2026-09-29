# -*- coding: utf-8 -*-
"""
仅复制 PDF 页面中的图片，生成"页数与原文件一致、图片位置不变"的新 PDF。

思路:
    1. 遍历原 PDF 的每一页;
    2. 用 page.get_image_info(xrefs=True) 取出本页每张位图的 xref 与其在页面上的显示位置 bbox;
    3. 在新 PDF 中创建一个与原页"等尺寸"的空白页;
    4. 把每张图片按其原始 bbox 插回相同位置 (keep_proportion=False 填满 bbox, 复刻原放置)。

依赖: pip install PyMuPDF
"""

import fitz  # PyMuPDF


def copy_images_keep_layout(input_pdf_path, output_pdf_path):
    """
    复制 PDF 中的图片, 保证位置不变, 输出页数与原 PDF 一致 (每页只保留图片)。

    :param input_pdf_path: 源 PDF 路径
    :param output_pdf_path: 输出 PDF 路径
    """
    src_doc = fitz.open(input_pdf_path)
    new_doc = fitz.open()

    total_images = 0

    try:
        # 逐页处理: 原 PDF 有几页, 新 PDF 就建立几页 (即使某页没有图片, 也保留一个空白页, 保证页数一致)
        for page_num in range(src_doc.page_count):
            page = src_doc[page_num]

            # 关键1: 新建一个与"原页"完全等尺寸(含旋转)的空白页, 保证版面 / 页数一一对应
            new_page = new_doc.new_page(
                width=page.rect.width,
                height=page.rect.height,
            )

            new_page.draw_rect(page.rect, color=(1, 1, 1), fill=(1, 1, 1))
            # 关键2: get_image_info 返回每张位图在页面上的真实显示位置 bbox 及 xref
            #         (比 get_images 更适合"按位置还原", 因为它给出的是图片在页面上的放置矩形)
            image_infos = page.get_image_info(xrefs=True)

            if not image_infos:
                print(f"[第 {page_num + 1} 页] 未检测到位图, 保留空白页")
                continue

            for img_index, info in enumerate(image_infos):
                xref = info.get("xref", 0)
                bbox = info.get("bbox")

                # xref<=0 说明该图不是可独立提取的位图(如内联图像), 跳过
                if xref <= 0 or bbox is None:
                    print(f"[跳过] 第 {page_num + 1} 页 图片 {img_index + 1}: 非可提取位图或无位置信息")
                    continue

                try:
                    # 提取原始图片字节流
                    base_image = src_doc.extract_image(xref)
                    image_bytes = base_image["image"]

                    # 把 bbox 转成 fitz.Rect, 注意裁剪到页面范围内
                    rect = fitz.Rect(bbox) & page.rect
                    if rect.is_empty or rect.width <= 0 or rect.height <= 0:
                        print(f"[跳过] 第 {page_num + 1} 页 图片 {img_index + 1}: 位置矩形为空")
                        continue

                    # 关键3: 按原 bbox 插回相同位置; keep_proportion=False 让图片恰好填满 bbox,
                    #         从而精确复刻原页面上的"位置 + 缩放尺寸"
                    new_page.insert_image(
                        rect,
                        stream=image_bytes,
                        keep_proportion=False,
                    )

                    total_images += 1
                    print(
                        f"[成功] 第 {page_num + 1} 页 图片 {img_index + 1} | "
                        f"位置=({rect.x0:.1f},{rect.y0:.1f},{rect.x1:.1f},{rect.y1:.1f}) | "
                        f"格式={base_image['ext']}"
                    )

                except Exception as e:
                    # 特殊色彩空间 / 加密 / 损坏图片可能提取失败, 跳过但不中断整体流程
                    print(f"[失败] 第 {page_num + 1} 页 图片 {img_index + 1}: {e}")

    finally:
        src_doc.close()

    # 保存新 PDF (页数 = 原 PDF 页数)
    new_doc.save(output_pdf_path)
    print(
        f"\n处理完成! 输出 {new_doc.page_count} 页 (与原文件一致), "
        f"共复制 {total_images} 张图片, 已保存至: {output_pdf_path}"
    )
    new_doc.close()


# 使用示例
if __name__ == "__main__":
    # 替换为你的源 PDF 路径
    input_pdf = "/Users/teacher/Desktop/百度网盘下载/未命名文件夹/卞氏3 - 0928.pdf"
    output_pdf = input_pdf.replace(".pdf", "_output_复制图片.pdf")
    copy_images_keep_layout(input_pdf, output_pdf)