import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
import json
from typing import List, Union, Tuple, Dict, Optional

import pandas as pd
import cpca
from filelock import FileLock



def csv_to_json(csv_file: str, json_file: str) -> None:
    """
    Convert a CSV file to JSON format and save it to the specified path.

    Args:
        csv_file (str): Path to the input CSV file.
        json_file (str): Path to save the output JSON file.

    Example:
        csv_to_json('data.csv', 'output.json')
    """
    df = pd.read_csv(csv_file)
    df.to_json(json_file, orient='records', force_ascii=False, indent=4)
    print(f"CSV file successfully converted to JSON and saved to: {json_file}")


def csv_to_jsonl(csv_file: str, jsonl_file: str) -> None:
    """
    Convert a CSV file to JSONL format and save it to the specified path.

    Args:
        csv_file (str): Path to the input CSV file.
        jsonl_file (str): Path to save the output JSONL file.

    Example:
        csv_to_jsonl('data.csv', 'output.jsonl')
    """
    df = pd.read_csv(csv_file)
    with open(jsonl_file, 'w', encoding='utf-8') as f:
        for record in df.to_dict(orient='records'):
            json_record = json.dumps(record, ensure_ascii=False)
            f.write(f"{json_record}\n")
    print(f"CSV file successfully converted to JSONL and saved to: {jsonl_file}")


def append_to_jsonl(new_data: Union[pd.DataFrame, List[Dict]], jsonl_file: str) -> None:
    """
    Append new data to an existing JSONL file.

    Args:
        new_data (Union[pd.DataFrame, List[Dict]]): Data to append, either as a DataFrame or a list of dictionaries.
        jsonl_file (str): Path to the JSONL file to append data to.

    Example:
        new_data = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
        append_to_jsonl(new_data, 'output.jsonl')
    """
    if isinstance(new_data, pd.DataFrame):
        records = new_data.to_dict(orient='records')
    elif isinstance(new_data, list) and all(isinstance(item, dict) for item in new_data):
        records = new_data
    else:
        raise ValueError("new_data must be a DataFrame or a list of dictionaries")

    lock_file = jsonl_file + '.lock'
    with FileLock(lock_file):
        try:
            with open(jsonl_file, 'a', encoding='utf-8') as f:
                for record in records:
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')
            print(f"Successfully appended data to JSONL file: {jsonl_file}")
        except Exception as e:
            print(f"Error writing to JSONL file: {e}")


def append_to_csv(new_data: Union[pd.DataFrame, List[Dict]], csv_file: str, header: bool = False, index: bool = False, encoding: str = 'utf-8') -> None:
    """
    Append new data to an existing CSV file.

    Args:
        new_data (Union[pd.DataFrame, List[Dict]]): Data to append, either as a DataFrame or a list of dictionaries.
        csv_file (str): Path to the CSV file to append data to.
        header (bool, optional): Whether to write the header. Defaults to False.
        index (bool, optional): Whether to write row index. Defaults to False.
        encoding (str, optional): File encoding. Defaults to 'utf-8'.
    """
    df_csv = pd.read_csv(csv_file)
    if isinstance(new_data, pd.DataFrame):
        new_data = new_data[df_csv.columns]  # Ensure column order consistency
    elif isinstance(new_data, list) and all(isinstance(item, dict) for item in new_data):
        new_data = pd.DataFrame(new_data)[df_csv.columns]  # Ensure column order consistency
    else:
        raise ValueError("new_data must be a DataFrame or a list of dictionaries")

    lock_file = csv_file + '.lock'
    with FileLock(lock_file):
        try:
            new_data.to_csv(csv_file, mode='a', header=header, index=index, encoding=encoding)
            print(f"Successfully appended data to CSV file: {csv_file}")
        except Exception as e:
            print(f"Error writing to CSV file: {e}")


def get_last_jsonl_record_safe(jsonl_file: str) -> Optional[Dict]:
    """
    Get the last valid record from a JSONL file, ignoring malformed lines.

    Args:
        jsonl_file (str): Path to the JSONL file.

    Returns:
        Optional[Dict]: The last valid JSON record, or None if no valid records found.

    Example:
        last_record = get_last_jsonl_record_safe('data.jsonl')
        print(last_record)
    """
    last_record = None
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                last_record = json.loads(line.strip())
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON on line {line_num}: {line.strip()}")
                print(f"Error message: {e}")

    if last_record:
        print(f"Last valid record: {last_record}")
    else:
        print("No valid JSON records found")

    return last_record


