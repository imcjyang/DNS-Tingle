import sys
import getopt
import socketserver
from datetime import datetime

from message_parser import MessageParser

class DNSServer(socketserver.BaseRequestHandler):
    def handle(self):
        # try:
        debugLevel = 0
        cacheFile = 'cache.txt'
        localFile = 'dnsrelay.txt'
        foreignServer = '10.3.9.4'
        helpDoc = ('usage: dnsrelay [OPTION]...\n'
                    '  -h, --help\t帮助文档\n'
                    '  -d, --debug=LEVEL\t调试等级1或2\n'
                    '  -c, --cache=PATH\t指定缓存文件路径\n'
                    '  -f, --filename=PATH\t指定配置文件路径\n'
                    '  -s, --server=IPADDR\t外部DNS服务器的IP地址')
        try:
            opts, args = getopt.getopt(sys.argv[1:], 'hd:c:f:s:', ['help', 'debug=', 'cache=', 'filename=', 'server='])
            for opt, arg in opts:
                if opt in ('-d', '--debug'):
                    debugLevel = int(arg)
                elif opt in ('-c', '--cache'):
                    cacheFile = arg
                elif opt in ('-f', '--filename'):
                    localFile = arg
                elif opt in ('-s', '--server'):
                    foreignServer = arg
        except getopt.GetoptError:
            print(helpDoc)
            sys.exit(1)

        queryMsg = self.request[0]
        querySock = self.request[1]
        msgParser = MessageParser(queryMsg, cacheFile, localFile, foreignServer)
        querySock.sendto(msgParser.resp, self.client_address)

        debugInfo = ''
        if debugLevel == 1:
            debugInfo += datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            debugInfo += '\tClient: %s' % self.client_address[0]
            debugInfo += '\t%s' % msgParser.queryMsg['question']['QNAME']
        elif debugLevel == 2:
            debugInfo += '****************************FROM****************************\n'
            debugInfo += datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            debugInfo += '\tClient: %s\n' % self.client_address[0]
            debugInfo += '****************************QUERY***************************\n'
            debugInfo += 'MESSAGE: %s\n' % msgParser.msg
            debugInfo += '***************************HEADER***************************\n'
            debugInfo += 'ID: %s\n' % msgParser.respMsg['header']['ID']
            debugInfo += 'QDCOUNT: %d\t' % msgParser.queryMsg['header']['QDCOUNT']
            debugInfo += 'ANCOUNT: %d\t' % msgParser.queryMsg['header']['ANCOUNT']
            debugInfo += 'NSCOUNT: %d\t' % msgParser.queryMsg['header']['NSCOUNT']
            debugInfo += 'ARCOUNT: %d\n' % msgParser.queryMsg['header']['ARCOUNT']
            debugInfo += '**************************QUESTION**************************\n'
            debugInfo += 'QNAME: %s\n' % msgParser.queryMsg['question']['QNAME']
            debugInfo += 'QTYPE: %d\t' % msgParser.queryMsg['question']['QTYPE'] 
            debugInfo += 'QCLASS: %d\n' % msgParser.queryMsg['question']['QCLASS']
            debugInfo += '***************************RESPONSE*************************\n'
            debugInfo += 'MESSAGE: %s\n' % msgParser.resp
            debugInfo += '***************************HEADER***************************\n'
            debugInfo += 'ID: %s\n' % msgParser.respMsg['header']['ID']
            debugInfo += 'QDCOUNT: %d' % msgParser.respMsg['header']['QDCOUNT']
            debugInfo += '\tANCOUNT: %d' % msgParser.respMsg['header']['ANCOUNT']
            debugInfo += '\tNSCOUNT: %d' % msgParser.respMsg['header']['NSCOUNT']
            debugInfo += '\tARCOUNT: %d\n' % msgParser.respMsg['header']['ARCOUNT']
            debugInfo += '***************************ANSWER***************************\n'
            debugInfo += 'ANAME: %s\n' % msgParser.respMsg['answer']['ANAME']
            debugInfo += 'ATYPE: %d\t' % msgParser.respMsg['answer']['ATYPE']
            debugInfo += 'ACLASS: %d\n' % msgParser.respMsg['answer']['ACLASS']
            debugInfo += 'TTL: %d\n' % msgParser.respMsg['answer']['TTL']
            debugInfo += 'RDLENGTH: %d\n' % msgParser.respMsg['answer']['RDLENGTH']
            debugInfo += 'RDDATA: %s\n\n\n' % msgParser.respMsg['answer']['RDDATA']
        if debugLevel > 0:
            print(debugInfo)


if __name__ == "__main__":
    helpDoc = ('usage: dnsrelay [OPTION]...\n'
            '  -h, --help\t帮助文档\n'
            '  -d, --debug=LEVEL\t调试等级1或2\n'
            '  -c, --cache=PATH\t指定缓存文件路径\n'
            '  -f, --filename=PATH\t指定配置文件路径\n'
            '  -s, --server=IPADDR\t外部DNS服务器的IP地址')
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hd:c:f:s:', ['help', 'debug=', 'cache=', 'filename=', 'server='])
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                print(helpDoc)
                sys.exit(0)
    except getopt.GetoptError:
        print(helpDoc)
        sys.exit(1)

    HOST_PORT = ('127.0.0.1', 53)
    server = socketserver.ThreadingUDPServer(HOST_PORT, DNSServer)
    server.serve_forever()