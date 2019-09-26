from mss import mss
import cv2
import numpy
from win32api import MapVirtualKey
import win32con
from win32gui import (IsWindowVisible, PostMessage,
                      IsWindowEnabled, EnumWindows,
                      GetClientRect, GetWindowText, ScreenToClient, GetWindowRect)
from win32process import GetWindowThreadProcessId, EnumProcesses
from time import sleep
from ctypes import (c_char_p, c_ulong, byref, windll, c_buffer, sizeof)
import os

class Client():
    def __init__(self, name):
        self.name = name
        self.pid = self.__get_process()
        self.hwnd = self.__get_hwnds()
        self.client = self.__get_client()

    def __get_process(self):
        hModule = c_ulong()
        modname = c_buffer(30)
        procs = []
        for pid in EnumProcesses():
            hProcess = windll.kernel32.OpenProcess(0x0400 | 0x0010, False, pid)
            if hProcess:
                windll.psapi.GetModuleBaseNameA(hProcess, hModule.value, modname, sizeof(modname))
                if modname.value == bytes(self.name, 'ascii'):
                    procs.append(pid)
                for i in range(modname._length_):
                    modname[i]=b'\x00'
                windll.kernel32.CloseHandle(hProcess)
        return procs[0]

    def __get_hwnds(self):
        def callback(hwnd, hwnds):
            if IsWindowVisible(hwnd) and IsWindowEnabled(hwnd):
                _, found_pid = GetWindowThreadProcessId(hwnd)
                if found_pid == self.pid:
                    hwnds.append(hwnd)
                    return True

        hwnds = []
        EnumWindows(callback, hwnds)
        return hwnds[0]

    def __get_client(self):
        rect = GetClientRect(self.hwnd)
        point = ScreenToClient(self.hwnd, (0,0))
        x = abs(point[0])
        y = abs(point[1])
        w = rect[2]
        h = rect[3]
        return Rect(y, x, w, h)

    def match(self, buff, area):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        template = cv2.imread(f"{dir_path}{os.sep}img{os.sep}{buff}.png", 0)
        res = cv2.matchTemplate(area, template, cv2.TM_CCOEFF_NORMED)
        loc = numpy.where(res >= 0.8)
        return any(zip(*loc[::-1]))

    def push_button(self, key):
        lparam = (MapVirtualKey(key, 0) << 16) + 1
        PostMessage(self.hwnd, win32con.WM_KEYDOWN, key, lparam)
        sleep(0.5)
        PostMessage(self.hwnd, win32con.WM_KEYUP, key, lparam)

class Rect:
    def __init__(self, y, x, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def as_mss(self):
        return {"top": self.y, "left": self.x, "width": self.w, "height": self.h}

    def area(self, top, left, width, height):
        return {"top": top + self.y, "left": self.x + left, "width": width, "height": height}

client = Client("Neuz.exe")
area = client.client.area(369, 0, 120, 240)

with mss() as sct:
    while True:
        buffs = cv2.cvtColor(numpy.array(sct.grab(area)), cv2.COLOR_BGRA2GRAY)
        if client.match("hc", buffs):
            client.push_button(0x73)
