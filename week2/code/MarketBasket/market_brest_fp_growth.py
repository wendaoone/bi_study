import pandas as pd
import fptools as fp
import collections

# 读取数据
# datas=pd.read_csv('./Market_Basket_Optimisation.csv',header=None)
# # 通过迭代器方式对pd读取出来的数据转成list数组，并且出去其中的nan
# itemsets = [[y for y in x if pd.notna(y)] for x in datas.values.tolist()]
# itemDits = {}

'''
整体流程
加载数据，并且对数据清洗，去除nan数据

计算订单中每个商品出现的次数，以及最小支持度，并且对其由大到小排序

根据最小支持度阈值获取符合条件的商品列表

根据商品列表对每一个订单所对应的商品进行排序

根据排序订单项构建fp-growth树

从最后一个向上遍历得到条件模式基对应的平凡项集

计算对应的支持度，置信度，提升度

'''
# 整体流程
# 加载数据，并且对数据清洗，去除nan数据
is_find_min_support = False


def loadUseAbleData():
    datas = pd.read_csv('./Market_Basket_Optimisation.csv', header=None)
    # 通过迭代器方式对pd读取出来的数据转成list数组，并且出去其中的nan
    return [[y for y in x if pd.notna(y)] for x in datas.values.tolist()]


def directItem(itemList, minSup, minItemCount):
    """
    把商品标签化，并且映射为字典，然后计算订单中每个商品出现的次数，以及最小支持度，并且对其由大到小排序
    :param itemList: 商品集
    :param minSup: 最小支持度
    :param minItemCount: 所需要的商品数量集合，用于根据业务筛选推荐的商品总数 当is_find_min_support=true时候 该项比较重要
    :return:
    """
    itemDits = {}
    # 遍历数组
    for items in itemList:
        for item in items:
            if item not in itemDits.keys():
                itemDits[item] = 1
            else:
                itemDits[item] = itemDits[item] + 1
    # 当为获取最小支持度时候
    if is_find_min_support:
        itemDitsList = sorted(itemDits.items(), key=lambda item: item[1], reverse=True)[:minItemCount]
        print('第{0}个商品所对应的支持度为{1},对应的商品出现的频次为：{2},总订单数{3}'.format(minItemCount, itemDitsList[-1][1] / len(itemList),
                                                                  itemDitsList[-1][1], len(itemList)))
        print(itemDitsList)
        return dict(itemDitsList)
    minCount = minSup * len(itemList)
    itemDits = {k: v for k, v in itemDits.items() if v > minCount}
    return sorted(itemDits.items(), key=lambda item: item[1], reverse=True)


def sortedAndFiltter(itemList, orgItemList):
    """
    对原始数据根据 itemsList排序，并将不存在于itemsList中对商品过滤掉
    :param itemList:
    :param itemsList: 目标商品列表
    :param orgItemList: 原始订单所对应的商品列表
    """
    itemSet = set(k[0] for k in itemList)
    itemDict = dict(itemsList)
    for index in range(len(orgItemList)):
        orgItemList[index] = list(set(orgItemList[index]).intersection(itemSet))
        orgItemList[index] = sorted(orgItemList[index], key=lambda s: itemDict[s], reverse=True)
    return itemDict, orgItemList


class FpNode(object):
    def __init__(self, code, parent=None):
        """
        树的基本结构单元
        """
        self.code = code
        self.child = collections.defaultdict()
        self.parent = parent
        # 说明是初始化的
        if parent is None:
            self.count = 0
            return
        self.count = 1
        parent.child.setdefault(code, self)
        return

    def add_count(self):
        self.count += 1
        return


