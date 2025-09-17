import json
import pickle
import pandas as pd
import random
import yaml
import numpy as np
import os

import random
random.seed(42)


def statistics_list(data):
    """
    计算并打印列表的基本统计量
    
    参数:
        data (list): 包含数值的列表
        
    打印:
        - 平均值(mean)
        - 最小值(min)
        - 25分位数(25%)
        - 中位数(median)
        - 75分位数(75%)
        - 最大值(max)
    """
    if not data:
        print("输入列表为空，无法计算统计量")
        return
    
    # 转换以确保所有元素都是数值
    try:
        data = [float(x) for x in data]
    except ValueError:
        print("错误：列表包含非数值元素")
        return
    
    # 计算并打印各项统计量
    print(f"列表长度为: {len(data)}")
    print(f"平均值(mean): {float(np.mean(data)):.4f}")
    print(f"最小值(min): {float(np.min(data))}")
    print(f"25分位数(25%): {float(np.percentile(data, 25))}")
    print(f"中位数(median): {float(np.median(data)):.4f}")
    print(f"75分位数(75%): {float(np.percentile(data, 75))}")
    print(f"最大值(max): {float(np.max(data))}")

def get_shuffle_index( datas ):
    total_length = len(datas)
    indices = list(range(total_length))
    random.shuffle(indices)
    return indices

def data_split( data: list, ratio: list, index: list):
    """
    param: data要分割的数据列表
    param: ratio分割比例，train:test
    """
    length = len( index )
    sep = int(length*ratio[0])
    train_index = index[:sep]
    test_index  = index[sep:]

    train, test = [], []
    for inde in train_index:
        train.append( data[inde] )
    for inde in test_index:
        test.append( data[inde] )
    
    return train, test

def online_local_chat( query, index=0 ):
    import redis
    import pickle
    redis_communication = redis.StrictRedis(host='localhost', port=6379, db=0)
    """将下面两行放置到环境中
    import redis
    import pickle
    redis_communication = redis.StrictRedis(host='localhost', port=6379, db=0)

    from vllm import LLM, SamplingParams
    model_dir = "/home/jiangpeiwen2/jiangpeiwen2/workspace/LLMs/Baichuan2-7B-Chat"
    sampling_params = SamplingParams(temperature=0.8, top_p=0.95)
    llm = LLM(
        model=model_dir,
        trust_remote_code=True,
        dtype='float16',
        gpu_memory_utilization=0.9,
        seed = 32,
    )   # 必须使用模型支持列表中的模型名
    print(f"LLM Inderence start!")

    task = ["静夜思全文", "天气怎么样"]
    outputs = llm.generate(task, sampling_params, use_tqdm=False)
    ret = []
    for output in outputs:
        ret.append( output.outputs[0].text )
    """
    redis_communication.rpush('Tasks', pickle.dumps( (index, query) ))
    while True:
        message = redis_communication.lpop('Response')
        if message!=None:
            index, ret = pickle.loads(message)
            return (index, ret)

#####################################################数据加载保存#################################################

def save_data( data: list, path, other_type = None ):
    type = path.split(".")[-1]
    if type == "text" or other_type == "txt":
        with open( path, 'w') as file:
            for i in range(len(data)):
                line = data[i]
                if i == len(data)-1:
                    file.write(line)
                else:
                    file.write(line + '\n')
    elif type == "json":
        with open( path, "w", encoding="utf-8") as f:
            json.dump( data, f,  ensure_ascii=False, indent=4)
    elif type == "pickle":
        with open( path, "wb") as f:
            pickle.dump( data, f )
    elif type == "csv":
        data.to_csv(path, index=False, encoding='utf-8')
    elif type == "yaml":
        with open(path, 'w') as file:
            yaml.safe_dump(data, file, default_flow_style=False, allow_unicode=True)
    elif type == "jsonl":
        with open( path, "w") as jsonl_file:
            for sub_data in data:
                jsonl_file.write( json.dumps(sub_data)+ '\n')
    elif type == "parquet":
        data.to_parquet(path)
    else:
        raise Exception(f"{type}类型数据目前无法使用save_data保存")

def load_data( path, type, header_None=False, sheet_name=False):
    if not os.path.exists( path ):
        raise Exception(f"Path {path} not exist!")
    if type == "text":
        with open(path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        strings_read = []
        for line in lines:
            if line.endswith("\n"):
                line = line[:-1]
            strings_read.append( line )
        return strings_read
    elif type == "json":
        with open( path, "r", encoding="utf-8") as f:
            datas = json.load( f)
        return datas
    elif type == "pickle":
        with open( path, "rb") as f:
            datas = pickle.load( f)
        return datas
    elif type == "yaml":
        with open(path, 'r') as file:
            datas = yaml.safe_load(file)
        return datas
    elif type == "docx":
        from docx import Document 
        doc = Document( path )  
        full_text = []  
        for para in doc.paragraphs:  
            full_text.append(para.text)  
        return '\n'.join(full_text)
    elif type == "csv":
        return pd.read_csv( path )
    elif type == "excel":
        if header_None:
            if sheet_name:
                return pd.read_excel( path, header=None, sheet_name=sheet_name )
            else:
                return pd.read_excel( path, header=None )
        else:
            if sheet_name:
                return pd.read_excel( path, sheet_name=sheet_name)
            else:
                return pd.read_excel( path)
    elif type == "jsonl":
        json_lines = []
        with open( path, "r") as jsonl_file:
            for line in jsonl_file:
                json_lines.append( json.loads(line))
        return json_lines
    elif type == "parquet":
        return pd.read_parquet(path)
    else:
        raise Exception(f"Type {type} not support!")


if __name__ == "__main__":
    path = "/home/jiangpeiwen2/jiangpeiwen2/projects/wayne_utils/test/config.yaml"
    
    config = load_data( path, "yaml" )
    print( config )


