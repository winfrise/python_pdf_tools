# -*- coding: utf-8 -*-
"""
PDF 倾斜文本去除（内容流级，两种模式）

用法
    python3 PDF倾斜文本去除_内容流.py 输入.pdf 输出.pdf [transparent|remove]
    python3 PDF倾斜文本去除_内容流.py 导出的内容流.txt 输出.txt transparent      # 先在流片段上验证

原理
    PDF 中的倾斜/旋转文本通过 cm（变换矩阵）操作符实现旋转变换，
    随后用 BT...ET 包裹文本绘制指令。
    旋转矩阵的特征：a = cos(θ), b = sin(θ), c = -sin(θ), d = cos(θ)
    即满足 a == d 且 b == -c，且 b/c 不全为 0（排除纯平移/缩放）。
    因此判别式：找到 BT...ET 文本块，向前追溯最近的 cm 操作符，
    检查其矩阵是否包含旋转分量，若是则判定为倾斜文本并丢弃。

两种模式
    transparent(默认): 只把文本块内的落墨符(Tj/TJ/'/"等)改成 n
                       文本路径照常构造但一个像素不落 -> 视觉透明
    remove           : 整段删除 BT...ET 文本块 -> 文本对象物理消失

注意
    transparent 是"隐形"不是"删除"：字形数据仍留在文件里；
    要彻底删除请用 remove。两种模式改完都要肉眼核对正文有无被误删。
"""

import os
import re
import sys

# ---------------- PDF 操作符词表（用于切分粘连在一起的 token） ----------------
OPERATORS = {
    b'q', b'Q', b'w', b'J', b'j', b'M', b'd', b'ri', b'i', b'gs',
    b'm', b'l', b'c', b'v', b'y', b'h', b're', b'cl', b'W', b'W*', b'n',
    b'S', b's', b'f', b'F', b'f*', b'B', b'B*', b'b', b'b*', b'sh',
    b'cs', b'CS', b'sc', b'scn', b'SC', b'SCN', b'g', b'G', b'rg', b'RG',
    b'k', b'K', b'cm', b'Tc', b'Tw', b'Tz', b'TL', b'Tf', b'Tr', b'Ts',
    b'Td', b'TD', b'Tm', b'T*', b'BT', b'ET', b'Tj', b'TJ', b"'", b'"',
    b'Do', b'MP', b'DP', b'BMC', b'BDC', b'EMC', b'BX', b'EX', b'd0', b'd1',
}
MAX_OP_LEN = max(len(o) for o in OPERATORS) + 1

# 透明模式需要改成 n 的"落墨"操作符（文本相关的）
TEXT_PAINT_OPS = {b'Tj', b'TJ', b"'", b'"'}

TOK_RE = re.compile(
    rb"""(?P<ws>\s+)
      | (?P<num>[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?)
      | (?P<name>/[^\s/<>()\[\]{}%]+)
      | (?P<hex><(?:[0-9A-Fa-f\s]*)>)
      | (?P<arr>\[|\])
      | (?P<str>\((?:\\.|[^\\()])*\))
      | (?P<op>[A-Za-z*'"`]+)
    """,
    re.X,
)


def _split_operator_run(run):
    """把粘连的字母串(如 ref / cfQQ / lhW / scnq)按最长匹配切成合法操作符。"""
    out, i, n = [], 0, len(run)
    while i < n:
        hit = None
        for L in range(min(n - i, MAX_OP_LEN), 1, -1):
            cand = run[i:i + L]
            if cand in OPERATORS:
                hit = cand
                break
        if hit is None:
            hit = run[i:i + 1]
        out.append(hit)
        i += len(hit)
    return out


def tokenize(raw):
    """内容流 -> token 列表(bytes)。兼容 token 之间没有空格的导出流片段。"""
    toks, pos, length = [], 0, len(raw)
    while pos < length:
        m = TOK_RE.match(raw, pos)
        if not m:
            pos += 1
            continue
        pos = m.end()
        if m.lastgroup == 'ws':
            continue
        if m.lastgroup == 'op':
            toks.extend(_split_operator_run(m.group()))
        else:
            toks.append(m.group())
    return toks


def _is_rotation_matrix(nums):
    """检查6个数字是否构成含旋转的变换矩阵。
    
    PDF cm 矩阵: a b c d e f
    对应变换矩阵:
        | a  c  e |
        | b  d  f |
        | 0  0  1 |
    
    纯旋转(可能含均匀缩放)的特征:
        a = s*cos(θ), b = s*sin(θ), c = -s*sin(θ), d = s*cos(θ)
        即 a == d 且 b == -c，且 b 不全为0（排除纯平移/无旋转）
    """
    if len(nums) < 6:
        return False
    # 解析6个浮点数
    try:
        vals = [float(x) for x in nums[:6]]
    except (ValueError, TypeError):
        return False
    a, b, c, d, e, f = vals
    # 排除纯平移/无旋转（b 和 c 都为0意味着没有旋转分量）
    if abs(b) < 0.01 and abs(c) < 0.01:
        return False
    # 旋转矩阵特征检查（允许浮点误差）
    if abs(a - d) > 0.05:
        return False
    if abs(b + c) > 0.05:
        return False
    return True


