import fitz
import re

def detect_watermark_location(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[0] # 先探测第一页
    
    print("="*50)
    print(f"正在探测文件: {pdf_path}")
    print("="*50)

    # --- 1. 检查是否有独立的 Form XObject 图层 ---
    print("\n[1] 检查独立图层 (XObject):")
    xobjects = page.get_xobjects()
    if not xobjects:
        print("  -> 未发现独立图层。")
    for xobj in xobjects:
        xref = xobj[0]
        name = xobj[1]
        # 查看这个图层的定义内容
        obj_str = doc.xref_object(xref)
        print(f"  -> 发现图层: 名称={name}, xref={xref}")
        print(f"     内容特征: {obj_str[:100]}...")

    # --- 2. 检查页面流中的透明度 (ExtGState) 和 旋转矩阵 ---
    print("\n[2] 检查页面流中的透明度与旋转矩阵:")
    xref = page.get_contents()[0]
    stream_bytes = doc.xref_stream(xref)
    stream_text = stream_bytes.decode('latin-1', errors='ignore')
    
    # 搜索水印常见的透明度指令 (gs)
    gs_matches = re.findall(r'/([A-Za-z0-9]+)\s+gs', stream_text)
    if gs_matches:
        print(f"  -> 发现透明状态引用: {set(gs_matches)}")
    else:
        print("  -> 未发现 gs 透明度指令。")

    # 搜索旋转矩阵 (cm)，水印通常是非 0 的旋转值
    cm_matches = re.findall(r'([\d\.-]+)\s+([\d\.-]+)\s+([\d\.-]+)\s+([\d\.-]+)\s+([\d\.-]+)\s+([\d\.-]+)\s+cm', stream_text)
    rotated_cms = []
    for cm in cm_matches:
        a, b, c, d, e, f = map(float, cm)
        # 如果 a 或 b 不为 0，且不是 1 或 -1，说明有旋转
        if (a != 1.0 and a != -1.0) or (b != 0.0):
            rotated_cms.append(cm)
    if rotated_cms:
        print(f"  -> 发现疑似旋转矩阵 (cm): {rotated_cms[:3]} ... (共{len(rotated_cms)}个)")
    else:
        print("  -> 未发现旋转矩阵。")

    # --- 3. 检查是否有重复的文本绘制指令 ---
    print("\n[3] 检查重复文本 (BT...ET):")
    bt_blocks = re.findall(r'BT(.*?)ET', stream_text, re.DOTALL)
    print(f"  -> 页面共有 {len(bt_blocks)} 个 BT...ET 文本块。")
    
    # 寻找特定的文本特征，比如带有 2 Tr 或者 特定字体的块
    watermark_blocks = []
    for block in bt_blocks:
        # 寻找带有半透明或非常规字号的块
        if 'gs' in block or re.search(r'[34]\d(\.\d+)?\s+Tf', block): # 字号很大，或者有gs
            watermark_blocks.append(block.strip()[:80])
            
    if watermark_blocks:
        print(f"  -> 发现疑似水印文本块特征: \n{watermark_blocks[:2]}")

if __name__ == "__main__":
    # 请把这里换成你的真实 PDF 路径
    detect_watermark_location("/Volumes/西数4T外置/百度网盘默认下载/百家有谱/2222222_已解密.pdf")