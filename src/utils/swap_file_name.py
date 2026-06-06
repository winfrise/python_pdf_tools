import os

def backup_file(file_path, backup_file_path=None, temp_file_path=None):
    try:
        # 1. 定义备份路径和临时路径
        base_name, ext = os.path.splitext(file_path)
        if backup_file_path == None:
            backup_file = f"{base_name}_备份{ext}"

        if temp_file_path == None:
            temp_file = f"{base_name}_temp{ext}"

        # 3. 执行备份和替换操作
        if os.path.exists(file_path):
            # 如果已有备份，先删除旧备份（可选）
            if os.path.exists(backup_file):
                os.remove(backup_file)

            # 将原文件重命名为备份文件
            os.rename(file_path, backup_file_path)
            print(f"原文件已备份为: {backup_file_path}")

        # 4. 将临时文件重命名为原文件名
        os.rename(temp_file, input_file)
        print(f"新文件已保存为: {input_file}")

    except Exception as e:
        print(f"保存文件时出错: {e}")
        # 如果出错，尝试清理临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)