# coding: utf-8
import time
import pandas as pd
import gc
import os
from contextlib import contextmanager
@contextmanager
def timer(name):
    t0 = time.time()
    yield
    print(f'[{name}] done in {time.time() - t0:.0f} s')

# 读取数据
with timer ("loading ..."):
    part_1 = pd.read_csv('./dataset/round1_data1.txt',sep='$')
    part_2 = pd.read_csv('./dataset/round1_data2.txt',sep='$')
    part_1_2 = pd.concat([part_1,part_2])
    del part_1,part_2
    gc.collect()

part_1_2 = pd.DataFrame(part_1_2).sort_values('vid').reset_index(drop=True)
begin_time = time.time()
print('begin')
# 重复数据的拼接操作
def merge_table(df):
    df['field_results'] = df['field_results'].astype(str)
    if df.shape[0] > 1:
        merge_df = " ".join(list(df['field_results']))
    else:
        merge_df = df['field_results'].values[0]
    return merge_df
# 数据简单处理
print('find_is_copy')
print(part_1_2.shape)

with timer ("get size of gpb ..."):
    is_happen = part_1_2.groupby(['vid','table_id']).size().reset_index()
# 重塑index用来去重
    is_happen['new_index'] = is_happen['vid'] + '_' + is_happen['table_id']
    is_happen_new = is_happen[is_happen[0]>1]['new_index']

    part_1_2['new_index'] = part_1_2['vid'] + '_' + part_1_2['table_id']
    gp = part_1_2[['vid', 'table_id', 'field_results']].groupby(by=['vid', 'table_id'])[
        ['field_results']].count().reset_index().rename(index=str,
                                                        columns={'field_results': 'vid_table_cnt'})
    part_1_2 = part_1_2.merge(gp, on=['vid', 'table_id'], how='left')

with timer ("get isin ..."):
    unique_part = part_1_2[part_1_2['new_index'].isin(list(is_happen_new))]

with timer ("get sort_values ..."):
    unique_part = unique_part.sort_values(['vid','table_id'])

with timer ("get not is in ..."):
    no_unique_part = part_1_2[~part_1_2['new_index'].isin(list(is_happen_new))]

print('begin')
part_1_2_not_unique = unique_part.groupby(['vid','table_id']).apply(merge_table).reset_index()
part_1_2_not_unique.rename(columns={0:'field_results'},inplace=True)
print('xxx')
tmp = pd.concat([part_1_2_not_unique,no_unique_part[['vid','table_id','field_results']]])
# 行列转换
print('finish')
tmp = tmp.pivot(index='vid',values='field_results',columns='table_id')
tmp.to_csv('./dataset/tmp.csv')
print(tmp.shape)
print('totle time',time.time() - begin_time)


train = pd.read_csv('./dataset/round1_train.csv', encoding = 'utf-8')
test= pd.read_csv('./dataset/round1_test_b.csv', encoding = 'utf-8')
data=pd.read_csv('./dataset/tmp.csv',low_memory=False)
train_new = data[data['vid'].isin(train['vid'].values)]
test_new = data[data['vid'].isin(test['vid'].values)]
train_new.to_csv("./dataset/train.csv",encoding='utf-8' )
test_new.to_csv("./dataset/test_b.csv",encoding='utf-8')
