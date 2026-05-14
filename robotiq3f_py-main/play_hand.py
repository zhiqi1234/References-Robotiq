"""
Try putting your hand in the gripper — safe weak-force test.

Usage:
    python play_hand.py
"""
from robotiqcontrol.GripperController import GripperController
import time


def bar(value, max_val=255, width=20):
    """Draw a simple progress bar."""
    filled = int(value / max_val * width)
    return "█" * filled + "░" * (width - filled)


def main():
    print("=" * 55)
    print("  Robotiq 3F — Hand Demo")
    print("  Safe mode: weak force, slow speed")
    print("=" * 55)

    g = GripperController(serial_port="COM8", unit_id=9)

    # Activate
    print("\n[1] Activating...")
    g.activate()
    for _ in range(20):
        time.sleep(0.1)
        g.status()
        if g.gACT and g.gIMC == 3:
            break

    # Open wide
    print("[2] Opening wide...")
    g.command_gripper(rPRA=0, rSP=80, rFR=30, rMOD="Basic")
    time.sleep(2)

    input("\n[3] Put your hand in the gripper, then press ENTER...")

    # Close — weak force, slow speed
    print("\n[4] Closing gently (Force=8, Speed=25)...")
    g.command_gripper(rPRA=220, rSP=25, rFR=8, rMOD="Basic")

    contacted = []
    last_pos = (0, 0, 0)
    for i in range(60):
        time.sleep(0.1)
        g.status()

        cur = (g.FingerA_Position, g.FingerB_Position, g.FingerC_Position)

        # Detect first contact
        for name, det, pos in [("A", g.gDTA, cur[0]),
                                ("B", g.gDTB, cur[1]),
                                ("C", g.gDTC, cur[2])]:
            if det == 2 and name not in contacted:
                contacted.append(name)
                print(f"\n  >>> Finger {name} touched you! (pos={pos}) <<<\n")

        # Show progress bars
        if cur != last_pos or any(d == 2 for d in [g.gDTA, g.gDTB, g.gDTC]):
            print(f"  A [{bar(cur[0])}] {cur[0]:3d}  "
                  f"B [{bar(cur[1])}] {cur[1]:3d}  "
                  f"C [{bar(cur[2])}] {cur[2]:3d}  "
                  f"| current: A={g.FingerA_Current:3d} B={g.FingerB_Current:3d} C={g.FingerC_Current:3d}")
            last_pos = cur

        if g.gSTA != 0:
            break

    # Result
    print(f"\n{'='*55}")
    print("  Result")
    print(f"{'='*55}")
    if contacted:
        print(f"  Fingers that touched you: {', '.join(contacted)}")
        print(f"  Final positions — A:{g.FingerA_Position}  B:{g.FingerB_Position}  C:{g.FingerC_Position}")
        if len(contacted) == 3:
            print("  All three fingers felt you! ✋")
        elif len(contacted) == 2:
            print("  Two fingers touched. Maybe your hand was tilted?")
        elif len(contacted) == 1:
            print("  Only one finger touched. Try centering your hand more.")
    else:
        print("  No contact detected — hand too thin? Try lowering Force further.")
        print(f"  Final positions — A:{g.FingerA_Position}  B:{g.FingerB_Position}  C:{g.FingerC_Position}")

    # Open to release
    print("\n[5] Opening to release...")
    g.command_gripper(rPRA=0, rSP=80, rFR=30, rMOD="Basic")
    time.sleep(2)

    g.close()
    print("Done. Hope it tickled!")


if __name__ == '__main__':
    main()
