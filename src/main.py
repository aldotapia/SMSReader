# Description: Main script for the RPi Pico W to read sensor data and send it to the server.
import gc
import time
from machine import Pin
import network
import ntptime
import ujson
from functions import *
import micropython
from umodbus.serial import Serial as ModbusRTUMaster


micropython.kbd_intr(ord('q'))

# load secrets.json
with open('secrets.json') as f:
    secrets = ujson.load(f)

print(secrets)

station_id = secrets.get('station_id')
url = secrets.get('url')
credentials = secrets.get('credentials')
api_login = secrets.get('api_login')
api_send = secrets.get('api_send')
api_send = f'{api_send}/{station_id}/data'
ssid = secrets.get('wifi_ssid')
password = secrets.get('wifi_password')

# config
rtu_pins = (0, 1) # (TX, RX)
uart_id = 0
ctrl_pin = 2
slave_addr = 1
address = 0
qty = 2
period = 10 # minutes
debug = False

# config modbus
host = ModbusRTUMaster(
    pins=rtu_pins,
    ctrl_pin=ctrl_pin,
    uart_id=uart_id
)

# set led pin to test reading the secrets file
blink("LED", 3, 0.15)

# print start
printd('Starting program', debug)
printd(f'Period: {period} minutes', debug)

# connect to wifi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
printd(f"Is the Wireless LAN active? {wlan.active()}", debug)
# list the available networks
printd(f"Available networks: {wlan.scan()}", debug)
wlan.connect(ssid, password)

i = 0
while wlan.isconnected() == False:
    printd('Waiting for connection...', debug)
    time.sleep(1)
    i = i + 1
    # reset the board if it can't connect in 30 seconds
    if i == 30:
        machine.reset()

# Get the IP address and subnet mask
ip_address = wlan.ifconfig()[0]
subnet_mask = wlan.ifconfig()[1]

printd(f'Connected to WiFi with IP address {ip_address} and subnet mask {subnet_mask}', debug)

# get time from server
ntptime.settime()
ntp_alarm = time.time() + 24*60*60*2 # set alarm to update time every 2 days

# get time
now = time.localtime()
min = now[4]
sec = now[5]

# set alarm
alarm = time.time() + (((min//period)*period + period) - min)*60 - (60 - sec) + 5
printd(f'Time: {time.time()}', debug)
printd(f'Alarm set to {alarm}', debug)

printd('Program started', debug)

token = None
token_alarm = time.time() - 1

gc.collect()

print('Starting main loop')
while True:
    if time.time() > alarm:
        printd('Reading data', debug)

        blink("LED", 5, 0.1)

        now = time.localtime()
        time_stamp = f'{now[0]:04}-{now[1]:02}-{now[2]:02} {now[3]:02}:{(now[4]//period)*period:02}:00'
        # read modbus
        t = 0
        while t < 5:
            try:
                values = host.read_holding_registers(slave_addr=slave_addr, starting_addr=address, register_qty=qty, signed=False)
                values = list(values)
                printd(values, debug)
                # physical signal
                blink("LED", 5, 0.1)
                t = 5
            except:
                printd('Error reading data', debug)
                # physical signal
                blink("LED", 2, 2)
                time.sleep(1)
                t = t + 1
                if t == 5:
                    values = [-999, -999]

        gc.collect()

        data = {'station_id': station_id, 'date': time_stamp, 's1': values[0], 's2': values[1]}

        if time.time() > token_alarm:
            token = None

        # check if connected
        if not wlan.isconnected():
            printd('Reconnecting to WiFi', debug)
            blink("LED", 2, 2)
            wlan.connect(ssid, password)
            i = 0
            while wlan.isconnected() == False:
                printd('Waiting for connection...', debug)
                time.sleep(1)
                i = i + 1
                # reset the board if it can't connect in 30 seconds
                if i == 30:
                    blink("LED", 1, 5)
                    machine.reset()
            printd('Connected to WiFi', debug)
            ntptime.settime()
            printd('Time updated', debug)

        gc.collect()

        # check ntp_alarm
        if time.time() > ntp_alarm:
            printd('Updating time', debug)
            ntptime.settime()
            ntp_alarm = time.time() + 24*60*60*2
            printd('Time updated', debug)

        if token == None:
            printd('Getting token', debug)
            auth_json = login(url, api_login, credentials, debug)
            token = auth_json.get('access_token')
            token_alarm = time.time() + 84400
            blink("LED", 5, 0.1)

        # check if is a dict
        if isinstance(auth_json, dict):
            printd('Login successful', debug)
            blink("LED", 5, 0.1)
        else:
            printd('Error logging in', debug)
            blink("LED", 2, 2)

        # send data
        i = 0
        response = 0
        while (response != 200) and (i < 5):
            printd('Sending data to server', debug)
            response = send_data(url, api_send, token, data, debug)
            time.sleep(1)
            i = i + 1

        if response == 200:
            printd('Data sent successfully', debug)
            blink("LED", 5, 0.1)
        else:
            printd('Error sending data', debug)
            blink("LED", 2, 2)

        now = time.localtime()
        min = now[4]
        sec = now[5]
        alarm = time.time() + (((min//period)*period + period) - min)*60 - (60 - sec) + 5
        gc.collect()
        blink("LED", 5, 0.1)
    time.sleep(1)
