def delete_last_10_xref_entries(input_pdf, output_pdf):
    # 以二进制模式读取原始 PDF 内容
    with open(input_pdf, 'rb') as f:
        content = f.read()

    # 寻找 xref 表的位置（从后往前找，因为 PDF 的 xref 表通常在文件末尾）
    xref_pos = content.rfind(b'xref')
    if xref_pos == -1:
        print("错误：未找到 xref 表，可能不是标准 PDF 或已被压缩。")
        return

    # 截取 xref 表之前的内容（包含文件头和所有对象）
    before_xref = content[:xref_pos]
    
    # 截取 xref 表及其之后的内容
    xref_section = content[xref_pos:]
    
    # 将 xref 部分按行分割
    lines = xref_section.split(b'\n')
    
    # 找到最后 10 个 xref 条目并删除
    # 注意：xref 表结构通常是：
    # xref
    # 0 11  (表示从0开始有11个条目)
    # 0000000000 65535 f 
    # ...
    # trailer
    # ...
    
    # 简单粗暴的做法：如果总行数大于10，就删掉最后10行
    # 但为了安全，我们最好只删条目，保留 trailer
    trailer_pos = -1
    for i, line in enumerate(lines):
        if b'trailer' in line:
            trailer_pos = i
            break
            
    if trailer_pos == -1:
        print("警告：未找到 trailer，直接截断最后10行。")
        new_xref_lines = lines[:-10]
    else:
        # 在 trailer 之前删除最后 10 个条目
        entries_before_trailer = lines[:trailer_pos]
        entries_after_trailer = lines[trailer_pos:]
        
        if len(entries_before_trailer) > 10:
            new_entries = entries_before_trailer[:-10]
        else:
            new_entries = entries_before_trailer  # 不足10个就不删
            
        new_xref_lines = new_entries + entries_after_trailer

    # 重新拼接文件内容
    new_content = before_xref + b'\n'.join(new_xref_lines)
    
    # 写入新文件
    with open(output_pdf, 'wb') as f:
        f.write(new_content)
        
    print(f"处理完成，已保存至: {output_pdf}")

# 使用示例
delete_last_10_xref_entries("/Users/teacher/Desktop/百度网盘下载/信息技术笔记_已解密.pdf", "output.pdf")