# 4.1 Generalities (总体概述)

> ⚠️ **Caution**
> 本节适用于固件版本 3.0（2011 年 11 月之后交付的夹爪）。对于早期版本，请参阅归档文档。

Robotiq Adaptive Gripper S-Model 通过工业通信协议（如 EtherNet/IP, DeviceNet, CANopen, EtherCat 等）由机器人控制器进行控制。夹爪的编程可以通过机器人的示教器（Teach Pendant）或离线编程完成。

> ℹ️ **Info**
>
> - 对于每种操作模式（Operation Mode），操作员都可以控制手指的速度（Speed）和力（Force）。
> - 除非选择了独立控制模式（Individual Control），否则手指的运动始终是同步的。动作由单个“转到请求位置（Go to requested position）”命令完成（每个机械指骨的运动是自动进行的）。

由于 Robotiq Adaptive Gripper S-Model 拥有独立的内部控制器，因此使用如“转到请求位置”等高级命令来控制它。内嵌的 Robotiq 控制器负责调节设定的速度和力，同时手指的机械结构会自动适应物体的形状。

---

# 4.2 Status overview (状态概述)

Adaptive Gripper S-Model 会向机器人控制器返回多个寄存器的信息以供读取：

- **Global Gripper Status (全局夹爪状态)** - 提供全局夹爪状态。显示当前处于哪种操作模式，或者夹爪是闭合还是张开。
- **Object Status (物体状态)** - 提供物体状态，让你知道夹爪中是否有物体；如果有，有多少根手指与物体接触。
- **Fault Status (故障状态)** - 提供有关故障原因的详细信息。
- **Position Request Echo (位置请求回显)** - 夹爪返回机器人请求的位置，以确保新命令已被正确接收。
- **Motor Encoder Status (电机编码器状态)** - 提供四个电机的编码器信息。
- **Current Status (电流状态)** - 提供电机的电流信息。由于电机扭矩是电流的线性函数，这反映了施加在手指驱动连杆上的力。

---

# 4.3 Control overview (控制逻辑概述)

夹爪控制器具有与机器人控制器共享的内部内存。内存的一部分用于机器人输出（Robot Output）/ 夹爪功能控制。另一部分内存用于机器人输入（Robot Input）/ 夹爪状态反馈。

因此，机器人控制器可以执行两种类型的操作：

1. **Write (写入)**：写入机器人输出寄存器以激活夹爪的特定功能；
2. **Read (读取)**：读取机器人输入寄存器以获取夹爪的当前状态。

> ℹ️ **Info**
> 夹爪在上电时必须进行初始化（激活位 activation bit）。此过程需要几秒钟，允许夹爪根据内部的机械限位进行自校准。

---

# 4.4 Status LEDs (状态指示灯)

夹爪上配有三个状态 LED 指示灯，提供有关 Adaptive Gripper S-Model 运行状态的一般信息。这在硬件调试和排障时非常有用。

## 4.4.1 Supply LED (电源指示灯)

| 颜色        | 状态     | 说明                         |
| :---------- | :------- | :--------------------------- |
| Blue (蓝色) | Off (灭) | 夹爪未供电                   |
| Blue (蓝色) | On (亮)  | 夹爪供电正常，控制板正在运行 |

## 4.4.2 Communication LED (通信指示灯)

| 颜色         | 状态            | 说明                                         |
| :----------- | :-------------- | :------------------------------------------- |
| Green (绿色) | Off (灭)        | 未检测到网络                                 |
| Green (绿色) | Blinking (闪烁) | 已检测到网络，但未建立连接                   |
| Green (绿色) | On (亮)         | 已检测到网络，且至少有一个连接处于已建立状态 |

## 4.4.3 Fault LED (故障指示灯)

| 颜色       | 状态            | 说明                           |
| :--------- | :-------------- | :----------------------------- |
| Red (红色) | Off (灭)        | 未检测到故障                   |
| Red (红色) | On (亮)         | 发生轻微故障（或夹爪正在启动） |
| Red (红色) | Blinking (闪烁) | 发生严重故障                   |

> ℹ️ **Info**
> 严重故障（Major fault）通常指的是夹爪必须重新激活才能恢复工作的情况。

---

# 4.5 Gripper register mapping

> ⚠️ **Caution**
> This section applies to firmware 3.0 (Grippers delivered after November 2011). For prior versions please see the documentation archives.

> ℹ️ **Info**
> Register format is Little Endian (Intel format), namely from LSB (Less Significant Bit) to MSB (Most Significant Bit).

Version 3 of the Adaptive Gripper S-Model firmware provides new functionalities such as the direct position control of the fingers via "go to" commands. There is also additional advanced options such as the individual control of the fingers and scissor and the automatic centering of the fingers.

A Simplified Control Mode is available for users which do not intend to use the advanced option otherwise a register mapping for the Advanced Control Mode containing all the gripper functionalities is also provided. From the gripper standpoint, there is no difference between the two modes. The Simple Control Mode is only intended to ease the usage of the gripper for users who are only interested in the basic functionalities.

> ⚠️ **Warning**
> When using the Simplified Control Mode, it is important to fill the unused registers with zeros. Neglecting to do so would result in the unwanted triggering of control options and could lead to a hazardous behavior of the Gripper.

---

## Register mapping for the Simplified Control Mode

> ⚠️ **Caution**
> Byte numeration starts on zero and not at 1 for the functionalities and status registers.

| REGISTER | ROBOT OUTPUT / FUNCTIONALITIES | ROBOT INPUT / STATUS    |
| -------- | ------------------------------ | ----------------------- |
| Byte 0   | ACTION REQUEST                 | GRIPPER STATUS          |
| Byte 1   | 00000000                       | OBJECT DETECTION        |
| Byte 2   | 00000000                       | FAULT STATUS            |
| Byte 3   | POSITION REQUEST               | POS. REQUEST ECHO       |
| Byte 4   | SPEED                          | FINGER A POSITION       |
| Byte 5   | FORCE                          | FINGER A CURRENT        |
| Byte 6   | 00000000                       | NOT USED IN SIMPLE MODE |
| Byte 7   | 00000000                       | FINGER B POSITION       |
| Byte 8   | 00000000                       | FINGER B CURRENT        |
| Byte 9   | 00000000                       | NOT USED IN SIMPLE MODE |
| Byte 10  | 00000000                       | FINGER C POSITION       |
| Byte 11  | 00000000                       | FINGER C CURRENT        |
| Byte 12  | 00000000                       | NOT USED IN SIMPLE MODE |
| Byte 13  | 00000000                       | SCISSOR POSITION        |
| Byte 14  | 00000000                       | SCISSOR CURRENT         |
| Byte 15  | RESERVED                       | RESERVED                |

