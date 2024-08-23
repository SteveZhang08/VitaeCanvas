import shutil
import os
import json
import sys

global life_path
global alive

life_path = os.path.abspath(__file__)
life_floder_path = os.path.dirname(life_path)
alive = True

class life:
    def breed(name,iterations):
        '''生命繁殖'''
        name1 = name + ".py"
        iterations = int(iterations) + 1
        name2 = name+str(iterations)
        shutil.copy(os.path.join(life_floder_path,name1),os.path.join(life_floder_path,name2+".py"))
        itDna = life.load(name)
        itDna["name"] = name + str(iterations)
        itDna["iterations"] = str(iterations)
        life.save(name2,itDna)

    def init(name):
        '''生命初始化'''
        try:
            loaded_DNA = get.read(name)       #读取DNA数据
        except:   #如果没有找到基因文件,则创建初始DNA
            life_DNA = {
            "iterations": 1,
            "name": name,
            "food":10
            }
            json_str = json.dumps(life_DNA, indent=4)    #将DNA文件存储为json并写入基因文件
            with open(os.path.join(life_floder_path, "vita.gene"), 'w') as file:
                file.write(json_str)
            with open(os.path.join(life_floder_path, name + ".gene"), 'r') as file:  #重新读取基因文件
                loaded_DNA = str(json.load(file))
        return get.DNA(loaded_DNA)                                        #解码DNA数据

    def eat():
        '''进食'''
        try:
            with open(os.path.join(life_floder_path, "food"), 'r') as file:
                food_num = int(file.read().replace(" ","").replace("\n",""))
            if food_num > 0:
                food_num = food_num - 1
                with open(os.path.join(life_floder_path, "food"), 'w') as file:
                    file.write(str(food_num))
                return True
            else:
                return False
        except FileExistsError:
            return False

    def save(name,life_DNA):
        '''存储DNA信息，需提供参数：生命名字（文件名）, DNA'''
        json_str = json.dumps(life_DNA, indent=4)    #将DNA文件存储为json并写入基因文件
        with open(os.path.join(life_floder_path, name + ".gene"), 'w') as file:
            file.write(json_str)

    def load(name):
        '''读取DNA信息，需提供参数：生命名字（文件名）'''
        loaded_DNA = get.read(name)                                         #读取DNA信息
        return get.DNA(loaded_DNA)                                        #解码DNA数据

class get:
    def name(file):
        '''请在参数中填入 __file__ 以获得文件名(不带后缀名)'''
        return os.path.basename(file).split(".")[0]

    def read(name):
        '''读取DNA数据'''
        try:
            with open(os.path.join(life_floder_path, name + ".gene"), 'r') as file:  #尝试寻找基因文件
                loaded_DNA = str(json.load(file))   #读取基因文件内容并存储在DNA中
            return loaded_DNA
        except FileExistsError:
            return False

    def any_read(name):
        '''读取任意数据'''
        try:
            with open(os.path.join(life_floder_path, name), 'r') as file:  #尝试寻找文件
                loaded = str(json.load(file))   #读取文件内容并存储在字典中
            return loaded
        except FileExistsError:
            return False
    
    def dict(loaded):
        '''解析字典文件'''
        loaded_Dict = {}
        list = loaded.replace("{","").replace("}","").replace(" ","").split(",")
        for i in list:
            loaded_Dict[i.split(":")[0].replace("'","")] = i.split(":")[1].replace("'","")
        return loaded_Dict

    def DNA(loaded_DNA):
        '''解码DNA数据'''
        life_DNA = {}
        DNA_list = loaded_DNA.replace("{","").replace("}","").replace(" ","").split(",")    #将基因文件转换成列表
        for i in DNA_list:
            life_DNA[i.split(":")[0].replace("'","")] = i.split(":")[1].replace("'","")     #将基因文件写入DNA
        life_DNA["iterations"] = int(life_DNA["iterations"])      #修正迭代数据,从字符串修正为整数类型
        life_DNA["food"] = int(life_DNA["food"])                  #修正能量数据,从字符串修正为整数类型
        return life_DNA 
    
    def event():
        '''获取事件信息'''
        try:
            with open(os.path.join(life_floder_path, "event"), 'r') as file:
                re = file.read()
            return re.replace("\n","")
        except FileExistsError:
            print("event 文件不存在!")
            return FileExistsError

    def Error():
        '''报错退出法，无需提供参数'''
        return 1 + "1"

    def Temperature():
        environment = get.dict(get.any_read("environment"))
        environment["temperature"] = int(environment["temperature"])
        return environment["temperature"]

    def any_save(name,dict):
        '''存储信息，需提供参数：完整文件名, 字典'''
        json_str = json.dumps(dict, indent=4)    #将字典存储为json并写入文件
        with open(os.path.join(life_floder_path, name), 'w') as file:
            file.write(json_str)