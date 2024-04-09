import numpy as np
import scipy.io
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

dir_path: str = "I:/001_Project_waibu/001_RUL_pre/resource_data/NASA/"

def get_bat_chg_data(file_name):
    data = pd.read_csv(dir_path + file_name + '_chg.csv')

    grouped_avg = data.groupby(['vin', 'cycle']).agg({
        'Voltage_measured': ['max', 'min', 'mean'],
        'Current_measured': ['max', 'min', 'mean'],
        'Temperature_measured': ['max', 'min', 'mean'],
        'Current_charge': ['max', 'min', 'mean'],
        'Voltage_charge': ['max', 'min', 'mean'],
        'Time': 'max'
    }).reset_index()

    # 重命名聚合后的列名
    column_mapping = {
        'max': 'max_',
        'min': 'min_',
        'mean': 'mean_'
    }
    grouped_avg.columns = [column_mapping.get(col[1], '') + col[0] for col in grouped_avg.columns]

    return grouped_avg


def get_bat_dcg_data(file_name):
    data = pd.read_csv(dir_path + file_name + '_dcg.csv')

    columns_list = ['Voltage_measured', 'Current_measured', 'Temperature_measured', 'Current_load', 'Voltage_load', 'Time']
    new_columns = {'{}'.format(col): 'dcg_{}'.format(col) for col in columns_list}
    data = data.rename(columns=new_columns)
    grouped_avg = data.groupby(['vin', 'cycle']).agg({
        'dcg_Voltage_measured': ['max', 'min', 'mean'],
        'dcg_Current_measured': ['max', 'min', 'mean'],
        'dcg_Temperature_measured': ['max', 'min', 'mean'],
        'dcg_Current_load': ['max', 'min', 'mean'],
        'dcg_Voltage_load': ['max', 'min', 'mean'],
        'dcg_Time': 'max'
    }).reset_index()

    print(grouped_avg)
    # 重命名聚合后的列名
    column_mapping = {
        'max': 'max_',
        'min': 'min_',
        'mean': 'mean_'
    }

    grouped_avg.columns = [column_mapping.get(col[1], '') + col[0] for col in grouped_avg.columns]

    return grouped_avg


def meg_ah_and_pro_data(file_name):
    ah_data = pd.read_csv(dir_path + file_name + '_cap.csv')
    pro_chg_data = get_bat_chg_data(file_name)
    pro_dcg_data = get_bat_dcg_data(file_name)

    combined_df = pd.merge(pro_chg_data, pro_dcg_data, on=['vin', 'cycle'], how='left')
    combined_df = pd.merge(combined_df, ah_data, on=['cycle'], how='left')

    return combined_df




def main():
    Battery_list = ['B0005', 'B0006', 'B0007', 'B0018'] # 4 个数据集的名字
    for name1 in Battery_list:
        combined_df = meg_ah_and_pro_data(name1)
        print(combined_df)

        combined_df.to_csv(dir_path + '{}_pro_data.csv'.format(name1), index=False)

if __name__ == '__main__':
    main()