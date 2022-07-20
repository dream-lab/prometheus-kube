## Set up node level exporters

### Node Exporter
```bash
# Download binaries
git clone https://github.com/dream-lab/prometheus-kube.git
cd prometheus-kube/binaries

# Extract package
tar -xvf node_exporter.tar.gz

# Move into system path
sudo mv node_exporter-1.3.1.linux-amd64/node_exporter /usr/local/bin/

#  Create a node_exporter user to run the node exporter service
sudo useradd -rs /bin/false node_exporter
# Create a node_exporter service file under systemd
sudo vi /etc/systemd/system/node_exporter.service
```

Add the following content to the service file
```bash
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter --collector.buddyinfo \
--collector.perf.cpus=0,1 \
--collector.processes \
--collector.systemd

[Install]
WantedBy=multi-user.target
```

### Process Counter Exporter
```bash
# Download binaries
cd prometheus-kube/binaries

# Install packages
sudo rpm -ivh pcm-0-395.1.x86_64.rpm

# Create a node_exporter service file under systemd
sudo vi /etc/systemd/system/pcm_exporter.service

```
Add the following content to the service file
```bash
[Unit]
Description=PCM Exporter
After=network.target

[Service]
User=root
Group=root
Type=simple
ExecStart=/usr/sbin/pcm-sensor-server

[Install]
WantedBy=multi-user.target
```

#### Start the service
```bash
# Add performance counter modules
sudo modprobe msr

# Reload the system daemon
sudo systemctl daemon-reload
sudo systemctl start node_exporter
sudo systemctl start pcm_exporter

# Enable the service for autostart
sudo systemctl enable node_exporter
sudo systemctl enable pcm_exporter

# Clear the firewall configuration
sudo iptables -F
```