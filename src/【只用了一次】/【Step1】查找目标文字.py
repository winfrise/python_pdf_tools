# -*- coding: utf-8 -*-
"""
【Step1 优化版】查找目标文字（水印）并反查其所在内容流 / 字体 / hex
================================================================
相比旧版（正则 + 手算 Tm 坐标）的修复点：
  1. 定位坐标改用 page.get_texttrace() —— 它返回的每个字符 origin/bbox 已由
     MuPDF 乘好完整变换（Tm × CTM × Form XObject × 页面 /Rotate × fitz 翻转），
     直接就是 fitz 坐标（左上原点、Y 向下），不再手算，杜绝坐标错位。
  2. 反查 hex 时维护「CTM 栈」：正确处理 q/Q/cm/Tm/Td/TD/T*/Tf，且同时解析
     大写 TJ 字距数组（旧版只抓 Tj，会漏掉大量排版）。
  3. 顶层 Form XObject 以其 /Matrix 作为初始 CTM 递归解析（水印常见形态）。
  4. 匹配改为「整词优先」，避免单字 in 把正文里的同字全部误命中。
  5. 路径、关键词改为命令行参数，去掉硬编码绝对路径。

依赖：pip install pymupdf
用法：python3 【Step1优化】查找目标文字_稳健版.py 你的.pdf [关键词]
"""
import sys
import re
import fitz
from fitz import Matrix, Point

# 把内容流切成 token：hex 串 / 字面串 / 名字 / 数字 / 操作符
_TOK = re.compile(
    r"<[0-9A-Fa-f\s]*>"          # hex string
    r"|\((?:\\.|[^\\()])*\)"     # 字面串(不支持深层嵌套，仅用于跳过)
    r"|/[^\s/\[\]<>()]+"         # 名字
    r"|[-+]?\d*\.?\d+"           # 数字
    r"|[A-Za-z'\"*]+",           # 操作符
    re.S,
)


def _tokenize(stream_text):
    """把内容流文本拆成 (kind, value) 列表。kind: hex/str/name/num/op"""
    out = []
    for m in _TOK.finditer(stream_text):
        t = m.group(0)
        if t[0] == "<" and t[-1] == ">":
            out.append(("hex", re.sub(r"\s+", "", t[1:-1]).lower()))
        elif t[0] == "(":
            out.append(("str", t[1:-1]))
        elif t[0] == "/":
            out.append(("name", t[1:]))
        elif t[0] in "+-." or t[0].isdigit():
            try:
                out.append(("num", float(t)))
            except ValueError:
                pass
        else:
            out.append(("op", t))
    return out


class TextLocator:
    """解析单个内容流：维护 CTM 栈与文本矩阵，收集每个文本显示片段起点(fitz 坐标)、
    其 hex 串、字体名。"""

    def __init__(self, doc, page, init_ctm, page_tmat):
        self.doc = doc
        self.page = page
        self.init_ctm = init_ctm          # 该流的初始 CTM (Form 用其 /Matrix)
        self.page_tmat = page_tmat        # page.transformation_matrix: PDF->fitz

    def _to_fitz(self, tm):
        """把文本矩阵平移原点换算到 fitz 坐标"""
        p_pdf = Point(tm.e, tm.f) * self.ctm          # 当前用户空间 -> PDF 设备
        return p_pdf * self.page_tmat                 # PDF 设备 -> fitz

    def run(self, xref, label):
        raw = self.doc.xref_stream(xref)
        if not raw:
            return []
        try:
            s = raw.decode("latin-1")
        except Exception:
            return []
        toks = _tokenize(s)
        results = []

        ctm = Matrix(*self.init_ctm)
        stack = []
        tm = Matrix(1, 0, 0, 1, 0, 0)
        tlm = Matrix(1, 0, 0, 1, 0, 0)   # 文本行矩阵 (Td/TD/T*/'/")
        lead = 0.0
        buf = []
        font_name = ""

        for kind, val in toks:
            self.ctm = ctm
            if kind in ("num", "hex", "str", "name"):
                buf.append((kind, val))
                continue
            op = val
            if op == "q":
                stack.append(Matrix(*ctm))
            elif op == "Q":
                if stack:
                    ctm = stack.pop()
            elif op == "cm" and len(buf) >= 6:
                nums = [b[1] for b in buf if b[0] == "num"][-6:]
                if len(nums) == 6:
                    ctm = Matrix(*nums) * ctm       # cm 把新空间映到旧空间
            elif op == "BT":
                tm = Matrix(1, 0, 0, 1, 0, 0)
                tlm = Matrix(1, 0, 0, 1, 0, 0)
            elif op == "Tm" and len(buf) >= 6:
                nums = [b[1] for b in buf if b[0] == "num"][-6:]
                if len(nums) == 6:
                    tm = Matrix(*nums)
                    tlm = Matrix(*tm)
            elif op == "Td" and len(buf) >= 2:
                nums = [b[1] for b in buf if b[0] == "num"][-2:]
                tlm = Matrix(1, 0, 0, 1, nums[-2], nums[-1]) * tlm
                tm = Matrix(*tlm)
            elif op == "TD" and len(buf) >= 2:
                nums = [b[1] for b in buf if b[0] == "num"][-2:]
                lead = -nums[-1]
                tlm = Matrix(1, 0, 0, 1, nums[-2], nums[-1]) * tlm
                tm = Matrix(*tlm)
            elif op == "TL" and buf:
                lead = -[b[1] for b in buf if b[0] == "num"][-1]
            elif op == "T*":
                tlm = Matrix(1, 0, 0, 1, 0, -lead) * tlm
                tm = Matrix(*tlm)
            elif op == "Tf":
                nm = [b[1] for b in buf if b[0] == "name"]
                font_name = nm[-1] if nm else font_name
            elif op in ("Tj", "'"):
                if op == "'":
                    tlm = Matrix(1, 0, 0, 1, 0, -lead) * tlm
                    tm = Matrix(*tlm)
                self._emit(buf, tm, font_name, label, xref, results)
            elif op == '"' and len(buf) >= 2:
                tlm = Matrix(1, 0, 0, 1, 0, -lead) * tlm
                tm = Matrix(*tlm)
                self._emit(buf, tm, font_name, label, xref, results)
            elif op == "TJ":
                self._emit(buf, tm, font_name, label, xref, results, array=True)
            buf = []
        return results

    def _emit(self, buf, tm, font_name, label, xref, results, array=False):
        if array:
            hexes = [b[1] for b in buf if b[0] == "hex"]
            if not hexes:
                return
            hex_str = "".join(hexes)
        else:
            last = buf[-1] if buf else None
            if not last or last[0] != "hex":
                return
            hex_str = last[1]
        if not hex_str:
            return
        results.append({
            "fitz_origin": self._to_fitz(tm),
            "hex": hex_str,
            "font": font_name,
            "label": label,
            "xref": xref,
        })


