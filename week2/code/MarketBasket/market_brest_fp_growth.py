import pandas as pd
import fptools as fp
# 读取数据
datas=pd.read_csv('./Market_Basket_Optimisation.csv',header=None)
# 通过迭代器方式对pd读取出来的数据转成list数组，并且出去其中的nan
itemsets = [[y for y in x if pd.notna(y)] for x in datas.values.tolist()]
itemDits = {}


