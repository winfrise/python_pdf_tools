import fitz  # PyMuPDF

def list_pdf_ocgs(pdf_path):
    """
    遍历并打印 PDF 文档中的所有 OCG（可选内容组/图层）
    """
    # 打开 PDF 文档
    doc = fitz.open(pdf_path)
    
    # 获取文档中所有的图层（OCG）配置
    layers = doc.get_layers()
    
    if not layers:
        print("该 PDF 文档中没有找到任何 OCG（图层）。")
    else:
        print(f"共找到 {len(layers)} 个 OCG 图层：")
        print("-" * 40)
        for layer in layers:
            # layer 是一个字典，通常包含 'number', 'name', 'creator' 等键
            print(f"图层编号 (number): {layer.get('number')}")
            print(f"图层名称 (name): {layer.get('name')}")
            print(f"创建者 (creator): {layer.get('creator')}")
            print("-" * 40)
            
    # 关闭文档释放资源
    doc.close()

# 使用示例
if __name__ == "__main__":
    pdf_file = "/Users/teacher/Desktop/未命名文件夹/自控思维导图（密码123）_unencrypted_output.pdf"  # 替换为你的 PDF 文件路径
    list_pdf_ocgs(pdf_file)