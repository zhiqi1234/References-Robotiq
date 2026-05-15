# Robotiq Adaptive Gripper S-Model 控制参考手册

## 夹爪结构概述

Adaptive Gripper S-Model 是一种用于工业应用的机器人末端夹爪，可拾取、放置和处理各种尺寸和形状的零件。

- **手指结构**：三根关节手指（手指 A 在前，手指 B 和 C 在后），每根手指有 3 个关节（3 段指骨）。夹爪最多可与物体产生 **10 个接触点**（每根手指 3 个指骨 + 手掌）。
- **欠驱动设计 (Under-actuated)**：电机数量少于关节总数，手指可自动适应物体形状，同时也简化了夹爪控制。
- **两种基本运动**：
  1. **切换操作模式**：改变手指 B 和 C 的朝向（4 种预设模式）；
  2. **开合手指**：通过单个"转到请求位置"命令完成，夹爪自动控制每根手指直到稳定——接触物体或到达机械限位。

## 关键安全警告

> ⚠️ **Warning**
>
> - 夹爪必须牢固安装后才能操作机器人。
> - **严禁使用交流电源供电**，必须使用 24V DC。
> - 始终遵守夹爪的推荐负载。根据应用场景合理设置抓取力和速度。
> - 夹爪通电时，手指和衣物远离夹爪。
> - 夹爪仅用于**抓取和临时固定零件**，**不得**用于对物体或表面施加力（如推、压等操作）。
> - 任何超出技术参数范围的使用均视为不当使用。

---

## 1. 总体概述 (Generalities)

> ⚠️ **Caution**
> 本节适用于固件版本 3.0（2011 年 11 月之后交付的夹爪）。对于早期版本，请参阅归档文档。

Robotiq Adaptive Gripper S-Model 通过工业通信协议（如 EtherNet/IP, DeviceNet, CANopen, EtherCat 等）由机器人控制器进行控制。夹爪的编程可以通过机器人的示教器（Teach Pendant）或离线编程完成。

> ℹ️ **Info**
>
> - 对于每种操作模式（Operation Mode），操作员都可以控制手指的速度（Speed）和力（Force）。
> - 除非选择了独立控制模式（Individual Control），否则手指的运动始终是同步的。动作由单个“转到请求位置（Go to requested position）”命令完成（每个机械指骨的运动是自动进行的）。

由于 Robotiq Adaptive Gripper S-Model 拥有独立的内部控制器，因此使用如”转到请求位置”等高级命令来控制它。内嵌的 Robotiq 控制器负责调节设定的速度和力，同时手指的机械结构会自动适应物体的形状。

### 四种操作模式 (Four Operation Modes)

夹爪支持四种预设操作模式，通过 `rMOD` 位（Byte 0, Bit 1-2）选择：

| rMOD | 模式                              | 说明                                                                                                |
| :--: | :-------------------------------- | :-------------------------------------------------------------------------------------------------- |
|  00  | **Basic Mode (基本模式)**   | 最通用的模式。最适合有一维尺寸大于另外两维的物体，但可以抓取各类物体。                              |
|  01  | **Wide Mode (宽开口模式)**  | 最适合抓取圆形或大型物体。                                                                          |
|  10  | **Pinch Mode (捏合模式)**   | 用于需要精确拾取的小物体。此模式只能在手指远端指骨之间抓取物体。                                    |
|  11  | **Scissor Mode (剪刀模式)** | 主要用于微小物体。此模式力量较小但精度高。手指 B 和 C 横向相向运动，手指 A 保持静止。无法包裹物体。 |

> ℹ️ **Info**
> 操作模式是由用户根据物体尺寸/形状和任务需求预设的输入。夹爪会自动决定产生包裹抓取（Encompassing Grip）还是指尖抓取（Fingertip Grip），取决于操作模式、物体几何形状以及物体相对夹爪的位置。

### 两种抓取类型 (Two Types of Grip)

夹爪闭合时会产生两种抓取类型之一，**由夹爪根据以下因素自动决定**：

- 操作模式 (Operation Mode)
- 零件的几何形状
- 零件相对夹爪的位置

> 同一零件、同一操作模式，因位置不同，可能产生不同的抓取类型。

