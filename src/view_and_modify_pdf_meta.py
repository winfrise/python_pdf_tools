import fitz  # PyMuPDF
import os

def view_pdf_metadata(pdf_path):
    """查看 PDF 的标准元数据和 XMP 元数据"""
    if not os.path.exists(pdf_path):
        print(f"❌ 文件不存在：{pdf_path}")
        return

    doc = fitz.open(pdf_path)
    print(f"📄 正在查看文件：{pdf_path}\n")
    
    # 1. 查看标准文档信息
    print("--- 标准文档信息 (Metadata) ---")
    metadata = doc.metadata
    for key, value in metadata.items():
        # 过滤掉空值，让输出更清爽
        if value:
            print(f"{key}: {value}")
    
    # 2. 查看 XMP 元数据 (XML格式)
    print("\n--- XMP 元数据 (XML) ---")
    xmp = doc.get_xml_metadata()
    if xmp:
        # 截取前 500 个字符预览，防止 XML 太长刷屏
        print(xmp[:500] + "..." if len(xmp) > 500 else xmp)
    else:
        print("该文档没有 XMP 元数据。")
        
    doc.close()
    print("-" * 30)

def modify_pdf_metadata(input_pdf, output_pdf, new_metadata=None):
    """
    修改 PDF 的标准元数据并保存为新文件
    :param new_metadata: 字典格式，例如 {"title": "新标题", "author": "新作者"}
    """
    if not os.path.exists(input_pdf):
        print(f"❌ 文件不存在：{input_pdf}")
        return

    doc = fitz.open(input_pdf)
    
    # 如果传入了新的元数据字典，则进行更新
    if new_metadata:
        # PyMuPDF 会自动将字典中有效的键（title, author等）更新到文档中
        doc.set_metadata(new_metadata)
        print(f"✅ 成功更新元数据：{new_metadata}")
    
    # 保存为新文件（如果想覆盖原文件，output_pdf 可以和 input_pdf 相同）
    doc.save(output_pdf)
    doc.close()
    print(f"💾 文件已保存至：{output_pdf}\n")

# ================= 使用示例 =================
if __name__ == "__main__":
    # 替换成你本地的 PDF 文件路径
    pdf_file = "example.pdf" 
    output_file = "example_modified.pdf"

    # 1. 先查看修改前的元数据
    view_pdf_metadata(pdf_file)

    # 2. 定义要修改的新元数据（不需要修改的键可以省略）
    new_meta = {
        "title": "PyMuPDF 测试文档",
        "author": "你的大名",
        "subject": "元数据修改测试",
        "keywords": "Python, PyMuPDF, 测试"
    }

    # 3. 执行修改并保存
    modify_pdf_metadata(pdf_file, output_file, new_meta)

    # 4. 再次查看，验证修改结果
    view_pdf_metadata(output_file)