# PromLib

Promlib is a library that helps pull metrics for machines/VMs at different granularities and the same for kubernetes based applications.


The promlib module has the following functions which provide the following results:

    machine_total(_host_list_) : A list of tuples (one tuple per host) that contains machine max resources.
    machine_current(_host_list_) : A list of tuples (one tuple per host) that contains machine instantaneous resource state.
    machine_average(_host_list_) : A list of tuples (one tuple per host) that contains current machine resource state by averaging over specified window.
    appication_average(_app_id_list_) : A list of tuples (one tuple per app) that contains application average resource usage over the specified window.
    application_quantile(_app_id_list_) : A list of tuples (one tuple per app) that contains application x-th percentile resource usage over the specified window.
    deploy(_host_id_,_app_id_list_,_namespace_) : A sample deployment function that helps deploy pods of deathstar benchmark's pods on to the hosts as returened by the solver algoruithm.
    clear_namespace(_namespace_) : A sample function to clear the specified namespace inside kubernetes deployment space.

_host_list_ is the list of ip(s) of the target hosts/VMs whose resource state need to obtained. 
    
    The target address is of the form <ip:port>

_app_id_list_ is the list of pod id(s) whose resource utilization need to be obtained.

    The target id is of the form <namespace:app_name>

Additionally, there is a config.yaml file with following configurable parameters:

    prometheus_source : <ip:port> of the prometheus source
    machine_window : Time window over which the average value for machine resource statistsics is to be calculated. Eg.: "10m", "300s", etc.
    app_scrape_interval : The scrape interval (in seconds) of application level metrics as specified in prometheus.yaml config of prometheus source. Eg.: "5s", "15s" ,etc.
    application_window : Time window over which the average or quantile value for app resource statistsics is to be calculated. Eg.: "10m", "300s", etc.
    app_metric_percentile: The percentile value for application resource's quantile statistics calculation. Eg. "0.99", "0.95" , etc.
    k8s_control_plane : The control plane <ip> where we want a sample kubernetes based deployment as per outputs from the solver.
    solver_source : <ip:port> for the host where the dolver algorithm is up and running.



The tuples returned are of the format:

    machine_total(_host_list_): (Max CPU CORES, Max MEMORY, Max DISK SPACE, Max NETWORK BANDWIDTH)
    machine_current(_host_list_) : (Intantaneous available CPU CORES, Intantaneous available MEMORY, Intantaneous available DISK SPACE, Intantaneous available NETWORK BANDWIDTH)
    machine_average(_host_list_) : (Average available CPU CORES, Average available  MEMORY, Average available  DISK SPACE, Average available NETWORK BANDWIDTH)
    appication_average(_app_id_list_) : (Average used CPU CORES, Average used MEMORY, Average used DISK SPACE, Average used NETWORK BANDWIDTH)
    appication_quantile(_app_id_list_) : (x-th percentile used CPU CORES, x-th percentile used MEMORY,x-th percentile used DISK SPACE, x-th percentile used NETWORK BANDWIDTH)

The units used (in order as in tuple):

    (Cores, GB, GB, Gbps)
    
See and run sample.py to see how to pass hosts/application with respective ids and use the functions present in promlib to get resource availabiliry/utilization. 

all_list.py is a sample code to list all available machines for placements and list of apps to get placed. It has 2 functions:

    get_all_machine_id() : Returns list of available machines for placement.
    get_all_app_list() : Returns list of available apps/pods in a given kubernetes deployment space (to be placed).

Apart from this there is also an app.py which has a swagger UI documentation over Flask API to visualize output from deployment runs samples. Solver_test.py is a sample program to use the solver (with an integrated end to end use shown in app.py) after its setup as given.

