import fitz

def replace_pdf_image_by_stream(pdf_path, output_path, image_map):
    doc = fitz.open(pdf_path)
    replaced_count = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_key = f"page{page_num + 1}"

        if page_key not in image_map:
            continue

        page_images = image_map[page_key]
        images = page.get_images(full=True)

        for img in images:
            xref = img[0]       # 图片的交叉引用号
            name = img[7]       # 图片名称

            if name in page_images:
                new_image_path = page_images[name]

                # ✅ 核心修改：使用 update_image 代替 update_stream
                # 它会自动处理色彩空间(RGB/CMYK)、透明度和压缩格式，防止变黑
                try:
                    doc.update_image(xref, filename=new_image_path)
                    print(f"✅ 已替换: {page_key} -> {name}")
                    replaced_count += 1
                except Exception as e:
                    print(f"❌ 替换失败 {name}: {e}")

    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    print(f"💾 完成！共替换 {replaced_count} 张图片 -> {output_path}")