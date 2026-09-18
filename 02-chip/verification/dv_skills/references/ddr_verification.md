# DDR验证指南（DDR Verification）

## 概述

DDR（Double Data Rate） SDRAM是现代SoC中广泛使用的存储接口。本文档覆盖DDR/LPDDR/GDDR/HBM的验证要点。

## DDR家族

```
DDR演进
├── SDR (Single Data Rate)
├── DDR1 (DDR-200/266/333/400)
├── DDR2 (DDR2-400/533/667/800)
├── DDR3 (DDR3-800/1066/1333/1600/1866)
├── DDR4 (DDR4-2133/2400/2666/3200)
├── DDR5 (DDR5-4800/5200/6400)
│
├── LPDDR (Low Power DDR)
│   ├── LPDDR1/2/3
│   ├── LPDDR4 (32-bit DQ bus)
│   └── LPDDR5 (64-bit DQ bus)
│
├── GDDR (Graphics DDR)
│   ├── GDDR3/4/5/5X/6
│   └── 用于GPU
│
└── HBM (High Bandwidth Memory)
    ├── HBM1/2/3/3E
    └── 堆叠封装，3D互连
```

## DDR架构

```
DDR系统架构
├── DDR Controller
│   ├── AXI/APB接口
│   ├── 命令调度
│   ├── 刷新管理
│   └── PHY接口 (DFI)
│
├── DDR PHY
│   ├── 时钟驱动
│   ├── 数据对齐
│   └── 阻抗匹配
│
└── DDR Device
    ├── Bank Group
    ├── Bank
    ├── Row/Column
    └── DRAM Array
```

## DDR命令与时序

### 基本命令

```verilog
// DDR命令类型
typedef enum bit [3:0] {
    ACT   = 4'b0011,  // Row激活
    PRE   = 4'b0100,  // 预充电
    PREA  = 4'b0101,  // 全-bank预充电
    REF   = 4'b1000,  // 刷新
    MRS   = 4'b1100,  // 模式寄存器设置
    WR    = 4'b1101,  // 写
    RD    = 4'b1010,  // 读
    NOP   = 4'b0111,  // 无操作
    DES   = 4'b1111   // 不可操作
} ddr_cmd_e;
```

### 关键时序参数（DDR4）

| 参数 | 描述 | 典型值(DDR4-3200) |
|------|------|------------------|
| tCK | 时钟周期 | 0.625ns |
| tRCD | RAS到CAS延迟 | 13.75ns |
| tRP | 预充电时间 | 13.75ns |
| tCL | CAS读延迟 | 14.06ns |
| tCWL | CAS写延迟 | 11.25ns |
| tRAS | Row激活时间 | 33ns |
| tRC | 行周期时间 | 46.75ns |
| tRFC | 刷新周期 | 350ns |
| tREFI | 刷新间隔 | 7.8us |
| tRRD_S | 短行间延迟 | 3.75ns |
| tRRD_L | 长行间延迟 | 6.4ns |
| tCCD | CAS到CAS延迟 | 4 clocks |
| tWTR | 写到读延迟 | 2.5ns |
| tRTP | 读到预充电延迟 | 7.5ns |
| tWR | 写恢复时间 | 15ns |

### DDR Bank结构

```
DDR Bank寻址
├── Bank Group (BG)
├── Bank (B)
├── Row (R)
└── Column (C)

地址映射示例:
| Bank Group | Bank | Row | Column | Description    |
|-------------|------|-----|--------|----------------|
| 2 bits     | 2    | 16  | 10     | Bank x Row x Col|
```

## DDR验证架构

### DDR VIP使用

```verilog
// DDR验证环境
class ddr_vip_env extends uvm_env;
    `uvm_component_utils(ddr_vip_env)
    
    // DDR VIP
    ddr_vip_agent  ddr_agent;
    
    // DDR控制器
    axi_to_ddr_bridge  bridge;
    
    // Scoreboard
    ddr_scoreboard  sb;
    
    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        
        ddr_agent = ddr_vip_agent::type_id::create("ddr_agent", this);
        bridge = axi_to_ddr_bridge::type_id::create("bridge", this);
        sb = ddr_scoreboard::type_id::create("sb", this);
        
        // 配置DDR VIP
        uvm_config_db #(ddr_vip_config)::set(this, "ddr_agent*", "cfg",
            ddr_config::type_id::create("cfg"));
    endfunction
    
    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        bridge.axi_port.connect(sb.axi_export);
        ddr_agent.mon.connect(sb.ddr_export);
    endfunction
