#! coding=utf-8


import string
#import dnslib
from dnslib import DNSRecord,RR,DNSLabel


from gevent import socket
from gevent.server import DatagramServer,StreamServer

LOCALDNS = ("223.5.5.5",53) 

Hosts = {  
    "wezgc.cn":"123.56.3.153", # google ip  
    "www.wezgc.cn":"123.56.3.153", # google ip 
}

def udp_send(address,data):  
    sock = socket.socket(type=socket.SOCK_DGRAM)  
    sock.connect(address)  
    sock.send(data)  
    response, address = sock.recvfrom(8192*4)  
    return response,address 

class DNSServer(DatagramServer):
    """docstring for DNSServer"""

    def parse(self,data):
        try:
            dns = DNSRecord.parse(data)
        except Exception as e:
            print e

        return dns

    def handle(self,data,address):
        dns = self.parse(data)
        #print "get dns query from %s,query:%s" %(str(address),str(dns))
        find = False  
        IPAddress = None
        for preg,ip in Hosts.iteritems():  
            if dns.q.qname == preg:  
                find = True  
                IPAddress = ip
                break  

        if find and dns.q.qtype == 1: #only handle A record  
            print 'domain:%s in hosts' % dns.q.qname
            
            dns = dns.reply()
            dns.add_answer(*RR.fromZone(" A ".join([str(dns.q.qname),IPAddress])))
            self.socket.sendto(dns.pack(),address)
        else:  
            #print 'transfer for %s' % dns.q.qname  
            response,serveraddress = udp_send(LOCALDNS,data)  
            self.socket.sendto(response,address) 


class DNSTCPServer(StreamServer):
    """docstring for DNSTCPServer"""
    def handle(self,data,address):
        print data
        print address
        

        
if __name__ == '__main__':
    dnss = DNSServer("0.0.0.0:53")
    dnss.serve_forever()

    #tcp = DNSTCPServer("0.0.0.0:53")
    #tcp.serve_forever()








