#把包含了引用文章作者列表的信息。保存到articles_id_{parallel_id}.json里面

#本程序主要：
#   排除他引并统计：总引用次数 自引次数 他引次数 输出他引文章的信息列表，以上四项保存到result/result.txt中

# tayin.json保存了所有他引文章
# 命令行打印他引和自引次数
# 保存引用信息到result/result.txt中

#**********指定参数：
target_id = 89    #要爬取google scholar 主页上的第几篇

from utils import load_json, save_json, load_txt
from pathlib import Path
from bs4 import BeautifulSoup
import time
import requests
import json

DBLP_BASE_URL = 'http://dblp.uni-trier.de/'
PUB_SEARCH_URL = DBLP_BASE_URL + "search/publ/"

def main():

    ieee_fellow = []
    file = load_json("fellow_results.json")
    for item in file:
        name = ''
        a = item[0]
        a = a.replace(',','')
        #姓氏在前 → 名字在前
        a = a.split(' ')
        last_name = a[0]    #姓氏
        for i in range(0,len(a)-1):
            a[i] = a[i+1]
        a[len(a)-1] = last_name
        for i in range(0,len(a)):
            name += a[i]
            if i < len(a)-1:
                name += ' '
        ieee_fellow.append(name)

#调试
    parallel_id = 0      #0~parallel_count之间的数，每parallel_count篇文章才执行爬取引用的作者列表

    save_path = Path("data/articles_id_{}.json".format(parallel_id))
    if not save_path.exists():
        base_path = Path("data/articles.json")     #base_path里面有去了标签的引用列表
    else:
        base_path = save_path


    articles = load_json(base_path)
    new_articles = articles.copy()

    for article_id, article in enumerate(articles):    #对作者的每篇paper

        #-----------只爬取所有引用第target_id篇论文的文章的作者列表--------
        if article_id != target_id:          #这里可以指定爬取哪篇文章
            continue


        current_authors = query(new_articles[article_id]["name"])       #目标文章的发表信息
        print("本文作者：",current_authors)

        if "cite_list" not in article:                 #无引用则跳过
            continue


        cite_articles = article["cite_list"]
        for cite_article_id, cite_article in enumerate(cite_articles):  #每篇引用的文章
            if "author" in cite_article:       #如果有作者列表了，就跳过（但是一般都没有，原作者是通过下面query函数找）
                continue
            title = cite_article["title"]
            while True:
                try:
                    authors = query(title)     #根据引用文章标题，查询作者
                    break
                except Exception as e:
                    print(e)
                    time.sleep(1)


            print("{}/{} {} {}".format(cite_article_id, len(cite_articles), title, " ".join(authors)))


            new_articles[article_id]["cite_list"][cite_article_id]["author"] = authors                   #加入了作者信息，authors为list型

            save_json(new_articles, save_path)    #把包含了引用文章作者列表的信息，保存到articles_id_0.json里面


#此处with open 后已经获得目标文章的被引用列表（文章标题+作者），进行自引删除和他引统计，他引次数会打印出来，他引文章会保存到tayin.json
        with open('data/target.json','w') as f:   #记录作者名单
            json.dump(new_articles[article_id]["cite_list"],f)      #写下该文章的cite_list：引用文章名称及作者

            ziyin_times = 0  # 自引次数
            tayin=[]         # 他引列表

            #下一步开发：将target.json中的自引词条去掉，并统计剩余的他引次数
            #检查是否自引，若是则删除该词条   和current_authors做对比
            for item in new_articles[article_id]["cite_list"] :       #item包含了title 和 author
                # print(item["author"])
                isziyin = 0  # 是否自引
                for author in item["author"]:           #是否自引的判断
                    if author in current_authors:         #自引
                        isziyin = 1
                        ziyin_times += 1
                        break
                    else:
                        continue

                if isziyin == 0:            #记录他引
                    tayin.append(item)

            with open('data/tayin.json','w') as file:                            #保存他引
                json.dump(tayin,file)
            print('tayin.json文件内列表的长度：',len(tayin))

            #统计最后剩余的 他引次数
            print('总计引用',len(new_articles[article_id]["cite_list"]))
            print('自引次数：', ziyin_times)
            print('他引次数：',len(new_articles[article_id]["cite_list"])-ziyin_times )

            write_to_txt(len(new_articles[article_id]["cite_list"]),
                         ziyin_times,
                         len(new_articles[article_id]["cite_list"])-ziyin_times,ieee_fellow)

#通过文章标题title查找作者列表author
def query(title):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:26.0) Gecko/20100101 Firefox/26.0',
        'Cookie': 'GSP=CF=4'
    }
    resp = requests.get(PUB_SEARCH_URL, headers=headers, params={'q': [title]})
    time.sleep(1)
    d = BeautifulSoup(resp.content, "html.parser")

    pub_list_raw = d.find(name="ul", attrs={"class": "publ-list"})      #找到包含发布信息的子树
    #爬取该文章的作者列表
    authors = []
    for pub_data in pub_list_raw.children:
        if pub_data.attrs.get('class')[0] == 'year':
            continue
        author_items = pub_data.findAll(name="span", attrs={"itemprop": "author"})
        for author_item in author_items:
            authors.append(author_item.text)
        break
    return authors



#按照引用格式，把他引写入到txt文件中
def write_to_txt(zongyin,ziyin,tayin,ieee_fellow):   #,authors   ,title    ,publisher    ,year
    num = 0   #fellow的名字出现次数
    txt_path = 'result/result.txt'
    file = open(txt_path,mode='w',encoding='utf-8')                   #用utf-8编码，防止一些作者名字不能写入txt（默认gbk）

#write参数必须为str
    file.write("总引用次数：")
    file.write(str(zongyin))
    file.write(" 自引次数：")
    file.write(str(ziyin))
    file.write(" 他引次数：")
    file.write(str(tayin))
    file.write("\n\n")

#把上面生成的tayin.jason中的信息写到result.txt中

    with open('data/tayin.json', encoding='utf-8') as fh:
        file_tayin = json.load(fh)

    for id, item in enumerate(file_tayin):
        author_num = len(item["author"])
        #文章作者
        i = 0
        for author in item["author"] :

            for fellow in ieee_fellow:
                #            print(fellow)
                if author == fellow:
                    num += 1
                    print(author)

            file.write(author)
            #最后一个作者后面要是句号.
            if i < author_num-1 :
                file.write(',')
                i+=1
            else:
                file.write('.')
        #文章标题
        file.write(' ')
        file.write(str(item["title"]))
        file.write("\n")

    print(num)
    file.close()



if __name__ == "__main__":
    main()