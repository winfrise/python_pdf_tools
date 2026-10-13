import fitz

def remove_watermark_by_logic(pdf_path, output_path):
    doc = fitz.open(pdf_path)
    
    # 定义关键锚点（转换为字节以便在二进制流中搜索）
    anchor_color = b"0.855 0.89 0.953 rg"
    anchor_start_marker = b"W* n"
    anchor_end_marker = b"EMC"
    
    total_removed = 0

    for page in doc:
        xrefs = page.get_contents()
        if not xrefs: continue
        if isinstance(xrefs, int): xrefs = [xrefs]

        for xref in xrefs:
            try:
                stream_data = doc.xref_stream(xref)
                if not stream_data: continue

                # 1. 找到颜色指令的位置
                color_idx = stream_data.find(anchor_color)
                
                # 如果当前流里没有这个颜色，直接跳过
                if color_idx == -1:
                    continue
                
                print(f"页面 {page.number + 1}: 发现目标颜色指令，开始定位删除范围...")

                # 2. 向前寻找最后一个 "W* n" (起点)
                # rfind 会返回指定范围内最后一次出现的索引
                start_idx = stream_data.rfind(anchor_start_marker, 0, color_idx)
                
                if start_idx == -1:
                    print("  ⚠️ 警告：在颜色指令前未找到 'W* n'，跳过此流以防损坏文件。")
                    continue
                
                # 3. 向后寻找第 5 个 "EMC" (终点)
                search_pos = color_idx
                found_count = 0
                end_idx = -1
                
                while found_count < 5:
                    next_emc = stream_data.find(anchor_end_marker, search_pos)
                    if next_emc == -1:
                        break # 没找够5个就结束了
                    
                    found_count += 1
                    # 移动搜索指针到当前 EMC 之后，继续找下一个
                    search_pos = next_emc + len(anchor_end_marker)
                    
                    # 如果找够了，记录位置
                    if found_count == 5:
                        end_idx = search_pos 

                if end_idx == -1:
                    print(f"  ⚠️ 警告：在颜色指令后未找够 5 个 'EMC' (只找到 {found_count} 个)，跳过。")
                    continue

                # 4. 执行删除操作
                # 拼接 "起点之前" 和 "终点之后" 的数据
                new_stream_data = stream_data[:start_idx] + stream_data[end_idx:]
                
                # 更新流
                doc.update_stream(xref, new_stream_data)
                total_removed += 1
                print(f"  ✅ 成功删除从偏移量 {start_idx} 到 {end_idx} 的数据块。")

            except Exception as e:
                print(f"处理页面 {page.number + 1} 时出错: {e}")

    if total_removed > 0:
        doc.save(output_path)
        print(f"\n处理完成！共修改 {total_removed} 个内容流，已保存至: {output_path}")
    else:
        print("\n未执行任何删除操作。")
        
    doc.close()


# --- 使用示例 ---
if __name__ == "__main__":
    input_path = "/Users/teacher/Desktop/pdf_command/pdf解密/output/去水印10个文件/蓝色水印/背诵-27考研押题专项考点班-方剂学.pdf"
    output_path = input_path.replace('.pdf', '_替换颜色2.pdf')
    remove_watermark_by_logic(input_path, output_path)