---

## Register mapping for the Advanced Control Mode

| REGISTER | ROBOT OUTPUT / FUNCTIONALITIES                 | ROBOT INPUT / STATUS       |
| -------- | ---------------------------------------------- | -------------------------- |
| Byte 0   | ACTION REQUEST                                 | GRIPPER STATUS             |
| Byte 1   | GRIPPER OPTIONS                                | OBJECT DETECTION           |
| Byte 2   | GRIPPER OPTIONS #2 (EMPTY)                     | FAULT STATUS               |
| Byte 3   | POSITION REQUEST (FINGER A IN INDIVIDUAL MODE) | POS. REQUEST ECHO          |
| Byte 4   | SPEED (FINGER A IN INDIVIDUAL MODE)            | FINGER A POSITION          |
| Byte 5   | FORCE (FINGER A IN INDIVIDUAL MODE)            | FINGER A CURRENT           |
| Byte 6   | FINGER B POSITION REQUEST                      | FINGER B POS. REQUEST ECHO |
| Byte 7   | FINGER B SPEED                                 | FINGER B POSITION          |
| Byte 8   | FINGER B FORCE                                 | FINGER B CURRENT           |
| Byte 9   | FINGER C POSITION REQUEST                      | FINGER C POS. REQUEST ECHO |
| Byte 10  | FINGER C SPEED                                 | FINGER C POSITION          |
| Byte 11  | FINGER C FORCE                                 | FINGER C CURRENT           |
| Byte 12  | SCISSOR POSITION REQUEST                       | SCISSOR POS. REQUEST ECHO  |
| Byte 13  | SCISSOR SPEED                                  | SCISSOR POSITION           |
| Byte 14  | SCISSOR FORCE                                  | SCISSOR CURRENT            |
| Byte 15  | RESERVED                                       | RESERVED                   |

---

# 4.6 Robot output registers & functionalities

> ⚠️ **Caution**
> This section applies to firmware 3.0 (Grippers delivered after November 2011). For prior versions please see the documentation archives.

> ℹ️ **Info**
> Register format is Little Endian (Intel format), namely from LSB (Less Significant Bit) to MSB (Most Significant Bit).

---

## Register: ACTION REQUEST

Address: Byte 0

| BIT | NAME | DESCRIPTION                                                                                                          |
| --- | ---- | -------------------------------------------------------------------------------------------------------------------- |
| 0   | rACT | 0 – Reset Gripper `<br>`1 – Activate Gripper (Must stay on after activation routine is completed)                |
| 1-2 | rMOD | 00 – Go to Basic Mode `<br>`10 – Go to Pinch Mode `<br>`01 – Go to Wide Mode `<br>`11 – Go to Scissor Mode |
| 3   | rGTO | 0 – Stop `<br>`1 – Go to Requested Position                                                                      |
| 4   | rATR | 0 – Normal `<br>`1 – Automatic release                                                                           |
| 5-7 | rRS0 | Reserved                                                                                                             |

`rACT`: First action to be made prior to any other actions, rACT bit will initialize the Adaptive Gripper. Clear rACT to reset Gripper and fault status.

> ⚠️ **Caution**
> rACT bit must stay on afterwards for any other action to be performed.

`rMOD`: Changes the Gripper Grasping Mode. When the Grasping Mode is changed, the Gripper first opens completely to avoid interferences between the fingers then go to the selected mode. This option is ignored if the bit rICS is set (individual control of the scissor motion option).

`rGTO`: The "Go To" action moves the Gripper fingers to the requested position using the configuration defined by the other registers and the rMOD bits. The only motions performed without the rGTO bit are the activation, the mode change and the automatic release routines.

`rATR`: Automatic Release routine action slowly open the Gripper fingers until all motions axes reach their mechanical limits. After the motion is completed, the Gripper sends a fault signal and needs to be reinitialized before any other motion is performed. The rATR bit overrides all other commands excluding the activation bit (rACT).

> ⚠️ **Caution**
> The Automatic Release is meant to disengage the Gripper after an emergency stop of the robot. The Automatic Release is not intended to be used under normal operating conditions.

---

## Register: GRIPPER OPTIONS

Address: Byte 1

`rAAC`: The Automatic Centering option synchronizes the Gripper fingers in order to automatically center the object it seizes. This option requires that fingers B and C have the same position request and velocity. It is not intended to be used in the scissor mode. This option is currently in a beta version and may be modified in future versions of the firmware.

`rICF`: In Individual Control of Fingers mode each finger receives its own command (position request, speed and force) unless the Gripper is in the Scissor Grasping Mode and the Independent Control of Scissor (rICS) is not activated. Please refer to the rPRA (Position Request) register description for information about the reachable positions of the fingers.

> ⚠️ **Caution**
> As soon as the rICF bit is set, the fingers will move towards the target defined by the position request bytes. To avoid unwanted motion of the fingers, it is preferable to define the position requests before setting the rICF bit. It is also possible to clear the rGTO bit, configure the registers according to the desired motion and then set the rGTO bit to start the motion.

| BIT | NAME | DESCRIPTION                                                                            |
| --- | ---- | -------------------------------------------------------------------------------------- |
| 0   | rGLV | Reserved                                                                               |
| 1   | rAAC | 0 – Normal `<br>`1 – Enable Automatic Auto-Centering                               |
| 2   | rICF | 0 – Normal `<br>`1 – Enable Individual Control of Fingers A, B and C               |
| 3   | rICS | 0 – Normal `<br>`1 – Enable Individual Control of Scissor. Disable Mode Selection. |
| 4-7 | rRS1 | Reserved                                                                               |

`rICS`: In Individual Control of Scissor the scissor axis moves independently from the Grasping mode. When this option is selected, the rMOD bits (Grasping Mode) are ignored as the scissor axis position is defined by the rPRS (Position Request for the Scissor axis) register.

> ⚠️ **Caution**
> To avoid geometrical interference between fingers B and C, the reachable positions for the scissor axis is reduced if the Individual Control of Scissor option is selected. Please refer to the rPRA (Position Request) register description for more information about the reachable positions of the scissor axis.

---

## Register: GRIPPER OPTIONS 2

Address: Byte 2

| BIT | NAME | DESCRIPTION |
| --- | ---- | ----------- |
| 0-7 | rRS2 | Reserved    |

---

## Register: POSITION REQUEST (FINGER A IN INDIVIDUAL MODE)

Address: Byte 3

