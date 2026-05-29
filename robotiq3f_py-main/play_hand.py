"""
Robotiq 3F — Grasp/Release loop.
ENTER=grasp, ENTER=release, ESC=quit.

Usage:
    python play_hand.py
"""
from robotiqcontrol.GripperController import GripperController
import time
import msvcrt


def wait_for_enter_or_esc():
    """Wait for ENTER (return True) or ESC (return False)."""
    print("  Press ENTER to continue, ESC to quit...")
    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'\x1b':  # ESC
                return False
            if key in (b'\r', b'\n'):  # ENTER
                return True


def main():
    print("=" * 55)
    print("  Robotiq 3F — Grasp/Release Loop")
    print("  ENTER=grasp  ENTER=release  ESC=quit")
    print("=" * 55)

    g = GripperController(serial_port="COM3", unit_id=9)

    # Check status
    print("\n[1] Checking gripper status...")
    g.status()
    print(f"  gACT={g.gACT}, gIMC={g.gIMC}, gMOD={g.gMOD}, Fault={g.FaultStatus}")
    if not g.gACT:
        print("  Gripper not activated! Run RUI initialization first.")
        g.close()
        return

    # Open wide to start
    print("\n[2] Opening wide...")
    g.command_gripper(rPRA=0, rSP=80, rFR=30, rMOD="Basic")
    time.sleep(2)

    try:
        while True:
            # --- GRASP ---
            print("\n" + "-" * 40)
            if not wait_for_enter_or_esc():
                break
            print("  Closing (Force=1, Speed=10)...")
            g.command_gripper(rPRA=220, rSP=10, rFR=1, rMOD="Basic")
            time.sleep(3)

            g.status()
            print(f"  Pos: A={g.FingerA_Position} B={g.FingerB_Position} C={g.FingerC_Position}")

            # --- RELEASE ---
            print("-" * 40)
            if not wait_for_enter_or_esc():
                break
            print("  Opening...")
            g.command_gripper(rPRA=0, rSP=80, rFR=30, rMOD="Basic")
            time.sleep(2)

    except KeyboardInterrupt:
        pass

    print("\nDone.")
    g.close()


if __name__ == '__main__':
    main()
