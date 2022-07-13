import re
import time
import os
from tqdm import tqdm
 
track = []
 
ompi = False

for size in tqdm(range(10000000, 100000000, 1000000)):
    for threads in range(1, 2):
        
        if ompi:
            os.system(f"gcc -O -fopenmp -D_OPENMP -DSTREAM_ARRAY_SIZE={size} stream.c -o stream")
            os.environ["OMP_NUM_THREADS"] = str(threads)
        else:
            os.system(f"gcc -O -DSTREAM_ARRAY_SIZE={size} stream.c -o stream")
        
        os.system("./stream > output")
 
        f = open('output', 'r')
        operations = ['Copy','Scale','Add','Triad']
 
        for line in f.readlines():
            if line.startswith('Memory per array'):
                mem_array = re.findall('\d*\.?\d+', line)[0]
            if line.startswith('Total memory required'):
                total_mem_array = re.findall('\d*\.?\d+', line)[0]
 
            if line.startswith('Number of Threads requested'):
                threads_req = line.split('=')[1]
            if line.startswith('Number of Threads counted'):
                threads_count = line.split('=')[1]
 
            if line.startswith('Each test below'):
                clock_ticks = [int(s) for s in line.split() if s.isdigit()][0]
 
            if list(filter(line.startswith, operations)) != []:
                temp = {"mpi" : 0, "num_threads" : 0, "array size" : 0, "array memory" : 0, "total memory" : 0, "threads requested" : 0, "threads counted" : 0, "clock ticks (ms)" : 0, "operation" : 0, "best_rate" : 0, "avg_time" : 0, "min_time" : 0, "max_time" : 0, "D1_read_miss_rate" : 0, "D1_write_miss_rate" : 0, "LL_read_miss_rate" : 0, "LL_write_miss_rate" : 0}
                operation, best_rate, avg_time, min_time, max_time = line.split()
 
                temp["mpi"] = ompi
                temp["num_threads"] = threads
                
                temp["array size"] = size
                temp["array memory"] = mem_array
                temp["total memory"] = total_mem_array
                
                temp["threads requested"] = threads_req if ompi else 1
                temp["threads counted"] = threads_count if ompi else 1
                
                temp["clock ticks (ms)"] = clock_ticks
                temp["operation"] = operation[:-1]
 
                temp["best_rate"] = best_rate
                temp["avg_time"] = avg_time
                temp["min_time"] = min_time
                temp["max_time"] = max_time
 
 
                track.append(temp)
 
ompi = True
print("Threaded Start Commenced")
time.sleep(30)
 
for threads in range(1, 5):
    os.environ["OMP_NUM_THREADS"] = str(threads)
    time.sleep(30)
    for size in tqdm(range(10000000, 100000000, 1000000)):
        
        if ompi:
            os.system(f"gcc -O -fopenmp -D_OPENMP -DSTREAM_ARRAY_SIZE={size} stream.c -o stream")
        else:
            os.system(f"gcc -O -DSTREAM_ARRAY_SIZE={size} stream.c -o stream")
        
        os.system("./stream > output")
 
        f = open('output', 'r')
        operations = ['Copy','Scale','Add','Triad']
 
        g = open('testing', 'r')
        for line in g.readlines():
 
            if "D1  miss rate" in line:
                D1_read_miss_rate, D1_write_miss_rate = re.findall('\((.*?)\)', line)[0].replace(' ','').split('+')
 
            if "LLd miss rate" in line:
                LL_read_miss_rate, LL_write_miss_rate = re.findall('\((.*?)\)', line)[0].replace(' ','').split('+')
 
        for line in f.readlines():
            if line.startswith('Memory per array'):
                mem_array = re.findall('\d*\.?\d+', line)[0]
            if line.startswith('Total memory required'):
                total_mem_array = re.findall('\d*\.?\d+', line)[0]
 
            if line.startswith('Number of Threads requested'):
                threads_req = line.split('=')[1]
            if line.startswith('Number of Threads counted'):
                threads_count = line.split('=')[1]
 
            if line.startswith('Each test below'):
                clock_ticks = [int(s) for s in line.split() if s.isdigit()][0]
 
            if list(filter(line.startswith, operations)) != []:
                temp = {"mpi" : 0, "num_threads" : 0, "array size" : 0, "array memory" : 0, "total memory" : 0, "threads requested" : 0, "threads counted" : 0, "clock ticks (ms)" : 0, "operation" : 0, "best_rate" : 0, "avg_time" : 0, "min_time" : 0, "max_time" : 0, "D1_read_miss_rate" : 0, "D1_write_miss_rate" : 0, "LL_read_miss_rate" : 0, "LL_write_miss_rate" : 0}
                operation, best_rate, avg_time, min_time, max_time = line.split()
 
                temp["mpi"] = ompi
                temp["num_threads"] = threads
                
                temp["array size"] = size
                temp["array memory"] = mem_array
                temp["total memory"] = total_mem_array
                
                temp["threads requested"] = threads_req if ompi else 1
                temp["threads counted"] = threads_count if ompi else 1
                
                temp["clock ticks (ms)"] = clock_ticks
                temp["operation"] = operation[:-1]
 
                temp["best_rate"] = best_rate
                temp["avg_time"] = avg_time
                temp["min_time"] = min_time
                temp["max_time"] = max_time
 
 
                track.append(temp)
 
import json
with open('stream.json', 'w') as fout:
    json.dump(track, fout)
