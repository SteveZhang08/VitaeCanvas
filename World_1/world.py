from life import *
def execution(name):
    while True:
        DNA = life.load(name)
        DNA["food"] = -114514
        life.save(DNA)
        DNA = life.load(name)
        if DNA["food"] <= 0:
            break

while True:
    i = input("$ >")
    if i.startswith("execution"):
        name = i.split(" ")[1]
        for i in range(10):
            execution(name)
        print("Finished.")