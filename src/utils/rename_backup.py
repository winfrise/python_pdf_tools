import os

def rename_backup(input_path, output_path = None):
    base_name, ext = os.path.splitext(input_path)
    
    if output_path == None:
        backup_path = f"{base_name}_backup{ext}"

    if os.path.exists(input_path):
        # 如果已有备份，先删除旧备份（可选）
        if os.path.exists(backup_path):
            os.remove(backup_path)

    # 将原文件重命名为备份文件
    os.rename(input_path, backup_path)
    print(f"原文件已备份为: {backup_path}")