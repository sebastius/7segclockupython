# mildly testes

import time
from neopixel import Neopixel
import random
import network
import ntptime


timezone_offset = 1* 3600
last_called=0
interval=3600

numpix = 14  # Number of NeoPixels
# Pin where NeoPixels are connected
strip0 = Neopixel(numpix, 0, 0, "GRB")
strip1 = Neopixel(numpix, 1, 1, "GRB")
strip2 = Neopixel(numpix, 2, 2, "GRB")
strip3 = Neopixel(numpix, 3, 3, "GRB")

digitcolor = (128, 0, 0)
# Wi-Fi credentials
SSID = ""
PASSWORD = ""

oldminutes=99

strip0.fill((0,0,0))
strip1.fill((0,0,0))
strip2.fill((0,0,0))
strip3.fill((0,0,0))

strip0.show()
strip1.show()
strip2.show()
strip3.show()

strips = [strip0, strip1, strip2, strip3]


#    0
#  5   1
#    6
#  4   2
#    3
#
#


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

digitmap = [2, 3, 4, 5, 13, 12, 11, 10, 9, 8, 0, 1, 7, 6]

print(digits[7])


def cijfer(positie, getal):
    for i in range(7):
        if (digits[getal][i]):
            strips[positie].set_pixel(digitmap[i*2], digitcolor)
            strips[positie].set_pixel(digitmap[(i*2)+1], digitcolor)
        else:
            strips[positie].set_pixel(digitmap[i*2], (0, 0, 0))
            strips[positie].set_pixel(digitmap[(i*2)+1], (0, 0, 0))
    strips[positie].show()


def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    while not wlan.isconnected():
        print("Connecting...")
        time.sleep(1)
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
    #cijfer(0,uren//10)
    #cijfer(1,uren%10)
    cijfer(0,minuten//10)
    cijfer(1,minuten%10)
    
def ntp_sync():
    ntptime.settime()  # This will set the time on the Pico W


def check_and_run():
    global last_called
    current_time = time.time()  # Get the current time in seconds

    # Check if the elapsed time since the last call is greater than the interval
    if current_time - last_called >= interval:
        ntp_sync()          # Call the function
        last_called = current_time  # Update last called time


print('hello')
connect_to_wifi()
print('wifi')

while 1:
    check_and_run()
    clock()
    time.sleep_us(100000)
