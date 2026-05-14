"""Serial diagnostic for Robotiq Modbus device.
用法示例：
python serial_diag.py --port COM8 --unit 1 --bauds 115200,38400,19200 --regs 0-8

脚本会尝试不同波特率建立 Modbus RTU 连接并读取若干保持寄存器（只读，不写）。
"""
import argparse
import time
import sys
try:
    from pymodbus.client.sync import ModbusSerialClient
except Exception:
    try:
        from pymodbus.client import ModbusSerialClient
    except Exception:
        ModbusSerialClient = None


def try_read(client, reg, unit):
    """Try multiple pymodbus call signatures to maximize compatibility.

    Returns (result, None) on success, or (None, exception) on failure.
    """
    last_exc = None
    callables = [
        lambda: client.read_holding_registers(address=reg, count=1, unit=unit),
        lambda: client.read_holding_registers(reg, 1),
        lambda: client.read_holding_registers(reg),
        lambda: client.read_input_registers(address=reg, count=1, unit=unit),
        lambda: client.read_input_registers(reg, 1),
        lambda: client.read_input_registers(reg),
    ]
    for fn in callables:
        try:
            rr = fn()
            return rr, None
        except Exception as e:
            last_exc = e
            continue
    return None, last_exc


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--port', required=True)
    p.add_argument('--unit', type=int, default=1)
    p.add_argument('--bauds', default='115200', help='comma separated')
    p.add_argument('--regs', default='0-6', help='range like 0-6 or comma list 0,1,2')
    p.add_argument('--timeout', type=float, default=1.0)
    args = p.parse_args()

    if '-' in args.regs:
        a,b = args.regs.split('-',1)
        regs = list(range(int(a), int(b)+1))
    else:
        regs = [int(x) for x in args.regs.split(',') if x.strip()]

    bauds = [int(x) for x in args.bauds.split(',')]

    for baud in bauds:
        print('--- Trying baud', baud, '---')
        try:
            client = ModbusSerialClient(port=args.port, baudrate=baud, timeout=args.timeout)
            ok = client.connect()
            print('connect ->', ok)
            if not ok:
                client.close()
                continue
            for reg in regs:
                try:
                    rr = try_read(client, reg, args.unit)
                    if rr is None:
                        print(f'reg {reg}: no response')
                    else:
                        # rr may be Exception or result
                        if hasattr(rr, 'isError') and rr.isError():
                            print(f'reg {reg}: read error:', rr)
                        else:
                            vals = rr.registers if hasattr(rr, 'registers') else rr
                            print(f'reg {reg}:', vals)
                except Exception as e:
                    print(f'reg {reg}: exc {e}')
            client.close()
        except Exception as e:
            print('baud', baud, 'failed:', e)
        time.sleep(0.1)

if __name__ == '__main__':
    main()
