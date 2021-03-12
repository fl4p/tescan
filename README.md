
```
sudo apt-get install libbluetooth-dev
pip install -r requirements.txt
```


# Bluetooth paring
sudo apt-get install bluetooth bluez-utils blueman
https://github.com/grimlockrocks/pi-bluetooth-obd
https://computingforgeeks.com/connect-to-bluetooth-device-from-linux-terminal/


https://stackoverflow.com/questions/63381965/bind-bluetooth-device-programmatically-to-rfcomm-via-python-in

https://sites.google.com/view/scanmytesla/home


# CAN Data

https://www.csselectronics.com/screen/page/simple-intro-to-can-bus/language/en

https://python-can.readthedocs.io/en/master/

DBC
https://www.csselectronics.com/screen/page/can-dbc-file-database-intro/language/en

##Model 3
https://github.com/joshwardell/model3dbc

Modifications:
* RawBattCurrent132: https://teslaownersonline.com/threads/diagnostic-port-and-data-access.7502/post-298438


##Model 3 samples
```
306 b'B395160064402000' # batV=383.25


# from https://docs.google.com/document/d/1QOUDZtQAxq2VuLvEkopZGWuEUu5NF1S-Tb9A0Fn-tV0/edit
306 70 96 AE FF 5C 26 FF 0F #batV=385.12 RawBattCurrent=9, SmoothBattCurrent=8.2, ChargeHRemain=4095


# nteresting vles
* battery: degradadion
* charging
 power consumption (dcdc, heater, drivetrain)
```


# Interesting Frames
* ID132HVBattAmpVolt # HV battery
* ID214FastChargeVA
* ID261_12vBattStatus
* ID352BMS_energyStatus # HV battery capacity

** Temperatures



# ELM & STN
https://www.scantool.net/downloads/98/stn1100-frpm.pdf


# Systemd
sudo cp tescan/etc/tescan-monitor.service /etc/systemd/system/


# Influx

```
CREATE DATABASE tescan_mon
CREATE USER tescan WITH PASSWORD 't3sc4n'
GRANT ALL ON tescan_mon TO tescan
```

# Send CAN message (write)
https://stackoverflow.com/questions/30983098/how-to-send-custom-can-messages-using-elm327
https://www.instructables.com/Exploring-the-Tesla-Model-S-CAN-Bus/
https://www.reddit.com/r/HackingTelsaMotors/comments/eroi0o/how_to_reverse_engineer_tesla_model_x_can_message/

# TODO
* fallback store to disk if influx na

* test multiplexing (ac&dc charge total )  
  https://cantools.readthedocs.io/en/latest/index.html?highlight=multiplex#cantools.database.can.Signal.multiplexer_signal
http://socialledge.com/sjsu/index.php/DBC_Format#:~:text=DBC%20file%20is%20a%20proprietary,bytes%20of%20CAN%20message%20data.&text=Essentially%2C%20each%20%22message%22%20defined,members%20of%20the%20C%20structure.
  