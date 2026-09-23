# -*- coding: utf-8 -*-
"""
基于 PyMuPDF 的"图层法"(Optional Content Groups, OCG) 删除/隐藏水印

原理
----
很多用专业编辑器(Acrobat / PitStop / 某些批量加水印工具)生成的水印，
会被放进一个独立的"可选内容图层"(OCG)。该图层在 PDF 目录里登记于
/OCProperties/OCGs, 页面上用两种方式挂接它:
  1) 内容流里用标带内容包起来:  /标签 << /OC <</OCGS N 0 R>> >> BDC ... EMC
  2) 整块画在一个带 /OC 的 Form XObject 里

因此"图层法"有两种强度的处理:
  hide   模式(默认, 最安全): 把目标图层置为"不可见"(从 /D/ON 移除、加入 /D/OFF)。
         图层仍在文件里, 但不再渲染, 正文毫发无损。绝大多数场景够用。
  remove 模式(更彻底): 在 hide 的基础上, 再尝试从页面内容流中删除引用
         该 OCG 的 BDC..EMC 标带块, 并清空引用该 OCG 的 Form XObject 内容,
         真正把水印指令从流里抠掉, 减小文件体积。

用法
----
  python 基于PyMuPDF图层法删除水印.py input.pdf                 # 默认 hide
  python 基于PyMuPDF图层法删除水印.py input.pdf --list          # 只列出图层
  python 基于PyMuPDF图层法删除水印.py input.pdf --name 水印     # 指定图层名关键词
  python 基于PyMuPDF图层法删除水印.py input.pdf --mode remove   # 隐藏并抠除指令
  python 基于PyMuPDF图层法删除水印.py input.pdf --dry-run       # 只探测不改文件

始终另存为新文件, 绝不覆盖原件。
"""

import sys
import os
import re
import argparse
import fitz  # PyMuPDF


# ---------- 检测图层 ----------
def list_ocgs(doc):
    """返回 {xref: {'name':str, 'intent':str}} , 即文档登记的全部 OCG 图层。"""
    try:
        return doc.get_ocgs() or {}
    except Exception:
        return {}


def pick_target_ocgs(ocgs, name_keywords):
    """按关键词挑选目标图层(水印)。关键词为空时, 自动挑名字含常见水印词的图层。"""
    kw = [k.lower() for k in name_keywords if k]
    auto_hint = ('watermark', '水印', 'confidential', '内部', '机密', 'draft',
                 '样本', 'sample', '绝密', '秘密')
    targets = {}
    for xref, info in ocgs.items():
        name = (info.get('name') or '').strip()
        low = name.lower()
        if kw:
            if any(k in low for k in kw):
                targets[xref] = name
        else:
            if any(h in low for h in auto_hint):
                targets[xref] = name
    return targets


# ---------- hide: 把图层置为不可见 ----------
def _parse_ref_array(value):
    """把 '[10 0 R 12 0 R]' 解析成 ['10 0 R', '12 0 R']; 非数组/空返回 []。"""
    if not value or value.strip().lower() in ('null', ''):
        return []
    m = re.search(r'\[([^\]]*)\]', value)
    inner = m.group(1) if m else ''
    refs = re.findall(r'(\d+)\s+0\s+R', inner)
    return [f'{r} 0 R' for r in refs]


def _array_str(refs):
    return '[' + ' '.join(refs) + ']'


def hide_ocg(doc, oc_props_xref, target_xrefs):
    """把目标 OCG 从 /D/ON 移除、加入 /D/OFF (并对每个 /Configs 同样处理)。"""
    tgt_refs = {f'{x} 0 R' for x in target_xrefs}

    def fix_dict(cfg_path):
        _, on_v = doc.xref_get_key(oc_props_xref, cfg_path + '/ON')
        _, off_v = doc.xref_get_key(oc_props_xref, cfg_path + '/OFF')
        on = _parse_ref_array(on_v)
        off = _parse_ref_array(off_v)
        changed = False
        new_on = [r for r in on if r not in tgt_refs]
        if len(new_on) != len(on):
            changed = True
        off_set = set(off)
        for r in tgt_refs:
            if r not in off_set:
                off.append(r)
                changed = True
        if changed:
            doc.xref_set_key(oc_props_xref, cfg_path + '/ON', _array_str(new_on))
            doc.xref_set_key(oc_props_xref, cfg_path + '/OFF', _array_str(off))
        return changed

    touched = fix_dict('D')

    # 处理 /Configs 里的每一个配置(内联字典数组)
    _, cfgs_v = doc.xref_get_key(oc_props_xref, 'Configs')
    n_cfg = len(re.findall(r'<<', cfgs_v or ''))
    for i in range(n_cfg):
        try:
            if fix_dict(f'Configs/{i}'):
                touched = True
        except Exception:
            continue
    return touched