def compare_dates(date1: Union[str, int, pd.Timestamp], date2: Union[str, int, pd.Timestamp]) -> bool:
    """
    Compare two dates, automatically handling different data types.

    Args:
        date1 (Union[str, int, pd.Timestamp]): The first date.
        date2 (Union[str, int, pd.Timestamp]): The second date.

    Returns:
        bool: True if date1 is later than date2, False otherwise.

    Example:
        result = compare_dates('2023-09-25', '2023-09-27')
        print(result)  # Output: False
    """
    try:
        date1_dt = pd.to_datetime(date1)
        date2_dt = pd.to_datetime(date2)
    except Exception as e:
        raise ValueError(f"Error in converting dates: {e}")

    return date1_dt > date2_dt


def load_data(file_path: str, date_range: Optional[Tuple[Union[str, int, pd.Timestamp], Union[str, int, pd.Timestamp]]] = None) -> pd.DataFrame:
    """
    Load CSV data and filter it based on the given date range.

    Args:
        file_path (str): Path to the CSV file.
        date_range (Optional[Tuple[Union[str, int, pd.Timestamp], Union[str, int, pd.Timestamp]]]): Date range for filtering data.

    Returns:
        pd.DataFrame: DataFrame containing non-empty content within the specified date range.
    """
    df = pd.read_csv(file_path, encoding='utf8')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df[df['content'].notnull()]

    if date_range:
        try:
            start_date = pd.to_datetime(date_range[0], errors='coerce', format=determine_date_format(date_range[0]))
            end_date = pd.to_datetime(date_range[1], errors='coerce', format=determine_date_format(date_range[1]))
        except Exception as e:
            raise ValueError(f"Error in date range conversion: {e}")

        if pd.isnull(start_date) or pd.isnull(end_date):
            raise ValueError("Invalid date range, please provide valid date formats")

        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    return df.sort_values(by='date', ascending=False).reset_index(drop=True)


def determine_date_format(date: Union[str, int, pd.Timestamp]) -> str:
    """
    Determine the format of a given date.

    Args:
        date (Union[str, int, pd.Timestamp]): The date to determine the format for.

    Returns:
        str: The determined date format.
    """
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


def extract_location_counts(data: pd.DataFrame, fields: List[str] = ['title', 'content']) -> Dict[str, pd.DataFrame]:
    """
    Extract and count location information from the given data using cpca.

    Args:
        data (pd.DataFrame): DataFrame containing text content.
        fields (List[str], optional): List of text fields to extract from. Defaults to ['title', 'content'].

    Returns:
        Dict[str, pd.DataFrame]: Dictionary containing count results for provinces, cities, and counties.
    """
    texts = data[fields].apply(lambda x: '\n'.join(x), axis=1)
    text_list = [text.replace('合作', '').replace('东方', '') for text in texts]
    location_data = cpca.transform(text_list)

    province_counts = process_location_counts(location_data['省'], 'Province')
    city_counts = process_location_counts(location_data['市'], 'City', ['市辖区', '省直辖县级行政区划'])
    county_counts = process_location_counts(location_data['区'], 'County', ['郊区', '市辖区', '合作市'])

    return {
        'province': province_counts,
        'city': city_counts,
        'county': county_counts
    }


def process_location_counts(series: pd.Series, column_name: str, exclude: List[str] = None) -> pd.DataFrame:
    """
    Process and count locations from a pandas Series.

    Args:
        series (pd.Series): Series containing location data.
        column_name (str): Name for the location column.
        exclude (List[str], optional): List of locations to exclude. Defaults to None.

    Returns:
        pd.DataFrame: Processed and sorted location counts.
    """
    counts = series.value_counts().reset_index()
    counts.columns = [column_name, 'Count']
    if exclude:
        counts = counts[~counts[column_name].isin(exclude)]
    return counts.sort_values(by='Count', ascending=False).reset_index(drop=True)