| BIT | NAME | DESCRIPTION                                                                                                                   |
| --- | ---- | ----------------------------------------------------------------------------------------------------------------------------- |
| 0-7 | rPRA | Set Position Request for the Gripper (finger A in individual mode).`<br>`0x00 (Minimum position) to 0xFF (Maximum position) |

This register is used to set the Adaptive Gripper fingers target position (or finger A only if bit rICF is set). The positions 0x00 and 0xFF correspond respectively to the fully opened and fully closed mechanical stops. Figure 4.6.1 represents the reachable workspace of the fingers and scissor axis. Note that the finger position on the figure represents the maximum value for the three fingers. Also, note that the fully opened and fully closed software limits are not shown on the figure for simplicity. The fully closed software limit of the scissor axis when the Individual Control of Scissor option is selected is also not shown for simplicity.

> ⚠️ **Caution**
> In order to protect the Gripper from geometric interferences, several software limits are implemented and therefore some positions are not reachable. When a finger reaches the software limit, the Gripper status will indicate that the requested position was reached. This is because the requested position is internally replaced by the software limit.

_(Figure 4.6.1: Reachable workspace of the fingers and scissor axis)_

---

## Register: SPEED (FINGER A IN INDIVIDUAL MODE)

Address: Byte 4

| BIT | NAME | DESCRIPTION                                                                                                                |
| --- | ---- | -------------------------------------------------------------------------------------------------------------------------- |
| 0-7 | rSPA | Set Grasping Speed of the Gripper (finger A in individual mode).`<br>`0x00 (Minimum velocity) to 0xFF (Maximum velocity) |

This register is used to setup the Gripper closing or opening speed (or finger A only if bit rICF is set) in real time, however, setting a speed will not initiate a motion.

> ℹ️ **Info**
> 0x00 speed does not mean absolute zero speed. It is the minimum speed of the Gripper.`<br>`Minimum speed: 22 mm/s `<br>`Maximum speed: 110 mm/s `<br>`Speed / count: 0.34 mm/s

---

## Register: FORCE (FINGER A IN INDIVIDUAL MODE)

Address: Byte 5

| BIT | NAME | DESCRIPTION                                                             |
| --- | ---- | ----------------------------------------------------------------------- |
| 0-7 | rFRA | Set Gripping Force `<br>`0x00 (Minimum force) to 0xFF (Maximum force) |

The force setting defines the final grasping force of the Adaptive Gripper (or finger A only if bit rICF is set). The force will fix maximum current sent to the motors while in motion. For each finger, if the current limit is exceeded, the finger stops and triggers an object detection notification.

> ℹ️ **Info**
> Force setting is overridden for a small distance when the motion is initiated. Also, note that 0x00 force does not mean zero force; it is the minimum force that the Gripper can apply.`<br>`Minimum force: 15 N `<br>`Maximum force: 60 N `<br>`Force / count: 0.175 N (approximate value, relation non-linear)

---

## Register: FINGER B POSITION REQUEST

Address: Byte 6

| BIT | NAME | DESCRIPTION                                                                                  |
| --- | ---- | -------------------------------------------------------------------------------------------- |
| 0-7 | rPRB | Set Position Request for finger B.`<br>`0x00 (Minimum position) to 0xFF (Maximum position) |

This register is used to set the finger B target position. It is only considered if the Individual Control of Finger option is selected (bit rICF is set). Please refer to rPRA (position request) register for more information.

---

## Register: FINGER B SPEED

Address: Byte 7

| BIT | NAME | DESCRIPTION                                                                                |
| --- | ---- | ------------------------------------------------------------------------------------------ |
| 0-7 | rSPB | Set Grasping Speed for finger B.`<br>`0x00 (Minimum velocity) to 0xFF (Maximum velocity) |

This register is used to set finger B speed. It is only considered if the Individual Control of Finger option is selected (bit rICF is set). Please refer to rSPA (speed) register for more information.

---

## Register: FINGER B FORCE

Address: Byte 8

| BIT | NAME | DESCRIPTION                                                                          |
| --- | ---- | ------------------------------------------------------------------------------------ |
| 0-7 | rFRB | Set Gripping Force for finger B.`<br>`0x00 (Minimum force) to 0xFF (Maximum force) |

This register is used to set finger B force. It is only considered if the Individual Control of Finger option is selected (bit rICF is set). Please refer to rFRA (force) register for more information.

---

## Register: FINGER C POSITION REQUEST

Address: Byte 9

| BIT | NAME | DESCRIPTION                                                                                  |
| --- | ---- | -------------------------------------------------------------------------------------------- |
| 0-7 | rPRC | Set Position Request for finger C.`<br>`0x00 (Minimum position) to 0xFF (Maximum position) |

This register is used to set the finger C target position. It is only considered if the Individual Control of Finger option is selected (bit rICF is set). Please refer to rPRA (position request) register for more information.

---

## Register: FINGER C SPEED

Address: Byte 10

| BIT | NAME | DESCRIPTION                                                                                |
| --- | ---- | ------------------------------------------------------------------------------------------ |
| 0-7 | rSPC | Set Grasping Speed for finger C.`<br>`0x00 (Minimum velocity) to 0xFF (Maximum velocity) |

This register is used to set finger C speed. It is only considered if the Individual Control of Finger option is selected (bit rICF is set). Please refer to rSPA (speed) register for more information.

---

## Register: FINGER C FORCE

Address: Byte 11

| BIT | NAME | DESCRIPTION                                                                          |
| --- | ---- | ------------------------------------------------------------------------------------ |
| 0-7 | rFRC | Set Gripping Force for finger C.`<br>`0x00 (Minimum force) to 0xFF (Maximum force) |

This register is used to set finger C force. It is only considered if the Individual Control of Finger option is selected (bit rICF is set). Please refer to rFRA (force) register for more information.

---

## Register: SCISSOR POSITION REQUEST

Address: Byte 12

| BIT | NAME | DESCRIPTION                                                                                          |
| --- | ---- | ---------------------------------------------------------------------------------------------------- |
| 0-7 | rPRS | Set Position Request for the scissor axis.`<br>`0x00 (Minimum position) to 0xFF (Maximum position) |

This register is used to set the scissor axis target position. It is only considered if the Individual Control of Scissor option is selected (bit rICS is set). Please refer to rPRA (position request) register for more information.

---

## Register: SCISSOR SPEED

Address: Byte 13

| BIT | NAME | DESCRIPTION                                                                                        |
| --- | ---- | -------------------------------------------------------------------------------------------------- |
| 0-7 | rSPS | Set Grasping Speed for the scissor axis.`<br>`0x00 (Minimum velocity) to 0xFF (Maximum velocity) |