# ---------- remove: 从内容流中抠掉引用该 OCG 的标带块 ----------
def _remove_marked_blocks(content, tgt_nums):
    """删除引用目标 OCG 的 BDC..EMC 块; 返回 (新内容, 删除数)。
    tgt_nums: 目标 OCG 的 xref 数字字符串集合, 如 {'10','12'}。
    要点: 操作数 <<...>> 不跨行匹配, 且删除前先保留操作数之前的正文,
    用 BDC/BMC 与 EMC 嵌套计数配对切除整块。"""
    out = []
    i = 0
    removed = 0
    bdc_re = re.compile(r'(/[^\s<]*)\s*(<<.*?>>|/[^\s<]*)?\s*BDC\b')
    num_alt = '|'.join(tgt_nums)

    def references_target(operand):
        return bool(re.search(r'/OCGS\s*\[?\s*(?:' + num_alt + r')(?![0-9])', operand)
                    or re.search(r'(?:' + num_alt + r')\s+0\s+R\b', operand))

    wpat = re.compile(r'\b(BDC|BMC|EMC)\b')
    while i < len(content):
        mm = bdc_re.search(content, i)
        if not mm:
            out.append(content[i:])
            break
        out.append(content[i:mm.start()])   # 保留操作数之前的一切(正文等)
        operand = content[mm.start():mm.end()]
        if not references_target(operand):
            out.append(operand)
            i = mm.end()
            continue
        depth = 1
        block_end = None
        for m2 in wpat.finditer(content, mm.end()):
            if m2.group(1) in ('BDC', 'BMC'):
                depth += 1
            else:
                depth -= 1
                if depth == 0:
                    block_end = m2.end()
                    break
        if block_end is None:
            out.append(operand)
            i = mm.end()
            continue
        removed += 1
        i = block_end
    return ''.join(out), removed


def _xobject_targets_ocg(doc, xref, tgt_nums):
    """判断某 Form XObject 字典是否挂目标 OCG 的 /OC。"""
    try:
        _, sub = doc.xref_get_key(xref, 'Subtype')
        if sub and '/Form' in sub:
            _, ocval = doc.xref_get_key(xref, 'OC')
            if ocval and '/OCGS' in ocval:
                for num in tgt_nums:
                    if re.search(r'(?<![0-9])' + num + r'(?![0-9])', ocval):
                        return True
    except Exception:
        pass
    return False


def _walk_all_content_xrefs(doc):
    """收集所有页面内容流 xref + 文档中全部 Form XObject xref。"""
    xrefs = set()
    for page in doc:
        for x in page.get_contents():
            xrefs.add(x)
    for xref in range(1, doc.xref_length()):
        try:
            _, sub = doc.xref_get_key(xref, 'Subtype')
            if sub and '/Form' in sub:
                xrefs.add(xref)
        except Exception:
            continue
    return xrefs


