import os
import json
import pandas as pd
import numpy as np

def read_any(path):
    if path.endswith('.json'):
        with open(path, 'r') as f:
            data = json.load(f)
    elif path.endswith('.jsonl'):
        with open(path, 'r') as f:
            data = [json.loads(line.strip()) for line in f]
    elif path.endswith('.parquet'):
        df = pd.read_parquet(path)
        df = df.map(lambda x: x.tolist() if isinstance(x, np.ndarray) else x)
        data = df.to_dict(orient='records')
    elif path.endswith('.csv'):
        df = pd.read_csv(path)
        data = df.to_dict(orient='records')
    elif path.endswith(".xlsx"):
        df = pd.read_excel(path, keep_default_na=False)
        data = df.to_dict(orient="records")
    else:
        raise("error type:{}".format(path))
    return data

def save_any(datas, save_path, exist_ok=True):
    if save_path.endswith('.json'):
        save_json(datas, save_path, exist_ok)
    elif save_path.endswith('.jsonl'):
        save_jsonl(datas, save_path, exist_ok)
    elif save_path.endswith('.parquet'):
        save_parquet(datas, save_path, exist_ok)
    elif save_path.endswith('.xlsx'):
        save_xlsx(datas, save_path, exist_ok)

def save_json(datas, save_path, exist_ok=True):
    dir_name = os.path.dirname(save_path)
    os.makedirs(dir_name, exist_ok=True)
    if os.path.exists(save_path) and not exist_ok:
        raise("file existed")
    with open(save_path, 'w', encoding="utf-8") as f:
        json.dump(datas, f, ensure_ascii=False, indent=4)

def save_jsonl(datas, save_path, exist_ok=True):
    dir_name = os.path.dirname(save_path)
    os.makedirs(dir_name, exist_ok=True)
    if os.path.exists(save_path) and not exist_ok:
        raise("file existed")
    with open(save_path, 'w', encoding="utf-8") as f:
        for data in datas:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

def save_parquet(datas, save_path, exist_ok=True):
    from datasets import load_dataset, Dataset
    dir_name = os.path.dirname(save_path)
    os.makedirs(dir_name, exist_ok=True)
    if os.path.exists(save_path) and not exist_ok:
        raise("file existed")
    dataset = Dataset.from_list(datas)
    dataset.to_parquet(save_path)

def save_xlsx(datas, save_path, exist_ok=True):
    from openpyxl import load_workbook
    from openpyxl.styles import Alignment
    dir_name = os.path.dirname(save_path)
    os.makedirs(dir_name, exist_ok=True)
    if os.path.exists(save_path) and not exist_ok:
        raise("file existed")

    df = pd.DataFrame(datas)

    # 保存为 Excel 文件
    df.to_excel(save_path, index=False, engine='openpyxl')

    # 打开保存的 Excel 文件
    wb = load_workbook(save_path)
    ws = wb.active

    # 调整列宽
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter  # 获取列名
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (38 + 2)  # 添加一些额外的空间
        ws.column_dimensions[column].width = adjusted_width
        if column != "system":
            for cell in col:
                cell.alignment = Alignment(wrap_text=True)

    # 保存调整后的 Excel 文件
    wb.save(save_path)

def save_csv(datas, save_path, exist_ok=True):
    dir_name = os.path.dirname(save_path)
    os.makedirs(dir_name, exist_ok=True)
    if os.path.exists(save_path) and not exist_ok:
        raise("file existed")
    df = pd.DataFrame(datas)
    df.to_csv(save_path, index=False, encoding="utf-8-sig")
