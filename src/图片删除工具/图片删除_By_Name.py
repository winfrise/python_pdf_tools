import fitz
import re

def remove_images_by_names(pdf_path, output_path, image_names):
    """
    根据图片名称列表，彻底删除PDF中的图片及其绘制指令
    
    :param pdf_path: 输入PDF路径
    :param output_path: 输出PDF路径
    :param image_names: 图片名称列表 (例如: ['Im1', 'Image5'])
    """
    doc = fitz.open(pdf_path)
    
    # 1. 预处理名称：PDF内容流中对象名通常带斜杠，如 /Im1
    # 使用正则转义防止特殊字符干扰，并加上 / 前缀
    target_refs = [f"/{re.escape(name)}" for name in image_names]
    
    print(f"正在处理，目标图片标记: {target_refs}")

    for page in doc:
        # 2. 获取原始二进制内容流
        content = page.read_contents()
        if not content:
            continue
            
        # 3. 按行分割（处理 \r\n 或 \n）
        # 注意：某些紧凑的PDF可能没有换行，这里假设标准格式化流
        lines = content.split(b'\n')
        
        new_lines = []
        skip_next_q = False 
        
        # 4. 遍历每一行指令进行清洗
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            matched_image = False
            
            # 检查当前行是否是目标图片的绘制指令 (例如: /Im1 Do)
            for ref in target_refs:
                # 匹配模式：以 /Name 开头，后面紧跟 Do (忽略中间空格)
                if re.match(rb'^' + ref.encode() + rb'\s+Do\s*$', line):
                    matched_image = True
                    print(f"  [Page {page.number}] 移除图片指令: {line.decode('utf-8', errors='ignore')}")
                    
                    # --- 智能清理逻辑 ---
                    # 通常图片绘制前会有 'q' (save state) 和 'cm' (transform matrix)
                    # 我们需要回溯删除这些关联指令
                    
                    # A. 尝试删除紧跟在后面的 'Q' (restore state) - 虽然少见，但有可能
                    if i + 1 < len(lines) and lines[i+1].strip() == b'Q':
                        # 标记下一行也要跳过
                        # 注意：这里简单处理，实际可能需要更复杂的栈匹配
                        pass 

                    # B. 向前查找并删除关联的 'cm' 和 'q'
                    # 我们向前看最多 5 行，寻找该图片的变换矩阵
                    look_back = 1
                    while look_back <= 5 and (i - look_back) >= 0:
                        prev_line = lines[i - look_back].strip()
                        
                        # 如果是变换矩阵 (6个数字 cm)
                        if re.match(rb'^[\d\.\-\s]+cm$', prev_line):
                            print(f"    -> 同步移除变换矩阵(cm)")
                            # 从新列表中弹出刚才加入的这一行
                            if new_lines and new_lines[-1] == prev_line:
                                new_lines.pop()
                            look_back += 1
                            continue
                            
                        # 如果是保存状态 (q)
                        if prev_line == b'q':
                            print(f"    -> 同步移除状态保存(q)")
                            if new_lines and new_lines[-1] == prev_line:
                                new_lines.pop()
                            break # 找到 q 就停止向前查找
                            
                        # 如果遇到其他指令，说明结构不典型，停止清理以防误删
                        break
                    
                    break # 已匹配到图片，跳出 ref 循环
            
            if not matched_image:
                new_lines.append(lines[i])
            
            i += 1

        # 5. 将清洗后的内容写回页面
        # 必须设置 clean=True 让 MuPDF 重新格式化流，否则可能报错
        new_content = b'\n'.join(new_lines)
        page.set_contents(new_content)

    # 6. 保存文件
    # garbage=4: 深度清理未使用的对象
    # deflate=True: 压缩输出
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    print(f"处理完成！已保存至: {output_path}")

# ================= 使用示例 =================
if __name__ == "__main__":
    # 你的图片名称列表
    my_image_list = ["Im1", "Im2", "Logo_Image"] 
    
    input_pdf = "input.pdf"
    output_pdf = "output_cleaned.pdf"
    
    remove_images_by_names(input_pdf, output_pdf, my_image_list)