import pymupdf
import re

doc = pymupdf.open("/Users/teacher/Desktop/pdf_command/pdf解密/output/001/01.pdf")
page = doc[0]

# 1. 获取该页所有内容流的 xref 列表
xrefs = page.get_contents()

# 2. 读取并合并所有流的数据
# 这样做是为了防止 GS15 的指令分散在不同的流对象中
full_stream = b""
for xref in xrefs:
    full_stream += doc.xref_stream(xref)

# 3. 执行替换逻辑
# 逻辑：找到 /GS15 gs 后面紧跟的 0 0 0 SCN (描边) 或 scn (填充)
# 将其颜色值 0 0 0 替换为 1 1 1 (白色)
# \s+ 用于匹配中间可能存在的换行符或空格
pattern = rb'(/GS15\s+gs\s+)(0\s+0\s+0\s+(?:SCN|scn))'

# 使用回调函数进行替换，保留前面的 GS 指令，只改后面的颜色
def replace_color(match):
    return match.group(1) + b'1 1 1 SCN' 

new_stream = re.sub(pattern, replace_color, full_stream)

# 4. 写入新流
# 注意：这里只传 new_stream，绝对不要传 xref！
# set_contents 会自动处理压缩和替换旧的所有流
page.set_contents(new_stream)

# 5. 保存
doc.save("output_white_final.pdf", garbage=3, deflate=True)
doc.close()

print("处理完成！")