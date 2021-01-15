import threading
import time
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q, A
from utils import create_simple_query_body
import random
import urllib3
import requests
from bs4 import BeautifulSoup
import statistics

topics = []
keyword_file = "/home/felipe/Escritorio/universidad/E/OpenCSMap/OpenCSMap/dataset/files/keywords_list.txt"
with open(keyword_file) as f:
    topics = eval(f.readline())




def do_a_query(topic):
    l = 0
    n = 0
    client = Elasticsearch()
    body = create_simple_query_body(topic)
    s = Search(using=client, index="papers_def").update_from_dict(body)

    t = s.execute()
    aggs = t.aggregations.my_buckets.buckets
    affiliations = [aggs]

    for aff in aggs:
        n += aff.doc_count
    l += len(aggs)

    try:
        after = t.aggregations.my_buckets.after_key
    except:
        after = ""

    while after:
        body['aggs']['my_buckets']['composite']['after'] = after
        s = Search(using=client, index="papers_def").update_from_dict(body)
        t = s.execute()

        aggs = t.aggregations.my_buckets.buckets
        affiliations.append(aggs)
        for aff in aggs:
            n += aff.doc_count
        l += len(aggs)

        try:
            after = t.aggregations.my_buckets.after_key
        except:
            break

    
    return (
        {
            'affiliations':affiliations,
            'topic':topic,
            'n_affiliations':format(l,',d'),
            'n_papers':format(n,',d')
        }
        )

def fun1(n):
    for _ in range(n):
        topic = random.choice(topics)
        url = f'http://localhost:8000/search/results/{topic}'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        

def fun2(n):
    for _ in range(n):
        topic = random.choice(topics)
        url = f'http://localhost:8000/search/results/{topic}'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        

def fun3(n):
    for _ in range(n):
        topic = random.choice(topics)
        url = f'http://localhost:8000/search/results/{topic}'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        

def fun4(n):
    for _ in range(n):
        topic = random.choice(topics)
        url = f'http://localhost:8000/search/results/{topic}'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        

def main():
    times = []

    for i in range(5):
        start_time = time.time()
        t1 = threading.Thread(target=fun1, args=(250,))
        t2 = threading.Thread(target=fun2, args=(250,))
        #t3 = threading.Thread(target=fun3, args=(250,))
        #t4 = threading.Thread(target=fun4, args=(250,))

        t1.start()
        t2.start()
        #t3.start()
        #t4.start()

        t1.join()
        t2.join()
        #t3.join()
        #t4.join()

        end_time = time.time()
        print(f"{i+1} finished")
        times.append(end_time-start_time)

    print(times)

def main2():
    times = []
    for _ in range(1000):
        topic = random.choice(topics)
        start_time = time.time()
        url = f'http://localhost:8000/search/results/{topic}'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        print(soup)
        end_time = time.time()
        total_time = end_time - start_time
        times.append(f"{topic}\t{total_time}\n")
        print(f"{topic}\t{total_time}\n")
    
    with open("/home/felipe/Escritorio/universidad/E/OpenCSMap/OpenCSMap/dataset/files/simple_search_times.tsv", 'w') as f:
        for t in times:
            f.write(t)

def main3():
    times = []
    with open("/home/felipe/Escritorio/universidad/E/OpenCSMap/OpenCSMap/dataset/files/simple_search_times.tsv") as f:
        for line in f:
            x = line.replace("\n","")
            time = x.split("\t")[1]
            times.append(float(time))

    print(f'Std: {statistics.stdev(times)}')
    print(f'Mean: {statistics.mean(times)}')
    print(f'Sum: {sum(times)}')

if __name__ == '__main__':
    start_time = time.time()
    #print(topics)
    main()
    print(time.time()-start_time)
    print((time.time()-start_time)/60.0)


"""
250
1 thread: [37.95138168334961, 40.569247007369995, 40.69446396827698, 40.01930379867554, 45.434876680374146]
2 thread:
3 thread:
4 thread:
5 thread:

125
1 thread:
2 thread:
3 thread:
4 thread:
5 thread:
"""