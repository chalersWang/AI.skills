# 边界值分析示例（Boundary Value Analysis Examples）

## 概述

本文档提供芯片验证中边界值分析的实战示例，包括常见接口、寄存器和协议的边界测试点。

## 1. 寄存器边界测试

### 1.1 时钟分频寄存器

```verilog
// 时钟分频寄存器
// 配置范围: 1 - 1000
// 边界值: 0, 1, 2, 999, 1000, 1001

class clk_div_boundary_test extends uvm_sequence;
    `uvm_object_utils(clk_div_boundary_test)
    
    // 边界测试点定义
    bit [31:0] test_points[] = '{
        32'h0000_0000,  // 0 - 无效（越界）
        32'h0000_0001,  // 1 - 最小有效值
        32'h0000_0002,  // 2 - min+1
        32'h0000_03E7,  // 999 - max-1
        32'h0000_03E8,  // 1000 - 最大有效值
        32'h0000_03E9   // 1001 - 越界
    };
    
    task body();
        foreach (test_points[i]) begin
            `uvm_do_with(req, {
                req.addr == CLK_DIV_REG;
                req.data == test_points[i];
                req.kind == REG_WRITE;
            })
        end
    endtask
endclass
```

### 1.2 32位计数器溢出

```verilog
// 32位计数器边界测试
// 范围: 0 - 4,294,967,295 (2^32 - 1)

class counter_boundary_test extends uvm_sequence;
    `uvm_object_utils(counter_boundary_test)
    
    bit [31:0] boundary_values[] = '{
        32'h0000_0000,  // 最小值
        32'h0000_0001,  // min+1
        32'h7FFF_FFFF,  // 正数最大 (2^31 - 1)
        32'h8000_0000,  // 负数最小 (2^31)
        32'hFFFF_FFFE,  // max-1
        32'hFFFF_FFFF   // 最大值 (溢出点)
    };
    
    task body();
        // 预设计数器到各边界值附近
        foreach (boundary_values[i]) begin
            preset_counter(boundary_values[i]);
            #100;
            trigger_increment();
            #100;
            check_counter_value(i);
        end
    endtask
endclass
```

## 2. AXI接口边界测试

### 2.1 AXI4突发长度边界

```verilog
// AXI4突发长度: 1 - 256
// 注意: AWLEN[7:0] = burst_length - 1

class axi_burst_len_boundary extends uvm_sequence;
    `uvm_object_utils(axi_burst_len_boundary)
    
    // 边界测试点
    bit [7:0] test_awlen[] = '{
        8'h00,   // 突发长度1 - 最小
        8'h01,   // 突发长度2 - min+1
        8'h0F,   // 突发长度16
        8'hFF,   // 突发长度256 - 最大
        8'hFE,   // 突发长度255 - max-1
        8'h00,   // 再次测试最小
    };
    
    task body();
        foreach (test_awlen[i]) begin
            `uvm_do_with(wr_seq, {
                wr_seq.awlen == test_awlen[i];
                wr_seq.awsize == 3'b010;  // 4字节
                wr_seq.awburst == 2'b01;   // INCR
            })
        end
    endtask
endclass
```

### 2.2 AXI地址对齐边界

```verilog
// AXI地址对齐要求
// 0x0: 1字节对齐
// 0x1: 2字节对齐 (需2字节传输)
// 0x2: 4字节对齐 (需4字节传输)
// 0x3: 8字节对齐 (需8字节传输)

class axi_addr_align_boundary extends uvm_sequence;
    `uvm_object_utils(axi_addr_align_boundary)
    
    struct {
        bit [31:0] addr;
        bit [2:0]  size;
        string     desc;
    } test_cases[] = '{
        '{32'h0000_0000, 3'b000, "1B aligned"},
        '{32'h0000_0001, 3'b001, "2B aligned"},
        '{32'h0000_0003, 3'b010, "4B aligned"},
        '{32'h0000_0007, 3'b011, "8B aligned"},
        '{32'h0000_000F, 3'b000, "Misaligned - 1B"},
        '{32'h0000_0010, 3'b010, "4B aligned on 16"},
        '{32'hFFFF_FFFC, 3'b010, "4B aligned - high addr"}
    };
    
    task body();
        foreach (test_cases[i]) begin
            `uvm_info("BVA", $sformatf("Testing: %s", test_cases[i].desc), UVM_MEDIUM)
            `uvm_do_with(wr_seq, {
                wr_seq.awaddr == test_cases[i].addr;
                wr_seq.awsize  == test_cases[i].size;
            })
        end
    endtask
endclass
```

