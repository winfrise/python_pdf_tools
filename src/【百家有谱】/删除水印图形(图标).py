import fitz

def remove_watermark_by_xobject(input_path, output_path):
    doc = fitz.open(input_path)
    
    for page in doc:
        # 1. 获取页面的资源字典（Resources）
        res = doc.xref_get_key(page.xref, "Resources")
        
        # 如果是直接写在页面字典里的（通常是这样）
        if res[0] == "dict":
            # 获取 XObject 字典
            xobj_key = doc.xref_get_key(page.xref, "Resources/XObject")
            if xobj_key[0] == "dict":
                # 解析出 XObject 字典的内容
                # xobj_key[1] 类似于 "<< /Fm2 10 0 R /Fm1 11 0 R >>"
                xobj_dict = xobj_key[1]
                
                # 如果里面包含了 /Fm2
                if "/Fm2" in xobj_dict:
                    # 从字典字符串中删掉 /Fm2 及其对应的 xref
                    # 比如把 "<< /Fm2 10 0 R >>" 变成 "<< >>"
                    import re
                    # 正则替换掉 /Fm2 加上后面的引用
                    new_xobj_dict = re.sub(r'/Fm2\s+\d+\s+\d+\s+R', '', xobj_dict)
                    
                    # 写回页面资源字典
                    doc.xref_set_key(page.xref, "Resources/XObject", new_xobj_dict)
                    print(f"第 {page.number + 1} 页：已移除 XObject 引用 /Fm2")

    doc.save(output_path, garbage=4, deflate=True)
    doc.close()


if __name__ == "__main__":
    input_path = "/Volumes/西数4T外置/百度网盘默认下载/百家有谱/2222222_已解密_删除百家有谱文字.pdf"
    output_path = input_path.replace('.pdf', '_删除百家有谱图标.pdf')

    remove_watermark_by_xobject(
        input_path = input_path, 
        output_path = output_path
    )