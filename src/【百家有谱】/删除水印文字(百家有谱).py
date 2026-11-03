import fitz
import re

def remove_text_watermark_safe(input_path, output_path):
    doc = fitz.open(input_path)
    
    # 核心思路：只匹配那一段文字绘制指令，不触碰前面的颜色设置和状态栈
    # 匹配类似: BT 1.1 0 0 0.6 93 75.3 Tm <04e5094611b60cf7>Tj ET
    # 我们只把 "<04e5094611b60cf7>Tj" 这一小段替换掉
    text_hex = b"<04e5094611b60cf7>"
    
    for page in doc:
        # 获取所有流
        xrefs = page.get_contents()
        
        for xref in xrefs:
            stream_data = doc.xref_stream(xref)
            
            # 如果流里包含目标文字
            if text_hex in stream_data:
                # 方法：将原始流按行或按段拆解，精准剔除文字展示指令
                # 使用正则查找：(BT 任意内容 <04e5094611b60cf7>Tj 任意内容 ET)
                # 替换为空，这样就完全不会影响前面的 q...Q 和颜色设置
                pattern = re.compile(rb'BT\s+[^E]*?' + text_hex + rb'\s*Tj\s*ET', re.DOTALL)
                
                new_stream, count = pattern.subn(b"", stream_data)
                
                if count > 0:
                    doc.update_stream(xref, new_stream)
                    print(f"第 {page.number + 1} 页：已安全剔除 {count} 个文字水印块")
    
    # 清理并保存
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    print("处理完成！")

if __name__ == "__main__":
    input_path = "/Volumes/西数4T外置/百度网盘默认下载/百家有谱/2222222_已解密_删除百家有谱图标.pdf"
    output_path = input_path.replace('.pdf', '_删除百家有谱文字.pdf')

    remove_text_watermark_safe(
        input_path=input_path,
        output_path = output_path
    )