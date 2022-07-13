### Running benchmarks

* Download and extract the [zip](https://drive.google.com/file/d/1_9sQjuFvSqIUR0LqBdgnvLylu7RiHmRH/view?usp=sharing)

* The above file has benchmark tests for cpu, memory and disk

* For network microbenchmarks, run the below command
```bash
yum install python3-pip python3-devel netperf epel-release -y
pip3 install flent
```

#### CPU
```bash
cd Benchmark/sysbench
python3 process.py
```

#### Memory
```bash
cd Benchmark/stream
python3 process.py
```

#### Disk
```bash
cd Benchmark/iozone
./iozone -Ra -g 8G -b iozone_benchmarks.xls
```

#### Network
```bash
Run a netperf server in a different physical host by issuing the following command
./netserver

flent rrul -p all_scaled -l 180 -H <IP of netserver> -t rrul_vm -o plots.png
```