This register is used to set the scissor axis speed. It is only considered if the Individual Control of Scissor option is selected (bit rICS is set). Please refer to rSPA (speed) register for more information.

---

## Register: SCISSOR FORCE

Address: Byte 14

| BIT | NAME | DESCRIPTION                                                                                  |
| --- | ---- | -------------------------------------------------------------------------------------------- |
| 0-7 | rFRS | Set Gripping Force for the scissor axis.`<br>`0x00 (Minimum force) to 0xFF (Maximum force) |

This register is used to set the scissor axis force. It is only considered if the Individual Control of Scissor option is selected (bit rICS is set). Please refer to rFRA (force) register for more information.

# 4.7 Robot input registers & status

> ⚠️ **Caution**
> This section applies to firmware 3.0 (grippers delivered after November 2011). For prior versions please see the documentation archives.

> ℹ️ **Info**
> Register format is Little Endian (Intel format), namely from LSB (Less Significant Bit) to MSB (Most Significant Bit).

---

## Register: GRIPPER STATUS

Address: Byte 0

| BIT | NAME | DESCRIPTION                                                                                                                                                                                                                                                                                                                        |
| --- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0   | gACT | Initialization status (Echo of the rACT bit (Activation bit)):`<br>`0 – Gripper reset `<br>`1 – Gripper activation                                                                                                                                                                                                           |
| 1-2 | gMOD | Echo of the rMOD bits (Grasping Mode request)`<br>`00 – Basic Mode `<br>`10 – Pinch Mode `<br>`01 – Wide Mode `<br>`11 – Scissor Mode                                                                                                                                                                                  |
| 3   | gGTO | Echo of the rGTO bit (Go to bit):`<br>`0 – Stopped (or performing activation/grasping mode change/automatic release)`<br>`1 – Go to Position Request                                                                                                                                                                         |
| 4-5 | gIMC | 00 – Gripper is in reset (or automatic release) state. See Fault Status if Gripper is activated.`<br>`10 – Activation in progress.`<br>`01 – Mode change in progress.`<br>`11 – Activation and mode change are completed.                                                                                                |
| 6-7 | gSTA | 00 – Gripper is in motion towards requested position (only meaningful if gGTO = 1)`<br>`10 – Gripper is stopped. One or two fingers stopped before requested position `<br>`01 – Gripper is stopped. All fingers stopped before requested position `<br>`11 – Gripper is stopped. All fingers reached requested position |

---

## Register: OBJECT STATUS

Address: Byte 1

| BIT | NAME | DESCRIPTION                                                                                                                                                                                                                                  |
| --- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0-1 | gDTA | 00 – Finger A is in motion (only meaningful if gGTO = 1)`<br>`10 – Finger A has stopped due to a contact while opening `<br>`01 – Finger A has stopped due to a contact while closing `<br>`11 – Finger A is at requested position |
| 2-3 | gDTB | 00 – Finger B is in motion (only meaningful if gGTO = 1)`<br>`10 – Finger B has stopped due to a contact while opening `<br>`01 – Finger B has stopped due to a contact while closing `<br>`11 – Finger B is at requested position |
| 4-5 | gDTC | 00 – Finger C is in motion (only meaningful if gGTO = 1)`<br>`10 – Finger C has stopped due to a contact while opening `<br>`01 – Finger C has stopped due to a contact while closing `<br>`11 – Finger C is at requested position |
| 6-7 | gDTS | 00 – Scissor is in motion (only meaningful if gGTO = 1)`<br>`10 – Scissor has stopped due to a contact while opening `<br>`01 – Scissor has stopped due to a contact while closing `<br>`11 – Scissor is at requested position     |

When a contact is detected, the corresponding axis will stop until one of these conditions is met: a new position request is commanded in the opposite direction, the requested force level is increased or the rGTO bit is cleared and set again.

> ⚠️ **Warning**
> Resetting the contact detection repeatedly at high frequency using the rGTO bit may cause a major failure of the Gripper. This is not considered a normal usage of the Gripper and it is not recommended by Robotiq.

> ⚠️ **Caution**
> The object detection is precise only to the order of a few mm. In some circumstances object detection may not detect an object even if it is successfully grasped. For example, picking up a thin object in a fingertip grip may be successful without object detection occurring. For such reasons, use this feature with caution. In such applications the "Gripper is stopped" status of register gSTA is sufficient to proceed to the next step of the routine.

---

## Register: FAULT STATUS

Address: Byte 2

| BIT | NAME | DESCRIPTION                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| --- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0-3 | gFLT | 0x00 – No Fault `<br><br>`**Priority Fault** `<br>`0x05 – Action delayed, activation (reactivation) must be completed prior to action `<br>`0x06 – Action delayed, mode change must be completed prior to action `<br>`0x07 – The activation bit must be set prior to action `<br><br>`**Minor Fault (red LED continuous)**`<br>`0x09 – The communication chip is not ready (may be booting)`<br>`0x0A – Changing mode fault, interferences detected on Scissor (for less than 20 sec)`<br>`0x0B – Automatic release in progress `<br><br>`**Major Fault (red LED blinking) – Reset is required** `<br>`0x0D – Activation fault, verify that no interference or other error occurred `<br>`0x0E – Changing mode fault, interferences detected on Scissor (for more than 20 sec)`<br>`0x0F – Automatic release completed. Reset and activation is required. |
| 4-7 | gRS1 | Reserved (zeros)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |

---

## Register: POSITION REQUEST ECHO (FINGER A IN INDIVIDUAL MODE)

Address: Byte 3

| BIT | NAME | DESCRIPTION                                                                                                                       |
| --- | ---- | --------------------------------------------------------------------------------------------------------------------------------- |
| 0-7 | gPRA | Echo of the requested position for the Gripper (or finger A in individual mode)`<br>`0x00 (Full Opening) to 0xFF (Full Closing) |

---

## Register: FINGER A POSITION

Address: Byte 4

| BIT | NAME | DESCRIPTION                                                             |
| --- | ---- | ----------------------------------------------------------------------- |
| 0-7 | gPOA | Position of Finger A `<br>`0x00 (Fully opened) to 0xFF (Fully closed) |

---

## Register: FINGER A CURRENT

Address: Byte 5

| BIT | NAME | DESCRIPTION                                        |
| --- | ---- | -------------------------------------------------- |
| 0-7 | gCUA | Current of Finger A `<br>`0.1 \* Current (in mA) |

---

## Register: FINGER B POSITION REQUEST ECHO

Address: Byte 6

