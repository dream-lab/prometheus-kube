## Setup Instructions
This repository houses the steps to mimic the experimental setup used for application benchmarking and microbenchmarking various deployment platforms and the VM placement algorithm that leverages PromLib library.

</br>

### Directory heirarchy
The folder hierarchy is as follows
```
root
├── Microbenchmarking scripts (Scripts for performing microbenchmarks)
│   ├── cpu                 (To benchmark the CPU using sysbench)
│   ├── disk                (To benchmark the disk using iozone)
│   ├── memory              (To benchmark the memory using stream)
│   └── network             (To benchmark the network using netperf)
├── binaries (Necessary binary packages for setting up the DC)
└── documentation (Detailed setup instructions for erecting the DC)
    ├── common              (Deployment of the monitoring server)
    ├── Application Benchmarking
    └── Microbenchmarking   (Setting up the hypervisors and configuring the VMs)
```

</br>

### Usage guidelines
*   Steps mentioned in `documentation/common` is for setting up the centralised monitoring server and hence, is the same for both application and micro benchmarks.
*   `documentation/Microbenchmarking` folder has instructions for setting up the individual servers (bare metal, hypervisor and VMs).
*   The `binaries` folder holds the necessary binary packages (prometheus, exporters, grafana, etc.) with the version that best works with the recommended setup.
*   `Microbenchmarking/scripts` holds instructions for running microbenchmarks on a per-resource fashion and has individual README files for detailed execution steps.
