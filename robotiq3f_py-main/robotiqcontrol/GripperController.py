"""
Robotiq 3F Gripper Controller — Modbus TCP & Modbus RTU (serial).

TCP usage:
    gripper = GripperController(ip="192.168.1.11")

Serial usage (COM8):
    gripper = GripperController(serial_port="COM8")

Register map:
    TCP:  output base 0x0000, input base 0x0000 (FC04)
    RTU:  output base 0x03E8, input base 0x07D0 (FC03)
"""

import time
import threading
import warnings

try:
    from pymodbus.client import ModbusTcpClient
except Exception:
    ModbusTcpClient = None

try:
    from pymodbus.client import ModbusSerialClient
except Exception:
    ModbusSerialClient = None


class GripperController:
    # Register base addresses differ between TCP and RTU
    _TCP_OUT_BASE = 0x0000
    _TCP_IN_BASE = 0x0000
    _RTU_OUT_BASE = 0x03E8
    _RTU_IN_BASE = 0x07D0

    def __init__(self, ip=None, port=502, unit_id=9, update_interval=0.1,
                 serial_port=None, baudrate=115200, parity='N',
                 stopbits=1, bytesize=8, timeout=1.0):
        self.update_interval = update_interval
        self.unit_id = unit_id

        if serial_port:
            if ModbusSerialClient is None:
                raise RuntimeError('pymodbus not installed; run: pip install pymodbus')
            self.client = ModbusSerialClient(
                port=serial_port, baudrate=baudrate,
                parity=parity, stopbits=stopbits,
                bytesize=bytesize, timeout=timeout,
            )
            if not self.client.connect():
                raise ConnectionError(f"Failed to open {serial_port}")
            self._out_base = self._RTU_OUT_BASE
            self._in_base = self._RTU_IN_BASE
            self._use_fc04 = False  # RTU reads input via FC03
            print(f"Connected via {serial_port} (RTU, device_id={unit_id})")
        elif ip:
            if ModbusTcpClient is None:
                raise RuntimeError('pymodbus not installed; run: pip install pymodbus')
            self.client = ModbusTcpClient(host=ip, port=port, timeout=timeout)
            if not self.client.connect():
                raise ConnectionError(f"Failed to connect to {ip}:{port}")
            self._out_base = self._TCP_OUT_BASE
            self._in_base = self._TCP_IN_BASE
            self._use_fc04 = True  # TCP can use FC04 for input registers
            print(f"Connected via TCP {ip}:{port}")
        else:
            raise ValueError("Must provide either 'ip' or 'serial_port'")

        self._running = True
        self._thread = threading.Thread(target=self._update_loop, daemon=True)
        self._thread.start()

    # -- status attributes --

    @property
    def gSTA(self): return getattr(self, '_gSTA', 0)
    @property
    def gIMC(self): return getattr(self, '_gIMC', 0)
    @property
    def gGTO(self): return getattr(self, '_gGTO', 0)
    @property
    def gMOD(self): return getattr(self, '_gMOD', 'Basic Mode')
    @property
    def gACT(self): return getattr(self, '_gACT', 0)
    @property
    def gDTS(self): return getattr(self, '_gDTS', 0)
    @property
    def gDTC(self): return getattr(self, '_gDTC', 0)
    @property
    def gDTB(self): return getattr(self, '_gDTB', 0)
    @property
    def gDTA(self): return getattr(self, '_gDTA', 0)
    @property
    def FaultStatus(self): return getattr(self, '_FaultStatus', 0)
    @property
    def FingerA_PositionReqEcho(self): return getattr(self, '_FingerA_PositionReqEcho', 0)
    @property
    def FingerA_Position(self): return getattr(self, '_FingerA_Position', 0)
    @property
    def FingerA_Current(self): return getattr(self, '_FingerA_Current', 0)
    @property
    def FingerB_PositionReqEcho(self): return getattr(self, '_FingerB_PositionReqEcho', 0)
    @property
    def FingerB_Position(self): return getattr(self, '_FingerB_Position', 0)
    @property
    def FingerB_Current(self): return getattr(self, '_FingerB_Current', 0)
    @property
    def FingerC_PositionReqEcho(self): return getattr(self, '_FingerC_PositionReqEcho', 0)
    @property
    def FingerC_Position(self): return getattr(self, '_FingerC_Position', 0)
    @property
    def FingerC_Current(self): return getattr(self, '_FingerC_Current', 0)
    @property
    def Scissor_PositionReqEcho(self): return getattr(self, '_Scissor_PositionReqEcho', 0)
    @property
    def Scissor_Position(self): return getattr(self, '_Scissor_Position', 0)
    @property
    def Scissor_Current(self): return getattr(self, '_Scissor_Current', 0)

    # -- background polling --

    def _update_loop(self):
        while self._running:
            try:
                self._update_status()
            except Exception:
                pass
            time.sleep(self.update_interval)

    def _update_status(self):
        readData = self._read_regs(self._in_base, 8)
        if readData:
            self._gSTA, self._gIMC, self._gGTO, self._gMOD, self._gACT, \
                self._gDTS, self._gDTC, self._gDTB, self._gDTA = \
                self._parse_status(self._pad_bin(readData[0]))
            self._FaultStatus, self._FingerA_PositionReqEcho = \
                self._split_byte(self._pad_bin(readData[1]))
            self._FingerA_Position, self._FingerA_Current = \
                self._split_byte(self._pad_bin(readData[2]))
            self._FingerB_PositionReqEcho, self._FingerB_Position = \
                self._split_byte(self._pad_bin(readData[3]))
            self._FingerB_Current, self._FingerC_PositionReqEcho = \
                self._split_byte(self._pad_bin(readData[4]))
            self._FingerC_Position, self._FingerC_Current = \
                self._split_byte(self._pad_bin(readData[5]))
            self._Scissor_PositionReqEcho, self._Scissor_Position = \
                self._split_byte(self._pad_bin(readData[6]))
            self._Scissor_Current, _ = \
                self._split_byte(self._pad_bin(readData[7]))

    def _read_regs(self, address, count):
        if self._use_fc04:
            try:
                rr = self.client.read_input_registers(
                    address=address, count=count, device_id=self.unit_id)
                if rr and not rr.isError() and rr.registers:
                    return rr.registers
            except Exception:
                pass
        # FC03 — works for both TCP and RTU
        try:
            rr = self.client.read_holding_registers(
                address=address, count=count, device_id=self.unit_id)
            if rr and not rr.isError() and rr.registers:
                return rr.registers
        except Exception:
            pass
        return None

    def _write_output(self, registers):
        wr = self.client.write_registers(
            address=self._out_base, values=registers, device_id=self.unit_id)
        if wr.isError():
            raise IOError("Modbus write error")

    # -- static helpers --

    @staticmethod
    def _pad_bin(value, total_length=16):
        return bin(value)[2:].zfill(total_length)

    @staticmethod
    def _split_byte(variable):
        return int(variable[0:8], 2), int(variable[8:16], 2)

    @staticmethod
    def _parse_status(variable):
        modes = ["Basic Mode", "Pinch Mode", "Wide Mode", "Scissor Mode"]
        return (
            int(variable[0:2], 2),   # gSTA
            int(variable[2:4], 2),   # gIMC
            int(variable[4], 2),     # gGTO
            modes[int(variable[5:7], 2)],  # gMOD
            int(variable[7], 2),     # gACT
            int(variable[8:10], 2),  # gDTS
            int(variable[10:12], 2), # gDTC
            int(variable[12:14], 2), # gDTB
            int(variable[14:16], 2), # gDTA
        )

    # -- public API --

    def activate(self):
        """Activate the gripper (rACT=1)."""
        self._write_output([
            self._action_req(rACT=1),
            self._position_req(0),
            self._write_req(0, 0),
        ])
        print("Gripper activated")
        time.sleep(0.5)

    def command_gripper(self, rPRA=None, rSP=None, rFR=None, rMOD="Basic", rICF=False):
        if rPRA is None:
            rPRA = [0, 0, 0]
        if rSP is None:
            rSP = [250, 250, 250]
        if rFR is None:
            rFR = [250, 250, 250]

        mode_map = {"Basic": 0, "Pinch": 1, "Wide": 2, "Scissor": 3}
        rMOD_val = mode_map[rMOD]

        if rICF:
            for var in [rPRA, rSP, rFR]:
                if isinstance(var, int):
                    raise ValueError("Need 3d vectors when Individual Control Flag is set.")
            self._write_output([
                self._action_req(rACT=1, rGTO=1, rMOD=rMOD_val, rICF=1),
                self._position_req(rPRA[0]),
                self._write_req(rSP[0], rFR[0]),
                self._write_req(rPRA[1], rSP[1]),
                self._write_req(rFR[1], rPRA[2]),
                self._write_req(rSP[2], rFR[2]),
            ])
        else:
            for var in [rPRA, rSP, rFR]:
                if isinstance(var, list):
                    warnings.warn("Only first value used without Individual Control Flag.")
            self._write_output([
                self._action_req(rACT=1, rGTO=1, rMOD=rMOD_val, rICF=0),
                self._position_req(rPRA[0] if isinstance(rPRA, list) else rPRA),
                self._write_req(
                    rSP[0] if isinstance(rSP, list) else rSP,
                    rFR[0] if isinstance(rFR, list) else rFR,
                ),
            ])

    def status(self):
        self._update_status()

    # -- bit-level encoding (matches Robotiq register map) --

    @staticmethod
    def _action_req(rARD=0, rATR=0, rGTO=0, rACT=0, rMOD=0,
                    rICS=0, rICF=0, rAAC=0):
        """Build register for ACTION REQUEST (byte 0) + GRIPPER OPTIONS (byte 1).

        Byte 0 (ACTION REQUEST):
            bit 0: rACT   — 1=activate (must stay 1 after activation)
            bit 1: rMOD0  — mode bit 0
            bit 2: rMOD1  — mode bit 1
            bit 3: rGTO   — 1=go to requested position
            bit 4: rATR   — 1=automatic release (emergency use only)
            bit 5-7: reserved

        Byte 1 (GRIPPER OPTIONS):
            bit 0: reserved
            bit 1: rAAC   — 1=enable automatic auto-centering (beta)
            bit 2: rICF   — 1=individual control of fingers A/B/C
            bit 3: rICS   — 1=individual control of scissor (overrides rMOD)
            bit 4-7: reserved
        """
        for var in [rARD, rATR, rGTO, rACT]:
            if var not in [0, 1]:
                raise ValueError("Bits must be 0 or 1.")
        rMOD_bits = bin(rMOD)[2:].zfill(2)
        action_byte = (0 << 7) | (0 << 6) | (rARD << 5) | (rATR << 4) | \
                      (rGTO << 3) | (int(rMOD_bits[0]) << 2) | \
                      (int(rMOD_bits[1]) << 1) | rACT
        options_byte = (0 << 7) | (0 << 6) | (0 << 5) | (0 << 4) | \
                       (rICS << 3) | (rICF << 2) | (rAAC << 1) | 0
        return (action_byte << 8) | options_byte

    @staticmethod
    def _position_req(rPR=0):
        """Build register for GRIPPER OPTIONS 2 (byte 2) + POSITION REQUEST (byte 3)."""
        if rPR not in range(0, 256):
            raise ValueError("Position must be 0-255.")
        return (0 << 8) | rPR

    @staticmethod
    def _write_req(X=0, Y=0):
        """Build register for two byte values (e.g. SPEED + FORCE)."""
        for v in [X, Y]:
            if v not in range(0, 256):
                raise ValueError("Values must be 0-255.")
        return (X << 8) | Y

    def close(self):
        self._running = False
        if self._thread.is_alive():
            self._thread.join(timeout=2)
        try:
            self.client.close()
        except Exception:
            pass
        print("Connection closed.")
