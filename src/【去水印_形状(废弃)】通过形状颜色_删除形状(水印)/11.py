import fitz  # PyMuPDF

def hide_by_whitening(doc):
    # 1. 修正白色指令：使用灰度 1 (纯白) 或 RGB 1 1 1
    # 注意：必须确保替换前后的字节长度或格式兼容，但在 update_stream 中通常直接替换即可
    WHITE = b"1 scn " 
    
    # 2. 增加容错性：尝试匹配不同空格数量的情况
    # PDF生成器有时会在数字间加多个空格
    TARGETS = [
        b"0.4 0.4 0.4 scn",
        b"0.4  0.4  0.4 scn",  # 双空格
        b"0.400000 0.400000 0.400000 scn" # 某些生成器会保留多位小数
    ]

    total = 0
    for page in doc:
        for xref in page.get_contents():
            data = doc.xref_stream(xref)
            if not data:
                continue
            
            modified = False
            new_data = data
            
            for target in TARGETS:
                hit = new_data.count(target)
                if hit > 0:
                    print(f"[XREF {xref}] 找到目标 {target}，共 {hit} 处")
                    # 执行替换
                    new_data = new_data.replace(target, WHITE)
                    total += hit
                    modified = True
            
            if modified:
                # 更新流
                doc.update_stream(xref, new_data)

    print(f"处理完成，共替换 {total} 处颜色")
    return total
if __name__ == "__main__":
    src = "/Users/teacher/Desktop/pdf_command/pdf解密/output/001/01.pdf"
    out = src.replace('.pdf', '_output.pdf')
    transparent = None
    doc = fitz.open(src)
    if transparent:
        print(f"准备设置透明")
        n = hide_by_whitening(doc)
        print(f"[方案B-透明] 已将 {n} 个 ExtGState 的不透明度置 0")
    else:
        print(f"准备填充白色")
        n = hide_by_whitening(doc)
        print(f"[方案A-改白] 已替换 {n} 处该颜色填充指令")
        
    doc.save(out, garbage=4, deflate=True, clean=True)
    doc.close()
    print(f"已保存: {out}")