from life import *

name = os.path.basename(__file__).split(".")[0] #获取文件名(去除后缀)
print(f"生命 {name} 已经启动。")

DNA = life.init(name)  #获取DNA信息

print(f"DNA数据:\n{DNA}")

while alive:
    life.load(name)
    if DNA["food"] <= 0:
        print(f"生命 {name} 死亡了。")
        alive = False
        break
    if life.eat():
        DNA["food"] = DNA["food"] + 1
        print(f"生命 {name} 进食，当前能量值:", DNA["food"])
    else:
        print(f"生命 {name} 没找到食物，当前能量值:", DNA["food"])
        DNA["food"] = DNA["food"] - 1
    life.save(DNA)

#life.breed(me,iterations)