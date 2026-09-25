# -*- coding: utf-8 -*-
"""
隐藏 PDF 中"某个 CMYK 填充颜色"的所有矢量形状。
原理：这些形状在内容流里都是同一串 `0 0 0 0.051  scn`，
      直接在 content stream 里按字节替换这一段，天然只命中该颜色的形状，
      文本(Tf/Tj/TJ)与图片不受影响。

用法:
    python 隐藏指定CMYK颜色形状.py 输入.pdf 输出.pdf            # 默认方案A 改白
    python 隐藏指定CMYK颜色形状.py 输入.pdf 输出.pdf --transparent  # 方案B 真透明
"""
import sys
import fitz

# 目标颜色指令(逐字节匹配，注意 0.051 后是两个空格)
TARGET = b"0 0 0 0.051  scn"
WHITE  = b"0 0 0 0  scn"   # CMYK 白色(分量个数与目标一致)


def hide_by_whitening(doc):
    """方案A：把该颜色改成白色。逐页、逐 content stream 做字节替换。"""
    total = 0
    for page in doc:
        for xref in page.get_contents():
            data = doc.xref_stream(xref)
            if not data:
                continue
            hit = data.count(TARGET)
            if hit:
                doc.update_stream(xref, data.replace(TARGET, WHITE))
                total += hit
    return total


def hide_by_transparency(doc):
    """方案B：把共享 ExtGState GS0 的填充/描边透明度设为 0。
    仅当整页矢量形状都引用同一个 GS0 时安全(本文件正是如此)。"""
    changed = 0
    for xref in range(1, doc.xref_length()):
        # 找到 ExtGState 字典里含 ca/CA 的对象
        try:
            keys = doc.xref_get_keys(xref)
        except Exception:
            continue
        if "ca" in keys or "CA" in keys:
            # 读原值并改为 0；更稳妥可先确认它被 GS0 引用
            doc.xref_set_key(xref, "ca", "0")
            doc.xref_set_key(xref, "CA", "0")
            changed += 1
    return changed


if __name__ == "__main__":
    src = "/Users/teacher/Desktop/百度网盘下载/1.【言语】理论刷题合集讲义&答案（全）-粉笔名师-讲义/1.【言语】理论刷题合集讲义&答案（全）-粉笔名师-讲义.pdf"
    out = src.replace('.pdf', '_output.pdf')
    transparent = None
    doc = fitz.open(src)
    if transparent:
        print(f"准备设置透明")
        n = hide_by_transparency(doc)
        print(f"[方案B-透明] 已将 {n} 个 ExtGState 的不透明度置 0")
    else:
        print(f"准备填充白色")
        n = hide_by_whitening(doc)
        print(f"[方案A-改白] 已替换 {n} 处该颜色填充指令")
        
    doc.save(out, garbage=4, deflate=True, clean=True)
    doc.close()
    print(f"已保存: {out}")
