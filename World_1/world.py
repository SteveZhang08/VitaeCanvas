from life import *

def execution(name):
    with open(os.path.join(life_floder_path, "event"), 'w') as file:
        write = "execution " + name
        file.write(write)
def temperature(temperature):
    environment = {}
    environment["temperature"] = int(temperature)
    get.any_save("environment",environment)

while True:
    i = input("$ >")
    if i.startswith("execution") or i.startswith("kill"):
        name = i.split(" ")[1]
        execution(name)
        print("[file:event] Finished.")
        #with open(os.path.join(life_floder_path, "event"), 'w') as file:
        #    pass

    elif i.startswith("set"):
        set = i.split(" ")[1]
        if set == "temperature" or set == "T":
            temperature(int(i.split(" ")[2]))
            print(f"[file:enveronment] 当前温度已被设置为 {get.Temperature()}")
            
    elif i == "exit":
        exit()