| 类型                                   | 说明                                                                                           | 触发条件                                                          |
| :------------------------------------- | :--------------------------------------------------------------------------------------------- | :---------------------------------------------------------------- |
| **Encompassing Grip (包裹抓取)** | 手指包围物体，物体被包裹在手指之间。稳定性与摩擦力无关，稳定性更高。**建议尽可能使用。** | 物体的近端/中段指骨先接触物体。应将物体抵住夹爪手掌以确保稳定性。 |
| **Fingertip Grip (指尖抓取)**    | 仅由远端指骨夹持物体，类似于传统平行夹爪。稳定性主要依赖摩擦力。                               | 物体的远端指骨先接触物体。                                        |

### 抓取类型 vs 操作模式兼容性

| 操作模式                | Encompassing Grip | Fingertip Grip |
| :---------------------- | :---------------: | :------------: |
| Basic Mode (基本模式)   |        ✓        |       ✓       |
| Wide Mode (宽开口模式)  |        ✓        |       ✓       |
| Pinch Mode (捏合模式)   |        ✗        |       ✓       |
| Scissor Mode (剪刀模式) |        ✗        |       ✓       |

---

## 2. 状态概述 (Status Overview)

Adaptive Gripper S-Model 会向机器人控制器返回多个寄存器的信息以供读取：

- **Global Gripper Status (全局夹爪状态)** - 提供全局夹爪状态。显示当前处于哪种操作模式，或者夹爪是闭合还是张开。
- **Object Status (物体状态)** - 提供物体状态，让你知道夹爪中是否有物体；如果有，有多少根手指与物体接触。
- **Fault Status (故障状态)** - 提供有关故障原因的详细信息。
- **Position Request Echo (位置请求回显)** - 夹爪返回机器人请求的位置，以确保新命令已被正确接收。
- **Motor Encoder Status (电机编码器状态)** - 提供四个电机的编码器信息。
- **Current Status (电流状态)** - 提供电机的电流信息。由于电机扭矩是电流的线性函数，这反映了施加在手指驱动连杆上的力。

---

## 3. 控制逻辑概述 (Control Overview)

夹爪控制器具有与机器人控制器共享的内部内存。内存的一部分用于机器人输出（Robot Output）/ 夹爪功能控制。另一部分内存用于机器人输入（Robot Input）/ 夹爪状态反馈。

因此，机器人控制器可以执行两种类型的操作：

1. **Write (写入)**：写入机器人输出寄存器以激活夹爪的特定功能；
2. **Read (读取)**：读取机器人输入寄存器以获取夹爪的当前状态。

> ℹ️ **Info**
> 夹爪在上电时必须进行初始化（激活位 activation bit）。此过程需要几秒钟，允许夹爪根据内部的机械限位进行自校准。

---

## 4. 状态指示灯 (Status LEDs)

夹爪上配有三个状态 LED 指示灯，提供有关 Adaptive Gripper S-Model 运行状态的一般信息。这在硬件调试和排障时非常有用。

### 4.1 电源指示灯 (Supply LED)

| 颜色        | 状态     | 说明                         |
| :---------- | :------- | :--------------------------- |
| Blue (蓝色) | Off (灭) | 夹爪未供电                   |
| Blue (蓝色) | On (亮)  | 夹爪供电正常，控制板正在运行 |

### 4.2 通信指示灯 (Communication LED)

| 颜色         | 状态            | 说明                                         |
| :----------- | :-------------- | :------------------------------------------- |
| Green (绿色) | Off (灭)        | 未检测到网络                                 |
| Green (绿色) | Blinking (闪烁) | 已检测到网络，但未建立连接                   |
| Green (绿色) | On (亮)         | 已检测到网络，且至少有一个连接处于已建立状态 |

### 4.3 故障指示灯 (Fault LED)

| 颜色       | 状态            | 说明                           |
| :--------- | :-------------- | :----------------------------- |
| Red (红色) | Off (灭)        | 未检测到故障                   |
| Red (红色) | On (亮)         | 发生轻微故障（或夹爪正在启动） |
| Red (红色) | Blinking (闪烁) | 发生严重故障                   |

> ℹ️ **Info**
> 严重故障（Major fault）通常指的是夹爪必须重新激活才能恢复工作的情况。

---

## 5. 寄存器映射 (Register Mapping)

> ⚠️ **Caution**
> 本节适用于固件版本 3.0（2011 年 11 月之后交付的夹爪）。对于早期版本，请参阅归档文档。

> ℹ️ **Info**
> 寄存器格式为小端序（Little Endian / Intel 格式），即从 LSB（最低有效位）到 MSB（最高有效位）。

固件版本 3.0 提供了新功能，如通过"Go To"命令直接控制手指位置，以及手指和剪刀轴的独立控制、手指自动居中（beta）等高级选项。

