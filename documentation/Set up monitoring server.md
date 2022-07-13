## Set up monitoring server

### Set up prometheus
```bash
# Download binaries
git clone https://github.com/dream-lab/prometheus-kube.git
cd prometheus-kube/binaries

# Extract and move to system path
tar -xvf prometheus-package.tar.gz
mv prometheus-2.36.0.linux-amd64 prometheus-files

# Adjust sytem configurations
sudo useradd --no-create-home --shell /bin/false prometheus
sudo mkdir /etc/prometheus
sudo mkdir /var/lib/prometheus
sudo chown prometheus:prometheus /etc/prometheus
sudo chown prometheus:prometheus /var/lib/prometheus

# Copy into respective paths
sudo cp prometheus-files/prometheus /usr/local/bin/
sudo cp prometheus-files/promtool /usr/local/bin/
sudo chown prometheus:prometheus /usr/local/bin/prometheus
sudo chown prometheus:prometheus /usr/local/bin/promtool

# Adjust permissions
sudo cp -r prometheus-files/consoles /etc/prometheus
sudo cp -r prometheus-files/console_libraries /etc/prometheus
sudo chown -R prometheus:prometheus /etc/prometheus/consoles
sudo chown -R prometheus:prometheus /etc/prometheus/console_libraries

# Create prometheus configuration file
sudo vi /etc/prometheus/prometheus.yml
```

Add the following content into the .yml file
```bash
global:
  scrape_interval: 10s

scrape_configs:
- job_name: 'node-exporter' # For node level exporters
  file_sd_configs:
  - files:
    - 'targets.json'
```

Create a targets.json file which holds IP addresses (endpoints) of all nodes/applications

```bash
# Follow and extend the below format of listing the endpoints
[
  {
    "targets": [ "10.112.19.219:9100" , "10.112.19.242:9100"],
    "labels": {
      "job": "node-exporter"
    }
  },
  {
    "targets": [ "10.112.19.219:5000" ],
    "labels": {
      "job": "flask-webapp"
    }
  },
  {
    "targets": [ "10.112.19.242:8000" ],
    "labels": {
      "job": "nodejs-webapp"
    }
  }
]
```

Adjust permissions
```bash
# Change ownership to created user
sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml

# Create systemd service
sudo vi /etc/systemd/system/prometheus.service
```

Add the following content into the service file
```
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \
    --config.file /etc/prometheus/prometheus.yml \
    --storage.tsdb.path /var/lib/prometheus/ \
    --web.console.templates=/etc/prometheus/consoles \
    --web.console.libraries=/etc/prometheus/console_libraries

[Install]
WantedBy=multi-user.target
```

```bash
# Reload system daemon and start the service
sudo systemctl daemon-reload
sudo systemctl start prometheus
sudo systemctl enable prometheus
```

### Set up grafana
```bash
cd prometheus-kube/binaries
sudo yum install grafana-8.5.4-1.x86_64.rpm

# Reload system daemon and start the service
sudo systemctl daemon-reload
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```