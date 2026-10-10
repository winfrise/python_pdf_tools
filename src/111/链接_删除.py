import fitz  # PyMuPDF

def remove_links_from_pdf(input_pdf_path, output_pdf_path):
    """
    删除PDF文档中的所有超链接，并打印每页删除的链接数量。
    """
    try:
        # 1. 打开PDF文档
        doc = fitz.open(input_pdf_path)
        total_deleted = 0

        # 2. 遍历文档中的每一页
        for page_num in range(len(doc)):
            page = doc[page_num]
            deleted_count = 0
            
            # 获取当前页面的所有链接
            links = page.get_links()
            
            # 从后向前遍历并删除链接，避免索引变化导致的遗漏
            for i in range(len(links) - 1, -1, -1):
                link = links[i]
                # 删除该链接注解
                page.delete_link(link)
                print(f"链接:{link.get('uri')}")
                deleted_count += 1
            
            # 打印当前页删除的链接数
            print(f"第 {page_num + 1} 页: 删除了 {deleted_count} 个链接")
            total_deleted += deleted_count

        # 3. 保存修改后的文档到新文件
        doc.save(output_pdf_path)
        doc.close()
        
        print("-" * 30)
        print(f"处理完成！共删除 {total_deleted} 个链接。")
        print(f"新文档已保存至: {output_pdf_path}")

    except Exception as e:
        print(f"处理PDF时发生错误: {e}")

# 使用示例
if __name__ == "__main__":
    input_file = "/Users/teacher/Desktop/百度网盘下载/附件1-2.pdf"      # 替换为你的PDF文件路径
    output_file = input_file.replace('.pdf', '_output_删除链接.pdf')
    remove_links_from_pdf(input_file, output_file)