系统提供了**简化控制模式（Simplified Control Mode）**和**高级控制模式（Advanced Control Mode）**两种寄存器映射。从夹爪的角度看，两种模式没有区别，简化模式只是为了方便仅需基本功能的用户。

> ⚠️ **Warning**
> 使用简化控制模式时，必须将未使用的寄存器填零。否则会意外触发控制选项，可能导致夹爪出现危险行为。

---

### 5.1 简化控制模式寄存器映射 (Simplified Control Mode)

> ⚠️ **Caution**
> 字节编号从 0 开始（而非 1），适用于功能和状态寄存器。

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

### 5.2 高级控制模式寄存器映射 (Advanced Control Mode)

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

## 6. 机器人输出寄存器 (Robot Output Registers)

> ⚠️ **Caution**
> 本节适用于固件版本 3.0（2011 年 11 月之后交付的夹爪）。对于早期版本，请参阅归档文档。

> ℹ️ **Info**
> 寄存器格式为小端序（Little Endian / Intel 格式），即从 LSB 到 MSB。

---

### 6.1 ACTION REQUEST

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

### 6.2 GRIPPER OPTIONS

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

### 6.3 GRIPPER OPTIONS 2

Address: Byte 2

| BIT | NAME | DESCRIPTION |
| --- | ---- | ----------- |
| 0-7 | rRS2 | Reserved    |

---

### 6.4 POSITION REQUEST (FINGER A)

Address: Byte 3

| BIT | NAME | DESCRIPTION                                                                                                                   |
| --- | ---- | ----------------------------------------------------------------------------------------------------------------------------- |
| 0-7 | rPRA | Set Position Request for the Gripper (finger A in individual mode).`<br>`0x00 (Minimum position) to 0xFF (Maximum position) |

This register is used to set the Adaptive Gripper fingers target position (or finger A only if bit rICF is set). The positions 0x00 and 0xFF correspond respectively to the fully opened and fully closed mechanical stops. Figure 4.6.1 represents the reachable workspace of the fingers and scissor axis. Note that the finger position on the figure represents the maximum value for the three fingers. Also, note that the fully opened and fully closed software limits are not shown on the figure for simplicity. The fully closed software limit of the scissor axis when the Individual Control of Scissor option is selected is also not shown for simplicity.

> ⚠️ **Caution**
> In order to protect the Gripper from geometric interferences, several software limits are implemented and therefore some positions are not reachable. When a finger reaches the software limit, the Gripper status will indicate that the requested position was reached. This is because the requested position is internally replaced by the software limit.

> 参考原版手册 Figure 4.6.1：手指与剪刀轴的可达工作空间

---

### 6.5 SPEED (FINGER A)

Address: Byte 4

| BIT | NAME | DESCRIPTION                                                                                                                |
| --- | ---- | -------------------------------------------------------------------------------------------------------------------------- |
| 0-7 | rSPA | Set Grasping Speed of the Gripper (finger A in individual mode).`<br>`0x00 (Minimum velocity) to 0xFF (Maximum velocity) |

This register is used to setup the Gripper closing or opening speed (or finger A only if bit rICF is set) in real time, however, setting a speed will not initiate a motion.

> ℹ️ **Info**
> 0x00 speed does not mean absolute zero speed. It is the minimum speed of the Gripper.`<br>`Minimum speed: 22 mm/s `<br>`Maximum speed: 110 mm/s `<br>`Speed / count: 0.34 mm/s

---

### 6.6 FORCE (FINGER A)

Address: Byte 5

| BIT | NAME | DESCRIPTION                                                             |
| --- | ---- | ----------------------------------------------------------------------- |
| 0-7 | rFRA | Set Gripping Force `<br>`0x00 (Minimum force) to 0xFF (Maximum force) |

The force setting defines the final grasping force of the Adaptive Gripper (or finger A only if bit rICF is set). The force will fix maximum current sent to the motors while in motion. For each finger, if the current limit is exceeded, the finger stops and triggers an object detection notification.

> ℹ️ **Info**
> Force setting is overridden for a small distance when the motion is initiated. Also, note that 0x00 force does not mean zero force; it is the minimum force that the Gripper can apply.`<br>`Minimum force: 15 N `<br>`Maximum force: 60 N `<br>`Force / count: 0.175 N (approximate value, relation non-linear)

---

### 6.7 FINGER B POSITION REQUEST

Address: Byte 6

