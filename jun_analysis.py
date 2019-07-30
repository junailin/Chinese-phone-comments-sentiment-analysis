import jieba
from snownlp import SnowNLP
import pandas as pd
import sklearn as sk
import json
import jieba.analyse
import jieba.posseg
import os
import sys
from tqdm import tqdm
import matplotlib.pyplot as plot

def read_write(infile, outfile):
    data = pd.read_csv(infile, sep='\t', header=0)
    data.columns = ['name','append','comment','day','color','buyday','cpu','score',
                    'device','level','province','agreement','reply','type']
    #print([[i,x] for i,x in enumerate(list(data.columns))])
    data.sort_values(by='score',ascending=False,inplace=True)
    #print(data.iloc[:4, [0,2,7]])
    comments = list(data['comment'])
    print("=="*40)
    #print(comments[:4])

    #stopword = [line.strip() for line in open('stop.txt').readlines()]

    comment_seg = []
    for text in comments:
        comment_seg.append(" ".join(jieba.cut(text)))
    #print(comment_seg[:4])
    data["comment_seg"] = comment_seg
    #print([[i,x] for i,x in enumerate(list(data.columns))])
    data = data.iloc[:,[0,1,2,3,4,5,6,7,9,11,12,13,14]]
    data.to_csv(outfile,sep='\t',index=False,encoding='utf-8')

def stat_score(mydir, out1, out2):
    scores = {}
    stats = {}
    for f in ['iqoo','x27','nex','z5x','mi','oppo','iphone','p30pro']:
        data = pd.read_csv(mydir + f + "/result.csv", sep='\t', header=0)
        scores[f] = list(data['score'])
        stats[f] = {}
        for i in [1, 2, 3, 4, 5]:
            stats[f][i] = scores[f].count(i)
    #json.dump(scores,open(out1,"w"))
    #json.dump(stats,open(out2,'w'))
    pd.DataFrame(stats,index=[1,2,3,4,5]).to_csv(out2, sep='\t',index=True,encoding='utf-8')


def top_k(mydir, out1, out2):
    comments = {}
    for f in ['iqoo','x27','nex','z5x','mi','oppo','iphone','p30pro']:
        print("="*40)
        print(f) 
        comments[f] = {}
        data = pd.read_csv(mydir + f + "/result.csv", sep='\t', header=0)
        comments[f]['high'] = '\n'.join(list(data[data['score'] >= 4]['comment']))
        comments[f]['medium'] = '\n'.join(list(data[data['score'] == 3]['comment']))
        comments[f]['low'] = '\n'.join(list(data[data['score'] <= 2]['comment']))
        
        jieba.analyse.set_stop_words('stopwords-master\百度停用词表.txt')
        with open(out2, 'a+', encoding='utf-8') as writer:
            writer.write("="*80)
            writer.write(f + '\n')

            writer.write("-"*40)
            writer.write('high' + '\n')
            for x, w in jieba.analyse.extract_tags(comments[f]['high'],withWeight=True,topK=40):
                writer.write("%s %.4f \n" % (x, w))
            writer.write("-"*40)
            writer.write('medium' + '\n')  
            for x, w in jieba.analyse.extract_tags(comments[f]['medium'],withWeight=True,topK=40):
                writer.write("%s %.4f \n" % (x, w))          
            writer.write("-"*40)
            writer.write('low' + '\n')  
            for x, w in jieba.analyse.extract_tags(comments[f]['low'],withWeight=True,topK=40):
                writer.write("%s %.4f \n" % (x, w))

    json.dump(comments,open(out1,'w',encoding='utf-8'),ensure_ascii=False)

