"""
Comprehensive test for Robotiq 3F Gripper via COM8.

Tests: activation, 4 modes (Basic/Pinch/Wide/Scissor),
       variable speed/force, individual finger control,
       object detection, fault monitoring.
"""
from robotiqcontrol.GripperController import GripperController
import time


def print_status(g):
    print(f"  gSTA={g.gSTA} gIMC={g.gIMC} gACT={g.gACT} gGTO={g.gGTO} gMOD={g.gMOD}")
    print(f"  Fault={g.FaultStatus}  Echo={g.FingerA_PositionReqEcho}")
    print(f"  FingerA: pos={g.FingerA_Position:3d}  cur={g.FingerA_Current:3d}")
    print(f"  FingerB: pos={g.FingerB_Position:3d}  cur={g.FingerB_Current:3d}")
    print(f"  FingerC: pos={g.FingerC_Position:3d}  cur={g.FingerC_Current:3d}")
    print(f"  Scissor: pos={g.Scissor_Position:3d}  cur={g.Scissor_Current:3d}")
    print(f"  Object: A={g.gDTA} B={g.gDTB} C={g.gDTC} S={g.gDTS}")
    print(f"          (0=move 1=stop_open 2=stop_close 3=at_pos)")


def wait_for_stop(g, timeout=5):
    """Wait until gripper stops moving (gSTA != 0)."""
    for _ in range(int(timeout / 0.2)):
        time.sleep(0.2)
        g.status()
        if g.gSTA != 0:
            return True
    return False


def main():
    print("=" * 55)
    print("Robotiq 3F Gripper — Comprehensive Test")
    print("=" * 55)

    g = GripperController(serial_port="COM8", unit_id=9)

    # ── Test 1: Activation ──
    print("\n[Test 1] Activation")
    g.activate()
    for i in range(10):
        time.sleep(0.2)
        g.status()
        if g.gACT == 1 and g.gIMC == 3:
            print(f"  Activation complete (gACT={g.gACT}, gIMC={g.gIMC})")
            break
        if i == 0:
            print(f"  Activating... gIMC={g.gIMC}")

    print_status(g)

    # ── Test 2: Open/Close at low speed ──
    print("\n[Test 2] Low-speed open (speed=40, force=50)")
    g.command_gripper(rPRA=0, rSP=40, rFR=50, rMOD="Basic")
    wait_for_stop(g)
    print_status(g)

    print("\n[Test 2b] Low-speed close (pos=200, speed=40)")
    g.command_gripper(rPRA=200, rSP=40, rFR=50, rMOD="Basic")
    wait_for_stop(g)
    print_status(g)

    # ── Test 3: Pinch Mode ──
    print("\n[Test 3] Pinch Mode — open")
    g.command_gripper(rPRA=0, rSP=100, rFR=80, rMOD="Pinch")
    wait_for_stop(g)
    print_status(g)

    print("\n[Test 3b] Pinch Mode — close")
    g.command_gripper(rPRA=255, rSP=100, rFR=80, rMOD="Pinch")
    wait_for_stop(g)
    print_status(g)

    # ── Test 4: Wide Mode ──
    print("\n[Test 4] Wide Mode — open")
    g.command_gripper(rPRA=0, rSP=120, rFR=80, rMOD="Wide")
    wait_for_stop(g)
    print_status(g)

    print("\n[Test 4b] Wide Mode — close")
    g.command_gripper(rPRA=255, rSP=120, rFR=80, rMOD="Wide")
    wait_for_stop(g)
    print_status(g)

    # ── Test 5: Scissor Mode ──
    print("\n[Test 5] Scissor Mode — open")
    g.command_gripper(rPRA=0, rSP=100, rFR=60, rMOD="Scissor")
    wait_for_stop(g)
    print_status(g)

    print("\n[Test 5b] Scissor Mode — close")
    g.command_gripper(rPRA=255, rSP=100, rFR=60, rMOD="Scissor")
    wait_for_stop(g)
    print_status(g)

    # ── Test 6: Individual finger control ──
    print("\n[Test 6] Individual finger control (Basic Mode)")
    print("  FingerA→100  FingerB→200  FingerC→50")
    g.command_gripper(rPRA=[100, 200, 50], rSP=[80, 80, 80],
                      rFR=[60, 60, 60], rMOD="Basic", rICF=True)
    wait_for_stop(g)
    print_status(g)

    # ── Test 7: Back to Basic, full open ──
    print("\n[Test 7] Return to Basic Mode, full open")
    g.command_gripper(rPRA=0, rSP=150, rFR=100, rMOD="Basic")
    wait_for_stop(g)
    print_status(g)

    print("\n" + "=" * 55)
    print("All tests complete!")
    print("=" * 55)

    g.close()


if __name__ == '__main__':
    main()