| BIT | NAME | DESCRIPTION                                                                                  |
| --- | ---- | -------------------------------------------------------------------------------------------- |
| 0-7 | rPRB | Set Position Request for finger B.`<br>`0x00 (Minimum position) to 0xFF (Maximum position) |

This register is used to set the finger B target position. It is only considered if the Individual Control of Finger option is selected (bit rICF is set). Please refer to rPRA (position request) register for more information.

---

### 6.8 FINGER B SPEED

Address: Byte 7

| BIT | NAME | DESCRIPTION                                                                                |
| --- | ---- | ------------------------------------------------------------------------------------------ |
| 0-7 | rSPB | Set Grasping Speed for finger B.`<br>`0x00 (Minimum velocity) to 0xFF (Maximum velocity) |

This register is used to set finger B speed. It is only considered if the Individual Control of Finger option is selected (bit rICF is set). Please refer to rSPA (speed) register for more information.

---

### 6.9 FINGER B FORCE

Address: Byte 8

| BIT | NAME | DESCRIPTION                                                                          |
| --- | ---- | ------------------------------------------------------------------------------------ |
| 0-7 | rFRB | Set Gripping Force for finger B.`<br>`0x00 (Minimum force) to 0xFF (Maximum force) |

This register is used to set finger B force. It is only considered if the Individual Control of Finger option is selected (bit rICF is set). Please refer to rFRA (force) register for more information.

---

### 6.10 FINGER C POSITION REQUEST

Address: Byte 9

| BIT | NAME | DESCRIPTION                                                                                  |
| --- | ---- | -------------------------------------------------------------------------------------------- |
| 0-7 | rPRC | Set Position Request for finger C.`<br>`0x00 (Minimum position) to 0xFF (Maximum position) |

This register is used to set the finger C target position. It is only considered if the Individual Control of Finger option is selected (bit rICF is set). Please refer to rPRA (position request) register for more information.

---

### 6.11 FINGER C SPEED

Address: Byte 10

| BIT | NAME | DESCRIPTION                                                                                |
| --- | ---- | ------------------------------------------------------------------------------------------ |
| 0-7 | rSPC | Set Grasping Speed for finger C.`<br>`0x00 (Minimum velocity) to 0xFF (Maximum velocity) |

This register is used to set finger C speed. It is only considered if the Individual Control of Finger option is selected (bit rICF is set). Please refer to rSPA (speed) register for more information.

---

### 6.12 FINGER C FORCE

Address: Byte 11

| BIT | NAME | DESCRIPTION                                                                          |
| --- | ---- | ------------------------------------------------------------------------------------ |
| 0-7 | rFRC | Set Gripping Force for finger C.`<br>`0x00 (Minimum force) to 0xFF (Maximum force) |

This register is used to set finger C force. It is only considered if the Individual Control of Finger option is selected (bit rICF is set). Please refer to rFRA (force) register for more information.

---

### 6.13 SCISSOR POSITION REQUEST

Address: Byte 12

| BIT | NAME | DESCRIPTION                                                                                          |
| --- | ---- | ---------------------------------------------------------------------------------------------------- |
| 0-7 | rPRS | Set Position Request for the scissor axis.`<br>`0x00 (Minimum position) to 0xFF (Maximum position) |

This register is used to set the scissor axis target position. It is only considered if the Individual Control of Scissor option is selected (bit rICS is set). Please refer to rPRA (position request) register for more information.

---

### 6.14 SCISSOR SPEED

Address: Byte 13

| BIT | NAME | DESCRIPTION                                                                                        |
| --- | ---- | -------------------------------------------------------------------------------------------------- |
| 0-7 | rSPS | Set Grasping Speed for the scissor axis.`<br>`0x00 (Minimum velocity) to 0xFF (Maximum velocity) |

This register is used to set the scissor axis speed. It is only considered if the Individual Control of Scissor option is selected (bit rICS is set). Please refer to rSPA (speed) register for more information.

---

### 6.15 SCISSOR FORCE

Address: Byte 14

| BIT | NAME | DESCRIPTION                                                                                  |
| --- | ---- | -------------------------------------------------------------------------------------------- |
| 0-7 | rFRS | Set Gripping Force for the scissor axis.`<br>`0x00 (Minimum force) to 0xFF (Maximum force) |

This register is used to set the scissor axis force. It is only considered if the Individual Control of Scissor option is selected (bit rICS is set). Please refer to rFRA (force) register for more information.

## 7. 机器人输入寄存器 (Robot Input Registers)

> ⚠️ **Caution**
> 本节适用于固件版本 3.0（2011 年 11 月之后交付的夹爪）。对于早期版本，请参阅归档文档。