| BIT | NAME | DESCRIPTION                                                                                    |
| --- | ---- | ---------------------------------------------------------------------------------------------- |
| 0-7 | gPRB | Echo of the requested position for finger B `<br>`0x00 (Full Opening) to 0xFF (Full Closing) |

---

## Register: FINGER B POSITION

Address: Byte 7

| BIT | NAME | DESCRIPTION                                                             |
| --- | ---- | ----------------------------------------------------------------------- |
| 0-7 | gPOB | Position of Finger B `<br>`0x00 (Fully opened) to 0xFF (Fully closed) |

---

## Register: FINGER B CURRENT

Address: Byte 8

| BIT | NAME | DESCRIPTION                                        |
| --- | ---- | -------------------------------------------------- |
| 0-7 | gCUB | Current of Finger B `<br>`0.1 \* Current (in mA) |

---

## Register: FINGER C POSITION REQUEST ECHO

Address: Byte 9

| BIT | NAME | DESCRIPTION                                                                                    |
| --- | ---- | ---------------------------------------------------------------------------------------------- |
| 0-7 | gPRC | Echo of the requested position for finger C `<br>`0x00 (Full Opening) to 0xFF (Full Closing) |

---

## Register: FINGER C POSITION

Address: Byte 10

| BIT | NAME | DESCRIPTION                                                             |
| --- | ---- | ----------------------------------------------------------------------- |
| 0-7 | gPOC | Position of Finger C `<br>`0x00 (Fully opened) to 0xFF (Fully closed) |

---

## Register: FINGER C CURRENT

Address: Byte 11

| BIT | NAME | DESCRIPTION                                        |
| --- | ---- | -------------------------------------------------- |
| 0-7 | gCUC | Current of Finger C `<br>`0.1 \* Current (in mA) |

---

## Register: SCISSOR POSITION REQUEST ECHO

Address: Byte 12

| BIT | NAME | DESCRIPTION                                                                                            |
| --- | ---- | ------------------------------------------------------------------------------------------------------ |
| 0-7 | gPRS | Echo of the requested position for the scissor axis `<br>`0x00 (Full Opening) to 0xFF (Full Closing) |

---

## Register: SCISSOR POSITION

Address: Byte 13

| BIT | NAME | DESCRIPTION                                                                     |
| --- | ---- | ------------------------------------------------------------------------------- |
| 0-7 | gPOS | Position of the scissor axis `<br>`0x00 (Fully opened) to 0xFF (Fully closed) |

---

## Register: SCISSOR CURRENT

Address: Byte 14

| BIT | NAME | DESCRIPTION                                                 |
| --- | ---- | ----------------------------------------------------------- |
| 0-7 | gCUS | Current for the scissor axis `<br>`0.1 \* Current (in mA) |

# 4.8 Example: Control Logic Flow (控制逻辑流程示例)

以下是一个典型的夹爪“抓取与放置（Pick and Place）”的控制逻辑流程图的文字描述版，展示了如何结合使用功能寄存器与状态寄存器：

### 1. 激活夹爪 (Activate Gripper)

- **写入 (Write)**：设置 `Bit 0 (rACT) = 1`（此位必须保持常开）。
- **读取等待 (Wait)**：循环读取状态，直到 `Bit 4 & 5 (gIMC) == 1`（表示初始化已完成）。

### 2. 选择操作模式 (Choose Operation Mode)

- **写入 (Write)**：设置 `Bit 1 & 2 (rMOD)` 选择模式。
  - `00` = Basic mode (基本模式)
  - `10` = Pinch mode (捏合模式)
  - `01` = Wide mode (宽开口模式)
  - `11` = Scissor mode (剪刀模式)
- **读取等待 (Wait)**：循环读取状态，直到 `Bit 4 & 5 (gIMC) == 1` 并且 `Bit 1 & 2 (gMOD) == 设定的模式`（表示模式切换完成）。

### 3. 移动机器人 (Move Robot)

- 此时可以将机械臂移动到需要抓取/放置的位置。

### 4. 执行动作指令 (Go To Requested Position)

- **写入 (Write)**：设定目标位置 (Position)、速度 (Speed) 和力 (Force)（范围为 0-255）。并设置 `Bit 3 (rGTO) = 1` 触发运动。
- **读取等待 (Wait)**：循环读取状态以判断是否到达位置或触碰物体。判断条件为：
  - `Byte 3 (echo) == 目标请求位置`
  - **并且** `Bit 6 & 7 (gSTA) == 1` （停止，所有手指均未达到设定位置），**或者** `Bit 6 (gSTA) == 1` ，**或者** `Bit 7 (gSTA) == 1`（停止，所有手指到达设定位置）。
- **完成**：重复步骤 3 和 4 进行下一个抓取/释放动作。

> ℹ️ **Info**
> `Go to requested position` 指令通常用于张开/闭合夹爪，直到夹爪检测到物体阻挡，或者到达请求的绝对位置为止。

# 4.9 Robotiq Adaptive Gripper S Model - Modbus RTU 通信手册

## 4.9.1 Connection setup

下表描述了使用Modbus RTU协议控制Robotiq Adaptive Gripper S型号夹爪的连接要求：

| PROPRIETY                                   | VALUE                                                                                                      |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Physical Interface                          | RS232                                                                                                      |
| Baud Rate                                   | 115,200 bps                                                                                                |
| Data Bits                                   | 8                                                                                                          |
| Stop Bit                                    | 1                                                                                                          |
| Parity                                      | None                                                                                                       |
| Number Notation                             | Hexadecimal                                                                                                |
| Supported Functions                         | Read Holding Registers (FC03)`<br>`Preset Single Register (FC06)`<br>`Preset Multiple Registers (FC16) |
| Exception Responses                         | Not supported                                                                                              |
| Slave ID                                    | 0x0009 (9)                                                                                                 |
| Robot Output / Gripper Input First Register | 0x03E8 (1000)                                                                                              |
| Robot Input / Gripper Output First Register | 0x07D0 (2000)                                                                                              |

> 说明：Modbus RTU协议的每个寄存器（字 - 16位）由Robotiq Adaptive Gripper S的2个寄存器（字节 - 8位）组成。第一个夹爪输出Modbus寄存器（0x07D0）由Robotiq Adaptive Gripper S的前2个寄存器（字节0和字节1）组成。

## 4.9.2 Read holding registers (FC03)

功能码03（FC03）用于读取夹爪状态（机器人输入），例如夹爪状态、物体状态、手指位置等。

**示例：** 读取寄存器0x07D0（2000）和0x07D1（2001），包含夹爪状态、物体检测、故障状态和位置请求回显。

### 请求帧

`09 03 07 D0 00 02 C5 CE`

