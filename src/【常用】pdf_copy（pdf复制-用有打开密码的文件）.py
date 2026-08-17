

import pymupdf  # 推荐使用新名称，fitz 已弃用

import fitz  # PyMuPDF
import os

def remove_pdf_password(input_file, password):
    """
    移除 PDF 的打开密码并保存为新文件。
    
    :param input_file: 输入文件的完整路径 (例如: "/Users/teacher/Desktop/test.pdf")
    :param password:   PDF 的打开密码 (字符串)
    :return:           输出文件的完整路径，如果失败则返回 None
    """
    
    # 1. 检查文件是否存在
    if not os.path.exists(input_file):
        print(f"❌ 错误：找不到文件 -> {input_file}")
        return None

    # 2. 构建输出文件路径
    # 获取目录和文件名
    dir_name = os.path.dirname(input_file)
    base_name = os.path.basename(input_file)
    
    # 分离文件名和后缀 (例如 "test.pdf" -> "test", ".pdf")
    name, ext = os.path.splitext(base_name)
    
    # 拼接新文件名：原文件名_unencrypted_output.pdf
    output_filename = f"{name}_unencrypted_output{ext}"
    output_file = os.path.join(dir_name, output_filename)

    try:
        # 3. 打开文档 (注意：新版 fitz 打开时不传 password)
        doc = fitz.open(input_file)

        # 4. 验证密码
        # 如果文件加密了，必须调用 authenticate
        if doc.is_encrypted:
            if not doc.authenticate(password):
                print(f"❌ 错误：密码不正确，无法解密 {input_file}")
                doc.close()
                return None
        
        # 5. 保存新文件 (直接 save 即可去除密码)
        # save 操作会重写文件结构，新生成的文件默认不再包含加密信息
        doc.save(output_file)
        doc.close()
        
        print(f"✅ 成功！无密码文件已保存至：\n{output_file}")
        return output_file

    except Exception as e:
        print(f"❌ 处理过程中发生异常：{e}")
        return None

# --- 使用示例 ---
if __name__ == "__main__":
    # 替换为你实际的文件路径和密码
    file_path = "/Users/teacher/Desktop/排版/（已压缩）海连内部图册2025.9.2（原）.pdf"
    pwd = ""
    
    remove_pdf_password(file_path, pwd)