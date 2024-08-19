from life import *
import json

name = os.path.basename(__file__).split(".")[0] #获取文件名(去除后缀)

DNA = {}    #创建空的DNA字典

try:
    with open(os.path.join(floder_path, name + ".gene"), 'r') as file:  #尝试寻找基因文件
        loaded_DNA = str(json.load(file))   #读取基因文件内容并存储在DNA中
except FileNotFoundError:   #如果没有找到基因文件,则创建初始DNA
    DNA = {
    "iterations": 1,
    "name": name
    }
    json_str = json.dumps(DNA, indent=4)    #将DNA文件存储为json并写入基因文件
    with open(os.path.join(floder_path, "vita.gene"), 'w') as file:
        file.write(json_str)
    with open(os.path.join(floder_path, name + ".gene"), 'r') as file:  #重新读取基因文件
        loaded_DNA = str(json.load(file))

DNA_list = loaded_DNA.replace("{","").replace("}","").replace(" ","").split(",")    #将基因文件转换成列表
for i in DNA_list:
    DNA[i.split(":")[0].replace("'","")] = i.split(":")[1].replace("'","")          #将基因文件写入DNA
DNA["iterations"] = int(DNA["iterations"])      #修正迭代数据,从字符串修正为整数类型
print(DNA)

#life.breed(me,iterations)