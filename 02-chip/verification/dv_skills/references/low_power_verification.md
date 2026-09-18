# 低功耗验证指南（Low Power Verification）

## 概述

低功耗设计是现代芯片设计的重要考量。本文档介绍常见的低功耗设计技术和验证方法。

## 低功耗设计技术

### 功耗类型

| 类型 | 描述 | 降低方法 |
|------|------|---------|
| 动态功耗 | 开关活动和充放电 | 时钟门控、频率调节 |
| 短路功耗 | NMOS/PMOS短暂导通 | 减少transition time |
| 泄漏功耗 | 亚阈值/栅极泄漏 | 多阈值、功率门控 |
| IO功耗 | 外部接口 | 低电压IO |

### 主要低功耗技术

```
低功耗技术
├── 多电压设计 (Multi-Voltage)
│   ├── 电压域划分
│   └── 电压调节 (DVFS)
│
├── 逻辑门控 (Clock Gating)
│   ├── 组合门控
│   └── 时序门控
│
├── 功率门控 (Power Gating)
│   ├── 浅睡眠
│   └── 深睡眠
│
├── 存储器优化
│   ├── 多个bank
│   └── 门控clock/ power
│
└── 版图优化
    ├── 单元布局
    └── 互连优化
```

## 低功耗架构

### 电压域划分

```
典型SoC电压域
├── VDD_CPU (0.8V - 1.2V)
│   └── CPU cores
├── VDD_GPU (0.7V - 1.0V)
│   └── GPU
├── VDD_LOGIC (1.0V)
│   └── 数字逻辑
├── VDD_MEM (1.2V)
│   └── 存储器
└── VDD_IO (3.3V/1.8V)
    └── I/O接口
```

### 电源关断架构

```
Power Domain架构
┌─────────────────────────────────────┐
│ Always-On Domain (VDD_AON)          │
│  ├── Always-on logic                │
│  ├── Retention registers            │
│  └── Wake-up logic                  │
├─────────────────────────────────────┤
│ Switchable Domain (VDD_SW)          │
│  ├── Main logic                     │
│  ├── Retention registers            │
│  └── Isolation cells               │
└─────────────────────────────────────┘
         │              │
         ▼              ▼
    ┌────────┐    ┌────────┐
    │Switch  │    │Switch  │
    │(ON/OFF)│    │(ON/OFF)│
    └────────┘    └────────┘
```

## UPF/CPF功耗意图描述

### UPF基本概念

```upf
# UPF 2.0示例
set_design top

# 创建电压域
create_power_domain -name PD_CPU -domain top
create_power_domain -name PD_GPU -domain top -parent PD_CPU

# 指定电源
create_supply_port VDD_CPU -direction in
create_supply_port VDD_GPU -direction in
create_supply_port VSS -direction in

# 创建电源网络
connect_supply_net VDD_CPU -ports {VDD_CPU}
connect_supply_net VDD_GPU -ports {VDD_GPU}
connect_supply_net VSS -ports {VSS}

# 为电源域供电
associate_power_supply -power VDD_CPU -ground VSS -domain PD_CPU

# 功率门控
create_power_switch -name SW_CPU \
    -domain PD_CPU \
    -input_supply_port {VDD_CPU VDD_CPU} \
    -output_supply_port {VDD_SW VDD_SW} \
    -control_port {CPU_PWRON CPU_PWRON} \
    -on_state {ON_STATE VDD_CPU -lib_cell AON} \
    -off_state {OFF_STATE}
```

## 低功耗验证要点

### 1. 功耗状态机（PSM）验证

```verilog
// 功耗状态枚举
typedef enum bit [2:0] {
    PSTATE_ACTIVE  = 3'b000,
    PSTATE_IDLE    = 3'b001,
    PSTATE_RET     = 3'b010,  // Retention
    PSTATE_PD      = 3'b100,  // Power Down
    PSTATE_SREF    = 3'b111   // Self Refresh
} power_state_e;

// 功耗状态转换验证
property psm_trans_active_to_idle;
    @(posedge clk) disable iff (!rst_n)
    (current_state == ACTIVE) && enter_idle 
        |-> ##[1:$] (next_state == IDLE);
endproperty

property psm_trans_idle_to_retention;
    @(posedge clk) disable iff (!rst_n)
    (current_state == IDLE) && enter_retention
        |-> ##[1:$] (next_state == RETENTION);
endproperty

// 禁止的转换
property psm_no_direct_trans;
    @(posedge clk)
    // 不能从ACTIVE直接到POWER_DOWN
    (current_state == ACTIVE) && (next_state == POWER_DOWN)
        |-> (error_flag == 1);
endproperty
```

