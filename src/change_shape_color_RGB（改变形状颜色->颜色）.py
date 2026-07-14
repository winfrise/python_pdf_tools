import fitz
import re
import os

def change_shapes_to_blue(input_path, output_path):
    """
    将PDF中的黑色/灰色形状变为蓝色。

    :param input_path: 输入文件路径
    :param output_path: 输出文件路径
    """
    doc = fitz.open(input_path)

    # 定义目标颜色 (R, G, B)
    TARGET_COLOR_R = 255
    TARGET_COLOR_G = 0
    TARGET_COLOR_B = 0

    # 预编译正则表达式，用于匹配 PDF 中的颜色设置指令
    # 匹配 0 g (灰度黑), 0 G, 0 0 0 rg (RGB黑), 0 0 0 RG 等
    # 这里的逻辑是：只要检测到设置颜色的指令是黑色(0)，就将其替换为蓝色
    pattern_black_gray = re.compile(rb'(\b0\b\s+g\b)')       # 匹配 "0 g"
    pattern_black_rgb_stroke = re.compile(rb'(\b0\s+0\s+0\s+RG\b)') # 匹配 "0 0 0 RG" (描边)
    pattern_black_rgb_fill = re.compile(rb'(\b0\s+0\s+0\s+rg\b)')   # 匹配 "0 0 0 rg" (填充)

    # 构建替换后的蓝色指令字符串
    blue_stroke_cmd = f"{TARGET_COLOR_R} {TARGET_COLOR_G} {TARGET_COLOR_B} RG".encode()
    blue_fill_cmd = f"{TARGET_COLOR_R} {TARGET_COLOR_G} {TARGET_COLOR_B} rg".encode()
    # 注意：PDF中没有直接的 "B g" (Blue Gray)，通常我们将灰度黑转为 RGB 蓝
    blue_gray_substitute = blue_stroke_cmd

    for page_num in range(len(doc)):
        page = doc[page_num]

        # 获取页面的原始内容流 (Content Stream)
        xref = page.get_contents()[0] # 获取第一个内容流的引用 ID
        stream = doc.xref_stream(xref)

        if not stream:
            continue

        content_bytes = bytearray(stream) # 转换为可修改的字节数组

        # --- 核心处理逻辑 ---

        # 1. 检查当前页面是否有签名区域需要保护
        # 如果有签名，处理起来比较复杂（需要切割流）。
        # 为了简化且保证稳定性，这里采用一种折中方案：
        # 如果定义了签名区域，我们暂时不处理该页（或者你可以手动在该页用画图工具覆盖）。
        # *但在本脚本中，为了演示“变蓝”，我们先假设全页处理，*
        # *如果你能提供具体坐标，我们可以做更精细的流切割（代码量会大增）。*

        # 简单的全局替换（针对主要由形状组成的文档）
        new_content = content_bytes

        # 替换 RGB 黑色描边 -> 蓝色
        new_content = pattern_black_rgb_stroke.sub(blue_stroke_cmd, new_content)
        # 替换 RGB 黑色填充 -> 蓝色
        new_content = pattern_black_rgb_fill.sub(blue_fill_cmd, new_content)
        # 替换灰度黑色 -> 蓝色 (作为描边处理)
        new_content = pattern_black_gray.sub(blue_gray_substitute, new_content)

        # 只有当内容发生变化时才更新 PDF
        if new_content != content_bytes:
            # 更新流数据
            doc.update_stream(xref, new_content)
            print(f"Page {page_num + 1}: 颜色指令已替换。")
        else:
            print(f"Page {page_num + 1}: 未检测到标准黑色指令（可能是图片、CMYK颜色或已加密）。")

    doc.save(output_path)
    doc.close()
    print(f"处理完成！文件已保存至: {output_path}")


# === 使用示例 ===
if __name__ == "__main__":

    # 如果你有签名的坐标，可以在这里填入，目前代码主要演示全局变色
    # 坐标可以通过 Adobe Acrobat 的 "测量工具" 或 PyMuPDF 的 page.get_text("dict") 辅助获取
    signatures = [
        # (x0, y0, x1, y1)
        # 例如: (400, 650, 550, 700)
    ]

    input_path = "/Users/teacher/Desktop/20260714去水印/《公基》《常识》系统课讲义（第二至第四章是敏感课内容讲义）.pdf"
    output_path = "/Users/teacher/Desktop/20260714去水印/《公基》《常识》系统课讲义（第二至第四章是敏感课内容讲义）_2.pdf"

    if os.path.isfile(input_path):
        input_file = input_path
        output_file = output_path

        change_shapes_to_blue(input_file, output_file)
    elif os.path.isdir(input_path):
        input_folder = input_path
        output_folder = output_path

        for root, dirs, files in os.walk(input_folder):
            for file in files:
                if file.lower().endswith('.pdf'):
                    input_pdf = os.path.join(root, file)
                    relative_input_pdf = os.path.relpath(input_pdf, input_folder)
                    output_pdf = os.path.join(output_folder, relative_input_pdf)
                    
                    # 确保输出目录存在
                    output_pdf_dir = os.path.dirname(output_pdf)
                    os.makedirs(output_pdf_dir, exist_ok=True)
                    
                    print(f"正在处理: {relative_input_pdf}")

                    change_shapes_to_blue(input_pdf, output_pdf)
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {input_path}")

