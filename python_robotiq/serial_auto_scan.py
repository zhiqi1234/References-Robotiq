"""Comprehensive serial Modbus RTU scanner.
尝试多种串口参数（baud, parity, stopbits, bytesize）和 unit id，读取 holding registers 区间
只读操作，不写入设备。将结果保存在 `serial_scan_report.json`。
"""
import json
import time
from datetime import datetime

# Import compatible Modbus serial client
try:
    from pymodbus.client.sync import ModbusSerialClient
except Exception:
    try:
        from pymodbus.client import ModbusSerialClient
    except Exception:
        ModbusSerialClient = None


def try_read(client, reg, unit):
    last_exc = None
    call_variants = [
        # holding registers variants
        lambda: client.read_holding_registers(address=reg, count=1, unit=unit),
        lambda: client.read_holding_registers(reg, 1, unit),
        lambda: client.read_holding_registers(reg, 1),
        lambda: client.read_holding_registers(address=reg, count=1),
        lambda: client.read_holding_registers(reg),
        # input registers variants
        lambda: client.read_input_registers(address=reg, count=1, unit=unit),
        lambda: client.read_input_registers(reg, 1, unit),
        lambda: client.read_input_registers(reg, 1),
        lambda: client.read_input_registers(address=reg, count=1),
        lambda: client.read_input_registers(reg),
    ]
    for fn in call_variants:
        try:
            rr = fn()
            return rr, None
        except TypeError as e:
            last_exc = e
            continue
        except Exception as e:
            # propagate I/O style errors up
            return None, e
    return None, last_exc


def scan(port='COM8', baud_list=None, parity_list=None, stopbits_list=None, bytesize_list=None, units=range(1,9), regs=range(0,16), timeout=0.5):
    if ModbusSerialClient is None:
        raise RuntimeError('pymodbus ModbusSerialClient not available')
    report = {
        'port': port,
        'started': datetime.utcnow().isoformat()+'Z',
        'results': []
    }
    if baud_list is None:
        baud_list = [115200, 38400, 19200, 9600]
    if parity_list is None:
        parity_list = ['N','E','O']
    if stopbits_list is None:
        stopbits_list = [1,2]
    if bytesize_list is None:
        bytesize_list = [8,7]

    for baud in baud_list:
        for parity in parity_list:
            for sb in stopbits_list:
                for bsize in bytesize_list:
                    config = dict(baud=baud, parity=parity, stopbits=sb, bytesize=bsize)
                    for unit in units:
                        cfg_entry = {'baud':baud,'parity':parity,'stopbits':sb,'bytesize':bsize,'unit':unit,'ok':False,'reads':{},'error':None}
                        try:
                            client = ModbusSerialClient(port=port, baudrate=baud, parity=parity, stopbits=sb, bytesize=bsize, timeout=timeout)
                            ok = client.connect()
                            cfg_entry['connect'] = bool(ok)
                            if not ok:
                                cfg_entry['error'] = 'connect_failed'
                                report['results'].append(cfg_entry)
                                try:
                                    client.close()
                                except Exception:
                                    pass
                                continue
                            for reg in regs:
                                try:
                                    rr, err = try_read(client, reg, unit)
                                    if err is not None:
                                        cfg_entry['reads'][str(reg)] = {'ok':False, 'error': str(err)}
                                    else:
                                        # extract registers if any
                                        if hasattr(rr, 'registers'):
                                            cfg_entry['reads'][str(reg)] = {'ok':True, 'registers': rr.registers}
                                            cfg_entry['ok'] = True
                                        else:
                                            cfg_entry['reads'][str(reg)] = {'ok':False, 'result': str(rr)}
                                except Exception as e:
                                    cfg_entry['reads'][str(reg)] = {'ok':False, 'error': str(e)}
                            client.close()
                        except Exception as e:
                            cfg_entry['error'] = str(e)
                        report['results'].append(cfg_entry)
    report['finished'] = datetime.utcnow().isoformat()+'Z'
    return report

if __name__ == '__main__':
    import argparse, os
    p = argparse.ArgumentParser()
    p.add_argument('--port', default='COM8')
    p.add_argument('--out', default='serial_scan_report.json')
    p.add_argument('--regs', default='0-15')
    args = p.parse_args()
    if '-' in args.regs:
        a,b = args.regs.split('-',1)
        regs = range(int(a), int(b)+1)
    else:
        regs = [int(x) for x in args.regs.split(',') if x.strip()]
    try:
        r = scan(port=args.port, regs=regs)
        with open(args.out, 'w', encoding='utf-8') as f:
            json.dump(r, f, ensure_ascii=False, indent=2)
        print('Wrote', os.path.abspath(args.out))
    except Exception as e:
        print('Scan failed:', e)
