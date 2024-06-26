# -*- coding: utf-8 -*-
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import current_thread
from tqdm import tqdm

import swiftclient


def bench_put(i):
    obj_name = '%s%08d' % (object_name_prefix, i) 
    start = time.time()
    with open(local_file, 'rb') as f:
        conn.put_object(bucket_name, obj_name, f) 
    end = time.time()
    duration = end - start
    client = current_thread().name
    return (duration, start, end, client)


def bench_get(i):
    obj_name = '%s%08d' % (object_name_prefix, i)  
    start = time.time()
    # print(current_thread().name,'start',start)
    resp_headers, obj_contents = conn.get_object(bucket_name, obj_name)
    with open(obj_name, 'wb') as f:
        f.write(obj_contents)
    end = time.time()
    # print(current_thread().name,'end',end)
    duration = end - start
    client = current_thread().name
    return (duration, start, end, client)


def bench_delete(i):
    obj_name = '%s%08d' % (object_name_prefix, i) 
    start = time.time()
    conn.delete_object(bucket_name, obj_name)
    end = time.time()
    duration = end - start
    client = current_thread().name
    return (duration, start, end, client)


switch = {'put': bench_put, 'get': bench_get, 'delete': bench_delete}
def run_test(test_type):
    print('-----' + test_type + '-----')
    latency = []
    test_start_time = time.time()
    with tqdm(desc="Accessing S3", total=num_samples) as pbar:
        with ThreadPoolExecutor(max_workers=num_client) as executor:
            futures = [executor.submit(switch[test_type],i) for i in range(num_samples)]
            for future in as_completed(futures):
                if future.exception():
                    os._exit(-1)
                else:
                    latency.append(future.result())  
                pbar.update(1)
    test_end_time = time.time()
    test_duration = test_end_time - test_start_time # s
    test_transferred = len(latency) * object_size # KB
    test_total_throughput=test_transferred/test_duration # KB/s
    test_average_latency=sum([latency[i][0] for i in range(len(latency))]) / len(latency) # s
    print('total duration: ', test_duration , 's')
    print('average latency: ', test_average_latency,"s")
    print('total transferred: ', test_transferred , 'KB')
    print('total throughput: ', test_transferred / test_duration, 'KB/s')
    print('success rate: ', len(latency) / num_samples * 100, '%')

    # tracefile_name = test_type + '_' + str(object_size) + '_' + str(num_clients) + '_' + str(num_samples) + '.csv'
    # with open(tracefile_name, "w+") as tracefile:
    #     tracefile.write("id,latency,start,end,client\n")
    #     tracefile.writelines([','.join(map(str, (i,) + latency[i])) + '\n' for i in range(len(latency))])
    if test_type=="put" or test_type=="get":
        with open(result_file,"a") as rf:
            rf.write("num_client: " + str(num_client) + " \n")
            rf.write(test_type + "_total_throughput: " + str(test_total_throughput) + " KB/s\n")
            rf.write(test_type + "_average_latency: " + str(test_average_latency) + " s\n")
# para init
server_addr = 'http://127.0.0.1:12345/'
_user = 'chris:chris1234'
_key = 'testing'
bucket_name = 'testbucket'
object_name_prefix = 'testObj'
# object_sizes=[1,2,4,8,16,32,64,128,256,512,1024] # /KB
total_size= 4*1024 # /KB    4MB
object_size=8 # /KB
num_samples=512
# num_clients = list(range(1,20,2))
num_clients = list(range(1,20,1))
result_file="result.out"
print('server_addr: ', server_addr)
print('bucket_name: ', bucket_name)
print('object_name_prefix: ', object_name_prefix)
print("total_size:",total_size,"KB")
print("object_size:",object_size,"KB")
print("num_samples:",num_samples)


if os.path.exists(result_file):
    os.remove(result_file)

# connect to swift
conn = swiftclient.Connection(authurl = server_addr + 'auth/v1.0', user = _user,key = _key)

for num_client in num_clients:
    print("=====TEST=====")
    print("num_client:", num_client)
    
    # 建立新容器
    conn.put_container(bucket_name)
    print('Test bucket %s created.' % bucket_name)

    # 初始化大小为object_size的文件
    local_file = "_test.bin"
    with open(local_file, 'wb') as file:
        file.write(b'\0' * object_size * 1024)
    print('Test file %s created.' % local_file)
    
    # 运行测试
    run_test('put')
    run_test('get')
    run_test('delete')

    # 删除本地文件
    for i in range(num_samples):
        obj_name = '%s%08d' % (object_name_prefix, i)
        os.remove(obj_name)
    print('Downloaded files deleted.')

    # 删除数据文件
    os.remove(local_file)
    print('Test file %s deleted.' % local_file)

    # 删除容器
    conn.delete_container(bucket_name)
    print('Test bucket %s deleted.' % bucket_name)

