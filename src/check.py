import fitz

def check_signature_type(input_file):
    doc = fitz.open("/Users/teacher/Desktop/未命名文件夹/消防建施-副本/消防建施-副本_1.pdf")

    # 1. 检查是否为“表单控件 (Widget)”类型的签名
    for page in doc:
        widgets = list(page.widgets())
        if widgets:
            print(f"第 {page.number + 1} 页包含表单控件 (Widgets):")
            for widget in widgets:
                print(f"  - 字段名: {widget.field_name}, 类型: {widget.field_type_string}, 区域: {widget.rect}")

    # 2. 检查是否为普通“注释 (Annotation)”类型的签名
    for page in doc:
        annots = list(page.annots())
        if annots:
            print(f"第 {page.number + 1} 页包含注释 (Annotations):")
            for annot in annots:
                print(f"  - 注释类型: {annot.type}, 信息: {annot.info}")

    # 3. 检查底层是否有“数字电子签章 (Digital Signature)”
    # 获取文档的加密和签名状态
    if doc.is_encrypted:
        print("该文档已加密。")

    # 遍历文档的所有对象寻找 /Sig 字典（数字签名的核心特征）
    signatures_found = False
    for xref in range(1, doc.xref_length()):
        try:
            obj_str = doc.xref_object(xref)
            if "/Type /Sig" in obj_str or "/SubFilter" in obj_str:
                signatures_found = True
                print(f"发现数字签名对象 (XREF: {xref})!")
                print(obj_str[:300])  # 打印前300个字符查看结构
                break
        except Exception as e:
            continue

    if not signatures_found and not any([list(page.widgets()) for page in doc]):
        print("未检测到明显的表单签名或数字证书签名，可能只是作为普通图像插入的印章。")

    doc.close()


def remove_all_screen_annotations(input_file, output_file):
    doc = fitz.open(input_file)
    removed_count = 0

    for page in doc:
        # 获取页面所有注释
        annots = list(page.annots())
        for annot in annots:
            # 检查是否为 Screen 类型 (类型代码 22)
            if annot.type[0] == 22:
                # 可选：进一步确认 title 是否包含 'xlsign' 以防误删其他控件
                if 'xlsign' in annot.info.get('title', '').lower():
                    page.delete_annot(annot)
                    removed_count += 1

    doc.save(output_file, garbage=4, deflate=True)
    doc.close()
    print(f"处理完成，共删除了 {removed_count} 个签名控件。")


def remove_signatures_by_index(pdf_path, output_path, index_range):
    """
    pdf_path: 输入文件路径
    output_path: 输出文件路径
    index_range: 字符串格式，如 "1", "1,3", "2-5", "1,3-6"
                 (注：这里默认用户习惯从 1 开始计数)
    """
    doc = fitz.open(pdf_path)

    # 1. 解析用户输入的索引，转换为一个包含所有目标数字的集合 (Set)
    # 假设用户输入的是人类习惯的 1-based 索引 (第1个，第2个...)
    target_indices = set()
    try:
        parts = index_range.split(',')
        for part in parts:
            if '-' in part:
                start, end = map(int, part.split('-'))
                # range是左闭右开，所以 end+1；同时存入集合
                target_indices.update(range(start, end + 1))
            else:
                target_indices.add(int(part))
    except ValueError:
        print("索引格式错误，请输入如 '1', '2-5' 或 '1,3-5' 的格式")
        return

    # 2. 全局计数器，用于追踪当前是第几个签名
    global_count = 0
    removed_count = 0

    print(f"准备删除的目标索引 (1-based): {sorted(target_indices)}")

    # 3. 遍历每一页
    for page in doc:
        # 获取页面所有注释的列表
        annots = list(page.annots())

        # 4. 遍历该页面的每一个注释
        # 注意：必须倒序遍历或使用 list 副本，防止删除时改变列表长度导致报错
        # 但在这里我们只是读取信息，真正的删除操作在下面判断后进行
        for annot in annots:
            # 检查是否为 Screen 类型 (Type 22) 且标题包含 xlsign
            is_target_type = (annot.type[0] == 22 and 'xlsign' in annot.info.get('title', '').lower())

            if is_target_type:
                global_count += 1  # 计数器加 1

                # 如果当前计数在目标集合中
                if global_count in target_indices:
                    print(f"正在删除全局第 {global_count} 个签名 (位于第 {page.number+1} 页)...")
                    page.delete_annot(annot)
                    removed_count += 1

    # 5. 保存结果
    if removed_count > 0:
        doc.save(output_path, garbage=4, deflate=True)
        print(f"\n完成！共删除了 {removed_count} 个签名。")
        print(f"文件已保存至: {output_path}")
    else:
        print("\n未找到匹配的签名进行删除。")

    doc.close()
# 使用示例
input_file = "/Users/teacher/Desktop/未命名文件夹/消防建施-副本/消防建施-副本_1.pdf"
output_file = "/Users/teacher/Desktop/未命名文件夹/消防建施-副本/消防建施-副本_1xxxx.pdf"
# check_signature_type(input_file)
# remove_all_screen_annotations(input_file, output_file)

index_range="1-2" # 示例1,2-3,9
remove_signatures_by_index(input_file, output_file, index_range)