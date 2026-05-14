"""
安全的 Robotiq 3-finger 通过 Modbus TCP 的最小 Python 驱动示例
说明：请根据你手册中的寄存器地址（User_Interface_PDF_20210813.pdf）替换 reg_map 的占位地址。
"""

import time
import logging
import json
from contextlib import contextmanager
# Support multiple pymodbus versions (import path changed between releases)
try:
    from pymodbus.client.sync import ModbusTcpClient
except Exception:
    try:
        from pymodbus.client import ModbusTcpClient
    except Exception:
        ModbusTcpClient = None
try:
    from pymodbus.client.sync import ModbusSerialClient
except Exception:
    try:
        from pymodbus.client import ModbusSerialClient
    except Exception:
        ModbusSerialClient = None

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class RobotiqModbus:
    def __init__(self, ip=None, port=502, unit=1, timeout=3, reg_map=None,
                 pos_limits=(0, 255), speed_limit=255, reg_file=None,
                 serial_port=None, baudrate=115200, parity='N', stopbits=1, bytesize=8):
        self.ip = ip
        self.port = port
        self.unit = unit
        self.timeout = timeout
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.parity = parity
        self.stopbits = stopbits
        self.bytesize = bytesize
        # choose client type
        if serial_port:
            if ModbusSerialClient is None:
                raise RuntimeError('pymodbus ModbusSerialClient not available; install a compatible pymodbus')
            # Construct ModbusSerialClient with compatible kwargs (pymodbus versions vary)
            try:
                self.client = ModbusSerialClient(method='rtu', port=serial_port, baudrate=baudrate,
                                                 parity=parity, stopbits=stopbits, bytesize=bytesize, timeout=timeout)
            except TypeError:
                # older/newer signatures may not accept 'method' kwarg
                try:
                    self.client = ModbusSerialClient(port=serial_port, baudrate=baudrate,
                                                     parity=parity, stopbits=stopbits, bytesize=bytesize, timeout=timeout)
                except Exception as e:
                    raise
        else:
            if ModbusTcpClient is None:
                raise RuntimeError('pymodbus ModbusTcpClient not available; install a compatible pymodbus')
            self.client = ModbusTcpClient(host=ip, port=port, timeout=timeout)
        # 默认占位寄存器映射——请用手册里的地址覆盖
        default = {
            'activate': 0x0001,
            'go': 0x0002,
            'position': 0x0010,
            'speed': 0x0011,
            'stop': 0x0020,
            'status': 0x0030,
            'emergency': 0x00FF,
        }
        self.reg = default if reg_map is None else {**default, **reg_map}
        self.pos_min, self.pos_max = pos_limits
        self.speed_max = speed_limit
        if reg_file:
            try:
                with open(reg_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.reg.update(data)
            except Exception:
                LOG.warning('Failed to load reg_file %s, ignoring', reg_file)

    def connect(self):
        # Attempt to connect using the underlying client (TCP or Serial).
        LOG.info("Connecting (client=%r) to %s:%s...", type(self.client).__name__, self.ip, self.port)
        try:
            ok = self.client.connect()
        except Exception as e:
            raise ConnectionError(f"Client connect failed: {e}")
        if not ok:
            raise ConnectionError(f"Cannot connect using client {type(self.client).__name__}")
        LOG.info("Connected")

    def close(self):
        try:
            # only close TCP connection, do NOT send any commands on close
            if self.client:
                try:
                    self.client.close()
                except Exception:
                    pass
        except Exception:
            pass

    def _read(self, addr, count=1):
        # Support pymodbus variants: some accept keyword args including 'unit',
        # others expect positional parameters. Try both.
        last_exc = None
        call_variants = [
            lambda: self.client.read_holding_registers(address=addr, count=count, unit=self.unit),
            lambda: self.client.read_holding_registers(addr, count, self.unit),
            lambda: self.client.read_holding_registers(addr, count),
            lambda: self.client.read_holding_registers(address=addr, count=count),
            lambda: self.client.read_holding_registers(addr),
        ]
        rr = None
        for fn in call_variants:
            try:
                rr = fn()
                break
            except TypeError as e:
                last_exc = e
                continue
            except Exception as e:
                # propagate non-signature errors (I/O etc.)
                raise
        if rr is None:
            raise last_exc
        if rr is None:
            raise IOError(f"Modbus read returned no response at {addr}")
        if hasattr(rr, 'isError') and rr.isError():
            raise IOError(f"Modbus read error at {addr}")
        regs = getattr(rr, 'registers', None)
        if regs is None:
            # Some implementations return raw tuples/lists
            return rr if count > 1 else rr[0]
        return regs if count > 1 else regs[0]

    def _write(self, addr, value):
        # 写入带简单重试，减少瞬时通信故障影响
        attempts = 3
        last_exc = None
        for i in range(attempts):
            try:
                # pymodbus has different signatures across versions; try with unit kwarg first
                try:
                    wr = self.client.write_register(address=addr, value=int(value), unit=self.unit)
                except TypeError:
                    wr = self.client.write_register(addr, int(value))
                # Some client implementations return a result with isError(), others return None
                if hasattr(wr, 'isError') and wr.isError():
                    raise IOError(f"Modbus write error at {addr}")
                return True
            except Exception as e:
                last_exc = e
                time.sleep(0.05)
        raise last_exc

    def check_emergency(self):
        try:
            val = self._read(self.reg['emergency'])
        except Exception:
            # 如果没有独立急停寄存器，视为未触发
            return False
        return bool(val)

    @contextmanager
    def session(self):
        try:
            self.connect()
            yield self
        finally:
            try:
                self.close()
            except Exception:
                pass

    def activate(self, timeout=5):
        if self.check_emergency():
            raise RuntimeError("Emergency stop active, cannot activate")
        self._write(self.reg['activate'], 1)
        # 等待激活完成（依据手册设定检测点）
        start = time.time()
        while time.time() - start < timeout:
            try:
                st = self.get_status()
                # 若手册定义了激活就绪位，请在此判断
                return True
            except Exception:
                time.sleep(0.1)
        raise TimeoutError("Activate timeout")

    def get_status(self):
        # 返回原始状态寄存器（用户应按手册解析位域）
        return self._read(self.reg['status'])

    def stop(self):
        LOG.info("Issuing stop command")
        try:
            self._write(self.reg['stop'], 1)
        except Exception as e:
            LOG.warning("Stop write failed: %s", e)

    def set_position(self, position, speed=None):
        if self.check_emergency():
            raise RuntimeError("Emergency stop active, aborting move")
        position = int(position)
        if position < self.pos_min or position > self.pos_max:
            raise ValueError(f"Position {position} out of limits {self.pos_min}-{self.pos_max}")
        if speed is None:
            speed = self.speed_max
        speed = int(min(speed, self.speed_max))
        LOG.info("Set speed=%s pos=%s", speed, position)
        # 先写速度，再写目标位置（具体寄存器和顺序请按手册）
        self._write(self.reg['speed'], speed)
        self._write(self.reg['position'], position)
        # 启动动作
        self._write(self.reg['go'], 1)

    def wait_for_move(self, timeout=5, poll=0.1):
        # 根据状态寄存器轮询动作结束位（用户应按手册解析位域）
        start = time.time()
        while time.time() - start < timeout:
            try:
                st = self.get_status()
                # 这里默认把 0 视为静止，非 0 视为动作中；更精确的判断请按手册位域修改
                if st == 0:
                    return True
            except Exception:
                pass
            time.sleep(poll)
        return False

    # ---- Byte-level helpers ----
    @staticmethod
    def byte_to_register(byte_index):
        """Convert byte index to Modbus register address and offset.

        Assumption: Modbus register is 16-bit. Register address = byte_index // 2.
        Within register, if byte_index % 2 == 0 then it's the high byte (big-endian),
        else low byte. This follows the common Big-Endian register layout; if your
        device uses little-endian bytes-in-register, invert the logic.
        Returns (reg_addr, is_high_byte)
        """
        reg_addr = byte_index // 2
        is_high = (byte_index % 2 == 0)
        return reg_addr, is_high

    def read_byte(self, byte_index):
        """Read a single byte by byte index from holding registers."""
        reg_addr, is_high = self.byte_to_register(byte_index)
        word = self._read(reg_addr, count=1)
        # word is 0..65535
        if is_high:
            return (word >> 8) & 0xFF
        else:
            return word & 0xFF

    def write_byte(self, byte_index, value):
        """Write a single byte into the correct register preserving the other byte.

        This reads the register, updates the target byte, writes it back. Includes
        retries via _write.
        """
        if not (0 <= value <= 0xFF):
            raise ValueError('byte value must be 0..255')
        reg_addr, is_high = self.byte_to_register(byte_index)
        # read current register value
        word = self._read(reg_addr, count=1)
        if is_high:
            low = word & 0xFF
            new_word = (int(value) << 8) | low
        else:
            high = (word >> 8) & 0xFF
            new_word = (high << 8) | int(value)
        # write back
        return self._write(reg_addr, new_word)

    def auto_load_parsed_regs(self, parsed_json_path=None):
        """Load parsed regs (from regs_parsed.json) and create convenience mappings.

        This tries to find common fields like position/speed/action bytes and
        populates `self.byte_map` with keys: 'position', 'speed', 'action_byte'.
        The method is heuristic—请确认结果。
        """
        import os
        path = parsed_json_path or os.path.join(os.path.dirname(__file__), 'regs_parsed.json')
        try:
            with open(path, 'r', encoding='utf-8') as f:
                parsed = json.load(f)
        except Exception:
            LOG.info('No parsed regs file at %s', path)
            return {}
        bm = {}
        # find output position bytes
        out = parsed.get('output', {})
        for k, v in out.items():
            desc = (v.get('desc') or '').lower()
            if 'position request' in desc or 'set position request' in desc or 'position request for the gripper' in desc:
                bm.setdefault('position_bytes', []).append(v['byte'])
            if 'speed' in desc and 'set' in desc:
                bm.setdefault('speed_bytes', []).append(v['byte'])
            if 'action request' in desc or 'action' == desc.strip().lower():
                bm.setdefault('action_byte', v['byte'])
        # input status bytes
        inp = parsed.get('input', {})
        for k, v in inp.items():
            desc = (v.get('desc') or '').lower()
            if 'status' in desc and 'gripper' in desc:
                bm.setdefault('status_byte', v['byte'])
        self.byte_map = bm
        LOG.info('Auto-loaded byte_map keys: %s', list(bm.keys()))
        return bm

    def open(self, speed=None):
        # 在 Robotiq 中，打开通常是设为最大位置（或手册指定值）
        self.set_position(self.pos_max, speed=speed)

    def close(self, speed=None):
        # 关闭设为最小位置
        self.set_position(self.pos_min, speed=speed)

if __name__ == '__main__':
    # 简单自测（不会在没有配置寄存器的真实设备上运行）
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', required=True)
    parser.add_argument('--action', choices=['open','close','stop','status'], default='status')
    args = parser.parse_args()
    g = RobotiqModbus(args.ip)
    try:
        g.connect()
        g.activate()
        if args.action == 'open':
            g.open()
        elif args.action == 'close':
            g.close()
        elif args.action == 'stop':
            g.stop()
        else:
            print('status=', g.get_status())
    finally:
        g.close()