class tree(object):
    """
     构建的fp-growth有且只有一个根节点，元素值为None
    """

    def __init__(self, itemDict, transaction_count):
        self.transaction_count = transaction_count
        self.root = FpNode(None, None)
        # 用于快速检索到所有同一个code的所有树叶信息 格式为 code：[]
        self.fpNodeDict = collections.defaultdict()
        self.itemDict = itemDict
        return

    def insert_node(self, transaction_items):
        """
        根据指定订单中的所有商品信息构建树的一条路径
        """
        parent = self.root
        for item in transaction_items:
            code = item  # hash(item)
            currentNode = parent.child.get(code)
            # 如果当前节点为空说明该商品还没有加入关系树木中
            if currentNode is None:
                currentNode = FpNode(code, parent)
                parent.child[code] = currentNode
                codeItems = self.fpNodeDict.get(code, [])
                codeItems.append(currentNode)
                self.fpNodeDict.setdefault(code, codeItems)
                parent = currentNode
                continue
                # 当前节点已经存在，直接对节点数量加一
            currentNode.add_count()
            parent = currentNode
        return self

    def build_tree(self, transaction):
        """
        根据所有订单构建树
        """
        for item in transaction:
            self.insert_node(item)
        return self

    def condition_merge(self, conditionList):
        """
        通过递归方式对同一条链路上的商品合并，获取其上所有可组合的频繁项集
        :param conditionList:链路上的所有商品
        :return: [(集合:count),(集合:count)]
        conditionList 中只有一个元素时候 则表示已经把所有情况组合完成
        """
        if len(conditionList) <= 1:
            return conditionList
        mergedConditionList = []
        for conditionItemIndex in range(len(conditionList)):
            conditionItem = conditionList[conditionItemIndex]
            groupConditionList = []
            for item in conditionList[conditionItemIndex+1:]:
                itemSet = set(item[0])
                itemSet.update(conditionItem[0])
                groupConditionList.append((itemSet, conditionItem[1]))
            # 对于同一层采用递归调用方式如
            #         A B C D E
            #           合成 AB AC AD AE后把它当作一个整体 做输入条件
            if len(groupConditionList) == 0:
                continue
            mergedConditionList.extend(self.condition_merge(groupConditionList))
        conditionList.extend(mergedConditionList)
        return conditionList

    def condition_frequent_item(self, conditionNodeList, comdition_item_count,min_threshold = 0):
        """
        对同一个商品的所有路径进行组合，得到条件模式基的频繁项集以及对应频次，并把各个路径的相同的平凡项集合并为同一个，数量叠加一起
        :param conditionNodeList: 同一个商品的所有路径列表
        :param min_threshold: 最小阈值
        """
        allConditionNodeList = []
        # 对不同路径上的商品进行组合，得到频繁项集
        for node in conditionNodeList:
            count = node.count
            parent = node.parent
            conditionList = []
            while parent.code is not None:
                code = parent.code
                conditionList.append(({code}, count))
                parent = parent.parent
            # 对 conditionList 进行自由组合 先从k=2开始组合
            allConditionNodeList.extend(self.condition_merge(conditionList))
        item_dict = {}
        for item in allConditionNodeList:
            item_tuple = tuple(item[0]);
            count = item_dict.pop(item_tuple, 0) + item[1]
            item_dict.setdefault(item_tuple, count)

        return [(k,v) for k, v in item_dict.items() if v >= min_threshold]

    def frequent_item_sets(self, items_list, min_sup=None):
        """
         获取条件基的频繁项集
         从排序最后的叶子作为条件模式基 向上获取条件频繁项集,
         然后根据最小支持度预集合得到最终频繁项集
        """
        minCount = min_sup * self.transaction_count
        for item in reversed(items_list):
            result = self.condition_frequent_item(self.fpNodeDict.get(item[0]),item[1], minCount)
            if len(result) > 0:
                print("条件模式基商品为：{},对应的可推荐的{}".format(item[0],result))

        return self


if __name__ == "__main__":
    is_find_min_support = False
    orgItemList = loadUseAbleData()
    itemsList = directItem(orgItemList, 0.0056, 100)
    itemDict, orgItemList = sortedAndFiltter(itemsList, orgItemList)
    tree(itemDict, len(orgItemList)).build_tree(orgItemList).frequent_item_sets(itemsList, 0.0056)
