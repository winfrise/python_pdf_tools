import fitz  # PyMuPDF

def repair_pdf_with_pymupdf(input_path, output_path):
    """
    使用 PyMuPDF 修复损坏的 PDF 文件
    """

    if not output_path:
        output_path = input_path.replace('.pdf', "_output_修复.pdf")
    try:
        # 1. 打开文件，PyMuPDF 会在加载时自动尝试修复内部结构错误
        # repair=True 是默认行为，它会清理损坏的对象并重建 xref 表
        doc = fitz.open(input_path)
        
        # 2. 检查文件是否处于加密状态（某些损坏会导致误判为加密）
        if doc.is_encrypted:
            print("⚠️ 文件被加密或损坏导致误判为加密，尝试使用空密码解锁...")
            if not doc.authenticate(""):
                print("❌ 无法解锁文件，修复终止。")
                return
        
        # 3. 将修复后的文档保存为新文件
        # garbage=4: 深度清理未使用的对象、空流等，能显著减小修复后的文件体积
        # deflate=True: 压缩流数据，进一步减小体积
        doc.save(output_path, garbage=4, deflate=True)
        doc.close()
        
        print(f"✅ 修复成功！已保存至: {output_path}")
        
    except Exception as e:
        print(f"❌ PyMuPDF 修复失败: {e}")


if __name__ == "__main__":
    input_path = "/Users/teacher/Downloads/百度网盘Download/Desktop/mask1.pdf"
    # 使用示例
    repair_pdf_with_pymupdf(
        input_path = input_path,
        output_path = None,
    )