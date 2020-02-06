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

TODO


- run it through systemd
- pin possible multiple CO2 meters through udev and usb port location they are plugged in to different devices
- run multiple exporters with different labels
