import fitz


def parse_range(range_str, total=None):
    """
    解析页码字符串，支持 "1, 3-5, 9-10, 12" 格式。
    :param page_str: 用户输入的页码字符串
    :param total_pages: PDF 总页数 (用于边界检查)，默认为 None 表示不限制上限
    :return: 0-based 的页码列表 
    """
    nums = set()

    parts = str(range_str).split(",")
    for part in parts:
        part = part.strip()
        if not part:
            continue

        if "-" in part:
            try:
                # 处理 "3-5" 这种区间
                start, end = map(int, part.split("-"))
                
                # 基础校验：防止 start > end 导致无效区间
                if start > end:
                    print(f"警告：空区间 '{part}' (起始大于结束)，已跳过。")
                    continue
                
                # 转换为 0-based 索引
                start_0 = start - 1
                end_0 = end  # range是左闭右开，所以直接用 end
                
                # 如果没有提供总数，则仅做非负校验；如果提供了，则严格校验上限
                if total is None:
                    # 确保起点合法，终点在循环中自然处理
                    safe_start = max(0, start_0)
                    for i in range(safe_start, end_0):
                        nums.add(i)
                else:
                    # 原有的带边界检查的逻辑
                    for i in range(start_0, end_0):
                        if 0 <= i < total:
                            nums.add(i)
                            
            except ValueError:
                print(f"警告：无法解析区间 '{part}'，已跳过。")
        else:
            try:
                # 处理单页 "1"
                p_0 = int(part) - 1
                
                if total is None:
                    # 无总页数时，仅过滤掉非法的负数索引
                    if p_0 >= 0:
                        nums.add(p_0)
                else:
                    # 原有逻辑：确保在合法范围内
                    if 0 <= p_0 < total:
                        nums.add(p_0)
                        
            except ValueError:
                print(f"警告：无法解析页码 '{part}'，已跳过。")

    return sorted(list(nums))

def check_signature_type(input_file):
    doc = fitz.open(input_file)

    # 1. 检查是否为“表单控件 (Widget)”类型的签名
    print(f"------------1.【检查表单控件签名】---------")
    for page in doc:
        widgets = list(page.widgets())
        if widgets:
            print(f"第 {page.number + 1} 页包含表单控件 (Widgets):")
            for widget in widgets:
                print(f"  - 字段名: {widget.field_name}, 类型: {widget.field_type_string}, 区域: {widget.rect}")

    # 2. 检查是否为普通“注释 (Annotation)”类型的签名
    print(f"------------2.【检查注释签名】---------")
    for page in doc:
        annots = list(page.annots())
        if annots:
            print(f"第 {page.number + 1} 页包含【注释类型签名】 (Annotations):")
            for index, annot in enumerate(annots):
                print(f"  ｜-{index + 1},[发现注释类型签名]: {annot.type}")


    # 3. 检查底层是否有“数字电子签章 (Digital Signature)”
    # 获取文档的加密和签名状态
    if doc.is_encrypted:
        print("该文档已加密。")

    # 遍历文档的所有对象寻找 /Sig 字典（数字签名的核心特征）
    print(f"------------3.【检查数字签名】---------")
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
        print("* 未检测到明显的表单签名或数字证书签名，可能只是作为普通图像插入的印章。")

    doc.close()

# 删除表单类型的签名
def remove_form_signatures(doc):
    
    for page in doc:
        # 获取页面上的所有 Widget（表单字段）
        widgets = list(page.widgets())
        for widget in reversed(widgets):
            if widget.field_type == fitz.PDF_WIDGET_TYPE_SIGNATURE: # 推荐使用常量代替数字 9
                print(f"正在删除: {widget.field_name}")
                page.delete_widget(widget)   

# 删除数字签名
def remove_digital_signatures(doc):

    
    # 获取 PDF 中对象的总数
    xref_length = doc.xref_length()
    
    # 遍历所有的交叉引用对象
    for xref in range(1, xref_length):
        try:
            # 获取对象的底层字典字符串
            obj_str = doc.xref_object(xref)
            
            # 检查该对象是否为数字签名类型 (/Type /Sig)
            if "/Type /Sig" in obj_str:
                # 将该对象替换为空字典，从而彻底抹除签名数据
                doc.update_object(xref, "<<>>")
                
        except Exception as e:
            # 忽略无效或无法读取的对象
            continue


def remove_annot_signatures_by_index(doc):
    """
    pdf_path: 输入文件路径
    output_path: 输出文件路径
    signatures_index_range: 字符串格式，如 "1", "1,3", "2-5", "1,3-6"
                 (注：这里默认用户习惯从 1 开始计数)
    """

    signatures_index_range = "1-10"

    # 1. 解析用户输入的索引，转换为一个包含所有目标数字的集合 (Set)
    # 假设用户输入的是人类习惯的 1-based 索引 (第1个，第2个...)
    target_indices = parse_range(signatures_index_range, len(doc))

    print(f"===============================")
    print(f"准备删除的目标索引 (1-based): {sorted(target_indices)}")

    # 3. 遍历每一页
    for page_num in range(len(doc)):
        page = doc[page_num]
        print(f"- 正在处理第 {page_num} 页")
        # 2.页面计数器，用于追踪当前是第几个签名
        page_find_count = 0
        page_removed_count = 0

        # 删除【表单类型】的签名


        # 删除【注释类型】的签名
        annots = list(page.annots())
        for annot in annots:
            # 检查是否为 Screen 类型 (Type 22) 且标题包含 xlsign
            is_target_type = (annot.type[0] == 22 and 'xlsign' in annot.info.get('title', '').lower())

            if is_target_type:
                page_find_count += 1  # 计数器加 1
                # 如果当前计数在目标集合中
                if (page_find_count - 1) in target_indices:
                    print(f"  |-正在删除第 {page_find_count} 个签名")
                    page.delete_annot(annot)
                    page_removed_count += 1
                    if(page_removed_count >= len(target_indices)):
                        break


def remove_signatures(input_path, output_path):
    doc = fitz.open(input_path)        

    # 删除【注释类型】的签名
    remove_annot_signatures_by_index(doc) 

    # 删除【表单类型】的签名 
    remove_form_signatures(doc) 

    # 删除数字签名
    remove_digital_signatures(doc)

    # 保存文档，garbage=4 会进行最高级别的垃圾回收，彻底清除未引用的签名数据
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()

if __name__ == "__main__":
    # 使用示例
    input_file = "/Users/teacher/Downloads/百度网盘下载/水/支付宝交易明细(20260101-20260612).pdf"
    output_file = "/Users/teacher/Downloads/百度网盘下载/水/支付宝交易明细(20260101-20260612)333.pdf"

    is_check = True
    if is_check:
        # 检查签名类型
        check_signature_type(input_file)

    remove_signatures(input_file, output_file)
