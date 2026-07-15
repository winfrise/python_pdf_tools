import os

def batch_process_file_with_callback(input_dir, output_dir, page_range, callback_func, **kwargs):
    """
    通用文件批量处理框架
    :param input_dir: 输入文件夹路径
    :param file_ext: 需要处理的文件后缀 (例如 '.pdf')
    :param callback_func: 回调函数，定义对每个文件的具体操作
    :param kwargs: 传递给回调函数的额外参数 (如 is_flat_output)
    """
    # 1. 公共逻辑：校验目录是否存在
    if not os.path.isdir(input_dir):
        print(f"错误：路径不存在 -> {input_dir}")
        return

    if not output_dir:
        output_dir = input_dir + "_output"

        # 确保输出目录存在，如果不存在则创建
        os.makedirs(output_dir, exist_ok=True)

    print(f"开始扫描目录: {input_dir} -> {output_dir}")
    
    # 2. 公共逻辑：遍历目录结构
    for dirpath, dirnames, filenames in os.walk(input_dir):
        for filename in filenames:
            # 3. 公共逻辑：筛选特定后缀的文件
            if filename.lower().endswith('.pdf'):
                input_file = os.path.join(dirpath, filename)

                # 计算当前遍历到的文件夹相对于 input_dir 的路径
                relative_path = os.path.relpath(input_file, input_dir)
                
                # 拼接出目标文件夹的完整路径
                output_file = os.path.join(output_dir, relative_path)
                
                # 确保目标文件夹存在
                dir_name = os.path.dirname(output_file)
                os.makedirs(dir_name, exist_ok=True)
                
                # 核心：执行传入的回调函数
                # 将当前文件路径和额外的配置参数传给具体业务逻辑
                try:
                    callback_func(
                        input_file, 
                        output_file, 
                        page_range,
                        **kwargs
                    )
                except Exception as e:
                    print(f"处理文件失败 [{input_file}]: {e}")
