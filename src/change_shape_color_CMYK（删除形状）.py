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
    # 定义数值匹配规则：匹配 "192" 或者 "0.75" (及其后可能跟的数字)
    # \b 表示单词边界，防止匹配到 1192 等数字
    val = rb'(?:192|0\.75[0-9]*)'

    # 1. 匹配 RGB 描边 (Stroke): 192 192 192 RG
    pattern_rgb_stroke = re.compile(
        rb'(' + val + rb'\s+' + val + rb'\s+' + val + rb'\s+RG\b)'
    )

    # 2. 匹配 RGB 填充 (Fill): 192 192 192 rg
    pattern_rgb_fill = re.compile(
        rb'(' + val + rb'\s+' + val + rb'\s+' + val + rb'\s+rg\b)'
    )

    # 3. 匹配灰度 (Gray): 192 g (很多 PDF 会把 R=G=B 简化为灰度指令)
    pattern_gray = re.compile(
        rb'(' + val + rb'\s+g\b)'
    )

    # CMYK 红色指令 (C M Y K 操作符)
    # 注意：指令之间最好保留空格，防止与后续内容粘连
    # cmyk_red_stroke = b'0 1 1 0 K ' 
    # cmyk_red_fill   = b'0 1 1 0 k '
    # cmyk_red_gray   = b'0 1 1 0 k ' # 灰度模式下没有直接的CMYK指令，通常转为填充指令或黑色K

    # CMYK 白色
    cmyk_red_stroke = b'0 0 0 0 K ' 
    cmyk_red_fill   = b'0 0 0 0 k '
    cmyk_red_gray   = b'0 0 0 0 k ' # 灰度模式下没有直接的CMYK指令，通常转为填充指令或黑色K

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

        # 1. 替换 RGB 描边 -> CMYK 红
        new_content = pattern_rgb_stroke.sub(cmyk_red_stroke, new_content)

        # 2. 替换 RGB 填充 -> CMYK 红
        new_content = pattern_rgb_fill.sub(cmyk_red_fill, new_content)

        # 3. 替换灰度 -> CMYK 红
        # 注意：PDF 中 'g' 是设置灰度，如果要变彩色，通常需要破坏原有的灰度状态
        # 这里直接替换为设置 CMYK 颜色的指令是可行的
        new_content = pattern_gray.sub(cmyk_red_gray, new_content)

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

    input_path = "/Users/teacher/Desktop/20260714去水印/未命名文件夹/《公基》《常识》系统课讲义（第二至第四章是敏感课内容讲义）.pdf"
    output_path = "/Users/teacher/Desktop/20260714去水印/未命名文件夹/《公基》《常识》系统课讲义（第二至第四章是敏感课内容讲义）——2.pdf"

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

