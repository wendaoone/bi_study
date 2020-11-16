import pandas as pd
import fptools as fp
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
# 读取数据
datas=pd.read_csv('./Market_Basket_Optimisation.csv',header=None)
# 通过迭代器方式对pd读取出来的数据转成list数组，并且出去其中的nan
itemsets = [[y for y in x if pd.notna(y)] for x in datas.values.tolist()]
itemDits={}
for items in itemsets:
    for item in items:
        if item not in itemDits.keys():
            itemDits[item] = 1
        else:
            itemDits[item] = itemDits[item] + 1
itemDits = sorted(itemDits.items(), key=lambda item:item[1], reverse=True)
# print(itemDits)
tree,ranks=fp.build_tree(itemsets,356)
print(sorted(ranks, key=lambda item:item[1], reverse=True))
ss=fp.frequent_itemsets(itemsets,356)
#
# fis=[iset for iset in ss]
# mfis=[iset for iset in fp.maximal_frequent_itemsets(itemsets,356)]

# 转换为算法可接受模型（布尔值）one-hot操作
te = TransactionEncoder()
df_tf = te.fit_transform(itemsets)
df = pd.DataFrame(df_tf, columns=te.columns_)

# 设置支持度求频繁项集
frequent_itemsets = apriori(df, min_support=0.02, use_colnames=True)
# 求关联规则,设置最小置信度为0.15
print(frequent_itemsets)
rules = association_rules(frequent_itemsets,  min_threshold=0.15)
# 设置最小提升度
rules = rules.drop(rules[rules.lift < 1.0].index)
# # 设置标题索引并打印结果
rules.rename(columns={'antecedents': 'from', 'consequents': 'to', 'support': 'sup', 'confidence': 'conf'}, inplace=True)
rules = rules[['from', 'to', 'sup', 'conf', 'lift']]
print(rules)