### 2. Isolation Cell验证

```verilog
// Isolation Cell检查
// 当电源域关断时，输出必须被隔离

property isolation_when_powered_off;
    @(posedge clk)
    // 当PD_CPU关闭时
    (PD_CPU.power_enable == 0) 
        |=>
        // CPU输出被隔离
        (cpu_to_gpu signal within {1'b0, 1'b1, 1'bz});
endproperty

// Isolation方向检查
// 输入隔离：A岛关断时，输出给B岛的信号需要隔离
// 输出隔离：B岛关断时，来自B岛的信号需要隔离

property output_isolation_check;
    @(posedge clk)
    // 当VDD_CPU关闭时
    !power_enable |-> 
        // 输出保持稳定值（isolation值）
        (iso_out == iso_value);
endproperty
```

### 3. Retention寄存器验证

```verilog
// Retention寄存器检查
// 进入Retention前，数据必须被保存
// 退出Retention后，数据必须被恢复

property retention_save_sequence;
    @(posedge clk) disable iff (!rst_n)
    // 进入Retention命令
    (enter_retention_cmd) 
        |=>
        // SAVE信号必须拉高
        (SAVE == 1) 
        ##[1:3] 
        // 然后进入Retention
        (state == RETENTION);
endproperty

property retention_restore_sequence;
    @(posedge clk) disable iff (!rst_n)
    // 退出Retention命令
    (exit_retention_cmd) 
        |=>
        // RESTORE信号必须拉高
        (RESTORE == 1) 
        ##[1:3] 
        // 然后恢复正常
        (state == ACTIVE);
endproperty

// Retention数据完整性
property retention_data_integrity;
    @(posedge clk)
    // 在Retention前后，寄存器的值必须一致
    (PREV_STATE == ACTIVE) && (NEXT_STATE == ACTIVE) 
        && (SAVE_EDGE) && (RESTORE_EDGE)
        |->
        (reg_value_before_save == reg_value_after_restore);
endproperty
```

### 4. Level Shifter验证

```verilog
// Level Shifter检查
// 不同电压域之间需要Level Shifter

// 当电压域切换时，Level Shifter必须正确工作
property level_shifter_correct;
    @(posedge clk)
    // A域电压切换到高电压
    (domain_A.voltage == HIGH) && (domain_A.voltage_transition)
        |->
        // Level Shifter输出必须在指定时间内稳定
        ##[0:LS_T propagation_delay]
        (domain_B.input signal stable);
endproperty
```

### 5. 时钟门控验证

```verilog
// 时钟门控检查
// 当时钟被门控后，逻辑应该处于静止状态

property clock_gating_functional;
    @(posedge clk) disable iff (!rst_n)
    // 时钟门控信号有效
    (clock_gate_enable == 1)
        |->
        // 内部节点不应该toggle
        (^internal_toggling_nodes) == 0;
endproperty

// 时钟门控使能检查
property clock_gate_enable_correct;
    @(posedge clk)
    // 门控使能时，时钟应该被关断
    (gate_enable) |-> (gated_clock == 0);
    
    // 门控禁用时，时钟应该正常
    (!gate_enable) |-> (gated_clock == clk);
endproperty
```

### 6. Wake-up验证

```verilog
// Wake-up序列检查
property wake_up_sequence;
    @(posedge wake_up_interrupt)
    // Wake-up中断触发
    disable iff (!rst_n)
    
    // 唤醒时间必须在规定范围内
    (wake_up_interrupt == 1)
        ##[min_wake_up_cycles:max_wake_up_cycles]
        // 系统恢复到正常工作状态
        (system_state == ACTIVE);
endproperty

// Wake-up期间的毛刺检查
property wake_up_glitch_free;
    @(posedge clk)
    // Wake-up过程中，不应该有非法转换
    during_wake_up |-> 
        !glitch_detected;
endproperty
```

