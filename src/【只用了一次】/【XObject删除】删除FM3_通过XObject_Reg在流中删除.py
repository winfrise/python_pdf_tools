import fitz
import re
import sys

def remove_fm3(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    removed = 0

    for pno, page in enumerate(doc):
        for xref in page.get_contents():
            raw = doc.xref_stream(xref)
            if not raw:
                continue
            text = raw.decode("latin-1")

            # 查找目标，并替换为空字符串
            new_text, n = re.subn(r"/Fm3\s+Do\b", "", text)
            if n:
                doc.update_stream(xref, new_text.encode("latin-1"))
                removed += n
                print(f"page {pno+1} xref {xref}: removed {n} Fm3 Do")

    doc.save(output_pdf, garbage=4, deflate=True)
    doc.close()
    print(f"total removed: {removed}")

if __name__ == "__main__":
    input_path = "/Users/teacher/Desktop/百度网盘下载/001/黄坪营黄氏挂图_副本.pdf"
    output_path = input_path.replace('.pdf', '_去水印.pdf')
    remove_fm3(input_path, output_path)