from life import *              #导入生命基本活动的库
import threading                #此库用来实现多线程

global name                     #一些需要全局变量的地方
global DNA
global temp

temp = "alive"                  #信息状态设置为"活动"

name = get.name(__file__)       #获取文件名(去除后缀)
Dead = "execution " + name      #设置死亡指令的内容
print(f"生命 {name} 已经启动。")

DNA = life.init(name)           #初始化,并获取DNA信息
print(f"DNA数据:\n{DNA}")

def DT():
    return get.Temperature() - DNA["midTemperature"]

def Alive(whether):             #先判断生命是否存活
    return (whether and temp != "dead")

def action():                   #定义生命的活动
    alive = True                #生命存活
    while alive:                #当生命存活时
        DNA = life.load(name)   #加载DNA信息

        if DNA["food"] <= 0 or temp == "dead":  #判断生命是否死亡
            '''如果上帝创造了生命,那么死亡一定是写死在生命逻辑中的首选项'''
            print(f"生命 {name} 死亡了。")
            break                          #如果已经死亡,程序退出

        #下列判断用法与普通的基本if一样,只是判断条件填写在Alive()的括号里,运行时首先会确认生命是否是存活的,如果生命是死的则不会执行该活动

        if Alive(life.eat()):   #life库中的函数"life.eat()",不需要参数,返回值是True或False(True代表完成进食,False代表无法进食)                  
            DNA["food"] = DNA["food"] + 1   #生命进食,能量增加,将DNA信息中的"food"项的值设置为原来的值+1
            print(f"生命 {name} 进食，当前能量值:", DNA["food"])
        elif Alive(True):       #此处用来代替原来的if else中的else,该情况即life.eat()的返回值为False
            DNA["food"] = DNA["food"] - 1   #生命未进食,因寻找食物消耗能量
            #print(f"生命 {name} 没找到食物，当前能量值:", DNA["food"])

        if Alive(DNA["food"] >= 200):
            DNA["food"] = int(DNA["food"] / 2)
            life.save(name,DNA)
            life.breed(name,DNA["iterations"])
            print(f"生命 {name} 完成了一次分裂繁殖")

        if abs(DT()) >= 10 and abs(DT()) < 15:
            DNA["food"] = DNA["food"] - 1
            print("温度小变化，能量值-1")
        elif abs(DT()) >= 15 and abs(DT()) < 20:
            DNA["food"] = DNA["food"] - 2
            print("温度稍变化,能量值-2")
        elif abs(DT()) >= 20 and abs(DT()) < 25:
            DNA["food"] = DNA["food"] - 3
            print("温度变化过大，能量值-3")
        elif abs(DT()) >= 25:
            DNA["food"] = DNA["food"] - (abs(DT()) - 25) - 3
            print(f"温度不适宜当前生命生存!,能量值-{abs(DT()) - 22}")
        
        if Alive(True):         #此处是单纯判断生命是否活着,如果生命已经死了,就不会存储DNA信息
            life.save(name,DNA)      #如果生命活着,则存储DNA信息
    
    sys.exit()

def dead():                     #定义接受死亡指令的函数
    while True:
        if Dead in get.event() or "all" in get.event(): #get.event() 此函数不需要参数,返回值为str类型,内容为指令内容
            '''如果接受的指令是死亡指令,审判就会降临'''
            alive = False       #生命状态设置为死亡
            temp = "dead"       #发送死亡信息
            DNA["food"] = -114514       #篡改生命DNA数据,确保死透
            life.save(name,DNA)         #存储DNA信息
            print(f"生命 {name} 被处决了。")
            exit()              #程序退出

t1 = threading.Thread(target=action)    #创建多线程 t1 ,执行的函数为 action()
t2 = threading.Thread(target=dead)      #创建多线程 t2 ,执行的函数为 dead()

t1.start()                      #启动线程 t1
t2.start()                      #启动线程 t2
#函数 action() 和 dead() 将同时运行
t1.join()                       #等待线程 t1 结束
t2.join()                       #等待线程 t2 结束