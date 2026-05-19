import os
import fitz  # PyMuPDF

def batch_remove_text(source_dir, target_dir, keyword):
    """
    批量移除 PDF 中的指定文字，并保持目录结构
    """
    print(f"🔍 正在扫描源目录: {source_dir}")
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"📂 已创建目标目录: {target_dir}")

    file_count = 0
    
    # 递归遍历文件夹
    for root, dirs, files in os.walk(source_dir):
        for filename in files:
            if filename.lower().endswith(".pdf"):
                # 1. 构建源文件路径和目标文件路径
                source_path = os.path.join(root, filename)
                
                # 计算相对路径，用于在目标目录重建结构
                relative_path = os.path.relpath(source_path, source_dir)
                target_path = os.path.join(target_dir, relative_path)
                
                # 2. 确保目标子文件夹存在
                target_sub_dir = os.path.dirname(target_path)
                if not os.path.exists(target_sub_dir):
                    os.makedirs(target_sub_dir)

                # 3. 处理单个 PDF
                try:
                    process_pdf(source_path, target_path, keyword)
                    file_count += 1
                    print(f"✅ 处理成功: {relative_path}")
                except Exception as e:
                    print(f"❌ 处理失败: {relative_path} - 错误: {str(e)}")

    print(f"\n🎉 全部完成！共处理 {file_count} 个文件。")

def process_pdf(input_path, output_path, keyword):
    """
    使用 PyMuPDF 真正移除文字
    """
    # 打开 PDF
    doc = fitz.open(input_path)
    
    # 遍历每一页
    for page in doc:
        # 1. 搜索关键字的所有出现位置
        # search_for 返回一个矩形列表，每个矩形代表文字的位置
        text_instances = page.search_for(keyword)
        
        # 2. 如果找到了文字，则执行移除操作
        if text_instances:
            for inst in text_instances:
                # add_redact_annot 是核心：
                # 它不仅仅是遮挡，而是标记该区域为“修订/删除”。
                # 当保存时，该区域的文字内容会被彻底清除。
                page.add_redact_annot(inst)
            
            # 应用修订（真正执行删除操作）
            # 注意：这一步会重写页面内容流，移除被标记的文字
            page.apply_redactions()

    # 保存文件
    # garbage=4: 清理未引用的对象，减小文件体积
    # deflate: 压缩数据
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()

if __name__ == "__main__":
    # ================= 配置区域 =================
    
    # 1. 源文件夹路径 (请修改)
    SOURCE_DIR = r"/Users/teacher/Desktop/未命名文件夹 2/split_pages"
    
    # 2. 目标文件夹路径 (请修改)
    TARGET_DIR = r"/Users/teacher/Desktop/未命名文件夹 2/split_pages2"
    
    # 3. 要删除的关键字
    KEYWORD = "Evaluation Warning : The document was created with Spire.PDF for Python." 
    
    # ===========================================
    
    if not os.path.exists(SOURCE_DIR):
        print(f"错误：找不到源目录 '{SOURCE_DIR}'，请检查路径。")
    else:
        batch_remove_text(SOURCE_DIR, TARGET_DIR, KEYWORD)