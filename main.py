# mildly tested

import time
from neopixel import Neopixel
import random
import network
import ntptime
import machine

timezone_offset = 1* 3600
last_called=0
interval=3600

print(time.localtime(time.mktime(time.localtime())))
 
numpix = 14  # Number of NeoPixels per digit
# Pin where NeoPixels are connected
strip0 = Neopixel(numpix, 0, 0, "GRB")
strip1 = Neopixel(numpix, 1, 1, "GRB")
strip2 = Neopixel(numpix, 2, 2, "GRB")
strip3 = Neopixel(numpix, 3, 3, "GRB")
strips = [strip0, strip1, strip2, strip3]

digitcolor = (255, 0, 0)
# Wi-Fi credentials
SSID = "revspace-pub"
PASSWORD = ""

oldminutes=99

def everythingoff():
    strip0.fill((0,0,0))
    strip1.fill((0,0,0))
    strip2.fill((0,0,0))
    strip3.fill((0,0,0))

    strip0.show()
    strip1.show()
    strip2.show()
    strip3.show()


#    0
#  5   1
#    6
#  4   2
#    3
#
#

rolf = [
    [0,0,0,0,1,0,1],
    [0,0,1,1,1,0,1],
    [0,0,0,1,1,1,0],
    [1,0,0,0,1,1,1],
    ]

digits = [
  [1,1,1,1,1,1,0],    # 0
  [0,1,1,0,0,0,0],    # 1
  [1,1,0,1,1,0,1],    # 2
  [1,1,1,1,0,0,1],    # 3
  [0,1,1,0,0,1,1],    # 4
  [1,0,1,1,0,1,1],    # 5
  [1,0,1,1,1,1,1],    # 6
  [1,1,1,0,0,0,0],    # 7
  [1,1,1,1,1,1,1],    # 8
  [1,1,1,1,0,1,1]     # 9
  ]

spinnertable = [
    [1,0,0,0,0,0,0],
    [0,1,0,0,0,0,0],
    [0,0,1,0,0,0,0],
    [0,0,0,1,0,0,0],
    [0,0,0,0,1,0,0],
    [0,0,0,0,0,1,0],
    ]


digitmap = [2, 3, 4, 5, 13, 12, 11, 10, 9, 8, 0, 1, 7, 6]

def cijfer(positie, getal):
    getal=getal%10
    for i in range(7):
        if (digits[getal][i]):
            strips[positie].set_pixel(digitmap[i*2], digitcolor)
            strips[positie].set_pixel(digitmap[(i*2)+1], digitcolor)
        else:
            strips[positie].set_pixel(digitmap[i*2], (0, 0, 0))
            strips[positie].set_pixel(digitmap[(i*2)+1], (0, 0, 0))
    strips[positie].show()

def spinner(positie, getal):
    getal=getal%6
    for i in range(7):
        if (spinnertable[getal][i]):
            strips[positie].set_pixel(digitmap[i*2], digitcolor)
            strips[positie].set_pixel(digitmap[(i*2)+1], digitcolor)
        else:
            strips[positie].set_pixel(digitmap[i*2], (0, 0, 0))
            strips[positie].set_pixel(digitmap[(i*2)+1], (0, 0, 0))
    strips[positie].show()
    
def rolfer(positie, getal):
    getal=getal%4
    for i in range(7):
        if (rolf[getal][i]):
            strips[positie].set_pixel(digitmap[i*2], digitcolor)
            strips[positie].set_pixel(digitmap[(i*2)+1], digitcolor)
        else:
            strips[positie].set_pixel(digitmap[i*2], (0, 0, 0))
            strips[positie].set_pixel(digitmap[(i*2)+1], (0, 0, 0))
    strips[positie].show() 

def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    tries=0
    while not wlan.isconnected():
        spinner(1,tries)
        cijfer(2, tries//10)
        cijfer(3, tries%10)
        print("Connecting to wifi...")
        tries=tries+1
        time.sleep(1)
        if tries>24:
            machine.reset()
        
    print("Connected!")

def is_dst_europe(year, month, day, hour):
    """
    Determine if the given date and time is within European DST.
    DST in Europe:
        - Begins last Sunday of March at 1:00 UTC
        - Ends last Sunday of October at 1:00 UTC
    """
    def last_sunday(year, month):
        # Calculate the last Sunday of a given month and year
        for day in range(31, 24, -1):
            try:
                date = time.localtime(time.mktime((year, month, day, 0, 0, 0, 0, 0, 0)))
                if date[6] == 6:  # 6 is Sunday
                    return day
            except:
                continue
        return 31  # Default if unable to calculate (shouldn't happen)

    march_last_sunday = last_sunday(year, 3)
    october_last_sunday = last_sunday(year, 10)

    # DST begins from last Sunday of March at 1:00 UTC to last Sunday of October at 1:00 UTC
    start_dst = time.mktime((year, 3, march_last_sunday, 1, 0, 0, 0, 0, 0))
    end_dst = time.mktime((year, 10, october_last_sunday, 1, 0, 0, 0, 0, 0))

    current_time = time.mktime((year, month, day, hour, 0, 0, 0, 0, 0))
    return start_dst <= current_time < end_dst

def get_local_time():
    """
    Returns the local time with DST adjustment for Europe.
    """
    local_time_in_seconds = time.mktime(time.localtime()) + timezone_offset
    local_time = time.localtime(local_time_in_seconds)
    year, month, day, hour, minute, second, _, _= local_time

    if is_dst_europe(year, month, day, hour):
        hour += 1  # Add 1 hour for DST
    return (year, month, day, hour, minute, second)


def clock():
    global oldminutes
    current_time = get_local_time()  # Get the local time
    if current_time[4]!=oldminutes:
        oldminutes=current_time[4]
        updateclock(current_time[3],current_time[4])
        print(current_time)

def updateclock(uren, minuten):
    cijfer(0,uren//10)
    cijfer(1,uren%10)
    cijfer(2,minuten//10)
    cijfer(3,minuten%10)
    
def ntp_sync():
    ntpsync=0
    tries=0
    global last_called
    wlan = network.WLAN(network.STA_IF)
    everythingoff()
    while not ntpsync:
        try:
            ntptime.settime()  # This will set the time on the Pico W
            ntpsync=1
            last_called = time.mktime(time.localtime())
        except Exception as e:
            print(f"An error occurred: {e}")
            if wlan.isconnected():
                print("WLAN is connected")
                spinner(1,tries)
                cijfer(2, tries//10)
                cijfer(3, tries%10)
                print("trying NTP sync...")
                print(tries)
                tries=tries+1
                time.sleep(1)
                if tries>8:
                    machine.reset()
            else:
                connect_to_wifi()

def check_and_run():
    global last_called
    current_time = time.mktime(time.localtime())  # Get the current time in seconds

    # Check if the elapsed time since the last call is greater than the interval
    if current_time - last_called >= interval:
        ntp_sync()          # Call the function

print('hello')
for a in range(4):
    rolfer(a,a)
time.sleep(2)

everythingoff()
connect_to_wifi()
print('wifi')
ntp_sync()

while 1:
    check_and_run()
    clock()
    time.sleep_us(100000)
