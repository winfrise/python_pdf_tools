import fitz
import re
import os
from utils import process_file_with_callback, batch_process_file_with_callback

# 使用场景：批量删除形状水印


INPUT_PATH = "/Users/teacher/Desktop/test_output"
OUTPUT_PATH = ""
PAGE_RANGE = "1-1000"
FROM_COLOR = rb'(?:192|0\.75[0-9]*)'
# CMYK颜色， 红色: [0, 1, 1, 0] 黑色:[0, 0, 0, 1] 白色:[0, 0, 0, 0] 蓝色: [1, 0, 0, 0]
TO_CMYK_COLOR = [0, 1, 1, 0]

def change_shapes_color_cmyk(input_file, output_file, page_range, from_color, to_color):
    def callback_func(page, page_num, doc):

        # 1. 匹配 RGB 描边 (Stroke): 192 192 192 RG
        pattern_rgb_stroke = re.compile(
            rb'(' + from_color + rb'\s+' + from_color + rb'\s+' + from_color + rb'\s+RG\b)'
        )

        # 2. 匹配 RGB 填充 (Fill): 192 192 192 rg
        pattern_rgb_fill = re.compile(
            rb'(' + from_color + rb'\s+' + from_color + rb'\s+' + from_color + rb'\s+rg\b)'
        )

        # 3. 匹配灰度 (Gray): 192 g (很多 PDF 会把 R=G=B 简化为灰度指令)
        pattern_gray = re.compile(
            rb'(' + from_color + rb'\s+g\b)'
        )


        # CMYK 最终的颜色
        c, m, y, k_val = to_color
        color_cmyk_fill = f'{c} {m} {y} {k_val} k '.encode()
        color_cmyk_stroke = f'{c} {m} {y} {k_val} K '.encode()
        color_cmyk_gray = f'{c} {m} {y} {k_val} k '.encode()

        # 获取页面的原始内容流 (Content Stream)
        xref = page.get_contents()[0] # 获取第一个内容流的引用 ID
        stream = doc.xref_stream(xref)

        if not stream:
            print(f'Page {page_num}: 没有steam')
            return

        content_bytes = bytearray(stream) # 转换为可修改的字节数组

        # 简单的全局替换（针对主要由形状组成的文档）
        new_content = content_bytes

        # 1. 替换 RGB 描边 -> CMYK 红
        new_content = pattern_rgb_stroke.sub(color_cmyk_stroke, new_content)

        # 2. 替换 RGB 填充 -> CMYK 红
        new_content = pattern_rgb_fill.sub(color_cmyk_fill, new_content)

        # 3. 替换灰度 -> CMYK 红
        # 注意：PDF 中 'g' 是设置灰度，如果要变彩色，通常需要破坏原有的灰度状态
        # 这里直接替换为设置 CMYK 颜色的指令是可行的
        new_content = pattern_gray.sub(color_cmyk_gray, new_content)

        # 只有当内容发生变化时才更新 PDF
        if new_content != content_bytes:
            # 更新流数据
            doc.update_stream(xref, new_content)
            print(f"Page {page_num}: 颜色指令已替换。")
        else:
            print(f"Page {page_num}: 未检测到标准颜色指令（可能是图片、CMYK颜色或已加密）。")

    process_file_with_callback(
        input_file = input_file, 
        output_file = output_file, 
        page_range = page_range, 
        callback_func = callback_func
    )


# === 使用示例 ===
if __name__ == "__main__":

    if os.path.isfile(INPUT_PATH):
        change_shapes_color_cmyk(
            input_file = INPUT_PATH,
            output_file = OUTPUT_PATH,
            page_range = PAGE_RANGE,
            from_color = FROM_COLOR,
            to_color = TO_CMYK_COLOR
        )
    elif os.path.isdir(INPUT_PATH):
        def callback_func(input_file, output_file):
            change_shapes_color_cmyk(
                input_file = input_file,
                output_file = output_file,
                page_range = PAGE_RANGE,
                from_color = FROM_COLOR,
                to_color = TO_CMYK_COLOR,
            )

        batch_process_file_with_callback(
            input_dir = INPUT_PATH,
            output_dir = OUTPUT_PATH,
            callback_func = callback_func
        )
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {INPUT_PATH}")

