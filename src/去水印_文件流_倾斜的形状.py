# -*- coding: utf-8 -*-
"""
PDF 水印去除（内容流级，两种模式）

用法
    python3 PDF水印去除_内容流.py 输入.pdf 输出.pdf [transparent|remove]
    python3 PDF水印去除_内容流.py 导出的内容流.txt 输出.txt transparent      # 先在流片段上验证

原理
    正文绘制是轴对齐矩形(re) + 字形轮廓路径，绝不会用斜向折线裁剪；
    斜置水印的铁证是  4 点多边形 -> h -> W -> n   (clip 进斜带后丢弃路径)，
    随后紧跟 近白填充(/CS0 cs 0.075 0 0.051 0 scn) 与 浅灰叠层(0 0 0 0.349 scn) 交替平铺。
    因此判别式：q...Q 块内出现 "W n" / "W* n"，且 W 的前驱是 h(折线闭合) 而不是 re(矩形)。

两种模式
    transparent(默认): 只把水印块内的落墨符 f/F/f*/B/B* 改成 n (end path, do not paint)
                       路径照常构造但一个像素不落 -> 视觉透明，且不会像"改成背景同色"
                       那样在斜带上铺不透明色块，把途经的正文一起盖成白条。
    remove           : 整段删除该 q...W n...Q 块 -> 水印对象物理消失，防再提取、减体积。
                       保存带 garbage=4，顺带回收水印用到的死字体 / ExtGState 对象。

注意
    transparent 是"隐形"不是"删除"：水印字形仍留在文件里，可被提取或改回；
    要别人也捞不回来请用 remove。两种模式改完都要肉眼核对正文有无被误删。
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

# 透明模式需要改成 n 的"落墨"操作符
PAINT_OPS = {b'f', b'F', b'f*', b'B', b'B*', b'b', b'b*'}

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


def _has_slanted_clip(body):
    """块内是否存在 'W n' 且前驱是 h(斜向折线裁剪) —— 水印判据。"""
    for idx, t in enumerate(body):
        if t not in (b'W', b'W*'):
            continue
        if body[idx + 1:idx + 2] != [b'n']:
            continue
        for back in range(idx - 1, max(-1, idx - 12), -1):
            tb = body[back]
            if tb == b'h':
                return True                     # 折线闭合后裁剪 = 斜带水印
            if tb in (b're', b'q', b'Q', b'W', b'W*'):
                break                           # 矩形裁剪或越界，判为非水印
        if b're' not in body[:idx]:
            return True                         # 全程无 re，只有斜线路径 + W n
    return False


def _find_clip_blocks(toks):
    """返回 (需处理的区间列表[(q下标, 配套Q下标)], 待处理下标集合)。"""
    spans, stack, drop = [], [], set()
    for i, t in enumerate(toks):
        if t == b'q':
            stack.append(i)
        elif t == b'Q':
            if not stack:
                continue
            s = stack.pop()
            if _has_slanted_clip(toks[s + 1:i]):
                spans.append((s, i))
    for s, e in spans:
        drop.update(range(s, e + 1))
    return spans, drop


def process_stream(raw, mode='transparent'):
    """处理单页内容流，返回 (新流 bytes 或 None, 统计 dict)。"""
    toks = tokenize(raw)
    spans, drop = _find_clip_blocks(toks)
    st = {'blocks': len(spans), 'paint_changed': 0, 'paint_kept_body': 0,
          'q_open': 0, 'q_close': 0}
    if not spans:
        return None, st

    out = []
    for i, t in enumerate(toks):
        if i in drop:
            if t in PAINT_OPS:
                if mode == 'transparent':
                    out.append(b'n')
                    st['paint_changed'] += 1
                else:                            # remove: 整块丢掉
                    st['paint_changed'] += 1
            elif mode == 'transparent':
                out.append(t)                    # 裁剪/颜色/cm 原样保留
            continue
        if t in PAINT_OPS:
            st['paint_kept_body'] += 1
        out.append(t)

    if mode == 'remove':
        st['paint_changed'] = sum(1 for i in drop if toks[i] in PAINT_OPS)

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
            print('[第%d页] 命中水印块 %d 个 | %s %d 处 | 正文落墨保留 %d 处'
                  % (pno, st['blocks'],
                     'f->n' if mode == 'transparent' else '整段删除落墨',
                     st['paint_changed'], st['paint_kept_body']))
    doc.save(pdf_out, garbage=4, deflate=True, clean=True)
    doc.close()
    print('完成：模式=%s，共处理水印块 %d 个 -> %s' % (mode, total, pdf_out))


def run_stream_file(txt_in, txt_out, mode):
    """直接处理导出的内容流片段，便于先在片段上验证再上真实 PDF。"""
    raw = open(txt_in, 'rb').read()
    new, st = process_stream(raw, mode)
    if new is None:
        print('%s：未命中含 W n 斜裁剪的水印块，未做改动' % txt_in)
        return
    open(txt_out, 'wb').write(new)
    print('[%s] 命中水印块 %d 个 | %s %d 处 | 正文落墨保留 %d 处 | q=%d Q=%d -> %s'
          % (os.path.basename(txt_in), st['blocks'],
             'f->n' if mode == 'transparent' else '整段删除落墨',
             st['paint_changed'], st['paint_kept_body'],
             st['q_open'], st['q_close'], txt_out))


if __name__ == '__main__':

    src = "/Volumes/西数4T外置/百度网盘默认下载/国家电网有限公司“四不两直”安全督查工作手册（2026年9月） (1).pdf"
    dst = "/Volumes/西数4T外置/百度网盘默认下载/国家电网有限公司“四不两直”安全督查工作手册（2026年9月） (1)222.pdf"
    mode = "transparent" # 'mode 只能是 transparent 或 remove'
    if src.lower().endswith('.pdf'):
        run_pdf(src, dst, mode)
    else:
        run_stream_file(src, dst, mode)