## 3. I2C协议边界测试

```verilog
// I2C时钟频率边界
// 标准模式: 100kHz
// 快速模式: 400kHz
// 快速模式+: 1MHz
// 高速模式: 3.4MHz

class i2c_speed_boundary extends uvm_sequence;
    `uvm_object_utils(i2c_speed_boundary)
    
    struct {
        int freq;
        string mode;
        time t_low_min;
        time t_high_min;
    } test_cases[] = '{
        '{ 100_000, "Standard", 4.7us, 4.0us},
        '{ 400_000, "Fast",     1.3us, 0.6us},
        '{   1_000_000, "Fast+",  0.5us, 0.26us},
        '{   3_400_000, "High",    0.12us, 0.09us}
    };
    
    task body();
        foreach (test_cases[i]) begin
            set_i2c_clock(test_cases[i].freq);
            `uvm_do_with(i2c_seq, {
                i2c_seq.t_low  >= test_cases[i].t_low_min;
                i2c_seq.t_high >= test_cases[i].t_high_min;
            })
        end
    endtask
endclass
```

## 4. DDR内存边界测试

```verilog
// DDR地址边界测试

class ddr_addr_boundary_test extends uvm_sequence;
    `uvm_object_utils(ddr_addr_boundary_test)
    
    // 假设DDR范围: 0x0000_0000 - 0xFFFF_FFFF
    bit [31:0] addr_boundaries[] = '{
        32'h0000_0000,  // DDR起始地址
        32'h0000_0001,  // 第一个有效地址
        32'h1000_0000,  // 256MB边界
        32'h2000_0000,  // 512MB边界
        32'h4000_0000,  // 1GB边界
        32'h8000_0000,  // 2GB边界
        32'hC000_0000,  // 3GB边界
        32'hFF00_0000,  // 高地址区
        32'hFFFF_FFF0,  // 接近最大地址
        32'hFFFF_FFFF   // DDR结束地址
    };
    
    task body();
        // 全地址边界扫描
        foreach (addr_boundaries[i]) begin
            `uvm_do_with(mem_seq, {
                mem_seq.addr == addr_boundaries[i];
                mem_seq.size == 64;  // 64字节突发
            })
        end
        
        // 跨行边界测试 (DDR行为边界)
        test_bank_boundary();
        test_row_boundary();
        test_col_boundary();
    endtask
    
    task test_bank_boundary();
        // DDR4: 4个bank，bank边界切换
        bit [31:0] bank_test_addrs[] = '{
            32'h0000_0000,  // Bank0
            32'h0001_0000,  // Bank1
            32'h0002_0000,  // Bank2
            32'h0003_0000   // Bank3
        };
    endtask
endclass
```

## 5. 协议状态机边界

