## Disk Benchmarking

Disk benchmarking is brought about by iozone. It stress tests the IO bandwidth by performing operations such a read, write (both in a sequential, random and backward fashion), fread, fwrite, etc. which accounts for all types of disk-level interactions that can possibly happen when an application is at play. The variation in different tests is the file size and the block size in which the above operations are executed. This benchmark tries to minimise the cache level influences from affecting the bandwidth by using a file size that overflows all standalone memory buffers and processor level caches.

## Running guidelines
* Install the package
    ```bash
    cd Microbenchmarking scripts/disk
    make
    make linux
    ```
* Run tests
    ```bash
    # All operations with maximum file size of 8GB
    ./iozone -Ra -g 8G -b iozone_benchmarks.xls

    # Write/rewrite operations with 16MB record length and maximum file size of 8GB
    ./iozone -Ra -i 0 -s 8G -r 16384k -b write_benchmarks.xls

    # Read/reread operations with 16MB record length and maximum file size of 8GB
    ./iozone -Ra -i 1 -s 8G -r 16384k -b write_benchmarks.xls
    ```