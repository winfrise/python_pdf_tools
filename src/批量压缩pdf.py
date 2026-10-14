#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量PDF压缩工具
支持两种压缩方式:
  1. PyMuPDF内置压缩 (fitzd) - 无需安装额外软件，压缩率中等
  2. Ghostscript压缩 (gs) - 压缩率更高，需系统安装Ghostscript

用法:
  python batch_compress_pdf.py <PDF文件夹路径> [输出文件夹] [方法] [质量]

示例:
  python batch_compress_pdf.py ./my_pdfs ./my_pdfs_out fitzd
  python batch_compress_pdf.py ./my_pdfs ./my_pdfs_out gs 0.5
"""

import os
import fitz  # PyMuPDF
import subprocess
import sys


def compress_pdf_by_gs(input_path, output_path, quality=0.75):
    """
    使用 Ghostscript 压缩 PDF（压缩率最高，适合图片多的PDF）
    quality: 0.75=中等, 0.5=高压缩, 0.9=低压缩
    """
    gs_map = {
        0.5: '/ebook',
        0.75: '/screen',
        0.9: '/printer',
    }
    gs_level = gs_map.get(quality, '/screen')

    cmd = [
        'gs',
        '-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.4',
        f'-dPDFSETTINGS={gs_level}',
        '-dNOPAUSE',
        '-dQUIET',
        '-dBATCH',
        f'-sOutputFile={output_path}',
        input_path,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"  [GS错误] {result.stderr}")
            return False
        return True
    except FileNotFoundError:
        print("  [错误] 未找到 Ghostscript，请确保已安装 gs 命令")
        return False
    except subprocess.TimeoutExpired:
        print("  [错误] 处理超时")
        return False


def compress_pdf_by_fitzd(input_path, output_path, deflate=True):
    """
    使用 PyMuPDF 内置压缩（无需安装额外软件，压缩率中等）
    """
    doc = fitz.open(input_path)
    doc.save(output_path, garbage=4, deflate=deflate)
    doc.close()
    return True


def batch_compress_pdf(folder_path, output_folder=None, method='fitzd', quality=0.75):
    """
    批量压缩指定文件夹下的所有PDF文件

    :param folder_path: 包含PDF的文件夹路径
    :param output_folder: 输出文件夹路径（默认覆盖原文件）
    :param method: 'gs'=Ghostscript(高压缩), 'fitzd'=PyMuPDF(免安装)
    :param quality: Ghostscript质量等级(仅gs方法有效)
    """
    if output_folder is None:
        output_folder = folder_path

    os.makedirs(output_folder, exist_ok=True)

    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print("未找到PDF文件")
        return

    print(f"找到 {len(pdf_files)} 个PDF文件")
    print(f"压缩方式: {method}")
    print(f"输出目录: {output_folder}")
    print("-" * 50)

    success_count = 0
    for pdf_name in pdf_files:
        input_path = os.path.join(folder_path, pdf_name)
        output_path = os.path.join(output_folder, pdf_name)

        # 显示原始大小
        orig_size = os.path.getsize(input_path)
        orig_mb = orig_size / (1024 * 1024)

        if method == 'gs':
            ok = compress_pdf_by_gs(input_path, output_path, quality)
        else:
            ok = compress_pdf_by_fitzd(input_path, output_path)

        if ok:
            new_size = os.path.getsize(output_path)
            new_mb = new_size / (1024 * 1024)
            ratio = (1 - new_size / orig_size) * 100
            print(f"[OK] {pdf_name}: {orig_mb:.1f}MB -> {new_mb:.1f}MB (压缩 {ratio:.1f}%)")
            success_count += 1
        else:
            print(f"[FAIL] {pdf_name}")

    print("-" * 50)
    print(f"完成: {success_count}/{len(pdf_files)} 个文件压缩成功")


# ================= 入口 =================
if __name__ == "__main__":
    if len(sys.argv) >= 2:
        folder = sys.argv[1]
        out_folder = sys.argv[2] if len(sys.argv) > 2 else None
        method = sys.argv[3] if len(sys.argv) > 3 else 'fitzd'
        qual = float(sys.argv[4]) if len(sys.argv) > 4 else 0.75
        batch_compress_pdf(folder, out_folder, method, qual)
    else:
        print("用法: python batch_compress_pdf.py <PDF文件夹路径> [输出文件夹] [方法] [质量]")
        print("")
        print("参数说明:")
        print("  文件夹路径  - 包含PDF文件的文件夹")
        print("  输出文件夹  - 压缩后文件保存位置(可选，默认覆盖原文件)")
        print("  方法        - 'gs'使用Ghostscript(压缩率高，需安装gs) 或 'fitzd'使用PyMuPDF(免安装)")
        print("  质量        - Ghostscript质量等级: 0.5=高压缩, 0.75=中等, 0.9=低压缩(仅gs方法)")
        print("")
        print("示例:")
        print("  python batch_compress_pdf.py ./my_pdfs ./my_pdfs_out fitzd")
        print("  python batch_compress_pdf.py ./my_pdfs ./my_pdfs_out gs 0.5")