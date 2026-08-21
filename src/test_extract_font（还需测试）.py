import pymupdf

# 打开源 PDF
source_doc = pymupdf.open("/Users/teacher/Desktop/test/京AE30128(2).pdf")

page = source_doc[0] # 确保第一页有文字内容
fonts = page.get_fonts()

# 【调试】打印获取到的字体列表长度和内容
print(f"检测到的字体数量: {len(fonts)}")
print(f"字体详情: {fonts}") 
# 修改后：判断一下，如果有多个字体，尝试取第二个（索引为1）
if len(fonts) > 1:
    # 尝试提取第二个字体 (STSong)
    xref = fonts[1][0] 
    print(f"正在尝试提取第二个字体: {fonts[1][3]}")
else:
    xref = fonts[0][0]

font_name, ext, font_type, font_content = source_doc.extract_font(xref)

if font_content:
    print(f"成功提取！文件名: {font_name}.{ext}")
    # 这里就可以保存了
else:
    print("依然提取失败。这说明该 PDF 的中文字体也是引用系统字体，未真正嵌入文件流。")