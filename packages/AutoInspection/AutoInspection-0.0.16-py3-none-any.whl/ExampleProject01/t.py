import subprocess

exe_path = r"C:\Users\c026730\AppData\Roaming\Python\Python312\Scripts\hexss.exe"

# รัน process และต่อ stdout/stderr กลับมาให้อ่าน
process = subprocess.Popen(
    [exe_path, "camera_server"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

print("hexss.exe started. Showing logs (Ctrl+C to stop):")

try:
    for line in process.stdout:
        print(line, end="")  # แสดง log แบบ realtime
except KeyboardInterrupt:
    print("\nStopped reading logs, but hexss.exe will stop when Python stops.")


import subprocess

exe_path = r"C:\Users\c026730\AppData\Roaming\Python\Python312\Scripts\hexss.exe"

DETACHED_PROCESS = 0x00000008
subprocess.Popen(
    [exe_path, "camera_server"],
    creationflags=DETACHED_PROCESS,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    close_fds=True
)

print("hexss.exe started and will keep running even if this script exits.")