## 低功耗测试用例

### 1. 基本功耗状态切换

```verilog
class low_power_basic_seq extends uvm_sequence;
    task body();
        // Active -> Idle
        test_active_to_idle();
        
        // Idle -> Active
        test_idle_to_active();
        
        // Idle -> Retention
        test_idle_to_retention();
        
        // Retention -> Active
        test_retention_to_active();
    endtask
endclass
```

### 2. 完整电源关断序列

```verilog
class power_down_seq extends uvm_sequence;
    task body();
        // 1. 确保没有挂起的操作
        wait_idle();
        
        // 2. 保存Retention数据
        send_save_command();
        wait(save_done);
        
        // 3. 隔离输出
        enable_output_isolation();
        
        // 4. 关断时钟
        disable_clock();
        
        // 5. 关断电源
        power_down_domain();
        
        // 6. 验证电源已关断
        verify_domain_powered_off();
    endtask
endclass

class power_up_seq extends uvm_sequence;
    task body();
        // 1. 开启电源
        power_up_domain();
        
        // 2. 等待电源稳定
        wait_power_stable();
        
        // 3. 恢复时钟
        enable_clock();
        
        // 4. 禁用Isolation
        disable_output_isolation();
        
        // 5. 恢复Retention数据
        send_restore_command();
        wait(restore_done);
        
        // 6. 验证恢复完成
        verify_domain_functional();
    endtask
endclass
```

### 3. DVFS验证

```verilog
class dvfs_sequence extends uvm_sequence;
    // 电压/频率对
    bit [15:0] voltage_levels[] = '{ 800, 700, 600, 500 };  // mV
    bit [15:0] freq_levels[]   = '{2000, 1800, 1200, 800}; // MHz
    
    task body();
        // 从高频高压开始
        for (int i = 0; i < voltage_levels.size(); i++) begin
            // 设置电压
            set_voltage(voltage_levels[i]);
            
            // 等待电压稳定
            wait_voltage_stable();
            
            // 设置频率
            set_frequency(freq_levels[i]);
            
            // 验证功能正常
            verify_operation();
        end
    endtask
endclass
```

## 低功耗验证Checklist

### 架构设计
- [ ] 电源域划分合理
- [ ] Always-on域包含关键逻辑
- [ ] Isolation cell数量和位置正确
- [ ] Retention寄存器规划

### 功耗状态机
- [ ] 所有状态转换路径覆盖
- [ ] 禁止的转换被正确阻止
- [ ] 状态转换时间符合规范
- [ ] 状态编码正确

### Isolation
- [ ] 所有跨域信号有Isolation
- [ ] Isolation值正确（0/1/保持）
- [ ] Isolation timing正确

### Retention
- [ ] SAVE/RESTORE序列正确
- [ ] Retention数据完整性
- [ ] 恢复后的状态正确

### Level Shifter
- [ ] 跨电压域信号有Level Shifter
- [ ] 方向正确（双向/单向）
- [ ] 延迟在范围内

### 时钟门控
- [ ] 功能正确性
- [ ] 无毛刺
- [ ] 功耗节省效果

### Wake-up
- [ ] Wake-up时间符合规范
- [ ] Wake-up后状态恢复
- [ ] 无数据丢失
- [ ] 无毛刺/异常

### DVFS
- [ ] 电压/频率匹配
- [ ] 电压稳定后再调频
- [ ] 频率变化时序正确
- [ ] 功能在所有PVT下正常

## 工具与技术

### 静态检查
- UPF/CPF语法检查
- 功耗意图完整性检查
- Isolation连接性检查
- Retention寄存器检查

### 动态验证
- 功耗状态机覆盖
- 时序仿真
- 低功耗UPF感知仿真
- 功耗计算

### 形式验证
- 状态机等价性
- Isolation完整性
- Retention正确性

## 总结

低功耗验证核心要点：

1. **理解架构** - 电压域、功率门控、Isolation设计
2. **验证意图** - UPF/CPF描述的功耗意图是否正确实现
3. **覆盖完整** - 所有功耗状态和转换路径
4. **时序正确** - 状态切换序列、保持时间
5. **数据完整** - Retention数据不丢失
6. **功能正确** - Wake-up后系统正常工作
