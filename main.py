def setRTC():
    from machine import RTC
    rtc = RTC()
    import ntptime
    ntptime.settime()
    print ("The time is", rtc.datetime())


print('RUNNING main.py')

# ---------------------------------------------------------------------------------------------------- #
# Set the onboard LED off
# ---------------------------------------------------------------------------------------------------- #
import machine
led = machine.Pin(2,machine.Pin.OUT)
led.off()

# ---------------------------------------------------------------------------------------------------- #
# Loop until we have a wifi connection. This will loop between trying to connect to a WIFI or setting
# new wifi credentials through an AP. If you type incorrect credentials, it will try them and return to
# AP mode so that you can re-enter the credentials.
# ---------------------------------------------------------------------------------------------------- #
import ConnectWifi
while ConnectWifi.connect() == False:
    pass

# ---------------------------------------------------------------------------------------------------- #
# It will continue the rest of the program only after wifi connection established.
# ---------------------------------------------------------------------------------------------------- #
print("we are connected to wifi")
setRTC() # Set the Real Time Clock to NTP
led.on() # Set the onboard LED off


