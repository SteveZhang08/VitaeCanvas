from life import *
import threading

global name
global DNA
global temp

temp = "alive"

name = get.name(__file__)   #获取文件名(去除后缀)
Dead = "execution " + name
print(f"生命 {name} 已经启动。")

DNA = life.init(name)  #获取DNA信息
print(f"DNA数据:\n{DNA}")

def Alive(weather):
    #temp = life.load(name)["food"]
    return (weather and temp != "dead")

def action():
    alive = True
    while alive:
        DNA = life.load(name)
        #print("hhhhhh")
        if DNA["food"] <= 0 or temp == "dead":
            print(f"生命 {name} 死亡了。")
            exit()
        if Alive(life.eat()):
            DNA["food"] = DNA["food"] + 1
            print(f"生命 {name} 进食，当前能量值:", DNA["food"])
        elif Alive(True):
            print(f"生命 {name} 没找到食物，当前能量值:", DNA["food"])
            DNA["food"] = DNA["food"] - 1
        if Alive(True):
            life.save(DNA)

def dead():
    while True:
        if Dead in get.event():
            alive = False
            temp = "dead"
            DNA["food"] = -114514
            life.save(DNA)
            print(f"生命 {name} 死亡了。")
            exit()

t1 = threading.Thread(target=action)
t2 = threading.Thread(target=dead)

t1.start()
t2.start()

t1.join()
t2.join()

#life.breed(me,iterations)