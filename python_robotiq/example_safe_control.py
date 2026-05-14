"""
示例：安全控制流程（交互确认、速率限制、异常保护）
使用方法：先按 README 填写寄存器映射（reg_map），然后运行：
python example_safe_control.py --ip 192.168.1.10 --cmd open
"""

import argparse
import sys
import time
import json
from robotiq_modbus import RobotiqModbus


def confirm(prompt):
    ans = input(prompt + ' (yes/no): ').strip().lower()
    return ans in ('y','yes')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', required=True)
    parser.add_argument('--cmd', choices=['open','close','stop','status'], required=True)
    parser.add_argument('--speed', type=int, default=120)
    parser.add_argument('--confirm', action='store_true', help='跳过交互确认')
    parser.add_argument('--reg-file', help='JSON 文件，包含寄存器映射')
    parser.add_argument('--serial', help='串口设备，例如 COM8（优先于 --ip）')
    parser.add_argument('--unit', type=int, default=1, help='Modbus unit id（从站号），默认 1')
    parser.add_argument('--force', action='store_true', help='强制执行（跳过确认）')
    parser.add_argument('--dry-run', action='store_true', help='不发送真实命令，仅打印')
    args = parser.parse_args()

    # TODO: 用实际寄存器映射替换下面的示例映射
    reg_map = {}
    if args.reg_file:
        try:
            with open(args.reg_file, 'r', encoding='utf-8') as f:
                reg_map = json.load(f)
        except Exception as e:
            print('Failed to load reg file:', e)
            sys.exit(1)

    # 如果同时指定了串口则优先使用串口连接
    if args.serial:
        gripper = RobotiqModbus(serial_port=args.serial, unit=args.unit, reg_map=reg_map, reg_file=args.reg_file)
    else:
        gripper = RobotiqModbus(args.ip, unit=args.unit, reg_map=reg_map, reg_file=args.reg_file)

    if not (args.confirm or args.force):
        ok = confirm(f"About to {args.cmd} gripper at {args.ip}, speed={args.speed}. Proceed?")
        if not ok:
            print('Aborted by user')
            sys.exit(1)

    if args.dry_run:
        print('Dry run: would connect and send command')
        print('Command:', args.cmd)
        sys.exit(0)

    try:
        with gripper.session():
            if gripper.check_emergency():
                raise RuntimeError('Emergency stop active, aborting')
            gripper.activate()
            # 强制限速
            speed = max(1, min(args.speed, gripper.speed_max))
            if args.cmd == 'open':
                gripper.open(speed=speed)
                gripper.wait_for_move(timeout=5)
            elif args.cmd == 'close':
                gripper.close(speed=speed)
                gripper.wait_for_move(timeout=5)
            elif args.cmd == 'stop':
                gripper.stop()
            elif args.cmd == 'status':
                print('status=', gripper.get_status())
            time.sleep(0.2)
    except Exception as e:
        print('Error:', e)
        try:
            gripper.stop()
        except Exception:
            pass

if __name__ == '__main__':
    main()
