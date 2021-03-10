
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


```




# ELM & STN
https://www.scantool.net/downloads/98/stn1100-frpm.pdf
