## CPU Benchmarking

CPU benchmarking is brough about by sysbench. It calculates prime numbers in a certain user-defined range by spawning different threads (each event is considered to be a compute-intensive transaction to calculate the primes) and then aggregating the time taken by each event (latency) to compute the overall CPU throughput. The design of the code is such that, the interference of memory is minimal and only the CPU’s performance along with minor cache effects is taken into study.

### Running guidelines
* Install sysbench, perf and necessary packages in the VM
    ```bash
    yum install sysbench perf python3-pip -y
    pip install tqdm
    ```
* Run the script
    ```bash
    nohup python3 -u process.py &>temp_output_2 < /dev/null &
    ```
* Monitor the progress
    ```bash
    tail -f temp_output_2
    ```
The test runs for 2-3 hours and at the end, a file (sysbench.json) holding the obtained statistics is generated in the same document hierarchy