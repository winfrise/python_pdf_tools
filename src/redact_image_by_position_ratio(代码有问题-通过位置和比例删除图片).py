import fitz  # PyMuPDF
import os
import sys


def parse_page_range(page_str, total_pages):
    """
    解析页码字符串，支持 "1, 3-5, 9-10, 12" 格式。
    :param page_str: 用户输入的页码字符串
    :param total_pages: PDF 总页数 (用于边界检查)
    :return: 0-based 的页码列表 [0, 2, 3, 4, 8, 9, 11]
    """
    pages = set()
    if not page_str or not page_str.strip():
        return []

    parts = page_str.split(",")
    for part in parts:
        part = part.strip()
        if not part:
            continue

        if "-" in part:
            try:
                # 处理 "3-5" 这种区间
                start, end = map(int, part.split("-"))
                # 转换为 0-based 索引，并确保范围合法
                for i in range(start - 1, end):
                    if 0 <= i < total_pages:
                        pages.add(i)
            except ValueError:
                print(f"警告：无法解析区间 '{part}'，已跳过。")
        else:
            try:
                # 处理单页 "1"
                p = int(part) - 1
                if 0 <= p < total_pages:
                    pages.add(p)
            except ValueError:
                print(f"警告：无法解析页码 '{part}'，已跳过。")

    return sorted(list(pages))


def process_pdf(input_path, page_range_str, image_rules=None):
    """
    主处理函数：备份文件 -> 解析页码 -> 执行操作
    """
    if not os.path.exists(input_path):
        print(f"错误：找不到文件 {input_path}")
        return

    # 1. 自动备份原文件
    base, ext = os.path.splitext(input_path)
    backup_path = f"{base}_备份{ext}"
    try:
        import shutil
        shutil.copy2(input_path, backup_path)
        print(f"✅ 原文件已备份为: {backup_path}")
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return

    doc = fitz.open(input_path)
    total_pages = len(doc)

    # 2. 解析页码
    target_pages = parse_page_range(page_range_str, total_pages)
    print(f"📄 目标页码 (0-based): {target_pages}")

    # 3. 遍历指定页面进行处理
    for page_num in target_pages:
        page = doc[page_num]
        print(f"\n正在处理第 {page_num + 1} 页...")


        # --- 功能 B: 删除符合条件的图片 ---
        if image_rules:
            page_w, page_h = page.rect.width, page.rect.height
            # images = page.get_images(full=True)
            drawings = page.get_drawings()
            for drawing in drawings:
                rect = drawing["rect"]

                # 计算相对位置和比例
                rel_x = rect.x0 / page_w
                rel_y = rect.y0 / page_h
                ratio = rect.width / rect.height if rect.height > 0 else 0

                # 匹配规则 (示例：右上角且接近正方形)
                # 你可以根据需要修改这里的判断逻辑
                if (image_rules['x_range'][0] <= rel_x <= image_rules['x_range'][1] and
                    image_rules['y_range'][0] <= rel_y <= image_rules['y_range'][1] and
                    image_rules['ratio_range'][0] <= ratio <= image_rules['ratio_range'][1]):

                    print(f"  🟦 匹配到形状 (位置: {rect}), 比例: {ratio:.2f}")
                    page.add_redact_annot(rect, fill=(1, 1, 1))
                    page.apply_redactions()

    # 4. 保存文件 (覆盖原文件)
    # 临时代码：
    output_path =  f"{base}_完成{ext}"
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    print(f"\n🎉 处理完成！文件已更新: {output_path}")


# ================= 使用示例 =================
if __name__ == "__main__":
    # 模拟参数输入
    input_file = "/Users/teacher/Desktop/未命名文件夹 2/Test.pdf"

    # 你的目标格式："1, 3-5, 9-10, 12"
    page_input = "1"

    # 配置要遮挡的文字
    texts_to_hide = ["机密", "绝密"]

    # 配置要删除的图片规则 (可选，不需要则传 None)
    # 这里演示：删除位于页面右上角 (x>0.8, y<0.2) 且宽高比在 0.8~1.2 之间的图片
    img_config = {
        'x_range': (0.7, 0.95),
        'y_range': (0.4, 0.6),
        'ratio_range': (0.1, 3)
    }

    process_pdf(
        input_path=input_file,
        page_range_str=page_input,
        image_rules=img_config
    )