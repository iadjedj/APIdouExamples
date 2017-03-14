# APIdou command-line tool

```
$ python main.py -h
usage: main.py [-h] -type {bled112,linux} -addr ADDR [-tcp] [-com]

optional arguments:
  -h, --help            show this help message and exit
  -type {bled112,linux}, -t {bled112,linux}
                        Are you using a BLED112 or regular BLE Adapter on Linux ?
  -addr ADDR, -a ADDR   MAC address of your APIdou, e.g. 00:07:80:02:F2:F2
  -tcp                  Activate a forward to TCP (port 3000)
  -com                  Activate a forward to a COM port
```