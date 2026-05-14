"""
Diagnostic: scan holding register ranges to find where status data lives.

Usage:
    python diagnose_com8.py
"""
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s')
logging.getLogger('pymodbus').setLevel(logging.DEBUG)

from pymodbus.client import ModbusSerialClient


def main():
    client = ModbusSerialClient(
        port="COM8", baudrate=115200, parity='N',
        stopbits=1, bytesize=8, timeout=2.0, retries=1,
    )
    if not client.connect():
        print("Failed to open COM8")
        return

    print("=" * 60)
    print("Step 1: Read holding regs [0..7] BEFORE activation")
    print("=" * 60)
    rr = client.read_holding_registers(address=0, count=8, device_id=9)
    if rr and not rr.isError():
        print(f"  regs[0:8] = {list(rr.registers)}")

    print()
    print("=" * 60)
    print("Step 2: Write activation (rACT=1, rGTO=1)")
    print("=" * 60)
    # Same bit layout as GripperController._action_req(rACT=1, rGTO=1)
    action = 0b0000100100000000  # rACT=bit8, rGTO=bit11
    wr = client.write_registers(address=0, values=[action, 0, 0], device_id=9)
    if wr and not wr.isError():
        print("  Write OK")

    import time
    time.sleep(0.5)

    print()
    print("=" * 60)
    print("Step 3: Read holding regs [0..7] AFTER activation")
    print("=" * 60)
    rr = client.read_holding_registers(address=0, count=8, device_id=9)
    if rr and not rr.isError():
        print(f"  regs[0:8] = {list(rr.registers)}")

    # Also try reading input registers (may fail)
    print()
    print("=" * 60)
    print("Step 4: Try input registers [0..7]")
    print("=" * 60)
    try:
        rr = client.read_input_registers(address=0, count=8, device_id=9)
        if rr and not rr.isError():
            print(f"  regs[0:8] = {list(rr.registers)}")
    except Exception as e:
        print(f"  Failed: {e}")

    # Scan holding registers at different base addresses
    print()
    print("=" * 60)
    print("Step 5: Scan holding regs at different base addresses")
    print("=" * 60)
    for base in [0, 0x1000, 0x2000, 0x3000, 0x4000, 0x5000]:
        try:
            rr = client.read_holding_registers(address=base, count=8, device_id=9)
            if rr and not rr.isError() and any(rr.registers):
                print(f"  base=0x{base:04X}: {list(rr.registers)}")
        except Exception as e:
            pass

    client.close()
    print("\nDone")


if __name__ == '__main__':
    main()
