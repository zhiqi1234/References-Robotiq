快速说明

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 填写寄存器映射

打开 `robotiq_modbus.py` 或在 `example_safe_control.py` 中的 `reg_map`，把手册（User_Interface_PDF_20210813.pdf）中对应的寄存器地址填入：

- `activate`：激活写寄存器
- `go`：触发动作寄存器
- `position`：目标位置寄存器
- `speed`：速度寄存器
- `stop`：停止寄存器
- `status`：状态寄存器
- `emergency`：急停寄存器（若有）

3. 运行示例

```bash
python example_safe_control.py --ip 192.168.1.10 --cmd open
```

示例：使用 JSON 寄存器映射文件

```bash
python example_safe_control.py --ip 192.168.1.10 --cmd open --reg-file regs.json
```

`regs.json` 应为类似内容：

```json
{
  "activate": 1,
  "go": 2,
  "position": 16,
  "speed": 17,
  "stop": 32,
  "status": 48,
  "emergency": 255
}
```

常见安全建议

- 在上电或连接前确保机械臂/夹爪无人员接近。
- 使用 `--dry-run` 测试脚本流程。
- 在实际部署前先在低速/空载条件下验证动作。

如果你希望，我可以：

- 从你提供的 PDF 中解析并填充寄存器地址。
- 根据你已有的寄存器地址把脚本默认映射替换成正确值。
- 为后续与机械臂（UR-like）集成给出桥接建议和示例。
