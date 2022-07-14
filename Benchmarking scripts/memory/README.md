## Memory Benchmarking

Memory benchmarking is brought about by stream. It performs 4 operations, namely, copy, scale, add, triad. These operations involve copying data from one location to another in memory, multiplying a large contiguous memory by a scalar, shifting all the values of a large vector by some value and a combination of all the above 3 operations in one, respectively. It calculates the time taken by each operation and computes the memory bandwidth by considering the given array size. The array size is kept to be around four times the size of the last level cache so that the cache level influences are negligible and only the involvement of RAM is brought into the picture.

### Running guidelines
* Install gcc and necessary packages in the VM
    ```bash
    yum install gcc -y
    pip install tqdm
    ```
* Run the script
    ```bash
    nohup python3 -u process.py &>testing < /dev/null &
    ```
* Monitor the progress
    ```bash
    tail -f testing
    ```

The test runs for 1-2 hours and at the end, a file (stream.json) holding the obtained statistics is generated in the same document hierarchy