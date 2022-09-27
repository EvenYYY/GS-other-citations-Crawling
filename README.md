# GS-other-citations-Crawling
This is a repo that help you crawl the citation list of a specific paper on Google Scholar, identify the "other ciitation" papers within the list, and eventually output a txt file containing the info of all the "other citation" papers and another one which records the IEEE fellows in the list.

Thanks to the effort of rpSebastian.
This work is based on his gs-cite-fellow:  https://github.com/rpSebastian/gs-cite-fellow




爬取Google Scholar上指定文章的他引次数，并输出由他引论文标题、作者组成的tayin.json文件

使用方法：  
先按github指示配置config.json里面的scholar_id和 chromedriver.exe在系统的路径
删除data文件夹下的 articles_id_0.json 文件
再依次执行01_ 02_ 03_ 04_的py文件，其中02_ 和04_开头指定哪篇论文
