#本程序从data/cite_info.json文件内，读取所有引用文章的标题、作者、发表位置、年份，进行自引排除和他引统计
#最终生成result/result.txt文件：内部统计： 总引用次数 自引次数 他引次数 每篇他引文章对应的作者+标题+发表位置+年份（按引用格式）
#要在main里面按格式写入本文作者

from utils import load_json, save_json

# DBLP_BASE_URL = 'http://dblp.uni-trier.de/'
# PUB_SEARCH_URL = DBLP_BASE_URL + "search/publ/"
# Qibin Hou, PengTao Jiang, Yunchao Wei, Ming-Ming Cheng

def main():
        #本文作者     考虑query()，按如下格式写入目前作者
        current_authors = ['Hou Qibin','Jiang PengTao','Wei Yunchao','Cheng Ming-Ming']
#此处with open 后已经获得目标文章的被引用列表（文章标题+作者+发表位置+年份），进行自引删除和他引统计，他引次数会打印出来，他引文章会保存到tayin.json

        tayin = 1  #他引统计

        txt_path = 'result/result.txt'
        file = open(txt_path, mode='w', encoding='utf-8')  # 用utf-8编码，防止一些作者名字不能写入txt（默认gbk）


        all_cite_info  = load_json('data/self_cite_info.json')
        for cite_info in all_cite_info:    #cite_info 为 list:10
            for item in cite_info:         #item单位为单篇引用文章的所有信息，item的格式为string，即所有信息都为字符串
                item = item.split("\n")

                #有些文章可能没有年份和发布位置信息
                year = 'NULL'
                booktitle = 'NULL'
                #以下均为 string 类型
                for info in item:         #字符串
                    if 'year' in info:
                        year = info
                    elif ('title' in info) and ('booktitle' not in info):
                        title = info
                    elif 'author' in info:
                        authors = info
                    elif ('booktitle' in info) or ('journal' in info):
                        booktitle = info


                #标题
                title_left_index = title.index('{')+1
                title_right_index = title.index('}')
                title = title[title_left_index:title_right_index]

                #作者
                authors_left_index = authors.index('{')+1
                authors_right_index = authors.index('}')
                authors = authors[authors_left_index:authors_right_index]

                #作者自引判断：
                authors = authors.replace(',','')
                authors_list = authors.split(" and ")    #作者列表
                ziyin = is_ziyin(authors_list,current_authors)     #0为他引 1为自引

                #发表位置
                if booktitle != 'NULL':
                    booktitle_left_index = booktitle.index('{')+1
                    booktitle_right_index = booktitle.index('}')
                    booktitle = booktitle[booktitle_left_index:booktitle_right_index]

                #年份
                if year != 'NULL':
                    year_left_index = year.index('{')+1
                    year_right_index = year.index('}')
                    year = year[year_left_index:year_right_index]

                #他引文章写入记录
                if ziyin == 0:
                    #写入txt中
                    write_to_txt(file,tayin,authors_list,title,booktitle,year)
                    tayin += 1

        file.close()

#作者自引判断：   传入作者列表    返回1表示自引，0表示他引
def is_ziyin(authors,current_authors):
    isziyin = 0
    for author in authors:  # 是否自引的判断
        if author in current_authors:  # 自引
            isziyin = 1
    return isziyin

#按照引用格式，把他引写入到txt文件中
def write_to_txt(file,tayin,authors_list,title,booktitle,year):

    file.write('[')
    file.write(str(tayin))
    file.write(']')

    authors = str(authors_list).replace('\'','')
    file.write(authors[1:len(authors)-1])
    file.write('. ')
    file.write(title)
    file.write('.')

    file.write(' ')
    file.write(booktitle)
    file.write(',')

    file.write(' ')
    file.write(year)
    file.write('\n')

    return


if __name__ == "__main__":
    main()