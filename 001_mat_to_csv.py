import numpy as np
import scipy.io
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

dir_path: str = "I:/001_Project_waibu/001_RUL_pre/resource_data/NASA/"

# 转换时间格式，将字符串转换成 datatime 格式
def convert_to_time(hmm):
    year, month, day, hour, minute, second = int(hmm[0]), int(hmm[1]), int(hmm[2]), int(hmm[3]), int(hmm[4]), int(hmm[5])
    return datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)


# 加载 mat 文件
def loadMat(matfile):
    data = scipy.io.loadmat(matfile)
    filename = matfile.split('/')[-1].split('.')[0]
    col = data[filename]
    col = col[0][0][0][0]
    size = col.shape[0]

    data = []
    for i in range(size):
        k = list(col[i][3][0].dtype.fields.keys())
        d1, d2 = {}, {}
        if str(col[i][0][0]) != 'impedance':
            for j in range(len(k)):
                t = col[i][3][0][0][j][0];
                l = [t[m] for m in range(len(t))]
                d2[k[j]] = l
        d1['type'], d1['temp'], d1['time'], d1['data'] = str(col[i][0][0]), int(col[i][1][0]), str(convert_to_time(col[i][2][0])), d2
        data.append(d1)

    return data


# 提取锂电池容量
def getBatteryCapacity(Battery):
    cycle, capacity = [], []
    i = 1
    for Bat in Battery:
        if Bat['type'] == 'discharge':
            capacity.append(Bat['data']['Capacity'][0])
            cycle.append(i)
            i += 1
    return [cycle, capacity]


# 获取锂电池充电或放电时的测试数据
def getBatteryValues(Battery, Type):
    data=[]
    for Bat in Battery:
        if Bat['type'] == Type:
            data.append(Bat['data'])
    return data


def get_dic_valte(dic_name):
    data = {}

    max_length = max(len(value) for item in dic_name for value in item.values())

    for item in dic_name:
        for key, value in item.items():
            if key not in data:
                data[key] = value + [np.nan] * (max_length - len(value))
            else:
                data[key].extend(value + [np.nan] * (max_length - len(value)))

    df = pd.DataFrame(data)

    return df


def get_data(name, capacity, charge, discharge):
    print('Load Dataset ' + name + '.mat ...')
    path = dir_path + name + '.mat'
    data = loadMat(path)
    capacity[name] = getBatteryCapacity(data)              # 放电时的容量数据
    charge[name] = getBatteryValues(data, 'charge')        # 充电数据
    discharge[name] = getBatteryValues(data, 'discharge')  # 放电数据

    df_capacity = pd.DataFrame(list(zip(capacity[name][0], capacity[name][1])), columns=['index', name + '_cap'])
    df_charge = get_dic_valte(charge[name])
    df_discharge = get_dic_valte(discharge[name])


    df_final = pd.concat([df_capacity, df_charge, df_discharge], axis=1)

    return df_final


def flatten_dict(dictionary, depth=0, max_depth=2, parent_key=''):
    flattened_dict = {}
    for key, value in dictionary.items():
        new_key = parent_key + '.' + key if parent_key else key
        if isinstance(value, dict) and depth < max_depth:  # 如果值是字典并且未达到最大展开层数
            flattened_dict.update(flatten_dict(value, depth + 1, max_depth, new_key))
        elif isinstance(value, list):  # 如果值是列表，则遍历列表中每个元素
            for i, item in enumerate(value):
                if isinstance(item, dict) and depth < max_depth:  # 如果列表元素是字典并且未达到最大展开层数
                    flattened_dict.update(flatten_dict(item, depth + 1, max_depth, f'{new_key}[{i}]'))
                else:
                    flattened_dict[f'{new_key}[{i}]'] = item
        else:  # 值不是字典或列表，则直接添加
            flattened_dict[new_key] = value
    return flattened_dict


def get_ch_dcg(name, capacity, charge, discharge):

    path = dir_path + name + '.mat'
    data = loadMat(path)
    capacity[name] = getBatteryCapacity(data)              # 放电时的容量数据
    charge[name] = getBatteryValues(data, 'charge')        # 充电数据
    discharge[name] = getBatteryValues(data, 'discharge')  # 放电数据

    df1 = pd.DataFrame({'cycle': capacity[name][0], 'capacity': capacity[name][1]})
    df1.to_csv(dir_path + '{}_cap.csv'.format(name), index=False)

    def get_df_output(type):
        flattened_discharge = flatten_dict(type, max_depth=3)
        output_data = {}
        for key, value in flattened_discharge.items():
            id_parts = key.split('.')
            id1 = id_parts[0].split('[')[0]
            id2 = id_parts[0].split('[')[1].split(']')[0]
            id3 = id_parts[1].split('[')[1].split(']')[0]
            row_key = (id1, id2, id3)
            if row_key not in output_data:
                output_data[row_key] = {}
            column_name = id_parts[1].split('[')[0].split(']')[0]
            output_data[row_key][column_name] = value

        rows = []  
        for (id1, id2, id3), measurements in output_data.items():  
            row = [id1, id2, id3] + list(measurements.values())  
            rows.append(row) 
        header_dcg = ['vin', 'cycle', 'index', 'Voltage_measured', 'Current_measured', 'Temperature_measured', 'Current_load', 'Voltage_load', 'Time', 'Capacity']
        header_chg = ['vin', 'cycle', 'index', 'Voltage_measured', 'Current_measured', 'Temperature_measured', 'Current_charge', 'Voltage_charge', 'Time']
        
        if type == charge:
            df = pd.DataFrame(rows, columns=header_chg)
            df.to_csv(dir_path + '{}_chg.csv'.format(name), index=False)
        elif type == discharge:
            df = pd.DataFrame(rows, columns=header_dcg)       
            df.to_csv(dir_path + '{}_dcg.csv'.format(name), index=False)

    get_df_output(charge)
    get_df_output(discharge)


def main():
    Battery_list = ['B0005', 'B0006', 'B0007', 'B0018'] # 4 个数据集的名字
    for name1 in Battery_list:
        capacity, charge, discharge = {}, {}, {}
        get_ch_dcg(name1, capacity, charge, discharge)


if __name__ == '__main__':
    main()