| BITS | DESCRIPTION                               |
| ---- | ----------------------------------------- |
| 09   | SlaveID                                   |
| 03   | Function Code 03 (Read Holding Registers) |
| 07D0 | Address of the first requested register   |
| 0002 | Number of registers requested (2)         |
| C5CE | Cyclic Redundancy Check (CRC)             |

### 响应帧

`09 03 04 E0 00 00 00 44 33`

| BITS | DESCRIPTION                                                                |
| ---- | -------------------------------------------------------------------------- |
| 09   | SlaveID                                                                    |
| 03   | Function Code 03 (Read Holding Registers)                                  |
| 04   | Number of data bytes to follow (2 registers × 2 bytes/register = 4 bytes) |
| E000 | Content of register 07D0                                                   |
| 0000 | Content of register 07D1                                                   |
| 4433 | Cyclic Redundancy Check (CRC)                                              |

> ⚠️ Note
> 自适应夹爪寄存器值以200Hz的频率更新。因此，建议发送FC03命令的间隔不小于5ms。

## 4.9.3 Preset single register (FC06)

功能码06（FC06）用于激活夹爪功能（机器人输出），例如动作请求、速度、力等。

**示例：** 将包含动作请求和夹爪选项的寄存器0x03E8（1000）设置为0x0100，初始化夹爪。

### 请求帧

`09 06 03 E8 01 00 09 62`

| BITS | DESCRIPTION                               |
| ---- | ----------------------------------------- |
| 09   | SlaveID                                   |
| 06   | Function Code 06 (Preset Single Register) |
| 03E8 | Address of the register                   |
| 0100 | Value to write                            |
| 0962 | Cyclic Redundancy Check (CRC)             |

### 响应帧（回显）

`09 06 03 E8 01 00 09 62`

| BITS | DESCRIPTION                               |
| ---- | ----------------------------------------- |
| 09   | SlaveID                                   |
| 06   | Function Code 06 (Preset Single Register) |
| 03E8 | Address of the register                   |
| 0100 | Value written                             |
| 0962 | Cyclic Redundancy Check (CRC)             |

## 4.9.4 Preset multiple registers (FC16)

功能码16（FC16）用于激活夹爪功能（机器人输出），例如动作请求、速度、力等。

**示例：** 设置寄存器0x03E9（1001）和0x03EA，配置夹爪的位置请求、速度和力。

### 请求帧

`09 10 03 E9 00 02 04 60 E6 3C C8 EC 7C`

| BITS | DESCRIPTION                                                                |
| ---- | -------------------------------------------------------------------------- |
| 09   | SlaveID                                                                    |
| 10   | Function Code 16 (Preset Multiple Registers)                               |
| 03E9 | Address of the first register                                              |
| 0002 | Number of registers to write                                               |
| 04   | Number of data bytes to follow (2 registers × 2 bytes/register = 4 bytes) |
| 00E6 | Value to write to register 0x03E9                                          |
| 3CC8 | Value to write to register 0x03EA                                          |
| EC7C | Cyclic Redundancy Check (CRC)                                              |

### 响应帧

`09 10 03 E9 00 02 91 30`

| BITS | DESCRIPTION                                  |
| ---- | -------------------------------------------- |
| 09   | SlaveID                                      |
| 10   | Function Code 16 (Preset Multiple Registers) |
| 03E9 | Address of the first register                |
| 0002 | Number of written                            |
| 9130 | Cyclic Redundancy Check (CRC)                |

## 4.9.5 Master read&write multiple registers (FC23)

功能码23（FC23）用于同时读取夹爪状态（机器人输入）和激活夹爪功能（机器人输出），例如夹爪状态、物体状态、手指位置、动作请求（速度、力等）。

> ⚠️ Note
> C-Model示例仅作为S-Model的操作说明示例，控制方式和位寻址不相同，请参考C-Model指令手册获取详细示例。

## 4.9.6 Modbus RTU example

本节描述了使用Modbus RTU协议实现取放应用的典型示例。激活夹爪后，机器人移动到拾取位置抓取物体，再移动到第二个位置释放物体。

### Step 1: Activation Request

#### 请求帧

`09 10 03 E8 00 03 06 01 00 00 00 00 00 72 E1`

| BITS | DESCRIPTION                                                                                                           |
| ---- | --------------------------------------------------------------------------------------------------------------------- |
| 09   | SlaveID                                                                                                               |
| 10   | Function Code 16 (Preset Multiple Registers)                                                                          |
| 03E8 | Address of the first register                                                                                         |
| 0003 | Number of registers to write to                                                                                       |
| 06   | Number of data bytes to follow (3 registers × 2 bytes/register = 6 bytes)                                            |
| 0100 | Value to write to register 0x03E9 (ACTION REQUEST = 0x01 and GRIPPER OPTIONS = 0x00): rACT = 1 for "Activate Gripper" |
| 0000 | Value to write to register 0x03EA                                                                                     |
| 0000 | Value to write to register 0x03EB                                                                                     |
| 72E1 | Cyclic Redundancy Check (CRC)                                                                                         |

#### 响应帧

`09 10 03 E8 00 03 01 30`

| BITS | DESCRIPTION                                  |
| ---- | -------------------------------------------- |
| 09   | SlaveID                                      |
| 10   | Function Code 16 (Preset Multiple Registers) |
| 03E8 | Address of the first register                |
| 0003 | Number of written registers                  |
| 0130 | Cyclic Redundancy Check (CRC)                |

### Step 2: Read Gripper status until the activation is completed

#### 请求帧

`09 03 07 D0 00 01 85 CF`

| BITS | DESCRIPTION                               |
| ---- | ----------------------------------------- |
| 09   | SlaveID                                   |
| 03   | Function Code 03 (Read Holding Registers) |
| 07D0 | Address of the first requested register   |
| 0001 | Number of registers requested (1)         |
| 85CF | Cyclic Redundancy Check (CRC)             |

#### 响应帧（激活未完成）

`09 03 02 11 00 55 D5`

| BITS | DESCRIPTION                                                                                                                                      |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| 09   | SlaveID                                                                                                                                          |
| 03   | Function Code 03 (Read Holding Registers)                                                                                                        |
| 02   | Number of data bytes to follow (1 registers × 2 bytes/register = 2 bytes)                                                                       |
| 1100 | Content of register 07D0 (GRIPPER STATUS = 0x11, OBJECT STATUS = 0x00): gACT = 1 for "Gripper Activation", gIMC = 1 for "Activation in progress" |
| 55D5 | Cyclic Redundancy Check (CRC)                                                                                                                    |

#### 响应帧（激活完成）

