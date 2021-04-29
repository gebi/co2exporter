# co2exporter
Prometheus exporter for different co2 sensors (TFA-Dostmann)

## Supported Hardware

Multiple CO2 Sensors are supported:

- [TFA-Dostmann AirControl Mini CO2 Messgerät](http://www.amazon.de/dp/B00TH3OW4Q) -- 65 euro (sends encrypted data)
- [TFA-Dostmann AIRCO2NTROL Coach CO2 Monitor](http://www.amazon.de/dp/B07R4XM9Z6) -- 72 euro (sends unencrypted data),
this is the modell i use, the other one is supported historically in the codebase.

## Usage

```
usage: co2exporter.py [-h] [--port PORT] [--addr ADDR] [--label LABEL] dev

co2sensor prometheus exporter

positional arguments:
  dev            CO2 Sensor hidraw device

optional arguments:
  -h, --help     show this help message and exit
  --port PORT    Listening Port
  --addr ADDR    Listening address
  --label LABEL  Labels included in metrics, name=value
```

## Usage Example

When running as prometheus exporter (deamon) just pipe `STDOUT` to `/dev/null`, all interesting messages go to `STDERR`

```bash
./co2exporter.py --addr 127.0.0.1 --label place=cellar --label room=workshop /dev/hidraw0
Listening on :9672, appending labels: {'place': 'cellar', 'room': 'workshop'}
*42: 1281  4737    T: 22.91
*41: 0830  2096,  42: 1281  4737    T: 22.91 RH: 20.96
 41: 0830  2096,  42: 1281  4737, *53: 0000     0    T: 22.91 RH: 20.96
 41: 0830  2096,  42: 1281  4737, *50: 0551  1361,  53: 0000     0    CO2: 1361 T: 22.91 RH: 20.96
 41: 0830  2096, *42: 1281  4737,  50: 0551  1361,  53: 0000     0    CO2: 1361 T: 22.91 RH: 20.96
*41: 0839  2105,  42: 1281  4737,  50: 0551  1361,  53: 0000     0    CO2: 1361 T: 22.91 RH: 21.05
...
```

## Metrics Generated

You can set multiple labels on metrics exported by this exporter, see USAGE

Main metrics:

- `co2sensor_co2_ppm`
- `co2sensor_temperature_celsius`
- `co2sensor_relative_humidity_percent`
- `co2sensor_packet_checksum_errors_total` (if there are problems decoding sensor data)

Full metrics output:

```
# HELP co2sensor_received_packets_total Number of datapoints received
# TYPE co2sensor_received_packets_total counter
co2sensor_received_packets_total{place="cellar",room="workshop"} 29.0
# TYPE co2sensor_received_packets_created gauge
co2sensor_received_packets_created{place="cellar",room="workshop"} 1.5810310826724613e+09
# HELP co2sensor_packet_checksum_errors_total Number of parsing/checksum errors in received data
# TYPE co2sensor_packet_checksum_errors_total counter
co2sensor_packet_checksum_errors_total{place="cellar",room="workshop"} 0.0
# TYPE co2sensor_packet_checksum_errors_created gauge
co2sensor_packet_checksum_errors_created{place="cellar",room="workshop"} 1.5810310826725068e+09
# HELP co2sensor_values_total Number of different values received from the sensor
# TYPE co2sensor_values_total gauge
co2sensor_values_total{place="cellar",room="workshop"} 4.0
# HELP co2sensor_temperature_celsius Temperature in Celsius
# TYPE co2sensor_temperature_celsius gauge
co2sensor_temperature_celsius{place="cellar",room="workshop"} 22.73
# HELP co2sensor_co2_ppm CO2 in ppm
# TYPE co2sensor_co2_ppm gauge
co2sensor_co2_ppm{place="cellar",room="workshop"} 1097.0
# HELP co2sensor_relative_humidity_percent Relative Humidity in percent
# TYPE co2sensor_relative_humidity_percent gauge
co2sensor_relative_humidity_percent{place="cellar",room="workshop"} 19.22
```

# Install & usage

Setup device permission stuff

```
install -o root -g root -m 0644 90-co2exporter.rules /etc/udev/rules.d/
udevadm control --reload-rules && udevadm trigger
```

Install `co2exporter` service and run it per default

```
install -o root -g root -m 0755 co2exporter /opt
install -o root -g root -m 0644 co2exporter.service /etc/systemd/system
systemctl daemon-reload
systemctl start co2exporter
systemctl enable co2exporter
```

scrape through prometheus like normal

# Integration example with grafana-agent

Example integration with grafana-agent as "IoT" device
Nice benefit of using grafana-agent is, that as long as there is enough RAM for WAL, data will be buffered on connection loss to server.

Install grafana agent (example with the version i used) and install sane config
```
wget https://github.com/grafana/agent/releases/download/0.14.0-rc.3/grafana-agent-0.14.0-rc.3-1.arm64.deb
dpkg -i grafana-agent-0.14.0-rc.3-1.arm64.deb
install -o root -g grafana-agent -m 0640 grafana-agent.yaml /etc/
mkdir -p /etc/systemd/system/grafana-agent.service.d/
install -o root -g root -m 0644 -T grafana-agent_systemd_override.conf /etc/systemd/system/grafana-agent.service.d/override.conf
```

Add auth settings to `/etc/default/grafana-agent`
```
PROM_REMOTE_WRITE_URL="https://prometheus-blocks-prod-us-central1.grafana.net/api/prom/push"
PROM_REMOTE_WRITE_USER="YOUR_USER"
PROM_REMOTE_WRITE_PW="YOUR_TOKEN"
```

Add co2exporter as proper target to intergrated prometheus from `grafana-agent`
```
mkdir -p /etc/prometheus/targets/co2exporter/
cat >/etc/prometheus/targets/co2exporter/manual__`hostname`.yml <<EOT
# use proper discovery mechanism of prometheus to add targets, even via file
# manual entry of co2exporter to separate targets from daemon config, and we don't want to restart :)
- {labels: {instance: '`hostname`:9672'}, targets: ['127.0.0.1:9672']}
EOT
```

Restart and check if everything works
```
systemctl daemon-reload
systemctl restart grafana-agent
```

Look at the data grafana-agent has discovered and sends
```
grafana-agentctl wal-stats /run/grafana-agent/*
grafana-agentctl target-stats /run/grafana-agent/* -j co2exporter -i `hostname`:9672
# or
grafana-agentctl target-stats /run/grafana-agent/* -j integrations/node_exporter -i `hostname`:9090
```

# TODO

- pin possible multiple CO2 meters through udev and usb port location they are plugged in to different devices
