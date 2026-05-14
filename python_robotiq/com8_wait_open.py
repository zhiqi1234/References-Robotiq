"""
等待并尝试使用 COM8 的脚本：
- 循环检测 COM8 是否被其他程序占用
- 在可用时尝试通过 Modbus RTU 读取设备状态
- 如果成功，执行低速空载 open -> wait -> close
- 将日志写入 `python_robotiq/com8_action_log.txt`

使用示例：
  python python_robotiq/com8_wait_open.py --port COM8 --baud 115200 --unit 1 --timeout 60

注意：运行此脚本前请确保现场已清空人员并允许低速空载测试。
"""

import time
import argparse
import json
import traceback
from pathlib import Path
import sys
import os

# Ensure local package imports work when running script directly
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

LOG_PATH = Path(__file__).parent / 'com8_action_log.txt'

def log(msg):
    t = time.strftime('%Y-%m-%d %H:%M:%S')
    s = f"[{t}] {msg}"
    print(s)
    try:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(s + '\n')
    except Exception:
        pass

def try_open_and_test(port, baud, parity, stopbits, bytesize, unit, max_wait):
    from python_robotiq.robotiq_modbus import RobotiqModbus
    start = time.time()
    while True:
        elapsed = time.time() - start
        if max_wait and elapsed > max_wait:
            log(f"Timeout waiting for COM port after {max_wait}s")
            return False
        try:
            # Raw pyserial open test to detect PermissionError quickly
            try:
                import serial
                ser = serial.Serial(port, baudrate=baud, timeout=0.5, parity=parity, stopbits=stopbits, bytesize=bytesize)
                ser.close()
            except Exception as e:
                log(f"COM open failed: {e}")
                time.sleep(2)
                continue

            # Try Modbus RTU via RobotiqModbus
            log('COM opened, instantiating RobotiqModbus...')
            m = RobotiqModbus(serial_port=port, baudrate=baud, parity=parity, stopbits=stopbits, bytesize=bytesize, unit=unit)
            try:
                m.connect()
            except Exception as e:
                log(f'm.connect() failed: {e}')
                time.sleep(2)
                continue

            # Try simple status read
            try:
                st = m.get_status()
                log(f'get_status -> {st}')
            except Exception as e:
                log(f'get_status failed: {e}')
                m.close()
                time.sleep(2)
                continue

            # 如果到这里说明通信可用，执行低速空载 open/close
            try:
                speed = 10
                log(f'Performing low-speed open (speed={speed})')
                m.open(speed=speed)
                m.wait_for_move(timeout=10)
                time.sleep(1)
                log('Performing low-speed close')
                m.close(speed=speed)
                m.wait_for_move(timeout=10)
                log('Open/close sequence completed')
            except Exception as e:
                log(f'Action failed: {e}')
                traceback.print_exc()
            finally:
                try:
                    m.close()
                except Exception:
                    pass
            return True
        except Exception as e:
            log(f'Unhandled loop error: {e}')
            traceback.print_exc()
            time.sleep(2)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--port', default='COM8')
    p.add_argument('--baud', type=int, default=115200)
    p.add_argument('--parity', choices=['N','E','O'], default='N')
    p.add_argument('--stopbits', type=int, choices=[1,2], default=1)
    p.add_argument('--bytesize', type=int, choices=[7,8], default=8)
    p.add_argument('--unit', type=int, default=1)
    p.add_argument('--timeout', type=int, default=60, help='maximum seconds to wait for port available (0 = forever)')
    args = p.parse_args()

    log(f'Starting COM watcher for {args.port} (baud={args.baud} unit={args.unit})')
    ok = try_open_and_test(args.port, args.baud, args.parity, args.stopbits, args.bytesize, args.unit, args.timeout)
    log(f'Done: ok={ok}')

if __name__ == '__main__':
    main()
