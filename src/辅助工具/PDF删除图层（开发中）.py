import fitz  # PyMuPDF

def list_pdf_layers(pdf_path):
    """遍历并打印 PDF 中所有的图层信息"""
    doc = fitz.open(pdf_path)
    # 获取所有图层（OCGs）
    ocgs = doc.get_ocgs()
    
    if not ocgs:
        print("该 PDF 文件中没有图层 (OCGs)。")
        doc.close()
        return

    print(f"共发现 {len(ocgs)} 个图层：")
    print("-" * 40)
    for xref, info in ocgs.items():
        # info 是一个字典，包含 'name', 'creator', 'usage' 等
        print(f"图层 XREF: {xref}")
        print(f"图层名称: {info['name']}")
        print(f"创建者: {info.get('creator', 'N/A')}")
        print("-" * 40)
    
    doc.close()

def delete_pdf_layers(pdf_path, output_path, layer_names_to_delete):
    """
    删除指定名称的图层及其内容
    :param pdf_path: 输入 PDF 路径
    :param output_path: 输出 PDF 路径
    :param layer_names_to_delete: 需要删除的图层名称列表
    """
    doc = fitz.open(pdf_path)
    ocgs = doc.get_ocgs()
    
    deleted_count = 0
    for xref, info in ocgs.items():
        layer_name = info['name']
        # 如果图层名称在待删除列表中
        if layer_name in layer_names_to_delete:
            # 删除图层对象及其关联的内容
            doc.delete_object(xref)
            deleted_count += 1
            print(f"已删除图层: {layer_name} (XREF: {xref})")
            
    if deleted_count == 0:
        print("未找到匹配的图层，未进行任何删除操作。")
    else:
        # 保存并清理冗余对象
        doc.save(output_path, garbage=4, deflate=True)
        print(f"成功删除 {deleted_count} 个图层，已保存至: {output_path}")
    
    doc.close()

# --- 使用示例 ---
if __name__ == "__main__":
    input_pdf = "/Users/teacher/Desktop/百度网盘下载/信息技术笔记_已解密.pdf"
    output_pdf = "output.pdf"
    
    # 1. 先遍历查看所有图层
    list_pdf_layers(input_pdf)
    
    # 2. 删除自定义的图层（传入图层名称列表）
    target_layers = ["Watermark", "Draft", "隐藏图层"] 
    # delete_pdf_layers(input_pdf, output_pdf, target_layers)