"""
Test Robotiq 3F Gripper via COM8 (Modbus RTU).

Usage:
    python test_serial.py
"""
from robotiqcontrol.GripperController import GripperController
import time


def main():
    print("Connecting to Robotiq 3F on COM8...")
    gripper = GripperController(serial_port="COM8", unit_id=9)

    print("Activating...")
    gripper.activate()

    # Wait for activation to complete
    for i in range(10):
        time.sleep(0.3)
        gripper.status()
        print(f"  gACT={gripper.gACT} gIMC={gripper.gIMC} gSTA={gripper.gSTA}")
        if gripper.gACT == 1 and gripper.gIMC == 3:
            print("  Activation complete!")
            break

    # ── Open ──
    print("\nOpening gripper (pos=255, speed=100)...")
    gripper.command_gripper(rPRA=255, rSP=100, rFR=100, rMOD="Basic")

    for i in range(10):
        time.sleep(0.3)
        gripper.status()
        print(f"  FingerA={gripper.FingerA_Position}  "
              f"FingerB={gripper.FingerB_Position}  "
              f"FingerC={gripper.FingerC_Position}  "
              f"gSTA={gripper.gSTA}")

    # ── Close ──
    print("\nClosing gripper (pos=50, speed=100)...")
    gripper.command_gripper(rPRA=50, rSP=100, rFR=100, rMOD="Basic")

    for i in range(10):
        time.sleep(0.3)
        gripper.status()
        print(f"  FingerA={gripper.FingerA_Position}  "
              f"FingerB={gripper.FingerB_Position}  "
              f"FingerC={gripper.FingerC_Position}  "
              f"gSTA={gripper.gSTA}")

    print("\nDone!")
    gripper.close()


if __name__ == '__main__':
    main()
