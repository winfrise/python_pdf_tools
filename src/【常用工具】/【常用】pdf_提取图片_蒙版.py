import fitz  # PyMuPDF
from PIL import Image, ImageOps
import io
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import parse_page_range, batch_process_file_with_callback

def extract_pdf_images(pdf_path, output_dir, page_range):
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)

    total_pages = len(doc)
    target_pages = parse_page_range(page_range, total_pages)

    for page_num in target_pages:
        page = doc[page_num]
        # 1. 获取当前页面的所有图片对象
        images = page.get_images(full=True)
        
        for img_index, img in enumerate(images):
            xref = img[0]
            
            try:
                # 2. 获取主图信息
                base_image = doc.extract_image(xref)
                if not base_image:
                    continue
                    
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # 获取蒙版引用 ID
                smask_xref = img[1] 
                mask_xref = img[2]   
                
                has_mask = False
                pil_mask = None
                
                # 3. 【防御性逻辑】尝试提取蒙版
                # 优先检查 SMask (smask_xref)，其次检查 Mask (mask_xref)
                target_mask_xref = smask_xref if smask_xref > 0 else mask_xref
                
                if target_mask_xref > 0:
                    try:
                        # 尝试提取蒙版数据，如果 xref 无效，这里会报错进入 except
                        mask_base = doc.extract_image(target_mask_xref)
                        
                        # 双重保险：确保提取到了图像数据
                        if mask_base and "image" in mask_base:
                            mask_bytes = mask_base["image"]
                            pil_mask = Image.open(io.BytesIO(mask_bytes)).convert("L")
                            
                            # 可选：如果合成结果反了（黑白颠倒），取消下面注释
                            # pil_mask = ImageOps.invert(pil_mask)
                            
                            has_mask = True
                            
                    except Exception as mask_err:
                        # 捕获 bad xref 错误，忽略蒙版，按原图处理
                        print(f"  [警告] 第 {page_num+1} 页图 {img_index+1} 蒙版引用无效 (bad xref)，将作为普通图片处理。")
                        has_mask = False

                # 4. 根据是否有有效蒙版执行保存逻辑
                if has_mask and pil_mask:
                    # --- 有蒙版逻辑 ---
                    pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                    pil_img.putalpha(pil_mask)
                    
                    output_path = os.path.join(output_dir, f"page{page_num+1}_img{img_index+1}_masked.png")
                    pil_img.save(output_path, "PNG")
                    print(f"[蒙版合成] {output_path}")
                    
                else:
                    # --- 无蒙版逻辑 (直接保存) ---
                    output_path = os.path.join(output_dir, f"page{page_num+1}_img{img_index+1}.{image_ext}")
                    with open(output_path, "wb") as f:
                        f.write(image_bytes)
                    print(f"[直接保存] {output_path}")

            except Exception as e:
                print(f"[严重错误] 第 {page_num+1} 页第 {img_index+1} 张图处理失败: {e}")

    doc.close()
    print("全部处理完成！")



if __name__ == "__main__":

    INPUT_FILE = "/Users/teacher/Desktop/百度网盘下载/test/未命名文件夹/test.pdf" 
    PAGE_RANGE = "1-1000"

    if os.path.isfile(INPUT_FILE):
        base_name, ext = os.path.splitext(INPUT_FILE)
        output_dir = f"{base_name}_extracted_images"
        extract_pdf_images(
            pdf_path = INPUT_FILE, 
            page_range = PAGE_RANGE, 
            output_dir = output_dir
        )
    elif os.path.isdir(INPUT_FILE):
        def callback_func(input_file, output_file):
            base_name, ext = os.path.splitext(input_file)
            output_dir = f"{base_name}_extracted_images"

            extract_pdf_images(
                pdf_path=input_file,
                page_range = PAGE_RANGE,
                output_dir = output_dir
            )
        input_dir = INPUT_FILE
        batch_process_file_with_callback(
            input_dir=input_dir, 
            output_dir="NO_SAVE",
            callback_func=callback_func    
        )
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {INPUT_FILE}")

