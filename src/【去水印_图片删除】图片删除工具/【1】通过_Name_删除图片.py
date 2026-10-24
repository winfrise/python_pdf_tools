import pymupdf


def delete_images_by_name(
    input_path: str,
    output_path: str,
    names_to_delete: list[str],
) -> dict:
    """
    根据图片内部名称删除 PDF 中的图片（支持批量）。

    参数:
        input_path: 输入 PDF 路径
        output_path: 输出 PDF 路径
        names_to_delete: 要删除的图片内部名称列表，例如 ["Im1", "Im3"]

    返回:
        dict: 统计信息，包含被删除的图片 xref 列表
    """
    doc = pymupdf.open(input_path)
    deleted_xrefs = []

    for page in doc:
        # get_images(full=True) 返回:
        # (xref, smask, width, height, bpc, colorspace, alt_colorspace, name, filter, referencer)
        # name 是第 8 个元素 (索引 7)
        for img_info in page.get_images(full=True):
            xref = img_info[0]
            img_name = img_info[7]  # 内部 name

            if img_name in names_to_delete and xref not in deleted_xrefs:
                try:
                    page.delete_image(xref)
                    deleted_xrefs.append(xref)
                    print(f"[删除] 页面 {page.number + 1}: xref={xref}, name='{img_name}'")
                except Exception as e:
                    print(f"[跳过] 页面 {page.number + 1}: xref={xref}, name='{img_name}'，原因: {e}")

    # 使用 ez_save 或 garbage=3 + deflate 彻底清理
    doc.ez_save(output_path)
    doc.close()

    return {"deleted_xrefs": deleted_xrefs}


# ========== 使用示例 ==========
if __name__ == "__main__":
    input_pdf = "/Users/teacher/Downloads/英语单词去水印/艾宾浩斯单词课件 (1).pdf"
    output_pdf = input_pdf.replace('.pdf', '_删除图片.pdf')

    # 要删除的图片内部名称（可多个）
    target_names = ["Im3", "KSPX1"]

    result = delete_images_by_name(input_pdf, output_pdf, target_names)
    print(f"\n完成。共删除 {len(result['deleted_xrefs'])} 张图片：{result['deleted_xrefs']}")