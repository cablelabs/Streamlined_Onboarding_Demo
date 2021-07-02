
import wpa_ctrl_iface as wpa_ctrl
import threading
import time
import subprocess
#import asyncio
import socketio 
import sys
#from socketIO_client import SocketIO
#from flask_socketio import SocketIO, emit

version = lambda: (1, 0, 1)



class Lease:

    def __init__(self,time,mac,ip,name="unknown"):
        self.mac = mac
        self.ip = ip
        self.time = time
        self.name = name

class WPACtrl:

    def __init__(self, ctrl_iface_path):
        self.attached = 0

        self.ctrl_iface_path = ctrl_iface_path

        self.ctrl_iface = wpa_ctrl.wpa_ctrl_open(ctrl_iface_path)

        if not self.ctrl_iface:
            raise error('wpa_ctrl_open failed')


    def close(self):
        if self.attached == 1:
            self.detach()

        wpa_ctrl.wpa_ctrl_close(self.ctrl_iface)

    def __del__(self):
        self.close()

    def request(self, cmd):
        '''
        Send a command to wpa_supplicant/hostapd. Returns the command response
		in a string.
        '''

        try:
            data = wpa_ctrl.wpa_ctrl_request(self.ctrl_iface, cmd)
        except wpa_ctrl.socket.error:
            raise error('wpa_ctrl_request failed')

        if data == -2:
            raise error('wpa_ctrl_request timed out')

        return data

    def attach(self):
        '''
        Register as an event monitor for the control interface.
        '''
        if self.attached == 1:
            return

        try:
            ret = wpa_ctrl.wpa_ctrl_attach(self.ctrl_iface)
        except wpa_ctrl.socket.error:
            raise error('wpa_ctrl_attach failed')

        if ret == True:
            self.attached = 1
        elif ret == -2:
            raise error('wpa_ctrl_attach timed out')

    def detach(self):
        '''
        Unregister event monitor from the control interface.
        '''
        if self.attached == 0:
            return

        try:
            ret = wpa_ctrl.wpa_ctrl_detach(self.ctrl_iface)
        except wpa_ctrl.socket.error:
            raise error('wpa_ctrl_detach failed')

        if ret == True:
            self.attached = 0
        elif ret == -2:
            raise error('wpa_ctrl_attach timed out')

    def pending(self):
        '''
        Check if any events/messages are pending. Returns True if messages are pending,
		otherwise False.
        '''
        try:
            return wpa_ctrl.wpa_ctrl_pending(self.ctrl_iface)
        except wpa_ctrl.socket.error:
            raise error('wpa_ctrl_pending failed')

    def recv(self):
        '''
        Recieve a pending event/message from ctrl socket. Returns a message string.
        '''
        data = wpa_ctrl.wpa_ctrl_recv(self.ctrl_iface)
        return data

    def scanresults(self):
        '''
        Return list of scan results. Each element of the scan result list is a string
		of properties for a single BSS. This method is specific to wpa_supplicant.
        '''

        bssids = []

        for cell in range(1000):
            ret = self.request('BSS %d' % cell)
            print(ret)
            if 'bssid=' in ret:
                bssids.append(ret)
            else:
                break

        return bssids

def get_dhcp_info(mac,leases_path):
    leases_file = open(leases_path,'r')
    ip =""
    #array of lease objects
    leases = []

    for line in leases_file:
        if len(line):
            lease_array = line.split(" ")
            if len(lease_array) == 5:
                lease = Lease(lease_array[0],lease_array[1],lease_array[2],lease_array[3])
            else:
                lease = Lease(lease_array[0],lease_array[1],lease_array[2])
            leases.append(lease)
    for lease in leases:
        #print("IP:{} MAC:{}".format(lease.ip,lease.mac))
        if mac == lease.mac:
            return lease




class error(Exception): pass

def delete_stale_files(mac):
    try:
        os.remove("/tmp/"+mac+"_capture_udp.csv")
        os.remove("/tmp/"+mac+"_capture_tcp.csv")
    except:
        print("Unable to remove:{}".format("/tmp/"+mac+"_capture_tcp.csv"))



print("Starting")

port =5000
ip = '192.168.2.7'


#websocket
#sio = SocketIO('localhost', 5000)
#sio = SocketIO()
#sio = socketio.AsyncClient()
sio = socketio.Client()
sio.connect("http://localhost:5000")

#initiate hostapd socket
wpa = WPACtrl("/var/run/hostapd/wlan1")
#path to leases file
leases_path ='/var/lib/misc/dnsmasq.leases'
#attach event listener
wpa.attach()

thread_names = []


while True:  #loop forever for new events
    if wpa.pending():
        event = wpa.recv().decode()
        if len(event):
            event_array = event.split(" ")
            if len(event_array) == 2:
                action = event_array[0]
                mac = event_array[1]
                mac_id = event_array[1].replace(':','')
                if "AP-STA-DISCONNECTED" in action:
                    print("Disconnected: {}".format(mac))
                    sio.emit('device_remove',{"mac":mac,"mac_id":mac_id})
                    #emit('device_remove',{"mac":mac,"mac_id":mac_id})
                    #remove mac from thread pool
                    if mac in thread_names:
                        thread_names.remove(mac)
                if "AP-STA-CONNECTED" in action:
                    ip = None 
                    while ip == None:
                        device_lease = get_dhcp_info(mac,leases_path)
                        try:
                            ip = device_lease.ip
                        except:
                            print("Waiting for IP: [{}] ".format(mac))
                            time.sleep(1)
                            continue
                        try:
                            name = device_lease.name
                        except:
                            name = "UNKNOWN"
                    print("Connected: {}".format(mac))
                    sio.emit('device_add',{"mac":mac,"mac_id":mac_id,"ip":ip,"name":name})
                    #emit('device_add',{"mac":mac,"mac_id":mac_id,"ip":ip,"name":name})
                    time.sleep(6)
                    for thread in threading.enumerate():
                        if thread.name == mac:
                            thread_names.append(mac)
  #                  if not mac in thread_names:
  #                      x = threading.Thread(target=start_capture, name=mac, kwargs={'mac':mac_id,'ip':ip})
  #                      x.start()
  #                  b = threading.Thread(target=get_device_complexities, kwargs={'mac':mac_id})
  #                  b.start()
  #                  c = threading.Thread(target=get_device_boundary_flows, kwargs={'mac':mac_id,'ip':ip})
  #                  c.start()
                    #x.join()
                    #b.join()
                    #c.join()

    else:
        time.sleep(0.5)



