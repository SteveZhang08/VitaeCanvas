from life import *

name = os.path.basename(__file__).split(".")[0] #获取文件名(去除后缀)
print(f"生命 {name} 已经启动。")

DNA = {}    #创建空的DNA字典

DNA_list = life.init(name)  #获取DNA信息

for i in DNA_list:
    DNA[i.split(":")[0].replace("'","")] = i.split(":")[1].replace("'","")          #将基因文件写入DNA
DNA["iterations"] = int(DNA["iterations"])      #修正迭代数据,从字符串修正为整数类型
DNA["food"] = int(DNA["food"])                  #修正能量数据,从字符串修正为整数类型
print(f"DNA数据:\n{DNA}")

while alive:
    if DNA["food"] <= 0:
        print(f"生命 {name} 死亡了。")
        alive = False
    if life.eat():
        DNA["food"] = DNA["food"] + 1
        print(f"生命 {name} 进食，当前能量值:", DNA["food"])
    else:
        print(f"生命 {name} 没找到食物，当前能量值:", DNA["food"])

#life.breed(me,iterations)