```verilog
// 协议状态机边界测试

enum {IDLE, SETUP, ACTIVE, PAUSE, DONE, ERROR} state_t;

// 状态机边界测试
class state_machine_boundary_test extends uvm_sequence;
    `uvm_object_utils(state_machine_boundary_test)
    
    state_t state_transitions[][] = '{
        {IDLE, SETUP},      // 正常启动
        {SETUP, ACTIVE},    // 正常激活
        {ACTIVE, PAUSE},    // 正常暂停
        {PAUSE, ACTIVE},    // 恢复
        {ACTIVE, DONE},     // 正常完成
        {IDLE, ERROR},      // 错误启动
        {SETUP, ERROR},     // 错误配置
        {ACTIVE, ERROR},    // 运行错误
        {PAUSE, ERROR},     // 暂停错误
        {ERROR, IDLE},      // 错误恢复
        {ERROR, ACTIVE},    // 错误后重试
        {DONE, IDLE}        // 重新开始
    };
    
    task body();
        // 测试所有状态转换
        foreach (state_transitions[i]) begin
            force_state(state_transitions[i][0]);
            #10;
            send_trigger();
            #10;
            check_state(state_transitions[i][1]);
        end
        
        // 测试非法转换
        test_illegal_transitions();
    endtask
    
    task test_illegal_transitions();
        state_t illegal_trans[][] = '{
            {IDLE, ACTIVE},     // 跳过SETUP
            {IDLE, PAUSE},      // 跳过前置状态
            {DONE, ACTIVE},     // 完成后的非法激活
            {DONE, PAUSE},      // 完成后的非法暂停
            {ERROR, SETUP}      // 错误后跳过IDLE
        };
        
        foreach (illegal_trans[i]) begin
            force_state(illegal_trans[i][0]);
            send_trigger();
            #10;
            // 期望进入ERROR状态或保持原状态
            check_illegal_behavior(illegal_trans[i][0]);
        end
    endtask
endclass
```

## 6. 数据边界测试

### 6.1 有符号数边界

```verilog
// 有符号数8位边界: -128 到 127
class int8_boundary_test extends uvm_sequence;
    `uvm_object_utils(int8_boundary_test)
    
    bit signed [7:0] test_values[] = '{
        -128,  // 最小值 8'h80
        -127,  // min+1
        -1,    // 负一
        0,     // 零
        1,     // 正一
        126,   // max-1
        127    // 最大值 8'h7F
    };
    
    // 溢出边界
    bit [7:0] overflow_test[] = '{
        8'h7F,  // 正数最大 + 1 = 溢出
        8'h80,  // 负数最小 - 1 = 下溢
        8'hFF   // 全1边界
    };
endclass
```

### 6.2 浮点数边界

```verilog
// IEEE 754 单精度浮点数边界
class float32_boundary_test extends uvm_sequence;
    `uvm_object_utils(float32_boundary_test)
    
    bit [31:0] test_patterns[] = '{
        32'h0000_0000,  // +0
        32'h8000_0000,  // -0
        32'h7F7F_FFFF,  // 最大正数 (~3.4e38)
        32'hFF7F_FFFF,  // 最小负数
        32'h0080_0000,  // 最小正规格化数 (~1.2e-38)
        32'h0000_0001,  // 最小正非规格化数
        32'h7F80_0000,  // +Infinity
        32'hFF80_0000,  // -Infinity
        32'h7FC0_0000,  // NaN
        32'h0000_8000   // 最小正数
    };
endclass
```

## 7. 边界值分析Checklist

### 通用边界
- [ ] 最小值 (min)
- [ ] 最大值 (max)
- [ ] min - 1 (越界下溢)
- [ ] max + 1 (越界上溢)
- [ ] 零值 (0)
- [ ] 负数最小值
- [ ] 典型值 (typ)

### 数值边界
- [ ] 有符号/无符号边界
- [ ] 2的幂边界 (2^n, 2^n-1)
- [ ] 溢出/下溢点
- [ ] 精度截断点

### 协议边界
- [ ] 协议规定的最大值
- [ ] 协议规定的最小值
- [ ] 时序约束临界点
- [ ] 突发长度限制

### 时序边界
- [ ] 建立时间 (setup time)
- [ ] 保持时间 (hold time)
- [ ] 传播延迟
- [ ] 时钟域切换

### 资源边界
- [ ] FIFO满/空边界
- [ ] 缓冲区边界
- [ ] 内存地址边界
- [ ] 带宽限制边界

## 总结

边界值分析的关键点：
1. **全面识别边界** - 规格、协议、物理三个维度
2. **科学选取测试点** - min, max, min±1, max±1, typ
3. **覆盖越界行为** - 测试越界时的错误处理
4. **组合边界** - 多边界条件组合产生Corner case
5. **迭代完善** - 根据测试结果持续补充边界点
