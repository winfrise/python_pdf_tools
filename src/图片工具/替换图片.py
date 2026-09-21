import fitz


def replace_pdf_images_by_nested_map(
    pdf_path: str,
    output_path: str,
    image_map: dict,          # {"page1": {"图片名称": "电脑路径"}, ...}
):
    """
    根据嵌套的 image_map 批量替换 PDF 中的图片。

    image_map 结构：
    {
        "page1": {
            "logo.png": "/Users/xxx/Desktop/new_logo.png",
            "banner.png": "/Users/xxx/Desktop/new_banner.png",
        },
        "page2": {
            "footer.png": "/Users/xxx/Desktop/new_footer.png",
        },
    }
    """
    doc = fitz.open(pdf_path)
    replaced_names = set()  # 记录已成功替换的图片名称

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_key = f"page{page_num + 1}"  # page1, page2, ...

        # 如果这个页码不在 image_map 里，跳过
        if page_key not in image_map:
            continue

        page_images = image_map[page_key]  # {"图片名称": "电脑路径"}
        images = page.get_images(full=True)

        for img in images:
            xref = img[0]
            name = img[7]  # 图片名称

            if name not in page_images:
                continue

            new_image_path = page_images[name]

            # 找到这张图在页面上的显示区域
            rects = page.get_image_rects(xref)
            if not rects:
                print(f"⚠️ 找不到图片 '{name}' 的显示区域（第 {page_num + 1} 页）")
                continue

            rect = rects[0]

            # 用红注擦掉原图
            page.add_redact_annot(rect, fill=(1, 1, 1))
            page.apply_redactions(
                images=fitz.PDF_REDACT_IMAGE_REMOVE,
                graphics=fitz.PDF_REDACT_LINE_ART_NONE,
            )

            # 在原位置插入新图
            page.insert_image(rect, filename=new_image_path)

            replaced_names.add(f"{page_key}/{name}")
            print(f"✅ 已替换第 {page_num + 1} 页的图片 '{name}' → {new_image_path}")

    # 提示未匹配的图片名称
    for page_key, page_images in image_map.items():
        for name in page_images:
            key = f"{page_key}/{name}"
            if key not in replaced_names:
                print(f"❌ 未找到 {page_key} 中名称为 '{name}' 的图片，请检查名称是否正确")

    doc.save(output_path)
    doc.close()
    print(f"💾 保存至 → {output_path}")


if __name__ == "__main__":
    # ====== 改这里 ======
    PDF_FILE    = "input.pdf"

    # 第一层 key: page1, page2, ...（对应第1页、第2页...）
    # 第二层 key: PDF里的图片名称
    # value: 你电脑上的图片路径
    IMAGE_MAP = {
        "page1": {
            "logo.png": "/Users/xxx/Desktop/new_logo.png",
            "banner.png": "/Users/xxx/Desktop/new_banner.png",
        },
        "page2": {
            "footer.png": "/Users/xxx/Desktop/new_footer.png",
        },
    }
    # ====================
    output_path = PDF_FILE.replace('.pdf', '_output_替换图片.pdf')
    replace_pdf_images_by_nested_map(
        pdf_path=PDF_FILE,
        output_path=output_path,
        image_map=IMAGE_MAP,
    )