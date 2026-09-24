import fitz
import re

def make_watermark_invisible(pdf_path, out_path, gray="0.949"):
    doc = fitz.open(pdf_path)
    for page in doc:
        xref = page.get_contents()[0]          # 取该页内容流 xref
        stream = doc.xref_stream(xref).decode("latin-1")

        # 1. 定位水印块：从 '0.949 g' 开始，到第一个正文文本块 'BT' 之前
        start = stream.find(f"{gray} g")
        if start == -1:
            continue
        end = stream.find("BT", start)
        if end == -1:
            end = len(stream)
        head, wm, tail = stream[:start], stream[start:end], stream[end:]

        # 2. 只在水印块内，把填充符 f/f* 换成 n（结束路径但不绘制）
        wm = re.sub(r"\bf\*?\b", "n", wm)

        # 3. 写回
        doc.update_stream(xref, (head + wm + tail).encode("latin-1"))

    doc.save(out_path, garbage=4, deflate=True)
    doc.close()

if __name__ == "__main__":
    input_pdf = "/Users/teacher/Desktop/百度网盘下载/去水印-四上阅读/四上阅读理解与答题模板.pdf"
    output_pdf = input_pdf.replace('.pdf', '_output_透明.pdf')
    gray = "0.949"
    make_watermark_invisible(
        pdf_path = input_pdf, 
        out_path = output_pdf,
        gray = gray
    )