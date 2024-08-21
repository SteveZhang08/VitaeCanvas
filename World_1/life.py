import shutil
import os
import json

global life_path
global alive

life_path = os.path.abspath(__file__)
floder_path = os.path.dirname(life_path)
alive = True

class life:
    def breed(me,iterations):
        '''生命繁殖'''
        shutil.copy(os.path.join(floder_path,me),os.path.join(floder_path,me+str(iterations)))

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
            with open(os.path.join(floder_path, "vita.gene"), 'w') as file:
                file.write(json_str)
            with open(os.path.join(floder_path, name + ".gene"), 'r') as file:  #重新读取基因文件
                loaded_DNA = str(json.load(file))
        return get.DNA(loaded_DNA)                                        #解码DNA数据

    def eat():
        '''进食'''
        try:
            with open(os.path.join(floder_path, "food"), 'r') as file:
                food_num = int(file.read().replace(" ","").replace("\n",""))
            if food_num > 0:
                food_num = food_num - 1
                with open(os.path.join(floder_path, "food"), 'w') as file:
                    file.write(str(food_num))
                return True
            else:
                return False
        except FileExistsError:
            return False

    def save(life_DNA):
        '''存储DNA信息，需提供参数：DNA'''
        json_str = json.dumps(life_DNA, indent=4)    #将DNA文件存储为json并写入基因文件
        with open(os.path.join(floder_path, "vita.gene"), 'w') as file:
            file.write(json_str)

    def load(name):
        '''读取DNA信息，需提供参数：生命名字（文件名）'''
        loaded_DNA = get.read(name)                                         #读取DNA信息
        return get.DNA(loaded_DNA)                                        #解码DNA数据

class get:
    def name():
        return os.path.basename(__file__).split(".")[0]

    def read(name):
        '''读取DNA数据'''
        try:
            while True:
                with open(os.path.join(floder_path, name + ".gene"), 'r') as file:  #尝试寻找基因文件
                    try:
                        loaded_DNA = str(json.load(file))   #读取基因文件内容并存储在DNA中
                        break
                    except:
                        pass
            return loaded_DNA
        except FileExistsError:
            return False

    def DNA(loaded_DNA):
        '''解码DNA数据'''
        life_DNA = {}
        DNA_list = loaded_DNA.replace("{","").replace("}","").replace(" ","").split(",")    #将基因文件转换成列表
        for i in DNA_list:
            life_DNA[i.split(":")[0].replace("'","")] = i.split(":")[1].replace("'","")     #将基因文件写入DNA
        life_DNA["iterations"] = int(life_DNA["iterations"])      #修正迭代数据,从字符串修正为整数类型
        life_DNA["food"] = int(life_DNA["food"])                  #修正能量数据,从字符串修正为整数类型
        return life_DNA 