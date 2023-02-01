from ctypes import *
import time
import win32api

class DDLib(object):
    def __init__(self):
        print("Load DD!")
        path = r'.\DD\DD94687.64.dll'
        print(path)
        self.dd_dll = windll.LoadLibrary(path)
        st = self.dd_dll.DD_btn(0)
        if st == 1:
            print("DD Initialize:OK")
        else:
            print("DD Initialize:Error")

        # DD虚拟码，可以用DD内置函数转换。
        self.vk = {'5': 205, 'c': 503, 'n': 506, 'z': 501, '3': 203, '1': 201, 'd': 403, '0': 210, 'l': 409, '8': 208,
                   'w': 302, 'u': 307, '4': 204, 'e': 303, '[': 311, 'f': 404, 'y': 306, 'x': 502, 'g': 405, 'v': 504,
                   'r': 304, 'i': 308, 'a': 401, 'm': 507, 'h': 406, '.': 509, ',': 508, ']': 312, '/': 510, '6': 206,
                   '2': 202, 'b': 505, 'k': 408, '7': 207, 'q': 301, "'": 411, '\\': 313, 'j': 407, '`': 200, '9': 209,
                   'p': 310, 'o': 309, 't': 305, '-': 211, '=': 212, 's': 402, ';': 410}
        # 需要组合shift的按键。
        self.vk2 = {'"': "'", '#': '3', ')': '0', '^': '6', '?': '/', '>': '.', '<': ',', '+': '=', '*': '8', '&': '7',
                    '{': '[', '_': '-', '|': '\\', '~': '`', ':': ';', '$': '4', '}': ']', '%': '5', '@': '2', '!': '1',
                    '(': '9'}

    def __del__(self):
        win32api.FreeLibrary(self.dd_dll._handle)

    def send_keys(self, keys):
        for i in keys:
            self.dd(i)
            time.sleep(0.3)

    def clickBtn(self):
        self.dd_dll.DD_btn(1)
        time.sleep(1)
        self.dd_dll.DD_btn(2)
        time.sleep(1)

    def move(x, y):
        self.dd_dll.DD_move(x, y)

    def down_up(self, code):
        # 进行一组按键。
        self.dd_dll.DD_key(self.vk[code], 1)
        self.dd_dll.DD_key(self.vk[code], 2)

    def dd(self, i):
        # 500是shift键码。
        if i.isupper():
            # 如果是一个大写的玩意。
            # 按下抬起。
            self.dd_dll.DD_key(500, 1)
            self.down_up(i.lower())
            self.dd_dll.DD_key(500, 2)
        elif i in '~!@#$%^&*()_+{}|:"<>?':
            # 如果是需要这样按键的玩意。
            self.dd_dll.DD_key(500, 1)
            self.down_up(self.vk2[i])
            self.dd_dll.DD_key(500, 2)
        else:
            self.down_up(i)


if __name__ == '__main__':
    dd = DDLib()
    dd.send_keys("helloworld")

















