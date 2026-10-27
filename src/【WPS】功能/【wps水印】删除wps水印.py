import pymupdf
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import parse_page_range, batch_process_file_with_callback

def remove_watermark_from_stream(input_path, output_path):
    doc = pymupdf.open(input_path)

    total_found = 0      # 总共找到的水印段数
    total_deleted = 0    # 成功删除的水印段数
    total_failed = 0     # 找到但删除失败的段数

    for page in doc:
        # 1. 整理并获取页面唯一的内容流
        page.clean_contents()
        contents = page.get_contents()
        if not contents:
            continue
        xref = contents[0]

        # 2. 以可修改的字节数组形式读取流
        cont = bytearray(doc.xref_stream(xref))

        # 3. 查找并删除水印代码段
        # WPS 水印通常以 "/Artifact <</Subtype/Watermark...>> BDC" 开始，以 "EMC" 结束
        while True:
            # 优先按 /Artifact 定位
            start = cont.find(b"/Artifact")
            tag = "Artifact"
            if start < 0:
                start = cont.find(b"/Watermark")  # 兼容另一种标记
                tag = "Watermark"

            if start < 0:
                break  # 找不到了，退出循环

            total_found += 1
            print(f"[页 {page.number + 1}] 找到水印标记: {tag} (位置 {start})")

            # 找到这一段代码的结束位置 "EMC"
            end = cont.find(b"EMC", start)
            if end < 0:
                total_failed += 1
                print(f"[页 {page.number + 1}] 警告: 找到 {tag} 但未找到结束符 EMC，跳过")
                break

            # 将这一段水印代码替换为空（即删除）
            cont[start: end + 3] = b""
            total_deleted += 1
            print(f"[页 {page.number + 1}] 已删除 {tag} 水印段 ({start} ~ {end + 3})")

        # 4. 将修改后的内容流写回页面
        doc.update_stream(xref, cont)

    # 5. 保存文件，必须用 ez_save 或 garbage=4 来物理清理垃圾
    doc.ez_save(output_path)
    doc.close()

    print(f"处理完成: {output_path}")
    print(f"统计: 找到 {total_found} 段, 删除 {total_deleted} 段, 失败 {total_failed} 段")

    # 返回状态码
    if total_found == 0:
        return 0        # 整篇文档未找到任何水印标记
    if total_deleted > 0 and total_failed == 0:
        return 1        # 全部删除成功
    if total_deleted > 0 and total_failed > 0:
        return 1        # 有成功删除即视为成功（部分失败已在日志中提示）
    return 2            # 找到了但全部删除失败



if __name__ == "__main__":

    INPUT_FILE = "/Volumes/西数4T外置/绵阳有色金属制造公司test/001"


    if os.path.isfile(INPUT_FILE):
        input_path = INPUT_FILE
        output_path = input_path.replace('.pdf', '_output.pdf')
        ret = remove_watermark_from_stream(input_path, output_path)
        print(f"返回值: {ret}")
    elif os.path.isdir(INPUT_FILE):
        stats = {
            "success": 0,   # 返回值 1：删除成功
            "failed": 0,    # 返回值 2：找到但删除失败
            "not_found": 0  # 返回值 0：未找到水印
        }

        def callback_func(input_file, output_file):
            ret = remove_watermark_from_stream(input_file, output_file)
            # 根据返回值进行分类统计
            if ret == 1:
                stats["success"] += 1
            elif ret == 2:
                stats["failed"] += 1
            elif ret == 0:
                stats["not_found"] += 1


        input_dir = INPUT_FILE
        output_dir = f"{input_dir}_output"
        batch_process_file_with_callback(
            input_dir=input_dir, 
            output_dir=output_dir,
            callback_func=callback_func    
        )

        # 在处理完毕后，打印汇总信息
        print("=" * 30)
        print("📊 批量处理统计结果：")
        print(f"✅ 成功删除水印: {stats['success']} 个")
        print(f"❌ 删除失败: {stats['failed']} 个")
        print(f"⚠️ 未找到水印: {stats['not_found']} 个")
        print("=" * 30)
    else:
        print(f"【错误】：输入路径既不是文件也不是目录 -> {INPUT_FILE}")