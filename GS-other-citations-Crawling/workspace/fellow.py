from utils import load_txt

fellows = load_txt("fellows.txt")
tar_list = []

for fellow in fellows:
    if fellow not in tar_list:
        tar_list.append(fellow)

with open('all_fellow.txt',mode='w',encoding='utf-8') as f:
    f.write("共计人数： ")
    f.write(str(len(tar_list)))
    f.write('\n')
    for fellow in tar_list:
        f.write(str(fellow))
        f.write('\n')

