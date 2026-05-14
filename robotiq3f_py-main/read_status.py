"""
Read complete status of Robotiq 3F Gripper — matches the manual's register set.

Covers:
  - Global Gripper Status  (gSTA, gIMC, gGTO, gACT, gMOD)
  - Object Status          (gDTA, gDTB, gDTC, gDTS)
  - Fault Status
  - Position Request Echo  (all fingers + scissor)
  - Motor Encoder Status   (all finger + scissor positions)
  - Current Status         (all motor currents)

Usage:
    python read_status.py
"""
from robotiqcontrol.GripperController import GripperController
import time


def main():
    print("=" * 55)
    print("  Robotiq 3F Gripper — Full Status")
    print("=" * 55)

    g = GripperController(serial_port="COM8", unit_id=9)
    time.sleep(0.3)
    g.status()

    # ── Global Gripper Status ──
    sta_map = {0: "Moving toward requested position",
               1: "Stopped (1-2 fingers before pos)",
               2: "Stopped (all fingers contacted object / before pos)",
               3: "Stopped (all fingers reached position)"}
    imc_map = {0: "Reset",
               1: "Activation in progress",
               2: "Mode change in progress",
               3: "Complete"}
    print("\n── Global Gripper Status ──")
    print(f"  Activated      : {'YES' if g.gACT else 'NO'}")
    print(f"  Status (gSTA)  : {g.gSTA} — {sta_map.get(g.gSTA, '?')}")
    print(f"  Init/Mode      : {g.gIMC} — {imc_map.get(g.gIMC, '?')}")
    print(f"  Goto (gGTO)    : {g.gGTO} — {'Moving to position' if g.gGTO else 'Idle'}")
    print(f"  Mode (gMOD)    : {g.gMOD}")

    # ── Object Status ──
    # Values confirmed by test: closing → value 2  (hit object while closing)
    #                           opening → value 1  (hit something while opening)
    dt_map = {0: "Moving",
              1: "Contact (opening direction)",
              2: "Contact (closing direction) — HIT OBJECT",
              3: "At position"}

    print("\n── Object Detection ──")
    print(f"  Finger A (gDTA): {g.gDTA} — {dt_map.get(g.gDTA, '?')}")
    print(f"  Finger B (gDTB): {g.gDTB} — {dt_map.get(g.gDTB, '?')}")
    print(f"  Finger C (gDTC): {g.gDTC} — {dt_map.get(g.gDTC, '?')}")
    print(f"  Scissor  (gDTS): {g.gDTS} — {dt_map.get(g.gDTS, '?')}")

    # ── Fault Status ──
    fault_map = {0x00: "No fault",
                 0x05: "Action delayed — complete activation first",
                 0x06: "Action delayed — complete mode change first",
                 0x07: "Activation bit must be set before action",
                 0x09: "Communication chip not ready (booting?)",
                 0x0A: "Mode change fault — Scissor interference (<20s)",
                 0x0B: "Automatic release in progress",
                 0x0D: "Activation fault — check interference",
                 0x0E: "Mode change fault — Scissor interference (>20s)",
                 0x0F: "Automatic release completed — reset required"}
    print("\n── Fault Status ──")
    print(f"  Fault          : 0x{g.FaultStatus:02X} — {fault_map.get(g.FaultStatus, '?')}")

    # ── Position Request Echo ──
    print("\n── Position Request Echo ──")
    print(f"  Gripper/FingerA : {g.FingerA_PositionReqEcho:3d}")
    print(f"  Finger B        : {g.FingerB_PositionReqEcho:3d}")
    print(f"  Finger C        : {g.FingerC_PositionReqEcho:3d}")
    print(f"  Scissor         : {g.Scissor_PositionReqEcho:3d}")

    # ── Motor Encoder Positions ──
    print("\n── Motor Encoder Positions (0=open, 255=closed) ──")
    print(f"  Finger A : {g.FingerA_Position:3d}")
    print(f"  Finger B : {g.FingerB_Position:3d}")
    print(f"  Finger C : {g.FingerC_Position:3d}")
    print(f"  Scissor  : {g.Scissor_Position:3d}")

    # ── Motor Currents ──
    print("\n── Motor Currents (unit: 10mA) ──")
    print(f"  Finger A : {g.FingerA_Current:3d}  ({g.FingerA_Current * 10} mA)")
    print(f"  Finger B : {g.FingerB_Current:3d}  ({g.FingerB_Current * 10} mA)")
    print(f"  Finger C : {g.FingerC_Current:3d}  ({g.FingerC_Current * 10} mA)")
    print(f"  Scissor  : {g.Scissor_Current:3d}  ({g.Scissor_Current * 10} mA)")

    print("\n" + "=" * 55)
    g.close()


if __name__ == '__main__':
    main()
