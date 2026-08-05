

import pymupdf  # 推荐使用新名称，fitz 已弃用

input_file = "/Users/teacher/Desktop/未命名文件夹/KA02000387e01e16c640001 (1).pdf"
output_file = "/Users/teacher/Desktop/未命名文件夹/unencrypted_copy.pdf"
password = "212421"

# 1. 打开加密的 PDF 文件（不传 password 参数）
doc = pymupdf.open(input_file)

# 2. 尝试用密码验证（如果文件有打开密码）
if doc.needs_pass:
    success = doc.authenticate(password)  # 替换为你的实际密码
    if not success:
        print("密码错误，无法打开文件！")
        exit(1)

# 3. 创建新文档并复制所有页面
new_doc = pymupdf.open()
for page_num in range(doc.page_count):
    new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

# 4. 保存无密码的新文件
new_doc.save(output_file)

# 5. 关闭文档
doc.close()
new_doc.close()

print("✅ 已成功生成无密码副本：unencrypted_output.pdf")