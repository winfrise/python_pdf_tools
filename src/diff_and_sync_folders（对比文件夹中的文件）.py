import os
import shutil
import filecmp

def diff_and_sync_folders(dir1, dir2, dir3):
    """
    对比两个文件夹的差异，并可选择将缺失的文件复制到新文件夹。
    :param dir1: 文件夹1的路径
    :param dir2: 文件夹2的路径
    """
    # 检查文件夹是否存在
    if not os.path.exists(dir1) or not os.path.exists(dir2) or not os.path.exists(dir3):
        print("错误：请确保提供的两个文件夹路径都存在！")
        return

    only_in_dir1 = []
    only_in_dir2 = []

    # 1. 查找 文件夹1中有，但 文件夹2中没有的文件
    for root, dirs, files in os.walk(dir1):
        rel_path = os.path.relpath(root, dir1)
        counterpart_root = os.path.join(dir2, rel_path)
        
        for file_name in files:
            if file_name == '.DS_Store':  # 忽略 .DS_Store
                continue

            path1 = os.path.join(root, file_name)
            path2 = os.path.join(counterpart_root, file_name)
            
            if not os.path.exists(path2):
                only_in_dir1.append(path1)

    # 2. 查找 文件夹2中有，但 文件夹1中没有的文件
    for root, dirs, files in os.walk(dir2):
        rel_path = os.path.relpath(root, dir2)
        counterpart_root = os.path.join(dir1, rel_path)
        
        for file_name in files:
            if file_name == '.DS_Store':  # 忽略 .DS_Store
                continue
            
            path2 = os.path.join(root, file_name)
            path1 = os.path.join(counterpart_root, file_name)
            
            if not os.path.exists(path1):
                only_in_dir2.append(path2)

    # 3. 打印对比结果
    print("\n===== 文件夹差异对比结果 =====")
    if not only_in_dir1 and not only_in_dir2:
        print("✅ 两个文件夹内容完全一致，没有缺失文件。")
        return

    if only_in_dir1:
        print(f"\n📁 仅在 [文件夹1] ({dir1}) 中发现 {len(only_in_dir1)} 个文件:")
        for f in only_in_dir1:
            print(f"   - {f}")

    if only_in_dir2:
        print(f"\n📂 仅在 [文件夹2] ({dir2}) 中发现 {len(only_in_dir2)} 个文件:")
        for f in only_in_dir2:
            print(f"   - {f}")

    # 4. 命令行交互提示：是否复制缺少的文件到新文件夹
    print("\n================================")
    choice = input("❓ 是否将所有缺少的文件统一复制到一个【新文件夹】中？ (y/n): ").strip().lower()
    
    if choice == 'y':
        new_folder = dir3
        
        # 创建新文件夹
        os.makedirs(new_folder, exist_ok=True)
        copied_count = 0

        # 复制文件夹1独有的文件
        for src_path in only_in_dir1:
            # 保持原有的相对目录结构
            rel_path = os.path.relpath(src_path, dir1)
            dst_path = os.path.join(new_folder, "from_dir1", rel_path)
            
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copy2(src_path, dst_path)  # copy2 可以保留文件的修改时间等元数据
            copied_count += 1

        # 复制文件夹2独有的文件
        for src_path in only_in_dir2:
            rel_path = os.path.relpath(src_path, dir2)
            dst_path = os.path.join(new_folder, "from_dir2", rel_path)
            
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copy2(src_path, dst_path)
            copied_count += 1

        print(f"\n✅ 操作完成！共复制了 {copied_count} 个缺失文件到 [{new_folder}] 中。")
    else:
        print("已取消复制操作。")


# ================= 运行示例 =================
if __name__ == "__main__":
    folder_1 = "/Users/teacher/Desktop/图纸修改/1-1交然桥至大河段-需要修改"  # 替换为你的实际文件夹1路径
    folder_2 = "/Users/teacher/Desktop/图纸修改/1-2交然桥至大河段-修改后"  # 替换为你的实际文件夹2路径
    folder_3 = "/Users/teacher/Desktop/图纸修改/1-4第一次有问题文件-需要修改" # 复制文件夹2中缺少的文件
    
    diff_and_sync_folders(folder_1, folder_2, folder_3)