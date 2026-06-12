import os
import pymupdf
from utils import parse_page_range

def add_vector_graphics(input_path, output_path, page_range, vector_items):
    try:
        doc = pymupdf.open(input_path)
        target_pages = parse_page_range(page_range, len(doc))
        for page_num in target_pages:
            page = doc[page_num]
            page_rect = page.rect
            print(f"\n正在处理第 {page_num + 1} 页...")

            for item in vector_items:
                vec_path = item["path"]
                vec_width = item.get("width")
                vec_height = item.get("height")
                
                # 解析位置参数
                vec_pos_top = item.get("top")
                vec_pos_left = item.get("left")
                vec_pos_right = item.get("right")
                vec_pos_bottom = item.get("bottom")
            
                
                # 1. 打开矢量图 PDF 并获取其原始尺寸
                vec_doc = pymupdf.open(vec_path)
                vec_page = vec_doc
                vec_orig_w = vec_page.rect.width
                vec_orig_h = vec_page.rect.height
                vec_doc.close()
                
                # 2. 计算实际宽高（如果未指定，则使用原始尺寸）
                vec_final_w = vec_width if vec_width is not None else vec_orig_w
                vec_final_h = vec_height if vec_height is not None else vec_orig_h
                
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
                page.show_pdf_page(target_rect, pymupdf.open(vec_path), 0)
                
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
    image_extensions = ('.pdf')

    success_count = 0
    fail_count = 0

    # 4. 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_dir):
        # 仅处理图片文件
        if filename.lower().endswith(image_extensions):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            # --- 关键：直接调用核心函数，不重复实现逻辑 ---
            status = add_vector_graphics(
                input_path=input_path,
                output_path=output_path,
                vector_items=vector_items
            )
            if status == True:
                success_count = success_count + 1
            else:
                fail_count = fail_count + 1


    print("\n🎉 批量任务完成！，成功数量： {success_count}，失败数量：{fail_count}")


if __name__ == "__main__":
    is_batch = False

    input_path = ""
    output_path = ""
    
    page_range = "1-10000"

    vector_items = [
        {
            "path": "logo.pdf",
            "page_index": 0,
            "top": 50,      # 距离页面顶部 50pt
            "left": 50,     # 距离页面左侧 50pt
            # 宽高不填，自动按照 logo.pdf 原始尺寸插入
        },
        {
            "path": "chart.pdf",
            "page_index": 0,
            "width": 200,   # 强制指定宽度为 200pt
            "height": 150,  # 强制指定高度为 150pt
            "bottom": 30,   # 距离页面底部 30pt
            "right": 30     # 距离页面右侧 30pt
        }
    ]

    if is_batch:
        batch_add_vector_graphics(
            input_dir=input_path,
            output_dir=output_path,
            page_range=page_range,
            vector_tasks=vector_items
        )
    add_vector_graphics(
        input_path=input_path,
        output_path=output_path,
        page_range=page_range,
        vector_items=vector_items
    )