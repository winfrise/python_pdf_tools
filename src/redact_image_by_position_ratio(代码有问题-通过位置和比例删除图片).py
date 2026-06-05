import fitz  # PyMuPDF
import os
import sys

def save_file(input_file, temp_file, backup_file=None):
    try:
        # 1. 定义备份路径和临时路径
        base_name, ext = os.path.splitext(input_file)
        if backup_file == None:
            backup_file = f"{base_name}_备份{ext}"

        if temp_file == None:
            temp_file = f"{base_name}_temp{ext}"

        # 3. 执行备份和替换操作
        if os.path.exists(input_file):
            # 如果已有备份，先删除旧备份（可选）
            if os.path.exists(backup_file):
                os.remove(backup_file)

            # 将原文件重命名为备份文件
            os.rename(input_file, backup_file)
            print(f"原文件已备份为: {backup_file}")

        # 4. 将临时文件重命名为原文件名
        os.rename(temp_file, input_file)
        print(f"新文件已保存为: {input_file}")

    except Exception as e:
        print(f"保存文件时出错: {e}")
        # 如果出错，尝试清理临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)


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

# 绘制刻度线
def draw_advanced_grid(page, minor_step=10, major_step=100):
    rect = page.rect
    w = rect.width
    h = rect.height

    # 定义样式
    minor_color = (0.9, 0.9, 0.9)  # 极浅灰
    major_color = (0.5, 0.5, 0.5)  # 深灰
    minor_width = 0.5
    major_width = 1.5

    # 绘制垂直线
    for x in range(0, int(w) + 1, minor_step):
        is_major = (x % major_step == 0)
        page.draw_line(
            (x, 0), (x, h),
            color=major_color if is_major else minor_color,
            width=major_width if is_major else minor_width
        )

    # 绘制水平线
    for y in range(0, int(h) + 1, minor_step):
        is_major = (y % major_step == 0)
        page.draw_line(
            (0, y), (w, y),
            color=major_color if is_major else minor_color,
            width=major_width if is_major else minor_width
        )

def process_pdf(input_path, page_range_str, rect_config=None):
    if not os.path.exists(input_path):
        print(f"错误：找不到文件 {input_path}")
        return

    # 1. 自动备份原文件
    base, ext = os.path.splitext(input_path)


    doc = fitz.open(input_path)
    total_pages = len(doc)

    # 2. 解析页码
    target_pages = parse_page_range(page_range_str, total_pages)
    print(f"📄 目标页码 (0-based): {target_pages}")

    # 3. 遍历指定页面进行处理
    for page_num in target_pages:
        page = doc[page_num]
        print(f"\n正在处理第 {page_num + 1} 页...")

        # 绘制刻度线
        draw_advanced_grid(page)

        # 绘制矩形
        page.draw_rect(
            rect=rect_config["rect"], 
            color=rect_config.get("color", (0, 0, 0)),     # 默认黑色边框
            fill=rect_config.get("fill", None),            # 默认无填充 (透明)
            width=rect_config.get("width", 1)              # 默认线宽为 1
        )

    # 保存文件 (覆盖原文件)
    # 临时代码：
    output_path =  f"{base}_output_check{ext}"
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    print(f"\n🎉 处理完成！文件已更新: {output_path}")


def mask_area(input_path, page_range_str, rect_config=None):
    if not os.path.exists(input_path):
        print(f"错误：找不到文件 {input_path}")
        return


    doc = fitz.open(input_path)
    total_pages = len(doc)

    # 2. 解析页码
    target_pages = parse_page_range(page_range_str, total_pages)
    print(f"📄 目标页码 (0-based): {target_pages}")

    # 遍历指定页面进行处理
    for page_num in target_pages:
        page = doc[page_num]
        print(f"\n正在处理第 {page_num + 1} 页...")

        # ---  删除区域内的形状 ---
        if rect_config:
            drawings = page.get_drawings()
            target_rect = fitz.Rect(rect_config["rect"])
            for drawing in drawings:
                shape_rect = drawing["rect"]
                if target_rect.contains(shape_rect):
                    print(f"发现完全在区域内的形状: {shape_rect}")
            
                    page.add_redact_annot(shape_rect, fill=(1, 1, 1))
                    page.apply_redactions()

    # 4. 保存文件 (覆盖原文件)
    # 临时代码：
    base, ext = os.path.splitext(input_path)
    output_path =  f"{base}_完成{ext}"
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()

    print(f"\n🎉 处理完成！文件已更新: {output_path}")

# ================= 使用示例 =================
if __name__ == "__main__":
    # 模拟参数输入
    input_file = "/Users/teacher/Desktop/未命名文件夹/消防建施-副本/消防建施-副本_1.pdf"

    # 你的目标格式："1, 3-5, 9-10, 12"
    page_range = "1"


    # 配置要删除的图片规则 (可选，不需要则传 None)
    rect_config = {
        # "rect": (930, 450, 1180, 670),       # 左上角矩形
        "rect": (200, 200, 1180, 800),       # 左上角矩形
        "color": (1, 0, 0),               # 红色边框
        "fill": None,            # 浅红色填充
        "width": 2                        # 边框宽度
    }

    # 绘制区域
    process_pdf(
        input_path=input_file,
        page_range_str=page_range,
        rect_config=rect_config
    )

    # 删除内容
    mask_area(
        input_path=input_file,
        page_range_str=page_range,
        rect_config=rect_config
    )