> ℹ️ **Info**
> 寄存器格式为小端序（Little Endian / Intel 格式），即从 LSB 到 MSB。

---

### 7.1 GRIPPER STATUS

Address: Byte 0

| BIT | NAME | DESCRIPTION                                                                                                                                                                                                                                                                                                                        |
| --- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0   | gACT | Initialization status (Echo of the rACT bit (Activation bit)):`<br>`0 – Gripper reset `<br>`1 – Gripper activation                                                                                                                                                                                                           |
| 1-2 | gMOD | Echo of the rMOD bits (Grasping Mode request)`<br>`00 – Basic Mode `<br>`10 – Pinch Mode `<br>`01 – Wide Mode `<br>`11 – Scissor Mode                                                                                                                                                                                  |
| 3   | gGTO | Echo of the rGTO bit (Go to bit):`<br>`0 – Stopped (or performing activation/grasping mode change/automatic release)`<br>`1 – Go to Position Request                                                                                                                                                                         |
| 4-5 | gIMC | 00 – Gripper is in reset (or automatic release) state. See Fault Status if Gripper is activated.`<br>`10 – Activation in progress.`<br>`01 – Mode change in progress.`<br>`11 – Activation and mode change are completed.                                                                                                |
| 6-7 | gSTA | 00 – Gripper is in motion towards requested position (only meaningful if gGTO = 1)`<br>`10 – Gripper is stopped. One or two fingers stopped before requested position `<br>`01 – Gripper is stopped. All fingers stopped before requested position `<br>`11 – Gripper is stopped. All fingers reached requested position |

---

### 7.2 OBJECT STATUS

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

### 7.3 FAULT STATUS

Address: Byte 2

| BIT | NAME | DESCRIPTION                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| --- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0-3 | gFLT | 0x00 – No Fault `<br><br>`**Priority Fault** `<br>`0x05 – Action delayed, activation (reactivation) must be completed prior to action `<br>`0x06 – Action delayed, mode change must be completed prior to action `<br>`0x07 – The activation bit must be set prior to action `<br><br>`**Minor Fault (red LED continuous)**`<br>`0x09 – The communication chip is not ready (may be booting)`<br>`0x0A – Changing mode fault, interferences detected on Scissor (for less than 20 sec)`<br>`0x0B – Automatic release in progress `<br><br>`**Major Fault (red LED blinking) – Reset is required** `<br>`0x0D – Activation fault, verify that no interference or other error occurred `<br>`0x0E – Changing mode fault, interferences detected on Scissor (for more than 20 sec)`<br>`0x0F – Automatic release completed. Reset and activation is required. |
| 4-7 | gRS1 | Reserved (zeros)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |

---

### 7.4 POSITION REQUEST ECHO (FINGER A)

Address: Byte 3

| BIT | NAME | DESCRIPTION                                                                                                                       |
| --- | ---- | --------------------------------------------------------------------------------------------------------------------------------- |
| 0-7 | gPRA | Echo of the requested position for the Gripper (or finger A in individual mode)`<br>`0x00 (Full Opening) to 0xFF (Full Closing) |

---

### 7.5 FINGER A POSITION

Address: Byte 4

| BIT | NAME | DESCRIPTION                                                             |
| --- | ---- | ----------------------------------------------------------------------- |
| 0-7 | gPOA | Position of Finger A `<br>`0x00 (Fully opened) to 0xFF (Fully closed) |

---

### 7.6 FINGER A CURRENT

Address: Byte 5

| BIT | NAME | DESCRIPTION                                        |
| --- | ---- | -------------------------------------------------- |
| 0-7 | gCUA | Current of Finger A `<br>`0.1 \* Current (in mA) |

---

### 7.7 FINGER B POSITION REQUEST ECHO

Address: Byte 6

| BIT | NAME | DESCRIPTION                                                                                    |
| --- | ---- | ---------------------------------------------------------------------------------------------- |
| 0-7 | gPRB | Echo of the requested position for finger B `<br>`0x00 (Full Opening) to 0xFF (Full Closing) |

---

### 7.8 FINGER B POSITION

Address: Byte 7

| BIT | NAME | DESCRIPTION                                                             |
| --- | ---- | ----------------------------------------------------------------------- |
| 0-7 | gPOB | Position of Finger B `<br>`0x00 (Fully opened) to 0xFF (Fully closed) |

---

### 7.9 FINGER B CURRENT

Address: Byte 8

