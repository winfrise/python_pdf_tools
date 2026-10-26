
import pymupdf

def remove_watermark_from_stream(input_path, output_path):
    doc = pymupdf.open(input_path)
    
    for page in doc:
        # 1. 整理并获取页面唯一的内容流
        page.clean_contents()
        xref = page.get_contents()[0]
        
        # 2. 以可修改的字节数组形式读取流
        cont = bytearray(doc.xref_stream(xref))
        
        # 3. 查找并删除水印代码段
        # WPS 水印通常以 "/Artifact <</Subtype/Watermark...>> BDC" 开始，以 "EMC" 结束
        while True:
            start = cont.find(b"/Artifact")
            if start < 0:
                start = cont.find(b"/Watermark")  # 兼容另一种标记
            
            if start < 0:
                break  # 找不到了，退出循环
            
            # 找到这一段代码的结束位置 "EMC"
            end = cont.find(b"EMC", start)
            if end < 0:
                break
            
            # 将这一段水印代码替换为空（即删除）
            # 注意：需要包含前面的 "q" 和后面的 "EMC" 结束符，以及中间的空格
            # 这里简化处理，直接删除从 start 到 end+3 (EMC 长度) 的内容
            cont[start : end + 3] = b""
        
        # 4. 将修改后的内容流写回页面
        doc.update_stream(xref, cont)
    
    # 5. 保存文件，必须用 ez_save 或 garbage=4 来物理清理垃圾
    doc.ez_save(output_path)
    doc.close()
    print(f"处理完成: {output_path}")


# 使用示例 1：通过水印文本定位
input_path = "/Users/teacher/Downloads/《高等数学(上)》精讲课-配套电子讲义1+2.pdf"
output_path = input_path.replace('.pdf', '_output.pdf')
remove_watermark_from_stream(input_path, output_path)

# 使用示例 2：通过固定区域定位（例如右下角）
# rect = pymupdf.Rect(400, 700, 595, 842)  # 以 A4 页面为例
# remove_wps_watermark("wps_file.pdf", "clean_file.pdf", watermark_rect=rect)