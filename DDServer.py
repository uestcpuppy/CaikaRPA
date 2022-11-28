import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib
from DD.DDLib import DDLib
import os
import config

data_true = {'result': 'ok'}
data_false = {'result': 'failed'}
host = ('localhost', config.PORT_NUMBER_DD)

class Resquest(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        try:
            if self.path.find("favicon") != -1:
                pass
            else:
                tempDict =  (urllib.parse.parse_qs(self.path[1:]))
                # action = sendkeys 或 enter
                if tempDict["action"][0] == "sendkeys":
                    dd = DDLib()
                    dd.send_keys(tempDict["str"][0])
                elif tempDict["action"][0] == "enter":
                    dd = DDLib()
                    dd.dd_dll.DD_key(815, 1)
                    dd.dd_dll.DD_key(815, 2)
                elif tempDict["action"][0] == "killie":
                    ret = os.system("taskkill /F /IM iexplore.exe")
                    print (ret)
                elif tempDict["action"][0] == "killccb":
                    ret = os.system("taskkill /F /IM USBKeyTools.exe")
                    print(ret)
            self.wfile.write(json.dumps(data_true).encode())
        except Exception as e:
            self.wfile.write(json.dumps(data_false).encode())

if __name__ == '__main__':
    server = HTTPServer(host, Resquest)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()
