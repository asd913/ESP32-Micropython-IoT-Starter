# ---------------------------------------------------------------------------------------------------- #
# open the simple text file and copy the ssid and password from it
# the wifi.txt file only contains two lines of text, the first is the wifi ssid, the 2nd is the password
# ---------------------------------------------------------------------------------------------------- #
def GetCurrentCreds():
    filepath = 'wifi.txt'
    with open(filepath, 'r') as fp:
        ssid1 = fp.readline().rstrip("\n").rstrip()
        password1 = fp.readline().rstrip("\n").rstrip()
    fp.close()
    return ssid1,password1

# ---------------------------------------------------------------------------------------------------- #
# Starts wifi in station mode, uses the saved wifi credentials. If after 5 seconds, it can't connect,
# it will start in AP mode so you can update and save new credentials. 
# ---------------------------------------------------------------------------------------------------- #
def connect():
    import network
    import time

    ssid1,password1 = GetCurrentCreds()
    print("Current ssid =", ssid1)
    print("Current password =", password1)


    station = network.WLAN(network.STA_IF)
    station.active(True)

    if station.isconnected() == True:
        print("Already connected")
        return
 
    station.active(True)
    station.connect(ssid1, password1)
    time.sleep(5)

    state1= station.isconnected()
    print("Connection Status = ",state1)
    
    # If after 5 secs, the esp32 can't connect to wifi, the code executes the apmode.py code to allow the
    # user to enter new credentials.
    if state1 == False:
        station.disconnect()
        import apmode
        ssid1,password1 = apmode.setupAP(ssid1,password1)
        print("New ssid is ", ssid1)
        print("New password is ", password1)
        with open(filepath, 'w') as wf:
            wf.write(ssid1 + "\n" + password1 + "\n")
        wf.close()

    print(station.ifconfig())
    return state1