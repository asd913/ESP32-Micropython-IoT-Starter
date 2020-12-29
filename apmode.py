# ---------------------------------------------------------------------------------------------------- #
# This is a simple form html so that we can get the ssid and the password
# ---------------------------------------------------------------------------------------------------- #
def web_page(ssid, pwd):
     
    html_page = """<!DOCTYPE html>
        <html>
        <head>
            <meta charset = "UTF-8">
            <title>IoT WIFI Update</title>
        </head>
          <body>
            <h2>Enter New WIFI Credentials</h2>
            <form>
              <label for="ssid">SSID: </label>
              <input type="text" id="fname" name="ssid" value=""" + ssid + """><br><br>
              <label for="password">Password: </label>
              <input type="text" id="password" name="password" value=""" + pwd + """><br><br><br><br>
              <input type="submit" value="Submit">
            </form> 
          </body>
        </html>"""  
    return html_page


# ---------------------------------------------------------------------------------------------------- #
# Extract the ssid and password from the response text
# ---------------------------------------------------------------------------------------------------- #
def pullData(request1):
    splitRequestStr = request1.split('?ssid=')
    ssidpwd_combined = splitRequestStr[1].split(' HTTP/1.1')
    ssidpwdsplit= ssidpwd_combined[0].split('&password=')
    ssid1 = ssidpwdsplit[0].rstrip("\n").rstrip()
    password1 = ssidpwdsplit[1].rstrip("\n").rstrip()
    return ssid1,password1


# ---------------------------------------------------------------------------------------------------- #
# This function will start an Access Point with hardcoded ssid. It will serve the webpage html and wait
# for a response that includes a ssid filled in. This method doesn't seem very secure so improvements 
# would be welcome. 
# ---------------------------------------------------------------------------------------------------- #
def setupAP(ssidOld,passwordOld):

    import network
    ssid = 'Update-IoT-WIFI'
    password = '123456789'

    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=ssid, password=password)
    while not ap.active():
        pass
    print('network config:', ap.ifconfig())


    # create the socket
    # AF_INET == ipv4
    # SOCK_STREAM == TCP
    import socket
    sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckt.bind(('',80)) 
    sckt.listen(5)     

    # Function for creating the
    request1 = ""
    while request1.find("ssid")==-1:  # wait for a response that includes ssid in it
        conn, addr = sckt.accept() #clientsocket, address of client
        print("Got connection from %s" % str(addr))
        response = web_page(ssidOld,passwordOld)#Prepare the webpage with old ssid and password stored
                                                #so the user can see what it was set to previously.
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response) #Send the webpage.
        request=conn.recv(1024)
        request1 = str(request) # Convert the url returned to string
        print("Content %s" % request1)
        conn.close()
    
    # Turn off the AP
    ap.disconnect()
    ap.active(False)
    
    #extract the ssid and password from the response text
    ssid1,password1 = pullData(request1)
    return ssid1,password1