def _find_slanted_text_blocks(toks):
    """查找所有被 cm 旋转变换的 BT...ET 文本块。
    
    返回: (区间列表[(BT下标, ET下标)], 待处理下标集合)
    """
    spans = []
    q_stack = []  # q/Q 栈，用于处理图形状态嵌套
    
    i = 0
    while i < len(toks):
        t = toks[i]
        
        if t == b'q':
            q_stack.append(i)
        elif t == b'Q':
            if q_stack:
                q_stack.pop()
        elif t == b'BT':
            # 向前查找最近的 cm 操作符（不跨越 Q/q 边界）
            cm_idx = None
            cm_nums = None
            for back in range(i - 1, max(-1, i - 50), -1):
                tb = toks[back]
                if tb == b'Q':
                    break  # 跨过了 Q，不能进入上层 q 块
                if tb == b'q':
                    break  # 进入了新的 q 块（嵌套）
                if tb == b'cm':
                    # 取 cm 前面的6个数字
                    if back >= 6:
                        candidate_nums = toks[back - 6:back]
                        # 验证这6个token确实都是数字
                        if all(
                            tok.startswith(b'-') or tok.startswith(b'+') or tok[0:1].isdigit() or tok.startswith(b'.')
                            for tok in candidate_nums
                        ):
                            cm_nums = candidate_nums
                            cm_idx = back
                    break  # 只取最近的 cm
            
            # 检查 cm 矩阵是否包含旋转
            if cm_nums and _is_rotation_matrix(cm_nums):
                # 向后查找配对的 ET（不跨越 Q 边界）
                et_idx = None
                nested_bt = 0
                for fwd in range(i + 1, len(toks)):
                    tf = toks[fwd]
                    if tf == b'Q':
                        break  # 跨过了 Q，文本块被截断
                    if tf == b'BT':
                        nested_bt += 1  # 嵌套的 BT
                    if tf == b'ET':
                        if nested_bt > 0:
                            nested_bt -= 1  # 匹配嵌套的 BT
                        else:
                            et_idx = fwd
                            break
                if et_idx is not None:
                    spans.append((i, et_idx))
        i += 1
    
    # 构建待处理下标集合
    drop = set()
    for bt_idx, et_idx in spans:
        drop.update(range(bt_idx, et_idx + 1))
    return spans, drop


def process_stream(raw, mode='transparent'):
    """处理单页内容流，返回 (新流 bytes 或 None, 统计 dict)。"""
    toks = tokenize(raw)
    spans, drop = _find_slanted_text_blocks(toks)
    st = {'blocks': len(spans), 'paint_changed': 0, 'paint_kept_body': 0,
          'q_open': 0, 'q_close': 0}
    if not spans:
        return None, st

    out = []
    for i, t in enumerate(toks):
        if i in drop:
            if mode == 'transparent':
                # 透明模式：把文本落墨操作符改成 n
                if t in TEXT_PAINT_OPS:
                    out.append(b'n')
                    st['paint_changed'] += 1
                else:
                    out.append(t)  # 其他token（字体设置等）原样保留
            # remove 模式：直接跳过（不写入out），整段删除
            continue
        if t in TEXT_PAINT_OPS:
            st['paint_kept_body'] += 1
        out.append(t)

    if mode == 'remove':
        st['paint_changed'] = sum(1 for i in drop if toks[i] in TEXT_PAINT_OPS)

    new = b' '.join(out) + b'\n'
    st['q_open'] = new.count(b' q ') + new.count(b' q\n')
    st['q_close'] = new.count(b' Q ') + new.count(b' Q\n')
    return new, st


def run_pdf(pdf_in, pdf_out, mode):
    import fitz
    doc = fitz.open(pdf_in)
    total = 0
    for pno, page in enumerate(doc, 1):
        for xref in page.get_contents():
            raw = doc.xref_stream(xref)
            new, st = process_stream(raw, mode)
            if new is None:
                continue
            doc.update_stream(xref, new, compress=True)
            total += st['blocks']
            print('[第%d页] 命中倾斜文本块 %d 个 | %s %d 处 | 正文落墨保留 %d 处'
                  % (pno, st['blocks'],
                     'Tj->n' if mode == 'transparent' else '整段删除文本',
                     st['paint_changed'], st['paint_kept_body']))
    doc.save(pdf_out, garbage=4, deflate=True, clean=True)
    doc.close()
    print('完成：模式=%s，共处理倾斜文本块 %d 个 -> %s' % (mode, total, pdf_out))


def run_stream_file(txt_in, txt_out, mode):
    """直接处理导出的内容流片段，便于先在片段上验证再上真实 PDF。"""
    raw = open(txt_in, 'rb').read()
    new, st = process_stream(raw, mode)
    if new is None:
        print('%s：未命中倾斜文本块，未做改动' % txt_in)
        return
    open(txt_out, 'wb').write(new)
    print('[%s] 命中倾斜文本块 %d 个 | %s %d 处 | 正文落墨保留 %d 处 | q=%d Q=%d -> %s'
          % (os.path.basename(txt_in), st['blocks'],
             'Tj->n' if mode == 'transparent' else '整段删除文本',
             st['paint_changed'], st['paint_kept_body'],
             st['q_open'], st['q_close'], txt_out))


if __name__ == '__main__':

    src = "/Volumes/西数4T外置/百度网盘默认下载/国家电网有限公司“四不两直”安全督查工作手册（2026年9月） (1).pdf"
    dst = "/Volumes/西数4T外置/百度网盘默认下载/国家电网有限公司“四不两直”安全督查工作手册（2026年9月） (1)333.pdf"
    mode = "transparent" # 'mode 只能是 transparent 或 remove'
    if src.lower().endswith('.pdf'):
        run_pdf(src, dst, mode)
    else:
        run_stream_file(src, dst, mode)