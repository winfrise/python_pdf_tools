import fitz

def get_shapes_from_page(page):
    """提取页面所有形状的关键特征"""
    shapes = []
    for d in page.get_drawings():
        shapes.append({
            "rect": d["rect"],
            "fill": d.get("fill"),
            "color": d.get("color")
        })
    return shapes

def shapes_match(s1, s2, tol=0.01):
    """判断两个形状是否一致（位置、宽高、颜色）"""
    if s1["fill"] != s2["fill"] or s1["color"] != s2["color"]:
        return False
    r1, r2 = s1["rect"], s2["rect"]
    # 检查边界框是否一致（允许极小误差）
    return (abs(r1.x0 - r2.x0) < tol and abs(r1.y0 - r2.y0) < tol and
            abs(r1.x1 - r2.x1) < tol and abs(r1.y1 - r2.y1) < tol)

def remove_shapes(pdf1_path, pdf2_path, output_path):
    doc1 = fitz.open(pdf1_path)
    doc2 = fitz.open(pdf2_path)
    
    if doc2.page_count == 0:
        print("PDF2 没有页面！")
        return
        
    # 获取 PDF2 第1页的形状作为模板
    template_shapes = get_shapes_from_page(doc2[0])
    
    for page_idx in range(doc1.page_count):
        page = doc1[page_idx]
        page_shapes = get_shapes_from_page(page)
        
        delete_count = 0
        # 遍历当前页形状，如果匹配模板，则添加红批注（用于擦除）
        for shape in page_shapes:
            for template in template_shapes:
                if shapes_match(shape, template):
                    # 添加一个覆盖该形状的红批注
                    # fill_color=(1,1,1) 表示用白色擦除
                    page.add_redact_annot(shape["rect"], fill=(1, 1, 1))
                    delete_count += 1
                    break  # 匹配到一个模板即可，避免重复擦除
        
        # 应用红批注，真正执行擦除操作
        if delete_count > 0:
            page.apply_redactions()
            
        print(f"第 {page_idx + 1} 页删除了 {delete_count} 个形状")
        
    doc1.save(output_path)
    doc1.close()
    doc2.close()
    print(f"处理完成，输出文件: {output_path}")

# 运行测试
remove_shapes("/Users/teacher/Desktop/未命名文件夹 2/2026胡源 高二数学精讲精练.pdf", "/Users/teacher/Desktop/未命名文件夹 2/提取自2026胡源 高二数学精讲精练.pdf", "cleaned_file1.pdf")