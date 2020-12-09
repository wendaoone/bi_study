#from surprise import SVD
from surprise import Dataset
from surprise import Reader
from surprise import BaselineOnly, KNNBasic, NormalPredictor,SlopeOne
from surprise import accuracy
from surprise.model_selection import KFold
#import pandas as pdkjx

# 数据读取
reader = Reader(line_format='user item rating timestamp', sep=',', skip_lines=1)
data = Dataset.load_from_file('./ratings.csv', reader=reader)
train_set = data.build_full_trainset()

# ALS优化用于解决稀疏矩阵分解的问题
# ALS先固定第一个变量，然后求解第二个变量。之后固定第二个变量，求解第一个变量。如此交替迭代直至收敛或者达到最大迭代次数
bsl_options = {'method': 'als','n_epochs': 5,'reg_u': 12,'reg_i': 5}

# SGD优化 随机梯度下降的速度较快
# 虽然理论上随机梯度下降的最终解是在最优解附近在这次预测中RMSE也是最高
#bsl_options = {'method': 'sgd','n_epochs': 5}
algo = BaselineOnly(bsl_options=bsl_options)
#algo = BaselineOnly()
#algo = NormalPredictor()


# 使用SlopeOne算法 SlopeOne基本上全对内存占用更高
# 当内存少时进行K折交叉验证第一次成功 第二次显示内存不足应该是K折交叉验证不释放内存的缘故
algo = SlopeOne()
algo.fit(train_set)
'''
# 定义K折交叉验证迭代器，K=3
kf = KFold(n_splits=3)
for trainset, testset in kf.split(data):
    # 训练并预测
    algo.fit(trainset)
    predictions = algo.test(testset)
    # 计算RMSE
    accuracy.rmse(predictions, verbose=True)
'''
uid = str(196)
iid = str(302)
# 输出uid对iid的预测结果
pred = algo.predict(uid, iid, r_ui=4, verbose=True)