| BIT | NAME | DESCRIPTION                                        |
| --- | ---- | -------------------------------------------------- |
| 0-7 | gCUB | Current of Finger B `<br>`0.1 \* Current (in mA) |

---

### 7.10 FINGER C POSITION REQUEST ECHO

Address: Byte 9

| BIT | NAME | DESCRIPTION                                                                                    |
| --- | ---- | ---------------------------------------------------------------------------------------------- |
| 0-7 | gPRC | Echo of the requested position for finger C `<br>`0x00 (Full Opening) to 0xFF (Full Closing) |

---

### 7.11 FINGER C POSITION

Address: Byte 10

| BIT | NAME | DESCRIPTION                                                             |
| --- | ---- | ----------------------------------------------------------------------- |
| 0-7 | gPOC | Position of Finger C `<br>`0x00 (Fully opened) to 0xFF (Fully closed) |

---

### 7.12 FINGER C CURRENT

Address: Byte 11

| BIT | NAME | DESCRIPTION                                        |
| --- | ---- | -------------------------------------------------- |
| 0-7 | gCUC | Current of Finger C `<br>`0.1 \* Current (in mA) |

---

### 7.13 SCISSOR POSITION REQUEST ECHO

Address: Byte 12

| BIT | NAME | DESCRIPTION                                                                                            |
| --- | ---- | ------------------------------------------------------------------------------------------------------ |
| 0-7 | gPRS | Echo of the requested position for the scissor axis `<br>`0x00 (Full Opening) to 0xFF (Full Closing) |

---

### 7.14 SCISSOR POSITION

Address: Byte 13

| BIT | NAME | DESCRIPTION                                                                     |
| --- | ---- | ------------------------------------------------------------------------------- |
| 0-7 | gPOS | Position of the scissor axis `<br>`0x00 (Fully opened) to 0xFF (Fully closed) |

---

### 7.15 SCISSOR CURRENT

Address: Byte 14

| BIT | NAME | DESCRIPTION                                                 |
| --- | ---- | ----------------------------------------------------------- |
| 0-7 | gCUS | Current for the scissor axis `<br>`0.1 \* Current (in mA) |

## 8. 控制逻辑流程示例 (Control Logic Flow)

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
  - **并且** `gSTA (Bit 6 & 7) == 3`（停止，所有手指到达设定位置），**或者** `gSTA == 1`（停止，所有手指均未到达设定位置——抓取到物体），**或者** `gSTA == 2`（停止，1-2根手指未到达设定位置——部分抓取到物体）。
  - 也可以通过 `Byte 1 (Object Status)` 中的 `gDTA/gDTB/gDTC` 位来更精确地判断每根手指是因接触物体而停止（01=闭合中接触, 10=张开中接触），还是已到达请求位置（11）。
- **完成**：重复步骤 3 和 4 进行下一个抓取/释放动作。

> ℹ️ **Info**
> `Go to requested position` 指令通常用于张开/闭合夹爪，直到夹爪检测到物体阻挡，或者到达请求的绝对位置为止。

## 9. Modbus RTU 通信 (Modbus RTU Communication)

### 9.1 连接设置 (Connection Setup)

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

### 9.2 读保持寄存器 FC03 (Read Holding Registers)

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

> ℹ️ **Note**
> 自适应夹爪寄存器值以200Hz的频率更新。因此，建议发送FC03命令的间隔不小于5ms。

### 9.3 预置单寄存器 FC06 (Preset Single Register)

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

### 9.4 预置多寄存器 FC16 (Preset Multiple Registers)

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

### 9.5 主站读写多寄存器 FC23 (Master Read&Write)

功能码23（FC23）用于同时读取夹爪状态（机器人输入）和激活夹爪功能（机器人输出），例如夹爪状态、物体状态、手指位置、动作请求（速度、力等）。

> ℹ️ **Note**
> C-Model示例仅作为S-Model的操作说明示例，控制方式和位寻址不相同，请参考C-Model指令手册获取详细示例。

### 9.6 Modbus RTU 完整示例 (Pick & Place)

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

---

## 附录 A: 关键规格参数速查 (Key Specifications)

### 机械参数

| 规格                            | 数值        |
| :------------------------------ | :---------- |
| 夹爪最大开度 (Stroke)           | 0 – 155 mm |
| 夹爪大约重量                    | 2.3 kg      |
| 推荐负载 (包裹抓取)             | 10 kg       |
| 推荐负载 (指尖抓取)             | 2.5 kg      |
| 指尖最大抓取力                  | 60 N        |
| 最大抗破坏力 (Break Away Force) | 100 N       |
| 手指最大闭合速度                | 110 mm/s    |

