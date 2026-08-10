import os
import pymupdf
from utils import parse_page_range

def add_vector_graphics(input_path, output_path, page_range, vector_items):
    try:
        doc = pymupdf.open(input_path)
        target_pages = parse_page_range(page_range, len(doc))

        if output_path == None:
            base_name, ext = os.path.splitext(input_path)
            output_path = f"{base_name}_output{ext}"

        for page_num in target_pages:
            page = doc[page_num]
            page_rect = page.rect
            print(f"\n正在处理第 {page_num + 1} 页...")

            for item in vector_items:
                vec_path = item["path"]
                vec_width = item.get("width")
                vec_height = item.get("height")
                vec_page_index = item.get("page_index")
                
                # 解析位置参数
                vec_pos_top = item.get("top")
                vec_pos_left = item.get("left")
                vec_pos_right = item.get("right")
                vec_pos_bottom = item.get("bottom")
            
                
                # 1. 打开矢量图 PDF 并获取其原始尺寸
                vec_doc = pymupdf.open(vec_path)
                vec_page = vec_doc.load_page(vec_page_index)
                vec_orig_w = vec_page.rect.width
                vec_orig_h = vec_page.rect.height


                # 默认比例为 1 (即不缩放)
                scale_ratio = 1.0 

                if vec_width is not None:
                    # 如果指定了宽度，计算宽度的缩放比例
                    scale_ratio = vec_width / vec_orig_w
                elif vec_height is not None:
                    # 如果没指定宽度但指定了高度，计算高度的缩放比例
                    scale_ratio = vec_height / vec_orig_h

                # 3. 根据比例计算最终的宽高
                # 这样即使只传了一个参数，另一个也会自动按比例变化
                vec_final_w = vec_orig_w * scale_ratio
                vec_final_h = vec_orig_h * scale_ratio
            
                
                # 3. 根据 top/left/right/bottom 计算目标矩形 (x0, y0, x1, y1)
                # 默认从页面左上角 (0,0) 开始
                vec_x0, vec_y0 = 0, 0 
                
                # 处理水平位置 (left / right)
                if vec_pos_left is not None:
                    vec_x0 = vec_pos_left
                elif vec_pos_right is not None:
                    # right 是从矢量图右侧到页面右侧的距离
                    vec_x0 = page_rect.width - vec_pos_right - vec_final_w
                    
                # 处理垂直位置 (top / bottom)
                if vec_pos_top is not None:
                    vec_y0 = vec_pos_top
                elif vec_pos_bottom is not None:
                    # bottom 是从矢量图底部到页面底部的距离
                    vec_y0 = page_rect.height - vec_pos_bottom - vec_final_h
                    
                # 构建目标矩形区域
                target_rect = pymupdf.Rect(
                    vec_x0, 
                    vec_y0, 
                    vec_x0 + vec_final_w, 
                    vec_y0 + vec_final_h
                )
                
                # 4. 将矢量图 PDF 的第一页嵌入到目标区域
                page.show_pdf_page(target_rect, vec_doc, vec_page_index, overlay=True)
                vec_doc.close()
                
        doc.save(output_path)
        doc.close()
        print(f"处理完成，已保存至: {output_path}")
        return True
    except Exception as e:
        print(f"❌ 处理失败 : {e}")
        return False


def batch_add_vector_graphics(input_dir, output_dir, page_range, vector_items):
    if not os.path.exists(input_dir):
        print(f"错误：输入文件夹不存在 -> {input_dir}")
        return

    # 2. 如果输出目录不存在，则自动创建
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"已自动创建输出文件夹：{output_dir}")

    # 3. 定义支持处理的图片后缀


    success_count = 0
    fail_count = 0

    # 4. 遍历输入文件夹中的所有文件
    file_extensions = ('.pdf')
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            # --- 过滤 macOS 自动生成的 ._ 开头文件 ---
            if file.startswith('._'):
                continue

            if file.lower().endswith(file_extensions):
                input_path = os.path.join(root, file)
                relative_input_path = os.path.relpath(input_path, input_dir)
                output_path = os.path.join(output_dir, relative_input_path)
                
                # 确保输出目录存在
                output_pdf_dir = os.path.dirname(output_path)
                os.makedirs(output_pdf_dir, exist_ok=True)

                # --- 关键：直接调用核心函数，不重复实现逻辑 ---
                status = add_vector_graphics(
                    input_path=input_path,
                    output_path=output_path,
                    page_range=page_range,
                    vector_items=vector_items
                )
                if status == True:
                    success_count = success_count + 1
                else:
                    fail_count = fail_count + 1


    print(f"\n🎉 批量任务完成！，成功文件数量： {success_count}，失败文件数量：{fail_count}")


if __name__ == "__main__":
    input_path = "/Users/teacher/Desktop/图纸修改/3#浅圆仓、4#提升发放塔、5#提升发放塔_2_建施01_建筑设计说明、建筑设计防火设计专篇、节能设计专篇、防水设计专篇、选用标准图集、工程做法表、门窗表、门窗分格示意图 第2版1481KB-副本.pdf"
    output_path = None
    
    page_range = "1-10000"

    vector_items = [
        {
            "path": "//Users/teacher/Desktop/图纸修改/mask.pdf",
            "page_index": 0,
            "width": 200,
            "top": 0,      # 距离页面顶部 50pt
            "left": 0,     # 距离页面左侧 50pt
            # 宽高不填，自动按照 logo.pdf 原始尺寸插入
        },
        # {
        #     "path": "/Users/teacher/Desktop/图纸修改/mask.pdf",
        #     "page_index": 0,
        #     "width": 800,   # 强制指定宽度为 200pt
        #     # "height": 150,  # 强制指定高度为 150pt
        #     "bottom": 0,   # 距离页面底部 30pt
        #     "right": 0     # 距离页面右侧 30pt
        # }
    ]

    if os.path.isfile(input_path):
        add_vector_graphics(
            input_path=input_path,
            output_path=output_path,
            page_range=page_range,
            vector_items=vector_items
        )
    elif os.path.isdir(input_path):
        batch_add_vector_graphics(
            input_dir=input_path,
            output_dir=output_path,
            page_range=page_range,
            vector_items=vector_items
        )
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {input_path}")