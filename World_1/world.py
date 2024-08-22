from life import *
def execution(name):
    with open(os.path.join(life_floder_path, "event"), 'w') as file:
        write = "execution " + name
        file.write(write)

while True:
    i = input("$ >")
    if i.startswith("execution"):
        name = i.split(" ")[1]
        execution(name)
        print("Finished.")