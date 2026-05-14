"""
Diagnostic: scan COM8 for responsive Modbus slave IDs, then run a test.

Usage:
    python scan_and_test.py

Make sure the Robotiq User Interface (RUI) is CLOSED before running this.
"""

from robotiqcontrol.GripperController import scan_slave_ids
from robotiqcontrol.GripperController import GripperController
import time


def main():
    print("=" * 50)
    print("Scanning COM8 for Robotiq 3F gripper...")
    print("(Close RUI software first!)")
    print("=" * 50)

    # Try common baud rates
    for baud in [115200, 19200, 38400, 9600]:
        print(f"\n--- Baud rate: {baud} ---")
        found = scan_slave_ids("COM8", baudrate=baud, ids=range(1, 17))
        if found:
            print(f"  Found {len(found)} responsive slave(s):")
            for uid, regs in found:
                print(f"    slave_id={uid}  regs[0:4]={regs[:4]}")
            # Use first found
            unit_id, _ = found[0]
            break
        else:
            print("  No response")
    else:
        print("\nNo device found! Check:")
        print("  1. Is RUI closed?")
        print("  2. Is the gripper powered and connected?")
        print("  3. Try different COM port number")
        return

    print(f"\nConnecting with slave_id={unit_id}...")
    try:
        gripper = GripperController(serial_port="COM8", unit_id=unit_id, baudrate=baud)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    print("Activating...")
    try:
        gripper.activate()
    except Exception as e:
        print(f"Activation failed: {e}")
        gripper.close()
        return

    print("Reading status...")
    time.sleep(0.5)
    gripper.status()
    print(f"  gACT={gripper.gACT}  gGTO={gripper.gGTO}  gMOD={gripper.gMOD}")
    print(f"  FingerA pos={gripper.FingerA_Position}  "
          f"FingerB pos={gripper.FingerB_Position}  "
          f"FingerC pos={gripper.FingerC_Position}")

    # Open
    print("\nOpening gripper (pos=255, speed=100)...")
    try:
        gripper.command_gripper(rPRA=255, rSP=100, rFR=100, rMOD="Basic")
    except Exception as e:
        print(f"Open failed: {e}")
        gripper.close()
        return

    time.sleep(3)
    gripper.status()
    print(f"  FingerA={gripper.FingerA_Position}  "
          f"FingerB={gripper.FingerB_Position}  "
          f"FingerC={gripper.FingerC_Position}")

    # Close
    print("\nClosing gripper (pos=50, speed=100)...")
    try:
        gripper.command_gripper(rPRA=50, rSP=100, rFR=100, rMOD="Basic")
    except Exception as e:
        print(f"Close failed: {e}")
        gripper.close()
        return

    time.sleep(3)
    gripper.status()
    print(f"  FingerA={gripper.FingerA_Position}  "
          f"FingerB={gripper.FingerB_Position}  "
          f"FingerC={gripper.FingerC_Position}")

    print("\nDone!")
    gripper.close()


if __name__ == '__main__':
    main()