> ℹ️ **Info**
>
> - **Actuation Force (驱动力)**：夹爪电机可施加在物体上的力。
> - **Break Away Force (抗破坏力)**：夹爪可承受的最大外力。由于夹爪自锁，抗破坏力高于驱动力。
> - 在 Pinch 模式下，手指 B 和 C 会对手指 A 施力，由于手指 A 被锁定，Pinch 驱动力 = 20 + 20 = 40 N。

### 电气参数

| 规格                         | 数值                   |
| :--------------------------- | :--------------------- |
| 工作电源电压                 | 24 V DC                |
| 绝对最大电源电压             | 26 V                   |
| 静态功耗 (最小)              | 4.1 W                  |
| 峰值功耗 (最大抓取力时)      | 36 W                   |
| 最大 RMS 电源电流 (24V 供电) | 1.5 A                  |
| 外部保险丝                   | 4 A (慢熔，由用户自备) |

> ⚠️ **Caution**
> 夹爪必须由 24V DC 电源供电，不可使用交流电源。外部 4A 保险丝不随夹爪提供，用户需自行安装。

### 环境条件

| 规格              | 数值           |
| :---------------- | :------------- |
| 工作温度范围      | -10°C ~ 50°C |
| 存储/运输温度范围 | -30°C ~ 60°C |
| 湿度 (无冷凝)     | 20% – 80% RH  |
| 振动              | < 0.5 G        |

---

## 附录 B: 故障排除 (Troubleshooting)

### LED 指示灯诊断流程

按照以下顺序检查三颗 LED 指示灯来定位问题：

### Step 1: 检查蓝色 Supply LED

| 状态     | 判断       | 处理                                                                    |
| :------- | :--------- | :---------------------------------------------------------------------- |
| 亮 (ON)  | 供电正常   | 进入 Step 2                                                             |
| 灭 (OFF) | 夹爪未供电 | 检查电源线完整性，检查电源是否符合规格（24V DC, ≥36W），检查外部保险丝 |

### Step 2: 检查绿色 Communication LED

| 状态            | 判断                     | 处理                                                        |
| :-------------- | :----------------------- | :---------------------------------------------------------- |
| 亮 (ON)         | 网络已检测，连接已建立   | 进入 Step 3                                                 |
| 闪烁 (Blinking) | 网络已检测，但未建立连接 | 进入 Step 4                                                 |
| 灭 (OFF)        | 未检测到网络             | 检查通信线缆和网络基础设施（参见具体协议章节），进入 Step 4 |

### Step 3: 检查红色 Fault LED

| 状态            | 判断                          | 处理                           |
| :-------------- | :---------------------------- | :----------------------------- |
| 灭 (OFF)        | 无故障                        | 进入 Step 5                    |
| 闪烁 (Blinking) | 发生严重故障 (Major Fault)    | 复位（重新激活）夹爪           |
| 亮 (ON)         | 轻微故障（或自动释放/启动中） | 等待熄灭；如果转为闪烁则需复位 |

### Step 4: 通信与网络问题

- 确保同一时间只使用一种连接（USB 或工业协议）
- **Ethernet 系列 (EtherNet/IP, Modbus TCP)**：使用正确 IP 设置（固定 IP），EtherCAT 需 DHCP
- **DeviceNet**：需要独立的 24V 电源供电（与夹爪主电源分开），MAC ID 默认为 11，波特率 250 kBaud
- **CANopen**：MAC ID 默认为 11，波特率 1 MBaud
- 主站通信设备必须使用与夹爪控制器相同的协议和选项设置
- 重新编程通信选项后，等待红色 LED 停止闪烁以完成配置更新

### Step 5: 其他常见问题

| 问题                            | 可能原因                | 解决方案                                                                                      |
| :------------------------------ | :---------------------- | :-------------------------------------------------------------------------------------------- |
| 夹爪激活时断电（蓝色 LED 熄灭） | 电源功率不足            | 检查电源是否满足最低要求（24V, 36W），电压不超过 26V                                          |
| 夹爪不响应运动指令              | 未激活或 rGTO 未置位    | 确保夹爪已激活（rACT=1），发送位置请求时确保 rGTO=1                                           |
| 无法建立 Ethernet 连接          | IP 地址或协议设置不匹配 | 默认 IP: 192.168.1.11, 网关: 255.255.255.0。通过 USB 使用 Robotiq User Interface 查看当前地址 |
| 无法建立 CAN bus 连接           | 供电或节点地址问题      | DeviceNet 需独立 24V 供电；默认节点地址均为 11                                                |
| 手指运动不流畅/抖动             | 杂物或碎屑堵塞          | 清洁夹爪，确保手指指骨和连杆之间无杂物或液体                                                  |
| 抓取力明显变化                  | 指垫脏污或磨损          | 清洁指垫，检查磨损情况。注意包裹抓取力始终大于指尖抓取力                                      |

