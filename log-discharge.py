import serial
import time
import DL24

load = DL24.DL24(serial.Serial('/dev/ttyUSB0', 9600))

load.resetStats()
load.setCutoffVoltage(2.8)

load.setTargetCurrent(0.3)
load.setTimer(None)

log = open("log.csv", "a")
log.write("time,seconds,voltage,current,capacity")
log.write("\n")

start = time.time()

load.enable()

while True:

    try:
        values = [
          load.getTime(),
          int(time.time() - start), # Can be calculated from time but just more convenient to use
          load.getVoltage(),
          load.getCurrent(),
          load.getCapacity()
        ]

        def text(v):
            if v is None:
                return ''
            else:
                return str(v)

        row = ",".join(map(text, values))
        log.write(row)
        log.write("\n")

        print(row)

    except:
        print("Error reading sample")

    time.sleep(10)

log.disable()

