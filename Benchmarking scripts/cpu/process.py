# --threads	The total number of worker threads to create	1
# --events	Limit for total number of requests. 0 (the default) means no limit	0
# --time	Limit for total execution time in seconds. 0 means no limit	10
# --warmup-time	Execute events for this many seconds with statistics disabled before the actual benchmark run with statistics enabled. This is useful when you want to exclude the initial period of a benchmark run from statistics. In many benchmarks, the initial period is not representative because CPU/database/page and other caches need some time to warm up	0
# --rate	Average transactions rate. The number specifies how many events (transactions) per seconds should be executed by all threads on average. 0 (default) means unlimited rate, i.e. events are executed as fast as possible	0
# --thread-init-timeout	Wait time in seconds for worker threads to initialize	30
# --thread-stack-size	Size of stack for each thread	32K
# --report-interval	Periodically report intermediate statistics with a specified interval in seconds. Note that statistics produced by this option is per-interval rather than cumulative. 0 disables intermediate reports	0
# --debug	Print more debug info	off
# --validate	Perform validation of test results where possible	off
# --help	Print help on general syntax or on a specified test, and exit	off
# --verbosity	Verbosity level (0 - only critical messages, 5 - debug)	4
# --percentile	sysbench measures execution times for all processed requests to display statistical information like minimal, average and maximum execution time. For most benchmarks it is also useful to know a request execution time value matching some percentile (e.g. 95% percentile means we should drop 5% of the most long requests and choose the maximal value from the remaining ones). This option allows to specify a percentile rank of query execution times to count	95
perf_line = 'perf stat -e bus-cycles,cache-misses,cache-references,cpu-cycles,major-faults,minor-faults '

import os
from tqdm import tqdm
import datetime

track = []
for num_threads in tqdm(range(1, 5)):
    for thread_size in range(32, 33, 32):
        for prime_size in range(10000, 10000001, 500000):
            thread_mem_size = str(thread_size) + 'K'

            ct = datetime.datetime.now()
            ts = ct.timestamp()

            print(f'threads={str(num_threads)} --thread-stack-size={thread_mem_size} --cpu-max-prime={prime_size}')
            # os.system(perf_line + f'sysbench --threads={str(num_threads)} --events=8 --time=0 --thread-stack-size={thread_mem_size} --cpu-max-prime={prime_size} cpu run > temp_output_1')
            os.system(f'sysbench --threads={str(num_threads)} --thread-stack-size={thread_mem_size} --cpu-max-prime={prime_size} cpu run > temp_output_1')
            # os.system(perf_line + f'sysbench --threads={str(num_threads)} --thread-stack-size={thread_mem_size} --cpu-max-prime={prime_size} cpu run > temp_output_1')

            f = open("temp_output_1", "r")
            
            temp = {}
            
            for line in f.readlines():

                if line.startswith('    events per second:'):
                    events_per_second = line.split(":")[1].strip()

                if line.startswith('    total time:'):
                    total_time = line.split(":")[1].strip()
                if line.startswith('    total number of events:'):
                    total_events = line.split(":")[1].strip()

                if line.startswith('         min:'):
                    min_latency = line.split(":")[1].strip()
                if line.startswith('         avg:'):
                    avg_latency = line.split(":")[1].strip()
                if line.startswith('         max:'):
                    max_latency = line.split(":")[1].strip()
                if line.startswith('         sum:'):
                    sum_latency = line.split(":")[1].strip()
                if line.startswith('         95th percentile:'):
                    percentile_latency = line.split(":")[1].strip()
                
                if line.startswith('    events (avg/stddev):'):
                    avg_events, stddev_events = line.split(":")[1].strip().split('/')
                if line.startswith('    execution time (avg/stddev):'):
                    avg_exec_time, stddev_exec_time = line.split(":")[1].strip().split('/')

            """f = open("temp_output_2", "r")

            for line in f.readlines():
                if "bus-cycles" in line:
                    bus_cycles = line.split()[0]
                if "cache-misses" in line:
                    cache_misses = line.split()[0]
                if "cache-references" in line:
                    cache_references = line.split()[0]
                if "cpu-cycles" in line:
                    cpu_cycles = line.split()[0]
                if "major-faults" in line:
                    major_faults = line.split()[0]
                if "minor-faults" in line:
                    minor_faults = line.split()[0]"""

            temp['events_per_second'] = events_per_second
            temp['total_time'] = total_time
            temp['total_events'] = total_events
            temp['min_latency'] = min_latency
            temp['avg_latency'] = avg_latency
            temp['max_latency'] = max_latency
            temp['sum_latency'] = sum_latency
            temp['percentile_latency'] = percentile_latency
            temp['avg_events'] = avg_events
            temp['stddev_events'] = stddev_events
            temp['avg_exec_time'] = avg_exec_time
            temp['stddev_exec_time'] = stddev_exec_time
            temp['threads'] = num_threads
            temp['problem_size'] = prime_size
            temp['thread_stack_size'] = thread_mem_size
            temp['timestamp'] = ts
            temp['time'] = ct

            """temp['bus_cycles'] = bus_cycles
            temp['cache_misses'] = cache_misses
            temp['cache_references'] = cache_references
            temp['cpu_cycles'] = cpu_cycles
            temp['major_faults'] = major_faults
            temp['minor_faults'] = minor_faults"""

            track.append(temp)

import json
with open('sysbench.json', 'w') as fout:
    json.dump(track, fout, default=str)
