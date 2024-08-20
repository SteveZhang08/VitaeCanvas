import shutil
import os
import json

global life_path

life_path = os.path.abspath(__file__)
floder_path = os.path.dirname(life_path)
alive = True

class life:
    def breed(me,iterations):
        '''生命繁殖'''
        shutil.copy(os.path.join(floder_path,me),os.path.join(floder_path,me+str(iterations)))

    def init(n1):
        '''生命初始化'''
        try:
            with open(os.path.join(floder_path, n1 + ".gene"), 'r') as file:  #尝试寻找基因文件
                loaded_DNA = str(json.load(file))   #读取基因文件内容并存储在DNA中
        except FileNotFoundError:   #如果没有找到基因文件,则创建初始DNA
            DNA = {
            "iterations": 1,
            "name": n1,
            "food":10
            }
            json_str = json.dumps(DNA, indent=4)    #将DNA文件存储为json并写入基因文件
            with open(os.path.join(floder_path, "vita.gene"), 'w') as file:
                file.write(json_str)
            with open(os.path.join(floder_path, n1 + ".gene"), 'r') as file:  #重新读取基因文件
                loaded_DNA = str(json.load(file))
        DNA_list = loaded_DNA.replace("{","").replace("}","").replace(" ","").split(",")    #将基因文件转换成列表
        return DNA_list

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

class get:
    def name():
        return os.path.basename(__file__).split(".")[0] 