import network
import socket
ssid = 'Update-IoT-WIFI'
password = '123456789'
ap_authmode = 3
sckt = None


# ---------------------------------------------------------------------------------------------------- #
# Send a header based on the payload length.
# ---------------------------------------------------------------------------------------------------- #
def send_header(client, status_code=200, content_length=None ):
    client.sendall("HTTP/1.0 {} OK\r\n".format(status_code))
    client.sendall("Content-Type: text/html\r\n")
    if content_length is not None:
      client.sendall("Content-Length: {}\r\n".format(content_length))
    client.sendall("\r\n")


    
# ---------------------------------------------------------------------------------------------------- #
# This is a simple form html that lists the ssid and allows the user to type a password
# ---------------------------------------------------------------------------------------------------- #
def web_page(ssids):
     
    html_page = """<!DOCTYPE html>
        <html>
        <head>
            <meta charset = "UTF-8">
            <title>IoT WIFI Update</title>
        </head>
          <body>
            <h2>IoT New WIFI Credentials</h2>
            <form action="entered" method="post">
                <table style="margin-left: auto; margin-right: auto;">
                    <tbody>
    """
    for x in ssids:  #this loop will list all the ssids passed into the function
        html_page = html_page + """\
                        <tr>
                            <td colspan="2">
                                <input type="radio" name="ssid" value=""" + x + """ />""" + x + """
                            </td>
                        </tr>
        """
    html_page = html_page +  """\
                        <tr>
                            <td>Password:</td>
                            <td><input name="password" type="password" /></td>
                        </tr>
                    </tbody>
                </table>
                <p style="text-align: center;">
                    <input type="submit" value="Submit" />
                </p>
            </form>
        </html>"""  
    return html_page


    
# ---------------------------------------------------------------------------------------------------- #
# Find the length of the data to send to the client and send them the data.
# ---------------------------------------------------------------------------------------------------- #
def send_response(client, payload, status_code=200):
    content_length = len(payload)
    if content_length > 0:
        client.sendall(payload)


    
# ---------------------------------------------------------------------------------------------------- #
# Returns the HTML for telling the user we are trying the new wifi credentials.
# ---------------------------------------------------------------------------------------------------- #
def newCredsPage():
    html_page = """
        <html>
            <center>
                <br><br>
                <h1 style="color: #5e9ca0; text-align: center;">
                    <span style="color: #ff0000;">
                        ESP trying new credentials now.<br>
                    </span>
                </h1>
                <br><br>
            </center>
        </html>"""  
    return html_page


    
# ---------------------------------------------------------------------------------------------------- #
# Returns the HTML for telling the user the new wifi credentials failed.
# ---------------------------------------------------------------------------------------------------- #
def FailedCredsPage():
    html_page = """
        <html>
            <center>
                <br><br>
                <h1 style="color: #5e9ca0; text-align: center;">
                    <span style="color: #AA0000;">
                        New credentials failed, please reenter.<br>
                    </span>
                </h1>
                <br><br>
            </center>
        </html>"""  
    return html_page


    
# ---------------------------------------------------------------------------------------------------- #
# Returns the HTML for telling the user the new wifi credentials succeeded.
# ---------------------------------------------------------------------------------------------------- #
def newCredsSuccessPage():
    html_page = """
        <html>
            <center>
                <br><br>
                <h1 style="color: #5e9ca0; text-align: center;">
                    <span style="color: #f0000bb;">
                        SUCCESS!!<br>
                    </span>
                </h1>
                <br><br>
            </center>
        </html>"""  
    return html_page


    
# ---------------------------------------------------------------------------------------------------- #
# Extract the ssid and password from the response text
# ---------------------------------------------------------------------------------------------------- #
def pullData(request1):
    splitRequestStr = request1.split('ssid=')
    ssidpwdsplit= splitRequestStr[1].split('&password=')
    ssid1 = ssidpwdsplit[0].rstrip("\n").rstrip()
    password1 = ssidpwdsplit[1].rstrip("\n").rstrip("'").rstrip()
    return ssid1,password1

def stop():
    global sckt

    if sckt:
        sckt.close()
        sckt = None

def checkWifi(ssid1, password1,station):
    import time
    station.connect(ssid1, password1)
    time.sleep(5)
    
    return station.isconnected()

    

# ---------------------------------------------------------------------------------------------------- #
# This function will start an Access Point with hardcoded ssid. It will serve the webpage html and wait
# for a response that includes a ssid filled in. This method doesn't seem very secure so improvements 
# would be welcome. 
# ---------------------------------------------------------------------------------------------------- #
def setupAP(ssids, station):


    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    stop()
    
    ap = network.WLAN(network.AP_IF)
    sckt = socket.socket()
    if not ap.active():
        ap.active(True)
        ap.config(essid=ssid, password=password, authmode=ap_authmode)
        while not ap.active():
            pass
        sckt.bind(addr) 
        sckt.listen(5)     
    print('network config:', ap.ifconfig())

    # create the socket
    # AF_INET == ipv4
    # SOCK_STREAM == TCP


    # Function for creating the
    request = b""
    while 'ssid=' not in str(request):  # wait for a response that includes ssid in it
        conn, addr = sckt.accept() #clientsocket, address of client
        print("Got connection from %s" % str(addr))
        response = web_page(ssids)
        send_header(conn)
        conn.sendall(response) #Send the webpage.
        request = b""
        try:
            while '\r\n\r\n' not in request:
                request += conn.recv(512)
        except OSError:
            pass
        print("Content ", str(request))
        if 'ssid=' in str(request):
            send_response(conn, newCredsPage())
            ssid1,password1 = pullData(str(request))
            if not checkWifi(ssid1, password1,station):
                print("Credentials, failed")
                send_response(conn, FailedCredsPage())
                request = b"" #force a new loop
                station.disconnect()
            else:
                send_response(conn, newCredsSuccessPage())
                station.disconnect()
        conn.close()
            
    # Turn off the AP
    sckt.close()
    sckt = None
    ap.active(False)
    
    #extract the ssid and password from the response text
    
    return ssid1,password1
