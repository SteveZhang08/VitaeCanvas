from life import *
import threading

global name
global DNA

name = os.path.basename(__file__).split(".")[0] #获取文件名(去除后缀)
print(f"生命 {name} 已经启动。")

DNA = life.init(name)  #获取DNA信息

print(f"DNA数据:\n{DNA}")

def Alive(weather):
    temp = life.load(name)["food"]
    return (weather and temp > 0)

def action():
    alive = True
    while alive:
        DNA = life.load(name)
        if DNA["food"] <= 0:
            print(f"生命 {name} 死亡了。")
            alive = False
            break
        if Alive(life.eat()):
            DNA["food"] = DNA["food"] + 1
            print(f"生命 {name} 进食，当前能量值:", DNA["food"])
        elif Alive(True):
            print(f"生命 {name} 没找到食物，当前能量值:", DNA["food"])
            DNA["food"] = DNA["food"] - 1
        life.save(DNA)

def dead():
    dead = life.load(name)
    if dead["food"] <= 0:
        print(f"生命 {name} 死亡了。")
        os._exit()

t1 = threading.Thread(target=action)
t2 = threading.Thread(target=dead)

t1.start()
t2.start()

t1.join()
t2.join()

#life.breed(me,iterations)