`09 03 02 31 00 4C 15`

| BITS | DESCRIPTION                                                                                                                                                        |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 09   | SlaveID                                                                                                                                                            |
| 03   | Function Code 03 (Read Holding Registers)                                                                                                                          |
| 02   | Number of data bytes to follow (1 registers × 2 bytes/register = 2 bytes)                                                                                         |
| 3100 | Content of register 07D0 (GRIPPER STATUS = 0x31, OBJECT STATUS = 0x00): gACT = 1 for "Gripper Activation", gIMC = 3 for "Activation and mode change are completed" |
| 4C15 | Cyclic Redundancy Check (CRC)                                                                                                                                      |

### Step 3: Move the robot to the pick-up location

### Step 4: Close the Gripper at full speed and full force

#### 请求帧

`09 10 03 E8 00 03 06 09 00 00 FF FF FF 42 29`

| BITS | DESCRIPTION                                                                                                                                                                                   |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 09   | SlaveID                                                                                                                                                                                       |
| 10   | Function Code 16 (Preset Multiple Registers)                                                                                                                                                  |
| 03E8 | Address of the first register                                                                                                                                                                 |
| 0003 | Number of registers to write to                                                                                                                                                               |
| 06   | Number of data bytes to follow (3 registers × 2 bytes/register = 6 bytes)                                                                                                                    |
| 0900 | Value to write to register 0x03E9 (ACTION REQUEST = 0x09 and GRIPPER OPTIONS = 0x00): rACT = 1 for "Activate Gripper", rMOD=0 for "Go to Basic Mode", rGTO = 1 for "Go to Requested Position" |
| 00FF | Value to write to register 0x03EA (GRIPPER OPTIONS 2 = 0x00 and POSITION REQUEST = 0xFF): rPRA = 255/255 for full closing of the Gripper                                                      |
| FFFF | Value to write to register 0x03EB (SPEED = 0xFF and FORCE = 0xFF): full speed and full force                                                                                                  |
| 4229 | Cyclic Redundancy Check (CRC)                                                                                                                                                                 |

#### 响应帧

`09 10 03 E8 00 03 01 30`

| BITS | DESCRIPTION                                  |
| ---- | -------------------------------------------- |
| 09   | SlaveID                                      |
| 10   | Function Code 16 (Preset Multiple Registers) |
| 03E8 | Address of the first register                |
| 0003 | Number of written registers                  |
| 0130 | Cyclic Redundancy Check (CRC)                |

### Step 5: Read Gripper status until the grip is completed

#### 请求帧

`09 03 07 D0 00 08 45 C9`

| BITS | DESCRIPTION                               |
| ---- | ----------------------------------------- |
| 09   | SlaveID                                   |
| 03   | Function Code 03 (Read Holding Registers) |
| 07D0 | Address of the first requested register   |
| 0008 | Number of registers requested (8)         |
| 45C9 | Cyclic Redundancy Check (CRC)             |

#### 响应帧示例（抓取未完成）

`09 03 10 39 C0 00 FF 08 0F 00 08 10 00 08 0F 00 89 00 00 73 70`

| BITS | DESCRIPTION                                                                                                                                                                               |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 09   | SlaveID                                                                                                                                                                                   |
| 03   | Function Code 03 (Read Holding Registers)                                                                                                                                                 |
| 10   | Number of data bytes to follow (8 registers × 2 bytes/register = 16 bytes)                                                                                                               |
| 39C0 | Content of register 0x07D0 (GRIPPER STATUS = 0x39, OBJECT STATUS = 0xC0): gSTA = 0 for "Gripper is in motion towards requested position"                                                  |
| 00FF | Content of register 0x07D1 (FAULT STATUS = 0x00, POSITION REQUEST ECHO = 0xFF): the position request echo tells that the command was well received and that the GRIPPER STATUS is valid.  |
| 080F | Content of register 0x07D2 (FINGER A POSITION = 0x08, FINGER A CURRENT = 0x0F): the position of finger A is 8/255 and the motor current is 150mA (these values will change during motion) |
| 0008 | Content of register 0x07D3 (FINGER B POSITION REQUEST ECHO = 0x00, FINGER B POSITION = 0x08)                                                                                              |
| 1000 | Content of register 0x07D4 (FINGER B CURRENT = 0x10, FINGER C POSITION REQUEST ECHO = 0x00)                                                                                               |
| 080F | Content of register 0x07D5 (FINGER C POSITION = 0x08, FINGER C CURRENT = 0x0F)                                                                                                            |
| 0089 | Content of register 0x07D6 (SCISSOR POSITION REQUEST ECHO = 0x00, SCISSOR POSITION = 0x89)                                                                                                |
| 0000 | Content of register 0x07D7 (SCISSOR CURRENT = 0x00)                                                                                                                                       |
| 7370 | Cyclic Redundancy Check (CRC)                                                                                                                                                             |

#### 响应帧示例（抓取完成）

`09 03 10 B9 EA 00 FF BC 00 00 C1 00 00 BD 00 00 89 00 00 4E 17`

| BITS | DESCRIPTION                                                                                                                                                                                                                                  |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 09   | SlaveID                                                                                                                                                                                                                                      |
| 03   | Function Code 03 (Read Holding Registers)                                                                                                                                                                                                    |
| 10   | Number of data bytes to follow (8 registers × 2 bytes/register = 16 bytes)                                                                                                                                                                  |
| B9EA | Content of register 0x07D0 (GRIPPER STATUS = 0xB9, OBJECT STATUS = 0xEA): gSTA = 2 for "Gripper is stopped. All fingers stopped before requested position", gDTA = gDTB = gDTC = 2 for "Finger X has stopped due to a contact while closing" |
| 00FF | Content of register 0x07D1 (FAULT STATUS = 0x00, POSITION REQUEST ECHO = 0xFF): the position request echo tells that the command was well received and that the GRIPPER STATUS is valid.                                                     |
| BC00 | Content of register 0x07D2 (FINGER A POSITION = 0xBC, FINGER A CURRENT = 0x00): the position of finger A is 188/255 and the motor current is 0mA                                                                                             |
| 00C1 | Content of register 0x07D3 (FINGER B POSITION REQUEST ECHO = 0x00, FINGER B POSITION = 0xC1)                                                                                                                                                 |
| 0000 | Content of register 0x07D4 (FINGER B CURRENT = 0x00, FINGER C POSITION REQUEST ECHO = 0x00)                                                                                                                                                  |
| BD00 | Content of register 0x07D5 (FINGER C POSITION = 0xBD, FINGER C CURRENT = 0x00)                                                                                                                                                               |
| 0089 | Content of register 0x07D6 (SCISSOR POSITION REQUEST ECHO = 0x00, SCISSOR POSITION = 0x89)                                                                                                                                                   |
| 0000 | Content of register 0x07D7 (SCISSOR CURRENT = 0x00)                                                                                                                                                                                          |
| 4E17 | Cyclic Redundancy Check (CRC)                                                                                                                                                                                                                |

