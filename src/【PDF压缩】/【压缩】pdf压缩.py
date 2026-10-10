import fitz  # PyMuPDF
from PIL import Image
import io
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import batch_process_file_with_callback


def get_images_total_count(pdf_path):
    doc = fitz.open(pdf_path)
    total_image_count = 0
    
    # 遍历文档中的每一页
    for page_num in range(len(doc)):
        page = doc[page_num]
        # 获取当前页的图片列表，full=True 会获取更完整的图片信息
        image_list = page.get_images(full=True) 
        # 将当前页的图片数量累加到总数中
        total_image_count += len(image_list) 
        
    doc.close()
    return total_image_count


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

def compress_pdf_by_budget(input_path, output_path, target_size_kb=900,total_images = None, overhead_kb = 500, rebuild_pdf = True):
    """
    基于预算分配的 PDF 压缩（每页一张图）
    """
    # 1. 计算单页预算（预留冗余给 PDF 结构）
    safe_target_kb = target_size_kb - overhead_kb



    doc = fitz.open(input_path)
    total_pages = len(doc)

    # 1. 根据模式选择操作对象
    if rebuild_pdf:
        new_doc = fitz.open() 
    else:
        new_doc = doc

    if not total_images:
        total_images = total_pages

    if total_pages == 0:
        print("PDF 没有页面！")
        return

    budget_per_page_kb = safe_target_kb / total_images
    print(f"目标大小: {target_size_kb} KB | 页数: {total_pages} | 图片总数: {total_images} | 每张图预算: {budget_per_page_kb:.2f} KB")

    # 2. 遍历每一页进行压缩
    for page_num in range(total_pages):
        page = doc[page_num]
        image_list = page.get_images(full=True)

        if not image_list:
            print(f"[页 {page_num+1}] 无图")
            raise Exception(f"[页 {page_num+1}] 无图片")

        for img_idx, img_info in enumerate(image_list):
            # 假设每页只有一张主图，取第一个
            xref = img_info[0]

            try:
                # 提取原始图像
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                original_size_kb = len(image_bytes) / 1024

                new_image_bytes = image_bytes

                # 压缩图片
                if original_size_kb > budget_per_page_kb:
                    # 3. 使用鲁班策略压缩当前图片
                    pil_img = Image.open(io.BytesIO(image_bytes))

                    # 生成临时文件用于二分搜索
                    temp_img_path = f"temp_page_{page_num}_{img_idx}.jpg"
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

                if rebuild_pdf:
                    # 再次读取对应页面（此时必定已存在），同页多图复用它
                    
                    if len(new_doc) == page_num:
                        new_doc.new_page(
                            width=page.rect.width, height=page.rect.height
                        )

                    new_page = new_doc[page_num]

                    # 取该图片在原页面中的实际位置矩形，按原位置插入以保留版面
                    rects = page.get_image_rects(xref)
                    if rects:
                        place_rect = rects[0]
                    else:
                        # 取不到位置时退化为铺满整页
                        place_rect = new_page.rect

                    # 将压缩后的图片按原位置插入到对应页面
                    new_page.insert_image(place_rect, stream=image_bytes)
                else:
                    # 4. 只有变小才替换
                    if len(new_image_bytes) < len(image_bytes):
                        # 用高层 API 一次性替换图像流并重建对象字典
                        # （自动同步 Width/Height/ColorSpace/BitsPerComponent/Filter 等键，
                        #   避免手动只改宽高导致字典与实际流不一致）
                        # 注意：xref 之后是关键字参数，必须写成 stream=...

                        # 【旧模式】：在原文档副本上替换
                        target_page = new_doc[page_num]
                        target_page.replace_image(xref, stream=new_image_bytes)

                        # page.replace_image(xref, stream=new_image_bytes)
                        print(f"[页 {page_num+1}_{img_idx}] {original_size_kb:.1f}KB -> {len(new_image_bytes)/1024:.1f}KB (质量:{best_quality})")
                    else:
                        print(f"[页 {page_num+1}_{img_idx}] 压缩后体积未减小，保留原图")

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
    input_path = "/Users/teacher/Desktop/百度网盘下载/2M/扫描"
    target_size_kb = 2 * 1024
    overhead_kb = 200
    rebuild_pdf = False

    if os.path.isfile(input_path):
        output_path = input_path.replace('.pdf', '_压缩.pdf')
        total_images = get_images_total_count(input_path)
        compress_pdf_by_budget(
            input_path=input_path,
            output_path=output_path,
            target_size_kb=target_size_kb,
            overhead_kb = overhead_kb,
            total_images = total_images,
            rebuild_pdf=rebuild_pdf,
        )
    elif os.path.isdir(input_path):
        def callback_func(input_file, output_file):
            total_images = get_images_total_count(input_file)
            compress_pdf_by_budget(
                input_path=input_file,
                output_path=output_file,
                target_size_kb=target_size_kb,
                overhead_kb = overhead_kb,
                total_images = total_images,
                rebuild_pdf=rebuild_pdf,
            )
        input_dir = input_path
        output_dir = f"{input_dir}_压缩"
        batch_process_file_with_callback(
            input_dir=input_dir,
            output_dir=output_dir,
            callback_func=callback_func
        )
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {input_path}")