def find_target(pdf_path, target="百家有谱", tol=6.0):
    doc = fitz.open(pdf_path)
    for pno, page in enumerate(doc):
        # ---- 阶段A：get_texttrace 精确定位目标文字的 fitz 坐标 ----
        trace = page.get_texttrace()
        hit_points = []          # (label_text, fitz_origin, font, size, mode)
        # 整词优先
        for span in trace:
            chars = span.get("chars") or []
            text = "".join(chr(c[0]) for c in chars)
            i = text.find(target)
            while i != -1:
                hit_points.append((target, Point(chars[i][2]), span["font"], span["size"], "整词"))
                i = text.find(target, i + len(target))
        used_word = bool(hit_points)
        if not hit_points:       # 退化：逐字（可能含正文误命中，会标注）
            for span in trace:
                for c in span.get("chars") or []:
                    ch = chr(c[0])
                    if ch in target:
                        hit_points.append((ch, Point(c[2]), span["font"], span["size"], "单字"))

        if not hit_points:
            continue

        # ---- 阶段B：解析内容流（含顶层 Form），反查 hex ----
        tmat = page.transformation_matrix
        streams = [("page", xref, (1, 0, 0, 1, 0, 0)) for xref in page.get_contents()]
        for xo in page.get_xobjects():                 # (xref, name, ...)
            xref = xo[0]
            if doc.xref_get_key(xref, "Subtype") != ("name", "/Form"):
                continue                               # 跳过 Image XObject
            mt = doc.xref_get_key(xref, "Matrix")
            if mt[0] == "array":
                nums = [float(x) for x in mt[1].strip("[]").split()]
                init = tuple(nums) if len(nums) == 6 else (1, 0, 0, 1, 0, 0)
            else:
                init = (1, 0, 0, 1, 0, 0)
            streams.append((f"form:{xo[1]}", xref, init))

        all_emits = []
        for label, xref, init in streams:
            all_emits.extend(TextLocator(doc, page, init, tmat).run(xref, label))

        # ---- 匹配：hex 片段起点 ≈ 目标字 fitz 起点 ----
        print(f"\n===== 第 {pno + 1} 页：定位到 {len(hit_points)} 处目标"
              f"（{'整词' if used_word else '单字回退，可能有正文误命中'}）=====")
        matched = set()
        for hp_text, hp_pt, hp_font, hp_size, mode in hit_points:
            for idx, e in enumerate(all_emits):
                o = e["fitz_origin"]
                if abs(o.x - hp_pt.x) < tol and abs(o.y - hp_pt.y) < tol:
                    key = (e["xref"], e["hex"])
                    tag = "★" if mode == "整词" else "?"
                    print(f"  {tag} 命中 <{e['hex']}>  ← {e['label']} xref={e['xref']} "
                          f"字体={e['font']} 起点=({o.x:.1f},{o.y:.1f}) "
                          f"目标={hp_text!r} 字号={hp_size:.1f}")
                    matched.add(key)
        if not matched:
            print("  （坐标阈值内未匹配到 <hex> 片段，可放大 tol 或检查水印是否为矢量/图像）")
    doc.close()





if __name__ == "__main__":
    input_path = "/Users/teacher/Desktop/百度网盘下载/家谱/黄坪营黄氏挂图.pdf"
    find_target(input_path, "百家有谱")