# ---------- 主流程 ----------
def process(pdf_path, output_path, name_keywords, mode, dry_run):
    doc = fitz.open(pdf_path)
    ocgs = list_ocgs(doc)

    if not ocgs:
        print('未检测到任何 OCG 图层。该 PDF 的水印可能不是图层实现,')
        print('请改用之前"有效字号+倾斜"的流删除方案。')
        doc.close()
        return

    print('== 文档中的 OCG 图层 ==')
    for xref, info in ocgs.items():
        print(f'  xref={xref}  name={info.get("name")!r}  intent={info.get("intent")!r}')

    targets = pick_target_ocgs(ocgs, name_keywords)
    if not targets:
        print('\n未匹配到目标水印图层。请用 --name 关键词指定要处理的图层名。')
        doc.close()
        return

    print('\n== 选定的目标水印图层 ==')
    for xref, name in targets.items():
        print(f'  xref={xref}  name={name!r}')

    if dry_run:
        print('\n[dry-run] 仅探测, 不修改文件。')
        doc.close()
        return

    tgt_nums = {str(x) for x in targets.keys()}

    # 步骤1: hide -- 置为不可见
    _, cat_val = doc.xref_get_key(doc.pdf_catalog(), 'OCProperties')
    oc_props_xref = None
    if cat_val and cat_val != 'null':
        oc_props_xref = int(cat_val.split()[0])
    hide_ok = False
    if oc_props_xref is not None:
        hide_ok = hide_ocg(doc, oc_props_xref, list(targets.keys()))
        print(f'\n[hide] 图层可见性置 OFF: {"成功" if hide_ok else "无需改动(可能已隐藏)"}')

    # 步骤2: remove -- 抠流(仅在 remove 模式)
    if mode == 'remove':
        removed_cells = 0
        cleaned_streams = 0
        for xref in sorted(_walk_all_content_xrefs(doc)):
            # 2a: 引用目标 OCG 的 Form XObject -> 内容清空
            if _xobject_targets_ocg(doc, xref, tgt_nums):
                try:
                    doc.update_stream(xref, b' ', compress=True)
                    cleaned_streams += 1
                    continue
                except Exception:
                    pass
            # 2b: 页面/普通流 -> 删除引用目标 OCG 的 BDC..EMC 块
            stream = doc.xref_stream(xref)
            if not stream:
                continue
            try:
                content = stream.decode('latin-1')
            except Exception:
                continue
            if 'BDC' not in content:
                continue
            new_content, cnt = _remove_marked_blocks(content, tgt_nums)
            if cnt > 0:
                doc.update_stream(xref, new_content.encode('latin-1'), compress=True)
                removed_cells += cnt
                cleaned_streams += 1
        print(f'[remove] 抠除标带块 {removed_cells} 处, 清理流对象 {cleaned_streams} 个。')

    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()
    print(f'\n完成。已另存: {output_path}')
    print('说明: hide 模式只是关掉图层渲染, 正文无损; remove 模式额外从流里抠掉水印指令。')


def main():
    ap = argparse.ArgumentParser(description='基于 PyMuPDF 的 OCG 图层法删除/隐藏水印')
    ap.add_argument('pdf', help='输入 PDF 路径')
    ap.add_argument('--output', default='', help='输出 PDF 路径(默认自动命名)')
    ap.add_argument('--name', nargs='*', default=[],
                    help='目标水印图层名关键词, 可多个; 不填则自动识别常见水印名')
    ap.add_argument('--mode', choices=['hide', 'remove'], default='hide',
                    help='hide=隐藏图层(默认最安全); remove=隐藏并从流中抠除水印指令')
    ap.add_argument('--dry-run', action='store_true', help='只探测不修改')
    ap.add_argument('--list', action='store_true', help='只列出全部图层后退出')
    args = ap.parse_args()

    if not os.path.isfile(args.pdf):
        print(f'找不到文件: {args.pdf}')
        return

    if args.list:
        doc = fitz.open(args.pdf)
        for xref, info in list_ocgs(doc).items():
            print(f'xref={xref}  name={info.get("name")!r}  intent={info.get("intent")!r}')
        doc.close()
        return

    out = args.output
    if not out:
        base = os.path.splitext(args.pdf)[0]
        out = base + '_水印已删.pdf'

    process(args.pdf, out, args.name, args.mode, args.dry_run)


if __name__ == '__main__':
    # main()
    input_pdf = "/Users/teacher/Downloads/百度网盘Download/综D基础理论（详细版）(1)_副本.pdf"
    output_pdf = input_pdf.replace('.pdf', '_output.pdf')
    name = "微"
    mode = "remove"
    dry_run = True
    process(
        input_pdf, 
        output_pdf, 
        name, 
        mode, 
        dry_run
    )