### Step 6: Move the robot to the release location

### Step 7: Open the Gripper at full speed and full force

#### 请求帧

`09 10 03 E8 00 03 06 09 00 00 00 FF FF 72 19`

| BITS | DESCRIPTION                                                                                                                                                                                   |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 09   | SlaveID                                                                                                                                                                                       |
| 10   | Function Code 16 (Preset Multiple Registers)                                                                                                                                                  |
| 03E8 | Address of the first register                                                                                                                                                                 |
| 0003 | Number of registers to write to                                                                                                                                                               |
| 06   | Number of data bytes to follow (3 registers × 2 bytes/register = 6 bytes)                                                                                                                    |
| 0900 | Value to write to register 0x03E9 (ACTION REQUEST = 0x09 and GRIPPER OPTIONS = 0x00): rACT = 1 for "Activate Gripper", rMOD=0 for "Go to Basic Mode", rGTO = 1 for "Go to Requested Position" |
| 0000 | Value to write to register 0x03EA (GRIPPER OPTIONS 2 = 0x00 and POSITION REQUEST = 0x00): rPR = 0/255 for full opening of the Gripper (partial opening would also be possible)                |
| FFFF | Value to write to register 0x03EB (SPEED = 0xFF and FORCE = 0xFF): full speed and full force                                                                                                  |
| 7219 | Cyclic Redundancy Check (CRC)                                                                                                                                                                 |

#### 响应帧

`09 10 03 E8 00 03 01 30`

| BITS | DESCRIPTION                                  |
| ---- | -------------------------------------------- |
| 09   | SlaveID                                      |
| 10   | Function Code 16 (Preset Multiple Registers) |
| 03E8 | Address of the first register                |
| 0003 | Number of written registers                  |
| 0130 | Cyclic Redundancy Check (CRC)                |

### Step 8: Read gripper status until the opening is completed

#### 请求帧

`09 03 07 D0 00 08 45 C9`

| BITS | DESCRIPTION                               |
| ---- | ----------------------------------------- |
| 09   | SlaveID                                   |
| 03   | Function Code 03 (Read Holding Registers) |
| 07D0 | Address of the first requested register   |
| 0008 | Number of registers requested (8)         |
| 45C9 | Cyclic Redundancy Check (CRC)             |

#### 响应帧示例（打开未完成）

`09 03 10 39 C0 00 00 B8 0B 00 BD 0E 00 BA 0B 00 89 00 00 10 85`

| BITS | DESCRIPTION                                                                                                                                                                                 |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 09   | SlaveID                                                                                                                                                                                     |
| 03   | Function Code 03 (Read Holding Registers)                                                                                                                                                   |
| 10   | Number of data bytes to follow (8 registers × 2 bytes/register = 16 bytes)                                                                                                                 |
| 39C0 | Content of register 0x07D0 (GRIPPER STATUS = 0x39, OBJECT STATUS = 0xC0): gSTA = 0 for "Gripper is in motion towards requested position"                                                    |
| 0000 | Content of register 0x07D1 (FAULT STATUS = 0x00, POSITION REQUEST ECHO = 0x00): the position request echo tells that the command was well received and that the GRIPPER STATUS is valid.    |
| B80B | Content of register 0x07D2 (FINGER A POSITION = 0xB8, FINGER A CURRENT = 0x0B): the position of finger A is 184/255 and the motor current is 170mA (these values will change during motion) |
| 00BD | Content of register 0x07D3 (FINGER B POSITION REQUEST ECHO = 0x00, FINGER B POSITION = 0xBD)                                                                                                |
| 0E00 | Content of register 0x07D4 (FINGER B CURRENT = 0x0E, FINGER C POSITION REQUEST ECHO = 0x00)                                                                                                 |
| BA0B | Content of register 0x07D5 (FINGER C POSITION = 0xBA, FINGER C CURRENT = 0x0B)                                                                                                              |
| 0089 | Content of register 0x07D6 (SCISSOR POSITION REQUEST ECHO = 0x00, SCISSOR POSITION = 0x89)                                                                                                  |
| 0000 | Content of register 0x07D7 (SCISSOR CURRENT = 0x00)                                                                                                                                         |
| 1085 | Cyclic Redundancy Check (CRC)                                                                                                                                                               |

#### 响应帧示例（打开完成）

`09 03 10 F9 FF 00 00 07 00 00 06 00 00 06 00 00 89 00 00 34 8D`

| BITS | DESCRIPTION                                                                                                                                                                              |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 09   | SlaveID                                                                                                                                                                                  |
| 03   | Function Code 03 (Read Holding Registers)                                                                                                                                                |
| 10   | Number of data bytes to follow (8 registers × 2 bytes/register = 16 bytes)                                                                                                              |
| F9FF | Content of register 0x07D0 (GRIPPER STATUS = 0xF9, OBJECT STATUS = 0xFF): gSTA = 3 for "Gripper is stopped. All fingers reached requested position"                                      |
| 0000 | Content of register 0x07D1 (FAULT STATUS = 0x00, POSITION REQUEST ECHO = 0x00): the position request echo tells that the command was well received and that the GRIPPER STATUS is valid. |
| 0700 | Content of register 0x07D2 (FINGER A POSITION = 0x07, FINGER A CURRENT = 0x00): the position of finger A is 7/255 and the motor current is 0mA                                           |
| 0006 | Content of register 0x07D3 (FINGER B POSITION REQUEST ECHO = 0x00, FINGER B POSITION = 0x06)                                                                                             |
| 0000 | Content of register 0x07D4 (FINGER B CURRENT = 0x00, FINGER C POSITION REQUEST ECHO = 0x00)                                                                                              |
| 0600 | Content of register 0x07D5 (FINGER C POSITION = 0x06, FINGER C CURRENT = 0x00)                                                                                                           |
| 0089 | Content of register 0x07D6 (SCISSOR POSITION REQUEST ECHO = 0x00, SCISSOR POSITION = 0x89)                                                                                               |
| 0000 | Content of register 0x07D7 (SCISSOR CURRENT = 0x00)                                                                                                                                      |
| 348D | Cyclic Redundancy Check (CRC)                                                                                                                                                            |

### Step 9: Loop back to step 7 if other objects have to be gripped.