> ⚠️ **Warning**
> 如果系统在夹爪激活时断电，务必检查电源。电源必须满足最低要求：24V 下至少 36W（1.5A），且工作电压不得超过 26V。

---

## 附录 C: 各通信协议出厂默认设置 (Factory Default Communication Settings)

夹爪出厂时仅配置一种通信协议。不同协议的默认设置如下：

### Modbus RTU (RS232 串口)

| 参数               | 默认值        |
| :----------------- | :------------ |
| 物理接口           | RS232         |
| 波特率             | 115,200 bps   |
| 数据位             | 8             |
| 停止位             | 1             |
| 校验               | None          |
| 从站 ID (Slave ID) | 0x0009 (9)    |
| 机器人输出首寄存器 | 0x03E8 (1000) |
| 机器人输入首寄存器 | 0x07D0 (2000) |

### Modbus TCP

| 参数               | 默认值        |
| :----------------- | :------------ |
| 协议               | TCP/IP        |
| 端口               | 502           |
| IP 地址            | 192.168.1.11  |
| 子网掩码           | 255.255.255.0 |
| 网关               | Disabled      |
| DHCP               | Disabled      |
| Unit ID            | 0x0002 (2)    |
| 机器人输出首寄存器 | 0x0000 (0)    |
| 机器人输入首寄存器 | 0x0000 (0)    |

> ℹ️ **Info**
> Modbus TCP 寄存器更新频率为 **100Hz**，建议命令间隔 ≥ **10ms**。Modbus RTU 更新频率为 200Hz，建议间隔 ≥ 5ms。

### EtherNet/IP

| 参数                             | 默认值          |
| :------------------------------- | :-------------- |
| IP 地址                          | 192.168.1.11    |
| 子网掩码                         | 255.255.255.0   |
| 网关                             | Disabled        |
| BootP / DHCP                     | Disabled        |
| 100Mbit / Full Duplex / Auto-neg | Enabled         |
| Assembly Instance (Input)        | 101             |
| Assembly Instance (Output)       | 100             |
| Configuration Instance           | 1               |
| Connection Type                  | Run/Idle Header |
| Prod. Data Length                | 20 bytes        |
| Cons. Data Length                | 20 bytes        |

### EtherCAT

| 参数              | 默认值                        |
| :---------------- | :---------------------------- |
| 寻址              | 动态寻址 (总线设置不可自定义) |
| Vendor ID         | 0x0000FFFF                    |
| Product Code      | 0x0000000B                    |
| Input Data Bytes  | 16                            |
| Output Data Bytes | 16                            |

### DeviceNet

| 参数              | 默认值           |
| :---------------- | :--------------- |
| MAC ID            | 11               |
| 波特率            | 250 kBaud        |
| Vendor ID         | 0x0000011B (283) |
| Product Code      | 0x00000023 (35)  |
| Product Type      | 0x0000000C (12)  |
| Prod. Data Length | 16 bytes         |
| Cons. Data Length | 16 bytes         |

> ⚠️ **Caution**
>
> - 夹爪内部**没有**安装终端电阻。
> - 电缆屏蔽层必须在机器人控制器端接地。
> - DeviceNet 通信需要**独立的 24V 供电**，建议与夹爪主电源分开供电。

### CANopen

| 参数                 | 默认值               |
| :------------------- | :------------------- |
| MAC ID (Node ID)     | 11                   |
| 波特率               | 1 MBaud              |
| Vendor ID            | 0x00000044 (68)      |
| Product Code         | 0x001785A4 (1541540) |
| Revision Number      | 0x00020000 (131072)  |
| Send Object Index    | 0x2000               |
| Receive Object Index | 0x2200               |

> ℹ️ **Info**
> CANopen 通信接口支持 SDO (Service Data Object) 和 PDO (Process Data Object) 协议。

> ⚠️ **Caution**
> 夹爪内部**没有**安装终端电阻。电缆屏蔽层必须在机器人控制器端接地。
