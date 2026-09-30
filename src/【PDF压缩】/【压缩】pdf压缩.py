import fitz  # PyMuPDF
from PIL import Image
import io
import os

def find_best_quality(img, temp_path, target_size_kb):
    """
    鲁班核心：二分搜索最佳质量参数
    """
    left, right = 1, 95
    best_q = 1
    while left <= right:
        mid = (left + right) // 2
        try:
            img.save(temp_path, quality=mid, optimize=True)
            size = os.path.getsize(temp_path) / 1024
            if size <= target_size_kb:
                best_q = mid
                left = mid + 1
            else:
                right = mid - 1
        except Exception:
            break
    return best_q

def compress_pdf_by_budget(input_path, output_path, target_size_kb=900, overhead_kb = 500, rebuild_pdf = True):
    """
    基于预算分配的 PDF 压缩（每页一张图）
    """
    # 1. 计算单页预算（预留冗余给 PDF 结构）
    safe_target_kb = target_size_kb - overhead_kb


    # 1. 根据模式选择操作对象
    if rebuild_pdf:
        new_doc = fitz.open()  # 创建全新的空文档
    else:
        # 必须复制一份，避免破坏原文件用于下一次二分尝试
        new_doc = fitz.open(input_path) 


    doc = fitz.open(input_path)
    total_pages = len(doc)

    if total_pages == 0:
        print("PDF 没有页面！")
        return

    budget_per_page_kb = safe_target_kb / total_pages
    print(f"目标大小: {target_size_kb} KB | 总页数: {total_pages} | 每页预算: {budget_per_page_kb:.2f} KB")

    # 2. 遍历每一页进行压缩
    for page_num in range(total_pages):
        page = doc[page_num]
        image_list = page.get_images(full=True)

        if not image_list:
            print(f"[页 {page_num+1}] 无图片，跳过")
            continue

        # 假设每页只有一张主图，取第一个
        xref = image_list[0][0]

        try:
            # 提取原始图像
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            original_size_kb = len(image_bytes) / 1024

            # 如果原图已经小于预算，无需压缩
            if original_size_kb <= budget_per_page_kb:
                print(f"[页 {page_num+1}] 原图 {original_size_kb:.1f}KB 已达标，跳过")
                continue

            # 3. 使用鲁班策略压缩当前图片
            pil_img = Image.open(io.BytesIO(image_bytes))

            # 生成临时文件用于二分搜索
            temp_img_path = f"temp_page_{page_num}.jpg"
            best_quality = find_best_quality(pil_img, temp_img_path, budget_per_page_kb)

            # 如果最低质量依然超标，强制缩小尺寸（每次缩小 20%）
            min_dimension = 100
            while True:
                pil_img.save(temp_img_path, quality=best_quality, optimize=True)
                current_size_kb = os.path.getsize(temp_img_path) / 1024

                if current_size_kb <= budget_per_page_kb or min(pil_img.size) <= min_dimension:
                    break

                # 强制缩放
                scale_factor = 0.8
                new_size = (int(pil_img.width * scale_factor), int(pil_img.height * scale_factor))
                pil_img = pil_img.resize(new_size, Image.LANCZOS)

            # 读取压缩后的字节流
            with open(temp_img_path, "rb") as f:
                new_image_bytes = f.read()

            # 清理临时文件
            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)

            # 4. 防呆替换：只有变小才替换
            if len(new_image_bytes) < len(image_bytes):
                # 用高层 API 一次性替换图像流并重建对象字典
                # （自动同步 Width/Height/ColorSpace/BitsPerComponent/Filter 等键，
                #   避免手动只改宽高导致字典与实际流不一致）
                # 注意：xref 之后是关键字参数，必须写成 stream=...
           
                if rebuild_pdf:
                    # 获取图片原始尺寸
                    img_w = base_image["width"]
                    img_h = base_image["height"]

                    # 【新模式】：计算适应图片大小的页面矩形
                    # 直接使用图片宽高作为页面大小，去除多余白边
                    img_rect = fitz.Rect(0, 0, img_w, img_h)
                    new_page = new_doc.new_page(width=img_w, height=img_h)
                    
                    # 将压缩后的图片插入到新页面，填满整个页面
                    new_page.insert_image(img_rect, stream=new_image_bytes)
                else:
                    # 【旧模式】：在原文档副本上替换
                    target_page = new_doc[page_num]
                    target_page.replace_image(xref, stream=new_image_bytes)

                # page.replace_image(xref, stream=new_image_bytes)
                print(f"[页 {page_num+1}] {original_size_kb:.1f}KB -> {len(new_image_bytes)/1024:.1f}KB (质量:{best_quality})")
            else:
                print(f"[页 {page_num+1}] 压缩后体积未减小，保留原图")

        except Exception as e:
            print(f"[页 {page_num+1}] 处理失败: {e}")
            continue

    # 5. 保存最终 PDF，彻底清理冗余
    new_doc.save(output_path, garbage=4, deflate=True, clean=True)
    new_doc.close()
    doc.close()

    final_size = os.path.getsize(output_path) / 1024
    print(f"\n压缩完成! 最终大小: {final_size:.1f} KB (目标: {target_size_kb} KB)")
    if final_size > target_size_kb:
        print("[警告] 最终体积略微超标，可能是 PDF 内部结构占用过大导致")


# ================= 使用示例 =================
if __name__ == "__main__":
    input_path = "/Users/teacher/Desktop/未命名文件夹 2/001/未命名文件夹/义乌市北遴电子商务商行欧盟授权代表续费（产品组）协议2026.10.20-2027.10.19.pdf"
    output_path = input_path.replace('.pdf', '_压缩.pdf')
    target_size_kb = 5 * 1024
    overhead_kb = 500
    rebuild_pdf = True
    compress_pdf_by_budget(
        input_path=input_path,
        output_path=output_path,
        target_size_kb=target_size_kb,
        overhead_kb = overhead_kb,
        rebuild_pdf=rebuild_pdf,
    )