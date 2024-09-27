# coding=utf-8
import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

import pandas as pd
import json
import os
from typing import List, Union, Tuple
from filelock import FileLock

def csv_to_json(csv_file: str, json_file: str) -> None:
    """
    将CSV文件转换为JSON格式，并保存到指定路径。
    
    Args:
        csv_file (str): 输入的CSV文件路径
        json_file (str): 输出的JSON文件路径
    
    示例:
        csv_to_json('data.csv', 'output.json')
    """
    # 读取CSV文件为DataFrame
    df = pd.read_csv(csv_file)
    
    # 将DataFrame转换为JSON格式并写入文件
    df.to_json(json_file, orient='records', force_ascii=False, indent=4)

    print(f"CSV文件成功转换为JSON并保存到: {json_file}")
    

def csv_to_jsonl(csv_file: str, jsonl_file: str) -> None:
    """
    将CSV文件转换为JSONL格式，并保存到指定路径。
    
    Args:
        csv_file (str): 输入的CSV文件路径
        jsonl_file (str): 输出的JSONL文件路径
    
    示例:
        csv_to_jsonl('data.csv', 'output.jsonl')
    """
    # 读取CSV文件为DataFrame
    df = pd.read_csv(csv_file)
    
    # 打开JSONL文件进行写入
    with open(jsonl_file, 'w', encoding='utf-8') as f:
        # 逐行将DataFrame转换为JSON格式并写入文件
        for record in df.to_dict(orient='records'):
            json_record = json.dumps(record, ensure_ascii=False)  # 转换为合法的JSON格式
            f.write(f"{json_record}\n")

    print(f"CSV文件成功转换为JSONL并保存到: {jsonl_file}")

def append_to_jsonl(new_data: Union[pd.DataFrame, List[dict]], jsonl_file: str) -> None:
    # TODO: json key 的顺序
    """
    将新的数据追加到已有的JSONL文件中。
    
    Args:
        new_data (pd.DataFrame or list[dict]): 要追加的数据，格式为DataFrame或字典列表
        jsonl_file (str): 要追加数据的JSONL文件路径
    
    示例:
        new_data = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
        append_to_jsonl(new_data, 'output.jsonl')
    """
    # 判断输入的数据类型
    if isinstance(new_data, pd.DataFrame):
        # 如果是DataFrame，将其转换为字典列表
        records = new_data.to_dict(orient='records')
    elif isinstance(new_data, list) and all(isinstance(item, dict) for item in new_data):
        # 如果是字典列表，直接使用
        records = new_data
    else:
        raise ValueError("new_data 必须是 DataFrame 或者字典列表")
    
    # 文件锁，防止并发写入冲突
    lock_file = jsonl_file + '.lock'
    with FileLock(lock_file):
        try:
            # 以追加模式打开JSONL文件
            with open(jsonl_file, 'a', encoding='utf-8') as f:
                # 逐行将字典写入JSONL文件
                for record in records:
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')
            print(f"成功将数据追加到JSONL文件: {jsonl_file}")
        except Exception as e:
            print(f"写入JSONL文件时出错: {e}")

def append_to_csv(new_data, csv_file: str, header: bool = False, index: bool = False, encoding: str = 'utf-8') -> None:
    if isinstance(new_data, pd.DataFrame):
        df_csv = pd.read_csv(csv_file)
        new_data = new_data[df_csv.columns] # 确保列顺序一致
    elif isinstance(new_data, list) and all(isinstance(item, dict) for item in new_data):
        df_csv = pd.read_csv(csv_file)
        new_data = pd.DataFrame(new_data)
        new_data = new_data[df_csv.columns] # 确保列顺序一致
    # 文件锁，防止并发写入冲突
    lock_file = csv_file + '.lock'
    with FileLock(lock_file):
        try:
            # 以追加模式将DataFrame写入CSV文件
            new_data.to_csv(csv_file, mode='a', header=header, index=index, encoding=encoding)
            print(f"成功将数据追加到CSV文件: {csv_file}")
        except Exception as e:
            print(f"写入CSV文件时出错: {e}")

