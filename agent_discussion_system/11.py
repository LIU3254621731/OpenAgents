import time
import pyautogui

INTERVAL = 10  # 按键间隔（秒）

print("自动按键工具已启动，每 10 秒按一次 →")
print("请将焦点切换到目标窗口，按 Ctrl + C 结束程序")

try:
    while True:
        pyautogui.press('right')
        print("已按下 →")
        time.sleep(INTERVAL)
except KeyboardInterrupt:
    print("\n程序已手动终止")
