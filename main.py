from ctypes import *
import win32process
import win32api
import win32gui
import win32con
import os

GAME_WIDTH_ADDR = 0x01005334
GAME_HEIGHT_ADDR = 0x01005338
GAME_DATA_ADDR = 0x01005361
MEM_WIDTH = 32
PAGE_EXECUTE_READWRITE = 0x40
PROCESS_ALL_ACCESS = (0x0020 | 0x0400 | 0x000F0000 | 0x00100000 | 0xFFF)
VIRTUAL_MEM = (0x1000 | 0x2000)

GAME_PATH = os.path.join(os.getcwd(), "winmine.exe")  # 游戏路径
GAME_TITLE = "扫雷"  # 游戏窗口标题

kernel32 = windll.LoadLibrary("kernel32.dll")


def enum_windows_callback(hwnd, result):
    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) == GAME_TITLE:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        result.append((hwnd, pid))


def find_game_window():
    hwnd = win32gui.FindWindow(None, GAME_TITLE)
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    return hwnd, pid


def wg(window_handle):
    _, pid = win32process.GetWindowThreadProcessId(window_handle)
    if not pid:
        return

    phand = win32api.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not phand:
        print("进程打开失败!")
        return

    game_width = c_int(0)
    kernel32.ReadProcessMemory(int(phand), GAME_WIDTH_ADDR, byref(game_width), 2, None)
    game_height = c_int(0)
    kernel32.ReadProcessMemory(int(phand), GAME_HEIGHT_ADDR, byref(game_height), 2, None)

    addr = create_string_buffer(MEM_WIDTH * game_height.value)
    kernel32.ReadProcessMemory(int(phand), GAME_DATA_ADDR, byref(addr), MEM_WIDTH * game_height.value, None)

    for i in range(game_height.value):
        for j in range(game_width.value):
            current = hex(addr.value[i * MEM_WIDTH + j])

            if current == "0xf":
                win32api.PostMessage(window_handle, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON,
                                     win32api.MAKELONG(19 + j * 16, 63 + i * 16))
                win32api.PostMessage(window_handle, win32con.WM_LBUTTONUP, 0, 0)
    print("通关成功!")


def main():
    try:
        window_handle, pid = find_game_window()
        wg(window_handle)
    except OSError:
        print("出现异常！请确保游戏进程已成功开启。")


if __name__ == "__main__":
    main()