def get_last_jsonl_record_safe(jsonl_file: str) -> dict:
    """
    获取JSONL文件中的最后一条有效记录，忽略格式错误的行。
    
    Args:
        jsonl_file (str): JSONL文件路径
    
    Returns:
        dict: 最后一条有效的JSON记录
    
    示例:
        last_record = get_last_jsonl_record_safe('data.jsonl')
        print(last_record)
    """
    last_record = None
    
    # 打开JSONL文件，逐行读取
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                # 尝试将每行转换为字典
                last_record = json.loads(line.strip())
            except json.JSONDecodeError as e:
                # 捕捉JSON解析错误，并输出问题行号和内容
                print(f"在第 {line_num} 行解析JSON失败: {line.strip()}")
                print(f"错误信息: {e}")
    
    if last_record:
        print(f"最后一条有效记录: {last_record}")
    else:
        print("未找到有效的JSON记录")
    
    return last_record

def compare_dates(date1: Union[str, int, pd.Timestamp], date2: Union[str, int, pd.Timestamp]) -> str:
    """
    比较两个日期，自动处理不同的数据类型。
    
    Args:
        date1 (Union[str, int, pd.Timestamp]): 第一个日期，可能是字符串、整数或 pandas 的 Timestamp。
        date2 (Union[str, int, pd.Timestamp]): 第二个日期，可能是字符串、整数或 pandas 的 Timestamp。
    
    Returns:
        str: 比较结果，返回 'date1 is earlier', 'date1 is later', 或 'date1 is equal to date2'
    
    示例:
        result = compare_dates('2023-09-25', '2023-09-27')
        print(result)  # 输出: date1 is earlier
    """
    # 转换 date1 和 date2 为 datetime 类型
    try:
        date1_dt = pd.to_datetime(date1)
        date2_dt = pd.to_datetime(date2)
    except Exception as e:
        return f"Error in converting dates: {e}"
    
    # 比较日期
    if date1_dt > date2_dt:
        return True
    else:
        return False
    

def load_data(file_path: str, date_range: Tuple[Union[str, int, pd.Timestamp], Union[str, int, pd.Timestamp]] = None) -> pd.DataFrame:
    """
    加载CSV数据，并根据给定的日期范围过滤数据。
    
    Args:
        file_path (str): 文件路径
        date_range (Tuple[Union[str, int, pd.Timestamp], Union[str, int, pd.Timestamp]]): 日期范围，用于过滤数据
    
    Returns:
        pd.DataFrame: 包含非空内容且在日期范围内的数据框
    """
    # 读取CSV文件
    df = pd.read_csv(file_path, encoding='utf8')
    # 确保 'date' 列是 datetime 类型
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    # 过滤掉内容为空的数据
    df = df[df['content'].notnull()]
    if date_range:
        # 处理 date_range 元组，转换为 datetime 格式
        try:
            start_date = pd.to_datetime(date_range[0], errors='coerce', format=determine_format(date_range[0]))  # 起始日期
            end_date = pd.to_datetime(date_range[1], errors='coerce', format=determine_format(date_range[1]))    # 结束日期
        except Exception as e:
            raise ValueError(f"日期范围转换错误: {e}")
        # 检查是否有无效日期
        if pd.isnull(start_date) or pd.isnull(end_date):
            raise ValueError("日期范围无效，请提供有效的日期格式")
        # 根据日期范围过滤数据
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        # 按日期降序排列并重置索引
    df = df.sort_values(by='date', ascending=False).reset_index(drop=True)
    return df

def determine_format(date):
    if isinstance(date, str):
        if '-' in date:
            return '%Y-%m-%d'
        elif '/' in date:
            return '%Y/%m/%d'
        else:
            return '%Y%m%d'
    elif isinstance(date, int):
        return '%Y%m%d'
    elif isinstance(date, pd.Timestamp):
        return ''
    return '%Y%m%d'