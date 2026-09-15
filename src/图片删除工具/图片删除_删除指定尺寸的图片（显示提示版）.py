import fitz  # PyMuPDF
import os
import sys
from collections import Counter

# 安全导入 utils 模块，未安装时给出友好提示而非直接崩溃
try:
    from utils import batch_process_file_with_callback
except ImportError:
    batch_process_file_with_callback = None


def _parse_size_string(ts):
    """解析尺寸字符串，如 '1002x263' -> (1002, 263)"""
    ts = str(ts).strip()
    if 'x' not in ts.lower():
        raise ValueError(f"无效的尺寸格式 '{ts}'，应为 '宽x高' 格式（如 '1002x263'）")
    parts = ts.split('x')
    if len(parts) != 2:
        raise ValueError(f"无效的尺寸格式 '{ts}'，应为 '宽x高' 格式")
    try:
        w = int(parts[0].strip())
        h = int(parts[1].strip())
    except ValueError:
        raise ValueError(f"尺寸值必须为整数: '{ts}'")
    if w <= 0 or h <= 0:
        raise ValueError(f"宽高必须为正整数: '{ts}'")
    return w, h


def remove_pdf_images(pdf_path, target_sizes, output_path=None):
    """
    删除 PDF 中指定尺寸的图片。

    参数:
        pdf_path: PDF 文件路径
        target_sizes: 目标尺寸列表，如 ['1002x263', '500x300']
        output_path: 输出文件路径（可选）
    """
    if output_path is None:
        pdf_dir = os.path.dirname(pdf_path)
        pdf_name = os.path.basename(pdf_path).replace('.pdf', '')
        output_path = os.path.join(pdf_dir, f"{pdf_name}_processed.pdf")

    # 预解析目标尺寸，非法格式提前报错而非运行中崩溃
    target_pairs = []
    for ts in target_sizes:
        try:
            w, h = _parse_size_string(ts)
            target_pairs.append((w, h))
        except ValueError as e:
            print(f"警告: {e}")

    if not target_pairs:
        print("错误: 没有有效的目标尺寸，请检查 target_sizes 参数。")
        return

    doc = fitz.open(pdf_path)

    try:
        # 用于统计的字典
        size_count = Counter()
        image_details = []
        seen_xrefs = set()

        print("正在扫描 PDF 中的图片信息...\n")

        # 1. 遍历所有页面，提取图片信息并统计
        for page_num in range(len(doc)):
            print(f"正在统计第{page_num + 1}页")
            page = doc[page_num]
            image_list = page.get_images(full=True)

            for img in image_list:
                xref = img[0]

                # 去重：同一 xref 可能被多次引用，只处理一次
                if xref in seen_xrefs:
                    continue
                seen_xrefs.add(xref)

                # extract_image 可能因特殊颜色空间/损坏数据而失败，捕获异常跳过
                try:
                    img_info = doc.extract_image(xref)
                except Exception as e:
                    print(f"警告: 无法提取页面 {page_num} 中 xref={xref} 的图片: {e}")
                    continue

                w, h = img_info['width'], img_info['height']
                ratio = round(w / h, 2)  # 宽高比保留两位小数

                size_count[(w, h)] += 1
                image_details.append({
                    'page': page_num,
                    'xref': xref,
                    'width': w,
                    'height': h,
                    'ratio': ratio
                })

        # 2. 打印统计结果
        print(f"统计完成！该 PDF 共有 {len(image_details)} 张图片（去重后）。")

        # 3. 删除功能 - 支持多尺寸批量删除
        removed = 0
        removed_counts = Counter()

        # 遍历记录，删除匹配的图片
        for img in image_details:
            for w, h in target_pairs:
                if img['width'] == w and img['height'] == h:
                    try:
                        page = doc[img['page']]
                        page.delete_image(img['xref'])
                        removed += 1
                        removed_counts[(w, h)] += 1
                    except Exception as e:
                        print(f"警告: 删除页面 {img['page']} 中 xref={img['xref']} 的图片失败: {e}")
                    break  # 已匹配到目标尺寸，跳过后续判断

        # 打印删除结果（使用 Counter，简洁高效）
        for (w, h), cnt in removed_counts.items():
            print(f"已删除尺寸为 {w}x{h} 的图片共 {cnt} 张。")
        print(f"合计删除图片: {removed} 张")

        try:
            print('正在保存文件...')
            doc.save(output_path, garbage=4, deflate=True)
            print('文件保存完成...')
        except Exception as e:
            print(f"保存失败: {e}")
            print(f"尝试修复模式...")
            doc.save(output_path, incremental=True)  # 增量保存，保留原始结构

    except Exception as e:
        print(f"处理出错: {e}")
    finally:
        # 确保无论是否异常都关闭文档，防止资源泄漏
        doc.close()


# ============================================================
# 直接传参调用区域 —— 修改以下变量即可运行
# ============================================================

# --- 模式一：处理单个 PDF 文件 ---
MODE = "single"  # "single" 或 "batch"

# 单个文件模式下的配置
PDF_PATH = "/Users/teacher/Desktop/未命名文件夹 2/PDF合并.pdf"           # PDF 文件路径（支持相对路径和绝对路径）
TARGET_SIZES = ["1002x263", "1002x262"]         # 要删除的图片尺寸列表，格式为 "宽x高"
OUTPUT_PATH = None                  # 输出文件路径（None 表示自动生成：原文件名_processed.pdf）

# 批量模式下的配置（当 MODE = "batch" 时生效）
BATCH_DIR = "./pdfs"              # 待处理的 PDF 目录路径
BATCH_OUTPUT_DIR = "./pdfs_output" # 输出目录路径


if __name__ == "__main__":
    if MODE == "single":
        # 单文件模式：直接传参调用函数
        remove_pdf_images(
            pdf_path=PDF_PATH,
            target_sizes=TARGET_SIZES,
            output_path=OUTPUT_PATH
        )
    elif MODE == "batch":
        # 批量模式：遍历目录中所有 PDF 文件
        if batch_process_file_with_callback is None:
            print("错误: 批量处理模式需要 utils 模块，请确保 utils.py 在可导入路径中。")
            sys.exit(1)

        # 注意：批量模式下需先取消上面 BATCH_DIR 和 BATCH_OUTPUT_DIR 的注释，并设置正确路径
        input_dir = BATCH_DIR
        output_dir = BATCH_OUTPUT_DIR

        def callback_func(input_file, output_file):
            remove_pdf_images(
                pdf_path=input_file,
                output_path=output_file,
                target_sizes=TARGET_SIZES
            )

        batch_process_file_with_callback(
            input_dir=input_dir,
            output_dir=output_dir,
            callback_func=callback_func
        )
    else:
        print(f"错误: 未知模式 '{MODE}'，请设置为 'single' 或 'batch'。")