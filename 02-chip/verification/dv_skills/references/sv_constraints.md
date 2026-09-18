# SystemVerilog 约束随机技巧

> 适用：芯片前端验证、UVM环境构建

---

## 目录

1. [约束随机基础](#1-约束随机基础)
2. [权重约束](#2-权重约束-dist weight)
3. [条件约束](#3-条件约束-implication and if-else)
4. [solve before 约束](#4-solve-before-约束)
5. [随机化失败处理](#5-随机化失败处理)
6. [约束层次与继承](#6-约束层次与继承)
7. [常用约束模式](#7-常用约束模式)
8. [实战示例](#8-实战示例)

---

## 1. 约束随机基础

### 1.1 内联约束

```systemverilog
class my_transaction extends uvm_sequence_item;
    rand bit [7:0] addr;
    rand bit [31:0] data;
    rand bit        wr_rd;

    constraint c_addr {
        addr inside {[0x0000:0x00FF], [0x1000:0x10FF]};
    }

    constraint c_data {
        if (wr_rd == 1'b1)  // write: data must be non-zero
            data != 0;
        else                // read: data is don't care
            data == 0;
    }
endclass

// 使用时指定额外约束
task usage();
    my_transaction tr;
    tr = new();
    // 随机化时加内联约束
    assert(tr.randomize() with { addr[11:8] == 4'hA; data[31:16] == 16'hDEAD; });
endtask
```

### 1.2 约束是声明性的

约束块内的表达式必须是**求解后为布尔值**的表达式：

```systemverilog
// 正确
constraint c_basic { a > b; }

// 错误：赋值语句不是布尔表达式
constraint c_wrong { a = b; }
```

### 1.3 pre_randomize / post_randomize 回调

```systemverilog
class my_transaction extends uvm_sequence_item;
    rand bit [31:0] length;
    bit [31:0] actual_length;  // 计算得出，不随机

    function void pre_randomize();
        `uvm_info("RAND", $sformatf("before randomize: length=%0d", length), UVM_MEDIUM)
    endfunction

    function void post_randomize();
        actual_length = length * 4;  // 随机后计算
        `uvm_info("RAND", $sformatf("after randomize: actual_length=%0d", actual_length), UVM_MEDIUM)
    endfunction
endclass
```

---

## 2. 权重约束 (dist weight)

### 2.1 基本权重分布

```systemverilog
class dist_example extends uvm_sequence_item;
    rand int val;

    // 均匀分布
    constraint c_even { val inside {[0:100]}; }

    // 权重分布: 0~25出现概率10%, 26~50出现概率30%, 51~100出现概率60%
    constraint c_weighted {
        val dist {
            [0:25]  := 10,   // := 每一项权重相同
            [26:50] := 30,
            [51:100] := 60
        };
    }

    // 权重列表用法: 10个特定值各占10%
    constraint c_list {
        val dist {
            1  := 10,
            2  := 10,
            3  := 10,
            4  := 10,
            5  := 10,
            10 := 10,
            20 := 10,
            50 := 10,
            75 := 10,
            100 := 10
        };
    }
endclass
```

### 2.2 := vs :/

| 运算符 | 含义 |
|--------|------|
| `:=` | 每个值/范围权重相同（列表内均匀） |
| `:/` | 权重在范围内均分（区间内均匀） |

```systemverilog
// := 示例: 0权重5, 1~9权重各1 (总共10)
constraint c1 { val dist { 5 := 5, [1:9] := 1 }; }

// :/ 示例: 0权重5, 1~9共权重5 (每个值权重0.555)
constraint c2 { val dist { 5 := 5, [1:9] :/ 5 }; }
```

### 2.3 实际场景：突发传输长度权重

```systemverilog
class axi_transaction extends uvm_sequence_item;
    rand bit [3:0]  len;    // AXI burst length
    rand bit [2:0]  size;    // burst size
    rand bit [1:0]  burst;   // burst type

    // 实际芯片验证中常见的权重分布
    constraint c_len_weighted {
        // 短突发为主，但偶尔长突发
        len dist {
            0      := 30,   // INCR1
            1      := 20,   // INCR2
            3      := 15,   // INCR4
            7      := 10,   // INCR8
            15     := 5,    // INCR16 (少见)
            [4:14] := 0     // 中间值几乎不出现
        };
    }

    constraint c_size_weighted {
        size dist {
            0 := 5,   // 1B
            1 := 40,  // 2B (常见)
            2 := 40,  // 4B (常见)
            3 := 10   // 8B
        };
    }
endclass
```

---

## 3. 条件约束 (implication and if-else)

### 3.1 `->` 蕴含约束

```systemverilog
class pkt extends uvm_sequence_item;
    rand bit [3:0]  pkt_type;
    rand bit [15:0] hdr;
    rand bit [31:0] payload;
    rand bit [31:0] fcs;  // frame check sequence

    // 蕴含: pkt_type==1 时才有payload
    constraint c_payload {
        (pkt_type == 4'h1) -> (payload != 0);
    }

    // 多条件蕴含
    constraint c_hdr_fcs {
        (pkt_type == 4'hF) -> { hdr == 16'hDEAD; fcs == 32'hCAFEBABE; }
    }
endclass
```

### 3.2 `if-else` 条件约束

```systemverilog
class reg_access extends uvm_sequence_item;
    rand bit [1:0]  access_type;  // 00=nop, 01=read, 10=write, 11=modify
    rand bit [11:0] addr;
    rand bit [31:0] wdata;
    bit        [31:0] rdata;

    // 读操作时 wdata 不关心（约束为 0）
    // 写操作时 wdata 必须非零
    constraint c_rw {
        if (access_type == 2'b01)   // read
            wdata == 32'h0;
        else if (access_type == 2'b10)  // write
            wdata != 32'h0;
        else
            wdata == 32'h0;  // nop/modify
    }

    // 地址高位决定访问哪个寄存器组
    constraint c_addr_region {
        if (addr[11:8] == 4'h0)  // GPIO组
            addr[7:0] inside {[0x00:0x3F]};
        else if (addr[11:8] == 4'h1)  // TIMER组
            addr[7:0] inside {[0x00:0x1F]};
        else
            addr[7:0] inside {[0x00:0xFF]};
    }
endclass
```

### 3.3 `soft` 软约束

软约束可被外部覆盖，适合默认约束：

```systemverilog
class soft_constraint_demo extends uvm_sequence_item;
    rand int len;

    // 软约束: 默认值，可被内联约束 override
    constraint c_default_len {
        soft len inside {[1:16]};
    }
endclass

// 使用时内联约束可覆盖软约束
task test_soft();
    soft_constraint_demo tr;
    tr = new();
    // 这里内联约束 len=100 覆盖了软约束的 [1:16]
    assert(tr.randomize() with { len == 100; });
endtask
```

---

## 4. solve before 约束

### 4.1 问题：solve before 控制随机顺序

默认 SystemVerilog 随机求解器**不保证**变量求解顺序，可能导致某些组合极难生成。

`solve A before B` 告诉求解器：**先求解 A，再基于 A 求解 B**。

```systemverilog
class solve_before_demo extends uvm_sequence_item;
    rand bit [2:0] sel;
    rand bit [7:0] data;

    // 不加 solve before: sel 和 data 随机组合
    // 可能很难生成特定的 (sel=0, data>200) 组合
    constraint c_normal {
        data inside {[100:250]};
    }

    // 加 solve before: 先确定 sel，再生成 data
    // 确保每个 sel 值都能被充分覆盖
    constraint c_solve {
        solve sel before data;
    }
endclass
```

### 4.2 典型应用：协议合法序列

```systemverilog
class axi_burst_seq extends uvm_sequence_item;
    rand bit [1:0]  burst;
    rand bit [3:0]  len;
    rand bit [2:0]  size;

    // 约束: burst 类型决定 len 合法值
    constraint c_legal_combo {
        // FIXED burst: len 只能是 1~16
        (burst == 2'b00) -> (len inside {[1:16]});
        // INCR burst: len 任意
        (burst == 2'b01) -> (len inside {[1:16]});
        // WRAP burst: len 必须是 2/4/8/16
        (burst == 2'b10) -> (len inside {2, 4, 8, 16});
    }

    // solve before: 先确定 burst 类型，使 len 的约束求解更容易
    constraint c_solve_order {
        solve burst before len;
    }
endclass
```

### 4.3 常见陷阱

```systemverilog
// 陷阱: solve before 会影响分布概率
class trap_demo extends uvm_sequence_item;
    rand bit a;
    rand bit b;

    constraint c_basic {
        a != b;
    }

    // 注意: 不加 solve before 时，求解器通常会给出接近 50/50 的分布
    // 加了 solve before 后，概率分布可能改变
    constraint c_solve {
        solve a before b;
    }
endclass
```

---

## 5. 随机化失败处理

### 5.1 `assert` 安全随机化

```systemverilog
class safe_randomize extends uvm_sequence_item;
    rand int x;
    constraint c_range { x inside {[1:10]}; }
endclass

task test();
    safe_randomize tr = new();
    // 推荐: 用 assert 包裹，检查随机化是否成功
    if (!tr.randomize())
        `uvm_error("RAND", "randomization failed!")
    else
        `uvm_info("RAND", $sformatf("x=%0d", tr.x), UVM_MEDIUM)
endtask
```

### 5.2 随机化失败回调

```systemverilog
class my_item extends uvm_sequence_item;
    rand int a, b;

    constraint c_ab {
        a inside {[1:100]};
        b inside {[1:100]};
        a + b <= 150;  // 约束空间较小，容易失败
    }

    // 随机化失败时的回调
    function void post_randomize();
        if (a + b > 150) begin
            `uvm_warning("RAND", "constraint violation detected in post_randomize")
        end
    endfunction
endclass
```

### 5.3 带重试的随机化

```systemverilog
class retry_randomize extends uvm_sequence_item;
    rand int length;
    rand int size;
    rand bit [31:0] payload[];

    constraint c_combo {
        length inside {[1:256]};
        size dist { 1 := 30, 2 := 30, 4 := 30, 8 := 10 };
        payload.size() == length;
        // 复杂约束可能导致失败
        length % size == 0;
    }
endclass

task gen_with_retry(retry_randomize tr, int max_retry=1000);
    int retries = 0;
    while (retries < max_retry) begin
        if (tr.randomize())
            return;  // 成功
        retries++;
    end
    `uvm_error("GEN", $sformatf("failed after %0d retries", max_retry))
endtask
```

### 5.4 在 sequence 中处理随机化失败

```systemverilog
class robust_sequence extends uvm_sequence #(my_transaction);
    `uvm_object_utils(robust_sequence)

    virtual task body();
        repeat(100) begin
            my_transaction tr;
            `uvm_create(tr)
            assert(tr.randomize() with {
                tr.addr[31:16] == 16'h4000;
                tr.len inside {[1:8]};
            }) else begin
                `uvm_warning("RAND", "randomize failed, skipping")
                continue;
            end
            `uvm_send(tr)
        end
    endtask
endclass
```

---

## 6. 约束层次与继承

### 6.1 约束继承

```systemverilog
class base_item extends uvm_sequence_item;
    rand int base_addr;
    constraint c_base { base_addr inside {[0x1000:0x1FFF]}; }
endclass

class extended_item extends base_item;
    rand int ext_addr;

    // 约束累积: base的c_base + 新约束
    constraint c_ext { ext_addr inside {[0x2000:0x2FFF]}; }
endclass
```

### 6.2 约束覆盖

```systemverilog
class base_seq extends uvm_sequence_item;
    rand int value;
    constraint c_val { value inside {[0:100]}; }
endclass

class child_seq extends base_seq;
    // 覆盖父类约束
    constraint c_val { value inside {[50:150]}; }
endclass
```

### 6.3 跨约束块引用

```systemverilog
class cross_block extends uvm_sequence_item;
    rand bit [7:0] mode;
    rand bit [15:0] addr;
    rand bit [31:0] data;

    // mode 决定 addr 范围
    constraint c_mode_addr {
        if (mode == 8'hAA)
            addr inside {[0x0000:0x0FFF]};
        else if (mode == 8'hBB)
            addr inside {[0x1000:0x1FFF]};
        else
            addr inside {[0x0000:0xFFFF]};
    }

    // data 范围与 addr 相关
    constraint c_addr_data {
        addr[15:12] == data[31:28];  // 地址高位 = 数据高4位
    }
endclass
```

---

## 7. 常用约束模式

### 7.1 按类别启用/禁用约束

```systemverilog
class multi_mode_item extends uvm_sequence_item;
    rand int len;

    constraint c_short  { len inside {[1:4]}; }
    constraint c_medium { len inside {[5:32]}; }
    constraint c_long   { len inside {[33:256]}; }

    // 模式控制
    string mode = "SHORT";
endclass

class test_base extends uvm_test;
    virtual task build_phase(uvm_phase phase);
        my_item = multi_mode_item::type_id::create("my_item");
        // 根据模式禁用不需要的约束
        case (mode)
            "SHORT":   my_item.c_short.constraint_mode(1);
            "MEDIUM":  my_item.c_medium.constraint_mode(1);
            "LONG":    my_item.c_long.constraint_mode(1);
        endcase
    endtask
endclass
```

### 7.2 rand_mode 动态控制

```systemverilog
class dynamic_rand extends uvm_sequence_item;
    rand int a;
    rand int b;
    rand int c;  // 默认不随机，作为固定值使用

    function new();
        c.rand_mode(0);  // 构造时关闭随机
    endfunction
endclass

// 运行时控制
task dynami_control();
    dynamic_rand d = new();
    d.a.rand_mode(0);   // 关闭 a 的随机
    d.b.rand_mode(1);   // 打开 b 的随机
    assert(d.randomize());
endtask
```

---

## 8. 实战示例

### 8.1 AXI4 协议验证中的完整约束

```systemverilog

// 文件: refs/axi_constrained_random.sv

class axi_txn extends uvm_sequence_item;
    // AXI 信号
    rand bit [3:0]   arid;
    rand bit [31:0]  araddr;
    rand bit [3:0]   arlen;
    rand bit [2:0]   arsize;
    rand bit [1:0]   arburst;
    rand bit [1:0]   arlock;
    rand bit [3:0]   arcache;
    rand bit [2:0]   arprot;
    rand bit         arvalid;
    bit              arready;

    // 写地址通道
    rand bit [3:0]   awid;
    rand bit [31:0]  awaddr;
    rand bit [3:0]   awlen;
    rand bit [2:0]   awsize;
    rand bit [1:0]   awburst;
    rand bit         awvalid;
    bit              awready;

    // 约束: ARBURST 合法值
    constraint c_arburst {
        arburst inside {2'b00, 2'b01, 2'b10};  // FIXED, INCR, WRAP
        awburst inside {2'b00, 2'b01};
    }

    // 约束: ARLEN 基于 ARBURST
    constraint c_arlen {
        arlen inside {[0:15]};
        (arburst == 2'b10) -> (arlen inside {1, 3, 7, 15});  // WRAP must be legal len
    }

    // 约束: ARSIZE 不能超过总线宽度
    constraint c_arsize {
        arsize inside {[0:2]};  // 1, 2, 4 bytes
        awsize inside {[0:2]};
    }

    // 约束: 地址对齐
    constraint c_addr_align {
        (arsize == 3'd0) -> (araddr[0:0]   == 1'b0);  // 1B align
        (arsize == 3'd1) -> (araddr[1:0]   == 2'b0);  // 2B align
        (arsize == 3'd2) -> (araddr[2:0]   == 3'b0);  // 4B align
    }

    // 约束: 地址空间划分
    constraint c_addr_space {
        araddr[31:28] == 4'h0;  // 0x0xxx_xxxx
    }

    `uvm_object_utils_begin(axi_txn)
        `uvm_field_int(araddr, UVM_ALL_ON)
        `uvm_field_int(arlen,  UVM_ALL_ON)
        `uvm_field_int(arburst, UVM_ALL_ON)
    `uvm_object_utils_end
endclass
```

### 8.2 DDR 刷新序列约束

```systemverilog

class ddr_refresh_seq extends uvm_sequence_item;
    typedef enum { REFRESH, SELF_REFRESH, SELF_REFRESH_EXIT, IDLE } refresh_state_t;
    rand refresh_state_t state;
    rand int refresh_count;
    rand int timing_delay;

    constraint c_state_machine {
        // 状态机约束: 合法状态转换
        solve state before timing_delay;
        solve state before refresh_count;

        if (state == SELF_REFRESH)
            timing_delay inside {[100:500]};
        else if (state == REFRESH)
            timing_delay inside {[1:50]};
        else
            timing_delay == 0;
    }

    constraint c_refresh_count {
        refresh_count inside {[1:8]};
        (state != REFRESH) -> (refresh_count == 0);
    }
endclass
```

---
