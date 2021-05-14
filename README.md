
Python library to interface with DL24-style electronic loads.

# History
I needed to build a dicharge curve for Lipo cell. The DL24 I had did not have anything for Linux (or at least I did not find it) and I have very little desire installing some unknown binaries to a Windows machine or my phone.

On the [EEVblog forum](https://www.eevblog.com/forum/testgear/atorch-dl24-electronic-load-software/msg3219530/#msg3219530) I found mention of a Github repository with software that was created for a previous model by reverse-engineering the [protocol](https://github.com/misdoro/Electronic_load_px100/blob/master/protocol_PX-100_2_70.md).

That software did not really work for me out of the box out of the box but after some tweaking I managed to run it. It was a somewhat unstable because my DL24 was sending some unsolicited data every second and it was mixing with command responses so the software was not happy.

So given I did not need the fancy GUI anyway, I just created a simple Python interface to the device and a script that polls it periodically creating a CSV file I needed.

# How to use
It is rather simple. Something like that
```python
load = DL24.DL24(serial.Serial('/dev/ttyUSB0', 9600))

while True:
  print(load.getCurrent())
  print(load.getVoltage())
  time.sleep(60)
```

Use `log-discharge.py` as an example how to control and query the device.

# log-discharge.py
The script just enables the load and polls it every 10 seconds putting data into a `log.csv` file of this format:
```
time,seconds,voltage,current,capacity
00:00:00,0,3.812,0.1,0
```
Note that you need to configure your mode using buttons on DL-24 before running the script (CC/CP/CV etc - see [limitations](#limitations))

# Limitations
* Only constant current mode is really supported. I have no idea what commands need to be sent to DL24 in order to switch to other modes (constant power, constant voltage etc) and also how to set target power/woltage/etc for these. So even though you can turn load on and off with your script, you need to manually configure everything.
* The waiting for a device response does not have any time out - it may just hang if device response is garbled somehow.
* I have got no idea of the format and structure of the 36-byte packet that DL24 sends every second. If there is something important, it would make sense to refactor the interface to read device data in the background and extract bits and bobs from there
* The whole idea of sending a command to device and waiting for a certain signature in the response data is not great - I saw data packets I cannot explain. But doing it properly requires some proper documentation on the device protocol rather than guesswork.

