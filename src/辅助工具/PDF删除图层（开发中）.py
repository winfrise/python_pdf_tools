import fitz  # PyMuPDF

def delete_last_drawings_safe(pdf_path, output_path, count=10):
    doc = fitz.open(pdf_path)
    
    for page_num, page in enumerate(doc):
        # 1. 获取页面内容流的引用 (xref)
        # get_contents() 可能返回 int 或 list[int]
        xrefs = page.get_contents()
        
        # 统一转为列表处理
        if isinstance(xrefs, int):
            xrefs = [xrefs]
            
        if not xrefs:
            continue

        print(f"正在处理第 {page_num + 1} 页...")

        # 2. 读取并合并所有流数据 (保持 bytes 类型)
        full_stream = b""
        for xref in xrefs:
            stream_data = doc.xref_stream(xref)
            if stream_data:
                full_stream += stream_data
        
        # 3. 按行切割并删除最后 N 行
        # 注意：这里必须使用 b'\n' (bytes) 进行切割
        lines = full_stream.split(b'\n')
        
        total_lines = len(lines)
        if total_lines <= count:
            print(f"  警告：行数不足，将清空该页内容流。")
            new_stream = b""
        else:
            new_lines = lines[:-count]
            # 重新拼接为 bytes
            new_stream = b'\n'.join(new_lines)
            print(f"  已移除最后 {count} 行指令。")

        # 4. 【核心修复】使用 update_stream 更新第一个 xref
        # 这个方法专门用于更新 Stream 对象，直接接受 bytes
        target_xref = xrefs[0]
        page.update_stream(target_xref, new_stream)
        
        # 5. 如果有多个 xref，清空其余的，防止旧数据残留
        if len(xrefs) > 1:
            for extra_xref in xrefs[1:]:
                # 将多余的流更新为空字节流
                page.update_stream(extra_xref, b"")

    # 6. 保存文件
    # garbage=4 会彻底清理那些被清空的 xref 对象
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    print(f"\n处理完成！已保存至: {output_path}")

# --- 使用示例 ---
if __name__ == "__main__":
    input_pdf = "/Users/teacher/Desktop/百度网盘下载/信息技术笔记_已解密.pdf"  # 替换为你的文件名
    output_pdf = "output_fixed.pdf"
    
    delete_last_drawings_safe(input_pdf, output_pdf, count=10)