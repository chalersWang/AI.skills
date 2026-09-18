# CDC 验证（跨时钟域验证）

> 适用：芯片前端验证，跨时钟域设计验证

---

## 目录

1. [CDC 问题概述](#1-cdc-问题概述)
2. [同步器类型](#2-同步器类型)
3. [异步FIFO验证](#3-异步fifo验证)
4. [握手协议验证](#4-握手协议验证)
5. [CDC检查清单](#5-cdc检查清单)
6. [CDC EDA工具使用](#6-cdc-eda工具使用)

---

## 1. CDC 问题概述

### 1.1 亚稳态 (Metastability)

```
时钟域A                时钟域B
    │                      │
    ├──► data ───────────────► [触发器]
    │                      │       │
 clk_a                  clk_b    │  t мета
    │                      │       ▼
    │                      │   [未知状态]
```

- 当 data 在 clk_b 采样边沿附近变化时，触发器输出可能进入亚稳态
- 亚稳态传播时间 = MTBF（平均无故障时间）
- MTBF = 1 / (fdata × fclk × τ)

### 1.2 CDC 违例类型

| 违例类型 | 描述 | 风险 |
|---------|------|------|
| 异步信号直接进入触发器 | 无同步器 | 亚稳态传播 |
| 多比特信号不同步 | 总线冒险 | 数据错误 |
| 握手信号不同步 | 竞态条件 | 死锁 |
| 组合逻辑直接穿越 | 毛刺传播 | 功能错误 |

### 1.3 CDC 验证目标

```
CDC 验证 = 结构检查 + 功能验证
├── 结构检查: 是否有足够的同步寄存器
├── 时序分析: 同步器延迟是否足够
└── 功能验证: 跨时钟域数据传输正确性
```

---

## 2. 同步器类型

### 2.1 单比特同步器

```systemverilog
// 两级触发器同步器 (最常用)
module sync_2stage (
    input  wire clk_sync,    // 目标时钟域
    input  wire rst_n,
    input  wire async_sig,   // 来自异步时钟域
    output wire sync_sig
);
    reg [1:0] sync_ff;

    always @(posedge clk_sync or negedge rst_n) begin
        if (!rst_n)
            sync_ff <= 2'b0;
        else
            sync_ff <= {sync_ff[0], async_sig};
    end

    assign sync_sig = sync_ff[1];  // 打两级后输出
endmodule
```

```systemverilog
// CDC 验证中的同步器建模
class cdc_monitor extends uvm_monitor;
    // 采样异步信号，打两级触发器
    bit  async_sig_sync1;
    bit  async_sig_sync2;
    bit  sync_sig;

    always @(posedge mon_if.clk) begin
        async_sig_sync1 <= mon_if.async_sig_raw;
        async_sig_sync2 <= async_sig_sync1;
        sync_sig        <= async_sig_sync2;
    end

    // 验证: 同步后信号是否符合预期
    covergroup cdc_cg @(posedge mon_if.clk);
        cp_toggle: coverpoint sync_sig {
            bins toggle_01 = (0 => 1);
            bins toggle_10 = (1 => 0);
        }
    endgroup
endclass
```

### 2.2 多比特信号同步

```systemverilog
// 格雷码同步器（适合指针）

module gray_cdc_ptr (
    input  wire clk_a,
    input  wire clk_b,
    input  wire [3:0] ptr_a,    // 二进制指针（时钟域A）
    output reg  [3:0] ptr_b,    // 同步后格雷码（时钟域B）
    output reg  [3:0] ptr_gray  // 二进制转换后
);
    reg [3:0] gray_sync;

    // 同步器
    always @(posedge clk_b) begin
        gray_sync <= ptr_a;  // ptr_a 需为格雷码
        ptr_b     <= gray_sync;
    end

    // 格雷码转二进制
    integer i;
    always @(*) begin
        ptr_gray = ptr_b;
        for (i = 0; i < 4; i++)
            ptr_gray[i] = ^ptr_b[i-1:0];  // 二进制转换
    end
endmodule
```

### 2.3 握手同步器

```systemverilog
// 请求-应答握手同步器
module handshake_cdc (
    // 时钟域A (source)
    input  wire clk_a,
    input  wire rst_n_a,
    input  wire req_a,
    output reg  ack_a,
    // 时钟域B (dest)
    input  wire clk_b,
    input  wire rst_n_b,
    output reg  req_b,
    input  wire ack_b,
    // 数据
    input  wire [31:0] data_a,
    output wire [31:0] data_b
);
    // 同步请求
    reg [2:0] req_sync;
    always @(posedge clk_b or negedge rst_n_b) begin
        if (!rst_n_b)
            req_sync <= 3'b0;
        else
            req_sync <= {req_sync[1:0], req_a};
    end
    assign req_b = req_sync[2];

    // 同步应答
    reg [2:0] ack_sync;
    always @(posedge clk_a or negedge rst_n_a) begin
        if (!rst_n_a)
            ack_sync <= 3'b0;
        else
            ack_sync <= {ack_sync[1:0], ack_b};
    end
    assign ack_a = ack_sync[2];

    // 数据锁存
    reg [31:0] data_hold;
    always @(posedge clk_a) begin
        if (req_a)
            data_hold <= data_a;
    end
    assign data_b = data_hold;
endmodule
```

---

## 3. 异步FIFO验证

### 3.1 异步FIFO结构

```
写入侧                    读出侧
[clk_a]                  [clk_b]
  │                         │
  ▼                         ▼
┌──────┐                 ┌──────┐
│ RAM  │◄────────────────│ RAM  │
└──────┘                 └──────┘
  │                         ▲
  │ wr_en                   │ rd_en
  │                         │
  ▼                         │
wr_ptr[3:0]                 │
  │格雷码                   │
  ▼                         ▼
sync_to_b ◄────────────── sync_to_a
(wr_ptr同步到clk_b)      (rd_ptr同步到clk_a)
```

### 3.2 异步FIFO UVM验证模型

```systemverilog
// 异步FIFO BFM / monitor
class async_fifo_monitor extends uvm_monitor;
    virtual async_fifo_if vif;

    // 同步器建模
    reg [PTR_WIDTH-1:0] wr_ptr_gray_sync1, wr_ptr_gray_sync2;
    reg [PTR_WIDTH-1:0] rd_ptr_gray_sync1, rd_ptr_gray_sync2;

    // 满/空标志
    bit full, empty;
    bit almost_full, almost_empty;

    covergroup fifo_cdc_cg;
        cp_full:    coverpoint full;
        cp_empty:   coverpoint empty;
        cp_afull:   coverpoint almost_full;
        cp_aempty:  coverpoint almost_empty;
        cp_occupancy: coverpoint occupancy {
            bins empty_bin  = {0};
            bins low        = {[1:DEPTH/4]};
            bins medium     = {[DEPTH/4+1:DEPTH*3/4]};
            bins high       = {[DEPTH*3/4+1:DEPTH-1]};
            bins full_bin   = {DEPTH};
        }
    endgroup

    virtual task run_phase(uvm_phase phase);
        // 监测写侧
        fork
            forever @(posedge vif.clk_a) begin
                if (vif.wr_en && !vif.full) begin
                    // 记录写操作
                end
            end
            // 监测读侧
            forever @(posedge vif.clk_b) begin
                if (vif.rd_en && !vif.empty) begin
                    // 记录读操作
                end
            end
            // CDC 同步监测
            forever @(posedge vif.clk_a) begin
                wr_ptr_gray_sync1 <= vif.wr_ptr_gray;
                wr_ptr_gray_sync2 <= wr_ptr_gray_sync1;
            end
            forever @(posedge vif.clk_b) begin
                rd_ptr_gray_sync1 <= vif.rd_ptr_gray;
                rd_ptr_gray_sync2 <= rd_ptr_gray_sync1;
            end
        join
    endtask
endclass
```

### 3.3 异步FIFO 边界测试

```systemverilog
class async_fifo_rand_seq extends uvm_sequence;
    `uvm_object_utils(async_fifo_rand_seq)

    // 约束随机: 同时读写
    constraint c_fifo_traffic {
        // 写请求和读请求随机
        wr_delay inside {[0:5]};
        rd_delay inside {[0:5]};
    }

    virtual task body();
        repeat(10000) begin
            fork
                write_one();
                read_one();
            join_any
            disable fork;
        end
    endtask

    virtual task write_one();
        @(posedge vif.clk_a);
        if (!vif.full) begin
            vif.wr_en <= 1;
            vif.wr_data <= $random;
        end
        @(posedge vif.clk_a);
        vif.wr_en <= 0;
    endtask

    virtual task read_one();
        @(posedge vif.clk_b);
        if (!vif.empty) begin
            vif.rd_en <= 1;
        end
        @(posedge vif.clk_b);
        vif.rd_en <= 0;
    endtask
endclass
```

---

## 4. 握手协议验证

### 4.1 四脉冲握手

```systemverilog
// 4-phase handshake CDC
// req_a → (sync) → req_b
// ack_b → (sync) → ack_a
// 数据在 req_a 有效时稳定

class handshake_cdc_seq extends uvm_sequence;
    `uvm_object_utils(handshake_cdc_seq)

    virtual task body();
        // 场景: 快→慢时钟域
        for (int i = 0; i < 100; i++) begin
            // 发送请求
            send_req(i);

            // 等待应答
            wait_for_ack();

            // 稳定间隔
            #100;
        end
    endtask

    virtual task send_req(int idx);
        @(posedge vif.clk_a);
        vif.req_a <= 1;
        vif.data_a <= idx;
        @(posedge vif.clk_a);
        while (vif.ack_a == 0)
            @(posedge vif.clk_a);
        vif.req_a <= 0;
    endtask
endclass
```

### 4.2 握手违例场景

```systemverilog
// CDC 验证重点: 握手信号稳定窗口
// req_a必须在ack_a为0时才能拉高
// 违例: req_a在ack_a=1时再次拉高（会导致数据错位）

class handshake_violation_seq extends uvm_sequence;
    // 故意制造违例: 快速连续请求
    virtual task body();
        // 第一个请求
        @(posedge vif.clk_a);
        vif.req_a <= 1;
        @(posedge vif.clk_a);
        vif.req_a <= 0;

        // 立即发第二个请求（不等ack）
        // 这违反了4-phase握手协议
        #1;  // tiny gap
        vif.req_a <= 1;  // VIOLATION: ack还没拉低
    endtask
endclass
```

---

## 5. CDC检查清单

### 5.1 结构检查清单

```markdown
□ 单比特异步信号是否有2级或更多同步器？
□ 多比特信号是否使用以下方式之一：
  □ 格雷码 + 两级同步
  □ 握手协议
  □ 异步FIFO
□ 复位信号是否正确同步？
□ 组合逻辑是否直接进入另一时钟域？
□ 时钟切换是否正确处理？
□ CDC信号是否在目标时钟域有稳定窗口？
```

### 5.2 CDC 功能验证测试点

```systemverilog
// 测试点: 快→慢时钟域
class fast_to_slow_cdc_test extends uvm_sequence;
    constraint c_freq_ratio { fast_period == 5ns; slow_period == 50ns; }
endclass

// 测试点: 慢→快时钟域
class slow_to_fast_cdc_test extends uvm_sequence;
    constraint c_freq_ratio { slow_period == 100ns; fast_period == 10ns; }
endclass

// 测试点: 数据稳定性
class data_stability_test extends uvm_sequence;
    // 数据信号在采样边沿附近是否稳定
    // 如果数据在同步期间变化，会导致采样错误
endclass

// 测试点: 背靠背传输
class back_to_back_cdc_test extends uvm_sequence;
    // 连续快速传输，测试同步器恢复时间
endclass
```

### 5.3 CDC 验证测试用例矩阵

| 测试场景 | 快→慢 | 慢→快 | 相近频率 | 关键点 |
|---------|------|------|---------|--------|
| 单比特同步 | ✓ | ✓ | ✓ | 同步延迟 |
| 格雷码指针 | ✓ | ✓ | ✓ | 指针跳变 |
| 握手协议 | ✓ | ✓ | ✓ | 时序违例 |
| 异步FIFO | ✓ | ✓ | ✓ | 满空判断 |
| 数据稳定性 | ✓ | ✓ | ✓ | 毛刺过滤 |

---

## 6. CDC EDA工具使用

### 6.1 静态 CDC 分析 ( JasperGold )

```bash
# 运行 CDC 静态检查

jdv -cdc design.v -top top_module -out cdc_run

# 关键 CDC 规则
#   - async_signal_not_synchronized
#   - multiple_bit_signal_no_sync
#   - combinational_logic_feeds_cdc_path
#   - reset_not_synchronized
```

```systemverilog
// CDC 分析需要的时钟/复位标注
module cdc_design (
    input wire clk_a,
    input wire clk_b,
    input wire rst_n_a,
    input wire rst_n_b,
    // ... signals ...
);

// synthesis_synopsis_loop_constraint = 2
// 告诉综合工具该路径有2级同步器
endmodule
```

### 6.2 Questa CDC 检查

```bash
# Questa CDC 静态分析
vlog design.v
# CDC 检查
questacdc -gui design
# 生成 CDC 报告
questacdc -report cdc_report.txt design
```

### 6.3 覆盖率驱动的 CDC 验证

```systemverilog
// CDC 功能覆盖率
class cdc_functional_cov extends uvm_subscriber;
    covergroup cdc_func_cov;
        cp_clk_ratio: coverpoint clk_ratio {
            bins slow_to_fast = {[1:10]};
            bins same_freq    = {1};
            bins fast_to_slow = {[10:100]};
        }

        cp_data_width: coverpoint data_width {
            bins single_bit = {1};
            bins byte_wise  = {8, 16, 32};
            bins wide_bus   = {[33:256]};
        }

        cross cp_clk_ratio, cp_data_width;
    endgroup

    covergroup sync_path_cov;
        cp_toggle_rate: coverpoint toggle_rate {
            bins slow_toggle   = {[0:1]};    // < 1%
            bins medium_toggle = {[1:50]};   // 1-50%
            bins fast_toggle   = {[50:100]}; // > 50%
        }
    endgroup
endclass
```

---
