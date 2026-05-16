import fitz  # PyMuPDF
import os
from collections import defaultdict

def analyze_and_remove_pdf_images(pdf_path, output_path=None):
    if output_path is None:
        pdf_dir = os.path.dirname(pdf_path)
        pdf_name = os.path.basename(pdf_path).replace('.pdf', '')
        output_path = os.path.join(pdf_dir, f"{pdf_name}_processed.pdf")

    doc = fitz.open(pdf_path)
    
    # 用于统计的字典
    size_count = defaultdict(int)      # 记录尺寸 (宽, 高) 出现的次数
    ratio_count = defaultdict(int)     # 记录宽高比 出现的次数
    image_details = []                 # 记录每张图片的详细信息 (页码, xref, 宽, 高, 宽高比)

    print("🔍 正在扫描 PDF 中的图片信息...\n")

    # 1. 遍历所有页面，提取图片信息并统计
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)
        
        for img in image_list:
            xref = img[0]
            # 提取图片的原始像素尺寸
            img_info = doc.extract_image(xref)
            w, h = img_info['width'], img_info['height']
            ratio = round(w / h, 2)  # 宽高比保留两位小数
            
            size_count[(w, h)] += 1
            ratio_count[ratio] += 1
            image_details.append({
                'page': page_num,
                'xref': xref,
                'width': w,
                'height': h,
                'ratio': ratio
            })

    # 2. 打印统计结果
    print(f"📊 统计完成！该 PDF 共有 {len(image_details)} 张图片。")
    
    print("\n--- 📏 相同尺寸 (宽x高) 统计 ---")
    # key=lambda x: x[1] 表示按照“数量”倒序排列，这样数量最多的排在最前面
    for size, count in sorted(size_count.items(), key=lambda x: x[1], reverse=True):
        # size 是一个元组 (width, height)，所以需要分别取值
        print(f"尺寸 {size[0]}x{size[1]} 像素: 共 {count} 张")

    print("\n--- ⚖️ 相同宽高比 统计 ---")
    # 按照数量倒序排列
    for ratio, count in sorted(ratio_count.items(), key=lambda x: x[1], reverse=True):
        print(f"宽高比 {ratio}: 共 {count} 张")

    # 3. 交互式删除功能
    while True:
        print("\n" + "="*40)
        print("请选择操作：")
        print("1. 按尺寸删除图片 (例如输入: 500x300)")
        print("2. 按宽高比删除图片 (例如输入: 1.5)")
        print("3. 保存并退出")
        print("4. 不保存直接退出")
        choice = input("请输入你的选择 (1-4): ").strip()

        if choice == '1':
            target_size = input("请输入要删除的尺寸 (格式如 500x300): ").strip()
            try:
                w, h = map(int, target_size.split('x'))
                removed = 0
                # 遍历记录，删除匹配的图片
                for img in image_details:
                    if img['width'] == w and img['height'] == h:
                        page = doc[img['page']]
                        page.delete_image(img['xref'])
                        removed += 1
                print(f"✅ 已删除尺寸为 {w}x{h} 的图片共 {removed} 张。")
            except:
                print("❌ 输入格式错误，请确保格式为 宽x高 (如 500x300)")

        elif choice == '2':
            target_ratio = input("请输入要删除的宽高比 (例如 1.5): ").strip()
            try:
                ratio_val = float(target_ratio)
                ratio_val = round(ratio_val, 2)
                removed = 0
                for img in image_details:
                    if img['ratio'] == ratio_val:
                        page = doc[img['page']]
                        page.delete_image(img['xref'])
                        removed += 1
                print(f"✅ 已删除宽高比为 {ratio_val} 的图片共 {removed} 张。")
            except:
                print("❌ 输入格式错误，请输入数字。")

        elif choice == '3':
            # 开启垃圾回收(garbage=4)以彻底减小文件体积
            doc.save(output_path, garbage=4, deflate=True)
            print(f"💾 文件已保存至: {output_path}")
            doc.close()
            break
        elif choice == '4':
            doc.close()
            print("已退出，未保存任何修改。")
            break
        else:
            print("❌ 无效的选择，请重新输入。")

if __name__ == "__main__":
    # 替换为你的 PDF 路径
    pdf_file = "/Users/teacher/Desktop/2026年4月/test/2023 FUSEN   CATALOG.pdf"
    analyze_and_remove_pdf_images(pdf_file)