def analysis(mydir, out):
    sentiments = {}
    for f in ['iqoo','x27','nex','z5x','mi','oppo','iphone','p30pro']:
        print("-"*20)
        print(f)
        data = pd.read_csv(mydir + f + "/result.csv", sep='\t', header=0)
        sentiment = []
        for text in tqdm(data['comment']):
            result = SnowNLP(text)
            sentiment.append(result.sentiments)
        data['sentiment'] = sentiment
        sentiments[f] = sentiment
        data.to_csv(mydir + f + "/result_sentiment.csv",sep='\t',index=False,encoding='utf-8')

    json.dump(sentiments,open(out, 'w', encoding='utf-8'),ensure_ascii=False)

def picture(mydir,out):
    sentiments = json.load(open(mydir,'r',encoding='utf-8'))
    params = {'iqoo':['iQOO','blue'],'x27':['X27','darkblue'],'nex':['NEX','midnightblue'],'z5x':['Z5x','cornflowerblue'],
        'mi':['mi9','orange'],'oppo':['reno','green'],'iphone':['iphone xr','silver'],'p30pro':['p30pro','red']}
    for name in ['iqoo','x27','nex','z5x','mi','oppo','iphone','p30pro']:
        plot.rcParams['font.sans-serif']=['SimHei']
        plot.hist(sentiments[name],10,facecolor=params[name][1])
        plot.xlabel("情感得分")
        plot.title("用户对%s手机评论的情感分布" % params[name][0])
        plot.grid(True)
        plot.savefig(out + name + '.png')
        plot.close()
        #plot.show()

    for item in ['iqoo','x27','nex','z5x']:
        #fig = plot.figure()
        for name in [item,'mi','oppo','iphone','p30pro']:
            plot.rcParams['font.sans-serif']=['SimHei']
            plot.hist(sentiments[name],200,cumulative=True,density=True,histtype='step',color=params[name][1],label=params[name][0])

        plot.title("用户对%s与友商手机评论的情感累积分布对比" % params[item][0])
        plot.legend(loc='upper left')
        plot.savefig(out + '%s与友商手机评论的情感累积分布对比.png' % params[item][0])
        plot.close()

    for item in ['z5x','iqoo','x27','nex']:
        plot.rcParams['font.sans-serif']=['SimHei']
        plot.hist(sentiments[item],200,cumulative=True,histtype='step',density=True,color=params[item][1],label=params[item][0])
        plot.title("用户对VIVO各个系列手机评论的情感累积分布对比")
    plot.legend(loc='upper left')
    plot.savefig(out + "用户对VIVO各个系列手机评论的情感累积分布对比.png")
    plot.close()

def find(mydir):
    for f in ['iqoo','x27','nex','z5x','mi','oppo','iphone','p30pro']:
        print("-"*20)
        print(f)
        data = pd.read_csv(mydir + f + "/result_sentiment.csv", sep='\t', header=0)
        data = data[data['sentiment'] == 1]
        data.to_csv(mydir + f + "/find_sentiment_best.csv",sep='\t',index=False,encoding='utf-8')

if __name__ == "__main__":
    mode = 6
    if mode == 1:    
        for x in ['iqoo','x27','nex','z5x','mi','oppo','iphone','p30pro']:
            infile = 'data/%s/data_clean.csv' % x
            outfile = 'data/%s/result.csv' % x
            read_write(infile, outfile)
    
    elif mode == 2:
        mydir = 'data/'
        out1 = 'data/summary/origin_scores.json'
        out2 = 'data/summary/stats_scores.csv'
        stat_score(mydir, out1, out2)
    
    elif mode == 3:
        mydir = 'data/'
        out1 = "data/summary/comments.json"
        out2 = 'data/summary/key_word_by_score.txt'
        if os.path.exists(out2):
            os.remove(out2)
        top_k(mydir, out1, out2)
    
    elif mode == 4:
        mydir = 'data/'
        out = 'data/summary/sentiments.json'
        analysis(mydir, out)
    
    elif mode == 5:
        mydir = 'data/summary/sentiments.json'
        out = 'data/summary/'
        picture(mydir, out)

    elif mode == 6:
        mydir = 'data/'
        find(mydir)







    

