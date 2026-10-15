import fitz  # PyMuPDF
import sys, io, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import parse_page_range, batch_process_file_with_callback

def remove_links_from_pdf(input_path, output_path):
    """
    删除PDF文档中的所有超链接，并打印每页删除的链接数量。
    """
    try:
        # 1. 打开PDF文档
        doc = fitz.open(input_path)
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
        doc.save(output_path)
        doc.close()
        
        print("-" * 30)
        print(f"处理完成！共删除 {total_deleted} 个链接。")

    except Exception as e:
        print(f"处理PDF时发生错误: {e}")



if __name__ == "__main__":

    input_path = "/Volumes/西数4T外置/百度网盘默认下载/上传材料/001"      # 替换为你的PDF文件路径

    if os.path.isfile(input_path):
        output_path = input_path.replace('.pdf', '_output_删除链接.pdf')
        remove_links_from_pdf(
            input_path = input_path, 
            output_path = output_path, 
        )
    elif os.path.isdir(input_path):
        def callback_func(input_file, output_file):
            remove_links_from_pdf(
                input_path = input_file, 
                output_path = output_file, 
            )
        input_dir = input_path
        output_dir = f"{input_dir}_删除超链接"
        batch_process_file_with_callback(
            input_dir=input_dir, 
            output_dir=output_dir,
            callback_func=callback_func    
        )
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {input_path}")