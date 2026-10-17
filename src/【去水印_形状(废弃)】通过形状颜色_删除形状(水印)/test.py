import pymupdf

doc = pymupdf.open("/Users/teacher/Desktop/pdf_command/pdf解密/output/001/01.pdf")

# 1. 直接定位到 GS15 的对象号 (从你截图看是 18)
gs15_xref = 18 

# 2. 验证一下这个对象是不是我们要找的
print("修改前:", doc.xref_get_key(gs15_xref, "CA")) 

# 3. 直接修改该对象的 CA 值
# 注意：这里不需要传 page.xref，直接传 gs15_xref
doc.xref_set_key(gs15_xref, "CA", "null")
# doc.xref_set_key(gs15_xref, "LW", "10")

# 4. 再次验证
print("修改后:", doc.xref_get_key(gs15_xref, "CA"))

# 5. 保存
doc.save("output_fixed.pdf", garbage=3, deflate=True)