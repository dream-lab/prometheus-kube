## Network Benchmarking

Network benchmarking is brought about by netperf. It runs several tests across the network and quantifies the performance of different types of networking protocols for a given interface. It measures both unidirectional throughput as well as end-to-end latency by running data transfer and request/response tests in TCP/UDP over IPv4/6. We use 2 tools (netperf and iperf) in this benchmark to get the best combination of loads.

### Running guidelines
* Install packages in the VM
    ```bash
    yum install netperf -y
    pip install flent
    ```
* Start netserver in another physical machine within the same network
    ```bash
    ./netserver
    ```
* Run the testing scripts in the client machine
    ```bash
    # Creates the standard graphic image used by the Bufferbloat project to show the down/upload speeds plus latency in three separate charts
    flent rrul -p all_scaled -l 60 -H <Server IP> -t rrul -o test_1_plots.png

    # A Cumulative Distribution Function plot showing the probability that ping times will be below a bound
    flent rrul -p ping_cdf -l 60 -H <Server IP> -t cdf -o test_2_plots.png

    # Display TCP upload speed and latency in two charts:
    flent tcp_upload -p totals -l 60 -H <Server IP> -t tcp-upload -o test_3_plots.png

    # Display TCP download speed and latency in two charts:
    flent tcp_download -p totals -l 60 -H <Server IP> -t tcp-download -o test_3_plots.png
    ```