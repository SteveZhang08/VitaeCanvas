import shutil
import os

global life_path

life_path = os.path.abspath(__file__)
print(life_path)
floder_path = os.path.dirname(life_path)

class life:
    def breed(me,iterations):
        shutil.copy(os.path.join(floder_path,me),os.path.join(floder_path,me+str(iterations)))