import fitz  # PyMuPDF

def replace_color_in_stream(pdf_path, output_path, old_color_str, new_color_str):
    """
    通过修改内容流替换 PDF 颜色指令
    """
    doc = fitz.open(pdf_path)
    
    # 将字符串转换为字节，用于二进制匹配
    target_bytes = old_color_str.encode('ascii') # PDF指令通常是ASCII
    replacement_bytes = new_color_str.encode('ascii')
    
    print(f"正在处理: {pdf_path}")
    print(f"查找目标: {old_color_str}")
    print(f"替换为: {new_color_str}")

    modified_count = 0
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # 1. 获取内容流的 xref
        # 注意：get_contents() 可能返回 None, int, 或 list[int]
        xrefs = page.get_contents()
        
        if not xrefs:
            continue
            
        # 统一转换为列表处理，兼容单个或多个内容流的情况
        if isinstance(xrefs, int):
            xrefs = [xrefs]
            
        for xref in xrefs:
            try:
                # 2. 读取流数据 (PyMuPDF 会自动处理解压)
                stream_data = doc.xref_stream(xref)
                
                if stream_data is None:
                    continue
                
                # 3. 执行替换
                if target_bytes in stream_data:
                    new_stream_data = stream_data.replace(target_bytes, replacement_bytes)
                    
                    # 4. 更新流 (PyMuPDF 会自动处理重新压缩)
                    doc.update_stream(xref, new_stream_data)
                    modified_count += 1
                    
            except Exception as e:
                print(f"警告: 页面 {page_num+1} 的流 {xref} 处理出错: {e}")
                continue

    if modified_count > 0:
        doc.save(output_path)
        print(f"成功！共修改了 {modified_count} 处流对象。文件已保存至: {output_path}")
    else:
        print("未在内容流中找到匹配的颜色指令，文件未保存。")
        
    doc.close()
# --- 使用示例 ---
if __name__ == "__main__":
    input_path = "/Volumes/西数4T外置/百度网盘默认下载/test/TSG 08—2026 特种设备使用管理规则222.pdf"
    output_path = input_path.replace('.pdf', '_替换颜色.pdf')
    replace_color_in_stream(
        pdf_path=input_path, 
        output_path=output_path, 
        old_color_str=".82 .953 .906 rg", 
        new_color_str="1 1 1 rg"
    )