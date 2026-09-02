import fitz
import os

def save_raw_content_streams(input_pdf):
    """
    提取 PDF 每一页的原始内容流（Content Stream）并保存为 txt 文件。
    保存路径为 PDF 同目录下的 content 文件夹。
    """
    # 1. 检查文件是否存在
    if not os.path.exists(input_pdf):
        print(f"错误：找不到文件 {input_pdf}")
        return

    # 2. 准备输出目录 (PDF 同级目录下的 content 文件夹)
    base_dir = os.path.dirname(os.path.abspath(input_pdf))
    output_dir = os.path.join(base_dir, "content")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"已创建输出文件夹: {output_dir}")

    # 3. 打开 PDF 文档
    try:
        doc = fitz.open(input_pdf)
        print(f"正在处理: {os.path.basename(input_pdf)} (共 {len(doc)} 页)")
    except Exception as e:
        print(f"无法打开 PDF: {e}")
        return

    # 4. 遍历每一页并保存
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # 获取当前页面的内容流引用列表
        # get_contents() 返回的是 xref 列表，例如 [15, 16]
        xrefs = page.get_contents()
        
        if not xrefs:
            print(f"第 {page_num + 1} 页: 无内容流，跳过")
            continue

        # 获取第一个内容流的 xref (对应你图片中的逻辑 [0])
        first_xref = xrefs[0]
        
        # 读取原始字节流
        raw_stream = doc.xref_stream(first_xref)
        
        if raw_stream:
            # 转换为 bytearray (对应你图片中的逻辑)
            content_bytes = bytearray(raw_stream)
            
            # 定义文件名，例如 page_1.txt
            file_name = f"page_{page_num + 1}.txt"
            file_path = os.path.join(output_dir, file_name)
            
            # 以二进制写入模式 ('wb') 保存
            with open(file_path, "wb") as f:
                f.write(content_bytes)
                
            print(f"成功保存: {file_name} (大小: {len(content_bytes)} bytes)")
        else:
            print(f"第 {page_num + 1} 页: 读取流失败")

    doc.close()
    print("处理完成！")

# --- 使用示例 ---
if __name__ == "__main__":
    # 将这里的路径替换为你实际的 PDF 文件路径
    pdf_path = "/Users/teacher/Desktop/test/TSG 08—2026 特种设备使用管理规则  (1).pdf" 
    save_raw_content_streams(pdf_path)