import random

# 定语从句语法
grammar = '''
战斗 => 人物施法 。
人物施法 => 施法1 | 施法2 | 施法3
施法1 => 张飞 使用 技能1 结果1
技能1 => 01 | 02 | 03 | 召唤师技能
01 => 画地为牢 获得 效果2
02 => 守护机关 获得 效果2
03 => 狂兽血性 获得 效果2
结果1 => 结果人物1 获得 效果
结果人物1 => 关羽 | 赵云 | 典韦 | 许褚 | 刘备 | 黄忠 | 曹操 | 鲁班七号 | 貂蝉
施法2 => 关羽 使用 技能2 结果2
技能2 => 单刀赴会 | 青龙偃月 | 刀锋铁骑 | 召唤师技能
结果2 => 结果人物2 获得 效果
结果人物2 => 张飞 | 赵云 | 典韦 | 许褚 | 刘备 | 黄忠 | 曹操 | 鲁班七号 | 貂蝉
施法3 => 赵云 使用 技能3 结果3
技能3 => 04 | 05 | 06
结果3 => 结果人物2 获得 效果
结果人物3 => 张飞 | 关羽 | 典韦 | 许褚 | 刘备 | 黄忠 | 曹操 | 鲁班七号 | 貂蝉
04 => 惊雷之龙 获得 效果2
05 => 破云之龙 获得 效果2
06 => 天翔之龙 获得 效果2
召唤师技能 => 惩戒 | 终结
获得 => 损失 
效果 => 数值 状态
效果2 => 数值 状态2
数值 => 1 | 1000 |5000 | 100 
状态 => 生命
状态2 => 法力
'''

# 得到语法字典
def getGrammarDict(gram, linesplit = "\n", gramsplit = "=>"):
    #定义字典
    result = {}

    for line in gram.split(linesplit):
        # 去掉首尾空格后，如果为空则退出
        if not line.strip(): 
            continue
        expr, statement = line.split(gramsplit)
        result[expr.strip()] = [i.split() for i in statement.split("|")]
    #print(result)
    return result

# 生成句子
def generate(gramdict, target, isEng = False):
    if target not in gramdict: 
        return target
    find = random.choice(gramdict[target])
    #print(find)
    blank = ''
    # 如果是英文中间间隔为空格
    if isEng: 
        blank = ' '
    return blank.join(generate(gramdict, t, isEng) for t in find)

gramdict = getGrammarDict(grammar)
print(generate(gramdict,"战斗"))
print(generate(gramdict,"战斗", True))


