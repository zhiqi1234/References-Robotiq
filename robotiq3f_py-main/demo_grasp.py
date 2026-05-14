"""
Demo: Grasp an object and report which fingers touched it.

Usage:
    python demo_grasp.py

Place an object between the gripper fingers before running.
"""
from robotiqcontrol.GripperController import GripperController
import time


def main():
    print("=" * 55)
    print("  Robotiq 3F — Grasp Demo")
    print("  Place an object between the fingers first!")
    print("=" * 55)

    g = GripperController(serial_port="COM8", unit_id=9)

    # 1. Activate
    print("\n[1/4] Activating...")
    g.activate()
    for _ in range(30):
        time.sleep(0.1)
        g.status()
        if g.gACT == 1 and g.gIMC == 3:
            break
    print("  Activated. Fingers at:", g.FingerA_Position)

    # 2. Open fully
    print("\n[2/4] Opening fingers...")
    g.command_gripper(rPRA=0, rSP=100, rFR=60, rMOD="Basic")
    for _ in range(30):
        time.sleep(0.1)
        g.status()
        if g.gSTA == 3:
            break
    print("  Opened. Fingers at:", g.FingerA_Position)

    # 3. Close — grasp the object
    print("\n[3/4] Closing fingers to grasp...")
    g.command_gripper(rPRA=255, rSP=60, rFR=40, rMOD="Basic")

    contact = {"A": False, "B": False, "C": False}
    dt_labels = {0: "moving", 1: "contact (opening)",
                 2: ">>> TOUCHED (closing)", 3: "at position"}

    last_pos = (0, 0, 0)
    for _ in range(50):
        time.sleep(0.1)
        g.status()

        # Check each finger for first contact while closing (value=2)
        for name, val in [("A", g.gDTA), ("B", g.gDTB), ("C", g.gDTC)]:
            if val == 2 and not contact[name]:
                contact[name] = True
                pos = getattr(g, f'Finger{name}_Position')
                print(f"  >>> Finger {name} touched the object! (pos={pos})")

        # Show positions only when they change
        cur = (g.FingerA_Position, g.FingerB_Position, g.FingerC_Position)
        if cur != last_pos:
            print(f"  pos: A={cur[0]:3d}  B={cur[1]:3d}  C={cur[2]:3d}  |  "
                  f"A={dt_labels[g.gDTA]}  B={dt_labels[g.gDTB]}  "
                  f"C={dt_labels[g.gDTC]}")
            last_pos = cur

        if g.gSTA != 0:
            break

    # 4. Report result
    print("\n[4/4] === Grasp Result ===")
    g.status()
    print(f"  Gripper stopped.  gSTA={g.gSTA}")

    contacted = [name for name, hit in contact.items() if hit]
    if contacted:
        print(f"  Fingers that touched the object: {', '.join(contacted)}")
    else:
        print("  No finger detected contact (object may be thin or already at limit)")

    print(f"\n  Final positions:")
    print(f"    Finger A: {g.FingerA_Position:3d}  current: {g.FingerA_Current:3d}")
    print(f"    Finger B: {g.FingerB_Position:3d}  current: {g.FingerB_Current:3d}")
    print(f"    Finger C: {g.FingerC_Position:3d}  current: {g.FingerC_Current:3d}")
    print(f"    Scissor : {g.Scissor_Position:3d}  current: {g.Scissor_Current:3d}")

    g.close()
    print("\nDone.")


if __name__ == '__main__':
    main()