endclass
```

### DDR初始化序列

```verilog
// DDR初始化序列验证
class ddr_init_seq extends uvm_sequence;
    task body();
        // 等待时钟稳定
        #100us;
        
        // CKE使能
        send_cmd(CKE, 1);
        #10us;
        
        // Reset释放
        send_cmd(nRESET, 1);
        
        // MR2配置
        send_mrs(MR2, 'h0000);
        
        // MR3配置
        send_mrs(MR3, 'h0000);
        
        // MR1配置
        send_mrs(MR1, 'h0440);  // DLL使能
        
        // MR0配置
        send_mrs(MR0, 'h1000);  // BL8, CL=9
        
        // ZQ校准
        send_cmd(ZQ_START);
        wait(zq_calib_done);
        
        // 刷新使能
        enable_auto_refresh();
    endtask
endclass
```

## DDR验证检查点

### 1. 初始化验证

```verilog
// 初始化序列检查
property ddr_init_sequence;
    @(posedge clk) disable iff (!rst_n)
    // CKE必须在reset后至少2个时钟才能拉高
    ($fell(nRESET)) |-> ##[2:$] (CKE == 1);
endproperty

property ddr_mrs_sequence;
    // MRS命令必须在CKE高后至少5个时钟
    ($rose(CKE)) |-> ##[5:$] (MRS_CMD == 1);
endproperty
```

### 2. Bank管理验证

```verilog
// Row激活约束
property ddr_row_activation;
    @(posedge clk) disable iff (!rst_n)
    // 同一bank的激活间隔必须满足tRRD
    (bank_active && same_row) |-> ##1 (!bank_active until (tRRD));
endproperty

// Bank冲突检测
property ddr_bank_conflict;
    @(posedge clk) disable iff (!rst_n)
    // 当bank忙碌时不能发起新命令
    (bank_busy && new_cmd) |-> (new_cmd inside {NOP, DES});
endproperty
```

### 3. 刷新验证

```verilog
// 自动刷新检查
property ddr_auto_refresh;
    @(posedge clk) disable iff (!rst_n)
    // tREFI内必须有一次刷新
    ($rose(ref_enable), 0) |-> ##[1:tREFI/tCK] (REF_CMD);
endproperty

// 刷新期间无访问
property ddr_refresh_no_access;
    @(posedge clk)
    REF_CMD |-> (AREF_VALID == 0) throughout (tRFC);
endproperty
```

### 4. 读写字验证

```verilog
// 写数据眼图
property ddr_write_data_valid;
    @(posedge clk) disable iff (!rst_n)
    (DQS_Toggling && !DQ_Tristate) |-> ##[0:tDQSQ] $stable(DQ);
endproperty

// 读数据捕获
property ddr_read_data_valid;
    @(posedge clk)
    (DQS_Received) |-> ##[tDQSCK] (DQ.Valid);
endproperty
```

## DDR边界测试

### 地址边界

```verilog
// DDR地址边界测试
class ddr_addr_boundary_test extends uvm_sequence;
    bit [31:0] boundary_addrs[] = '{
        32'h0000_0000,  // Row 0
        32'h0001_0000,  // Row 1
        32'h0002_0000,  // Row 2
        32'h1000_0000,  // Bank切换
        32'hFFFF_FFFF   // 最大地址
    };
    
    task body();
        foreach (boundary_addrs[i]) begin
            // 激活该地址对应行
            `uvm_do_with(act_req, {
                act_req.bank == boundary_addrs[i][BANK_BITS];
                act_req.row == boundary_addrs[i][ROW_BITS];
            })
            
            // 读写测试
            `uvm_do_with(wr_req, { wr_req.row == boundary_addrs[i][ROW_BITS]; })
            `uvm_do_with(rd_req, { rd_req.row == boundary_addrs[i][ROW_BITS]; })
            
            // 预充电
            `uvm_do_with(pre_req, { pre_req.bank == boundary_addrs[i][BANK_BITS]; })
        end
    endtask
endclass
```

### 时序边界

```verilog
// tRCD边界测试
class ddr_trcd_boundary_test extends uvm_sequence;
    // tRCD最小值测试
    task test_trcd_min();
        send_act(bank, row, 0);      // 激活
        #0.1ns;                      // tRCD - epsilon
        send_rd(bank, col);          // 应该失败
    endtask
    
    // tRCD满足测试
    task test_trcd_ok();
        send_act(bank, row, tRCD);   // 满足tRCD
        send_rd(bank, col);          // 应该成功
    endtask
    
    // tRP边界测试
    task test_trp_boundary();
        send_pre(bank, 0);           // 立即预充电
        send_act(bank, row, 0);      // 应该等待tRP
    endtask
endclass
```

### 数据边界

```verilog
// DDR数据边界测试
class ddr_data_pattern_test extends uvm_sequence;
    bit [31:0] patterns[] = '{
        32'h0000_0000,  // 全0
        32'hFFFF_FFFF,  // 全1
        32'h5555_5555,  // 0101...
        32'hAAAA_AAAA,  // 1010...
        32'hFFFF_0000,  // 高低位不同
        32'h0000_FFFF,  // 低高低位不同
        32'hA5A5_A5A5,  // 混合格式
        32'h5A5A_5A5A   // 互补格式
    };
endclass
```

## DDR低功耗验证

### DDR功耗状态

```
DDR功耗状态机
                ┌─────────┐
                │ Activity│
                └────┬────┘
         ┌──────────┼──────────┐
         ▼          ▼          ▼
    ┌────────┐ ┌────────┐ ┌────────┐
    │Active  │ │Idle    │ │Self-   │
    │(ACT)   │ │(IDLE)  │ │Refresh │
    └────────┘ └────┬───┘ └────────┘
         │          │         ▲
         │    ┌─────┴────┐    │
         │    ▼          ▼    │
         │ ┌──────┐ ┌────────┐│
         │ │Power │ │Deep    ││
         │ │Down  │ │Power   ││
         │ │(PD)  │ │Down    ││
         │ └──────┘ └────────┘│
         │    ( DPD )         │
         └────────────────────┘
```

### 功耗状态切换验证

```verilog
// 功耗状态切换测试
class ddr_power_state_test extends uvm_sequence;
    
    // Active到IDLE切换
    task test_active_to_idle();
        send_act(bank, row);
        #tRAS;
        send_pre(bank);
        // 验证进入IDLE状态
    endtask
    
    // IDLE到Power Down
    task test_idle_to_powerdown();
        // 进入IDLE
        wait_idle_state();
        send_cmd(PD_ENTER);
        #10us;
        // CKE必须拉低
        assert(CKE == 0);
        send_cmd(PD_EXIT);
        #tXP;
        assert(CKE == 1);
    endtask
    
    // IDLE到Self Refresh
    task test_idle_to_selfref();
        wait_idle_state();
        send_cmd(SREF_ENTER);
        #10us;
        assert(CKE == 0);
        send_cmd(SREF_EXIT);
        #tCKESR;
        assert(CKE == 1);
    endtask
endclass
```

## DDR验证Checklist

### 初始化
- [ ] 时钟稳定后CKE使能
- [ ] MR寄存器配置正确
- [ ] ZQ校准完成
- [ ] 初始刷新执行

### 基本功能
- [ ] Row激活/预充电
- [ ] 单次读写
- [ ] 突发读写
- [ ] 读写切换

### 时序
- [ ] tRCD时序
- [ ] tRP时序
- [ ] tRAS时序
- [ ] tRC时序
- [ ] tRRD时序

### 协议
- [ ] Bank管理
- [ ] 刷新机制
- [ ] 模式寄存器设置
- [ ] 错误检测/纠正

### 边界
- [ ] 地址边界
- [ ] 时序边界
- [ ] 数据边界
- [ ] 功耗状态切换

### 性能
- [ ] 带宽测试
- [ ] 延迟测试
- [ ] 跨Bank访问
- [ ] 跨Row访问

## 总结

DDR验证核心要点：

1. **理解JEDEC规范** - 时序参数、命令协议、功耗状态
2. **验证初始化** - 严格按照规范序列
3. **测试Bank管理** - 激活/预充电/刷新
4. **边界条件** - tRCD、tRP、tRAS等临界值
5. **功耗验证** - Power Down、Self Refresh状态切换
