from life import*

class base():
    '''This contains the basic activities of the paramecium life type.

    这里包含着草履虫生命类型的基本生命活动'''

    def inhale(num: int):
        '''inhale  吸气'''
        TempDict = get.dict(get.any_read("./argument/environment"))
        TempDict["oxygen"] = int(TempDict["oxygen"])
        oxygen = TempDict["oxygen"]
        if oxygen - num >= 0:
            oxygen = oxygen - num
            re_Value = True
            TempDict["oxygen"] = oxygen
            get.any_save("./argument/environment", TempDict)
        else:
            re_Value = False
        return re_Value

    def exhale(num: int):
        '''exhale  呼气'''
        TempDict = get.dict(get.any_read("./argument/environment"))
        TempDict["co2"] = int(TempDict["co2"])
        co2 = TempDict["co2"]
        co2 = co2 + num
        TempDict["co2"] = co2
        get.any_save("./argument/environment", TempDict)
