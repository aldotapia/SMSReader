import time
import ujson
import machine
from machine import Pin
import urequests as requests


# led blink
def blink(led, times, seconds):
    '''
    Function to blink a led

    Parameters:
    led: int, pin number
    times: int, number of times to blink the led
    seconds: int, seconds to wait between blinks

    Returns:
    None
    '''
    led = Pin(led, machine.Pin.OUT)
    i = 0
    while i < times:
        led.on()
        time.sleep(seconds)
        led.off()
        time.sleep(seconds)
        i = i + 1

def printd(message, debug = False):
    '''
    Function to print messages for debugging

    Parameters:
    message: str, message to print
    debug: bool, if True, print the message

    Returns:
    None
    '''
    if debug:
        print(message)
    else:
        pass

def login(url, api_login, credentials, debug = False):
    '''
    Function to login to the API

    Parameters:
    url: str, url of the API
    api_login: str, endpoint to login
    credentials: dict, credentials to login

    Returns:
    json, response from the server or int, status code
    '''
    headers = {'Content-Type': 'application/json'}
    res = requests.post(url=f'{url}{api_login}', data = ujson.dumps(credentials), headers = headers)
    if res.status_code != 200:
        printd(f'Error: {res.status_code}', debug)
        return res.status_code
    return res.json()

def send_data(url, api_send, token, data, debug = False):
    '''
    Function to send data to the server

    Parameters:
    url: str, url of the API
    api_send: str, endpoint to send data
    token: str, token to authenticate
    data: dict, data to send
    debug: bool, if True, print the message

    Returns:
    json, response from the server or int, status code
    '''
    headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {token}'}
    res = requests.post(url=f'{url}{api_send}', data = ujson.dumps(data), headers = headers)
    if res.status_code != 200:
        printd(f'Error: {res.status_code}', debug)
        return res.status_code
    return res.status_code