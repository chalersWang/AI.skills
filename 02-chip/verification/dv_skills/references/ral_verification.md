# 寄存器验证（RAL Model）

> 适用：芯片前端验证，寄存器验证与RAL模型

---

## 目录

1. [RAL 模型概述](#1-ral-模型概述)
2. [RAL 模型构建](#2-ral-模型构建)
3. [mirror / preload / predict](#3-mirror--preload--predict)
4. [寄存器访问序列](#4-寄存器访问序列)
5. [存取属性（access attribute）](#5-存取属性access-attribute)
6. [前后门访问](#6-前后门访问)
7. [寄存器模型集成](#7-寄存器模型集成)

---

## 1. RAL 模型概述

### 1.1 为什么需要RAL

```
不使用RAL:
  - 寄存器地址硬编码在sequence中
  - 读回值与期望值逐个比较
  - 无法跟踪寄存器状态变化
  - 跨模块寄存器访问难以协调

使用RAL:
  - 寄存器结构化描述，自动生成地址映射
  - mirror/期望值统一管理
  - predict机制自动更新寄存器状态
  - 支持前后门访问抽象
```

### 1.2 RAL 组件层级

```
uvm_reg_block (顶层块)
    ├── uvm_reg (单个寄存器)
    │    └── uvm_reg_field (位域)
    └── uvm_reg_map (地址映射)
         ├── 0x1000_0000 → reg_file0
         └── 0x2000_0000 → reg_file1
```

---

## 2. RAL 模型构建

### 2.1 单个寄存器

```systemverilog

class ctrl_reg extends uvm_reg;
    // 寄存器位域定义
    rand uvm_reg_field en;       // bit[0]:   使能
    rand uvm_reg_field mode;     // bit[2:1]: 模式
    rand uvm_reg_field intr_en;  // bit[3]:   中断使能
    rand uvm_reg_field reserved; // bit[31:4]: Reserved

    virtual function void build();
        en.configure(this, 1, 0, "RW", 0, 1'h0, 1, 0, 0);
        mode.configure(this, 2, 1, "RW", 0, 2'h0, 1, 0, 0);
        intr_en.configure(this, 1, 3, "RW", 0, 1'h0, 1, 0, 0);
        reserved.configure(this, 28, 4, "RO", 0, 28'h0, 1, 0, 0);
    endfunction

    `uvm_object_utils(ctrl_reg)
endclass

// configure 参数说明:
// (parent, n_bits, lsb_pos, access, has_reset, reset_value,
//  volatile, individual, coverage)
```

### 2.2 寄存器块

```systemverilog
class my_reg_block extends uvm_reg_block;
    rand ctrl_reg   ctrl;       // 控制寄存器
    rand status_reg status;     // 状态寄存器
    rand data_reg   data;       // 数据寄存器

    virtual function void build();
        // 1. 实例化并配置每个寄存器
        ctrl = ctrl_reg::type_id::create("ctrl");
        ctrl.configure(this);
        ctrl.build();

        status = status_reg::type_id::create("status");
        status.configure(this);
        status.build();

        data = data_reg::type_id::create("data");
        data.configure(this);
        data.build();

        // 2. 定义地址映射 (default_map)
        default_map = create_map("default_map", 'h1000_0000, 4, UVM_LITTLE_ENDIAN);
        // 参数: name, base_addr, n_bytes, endian, byte_addressing

        // 3. 添加寄存器到地址映射
        default_map.add_reg(ctrl,   'h00, "RW");   // offset 0x00
        default_map.add_reg(status, 'h04, "RO");   // offset 0x04
        default_map.add_reg(data,   'h08, "RW");   // offset 0x08

        // 4. 设置锁
        lock_model();
    endfunction

    `uvm_object_utils(my_reg_block)
endclass
```

### 2.3 寄存器域的存取属性

| access | 说明 | 读返回值 | 写行为 |
|--------|------|---------|--------|
| RO | 只读 | 硬件返回 | 忽略 |
| RW | 读写 | 总线返回 | 写入DUT |
| RC | 读清除 | 读后清除为0 | 写入无效 |
| WC | 写清除 | 读返回0 | 写入0清除 |
| WO | 只写 | 读返回0 | 写入DUT |
| RW1 | 写1读 | 当前值 | 写1翻转 |
| WRC | 读时写 | 总线返回 | 写入DUT |

### 2.4 实际代码：带位域的完整寄存器

```systemverilog
// GPIO 寄存器定义
class gpio_ctrl_reg extends uvm_reg;
    rand uvm_reg_field gpio_en;    // bit[7:0]: GPIO使能
    rand uvm_reg_field dir;        // bit[15:8]: 方向 (1=out, 0=in)
    rand uvm_reg_field intr_mask;  // bit[23:16]: 中断屏蔽
    rand uvm_reg_field intr_type;  // bit[31:24]: 中断类型 (1=edge, 0=level)

    virtual function void build();
        gpio_en.configure(this, 8, 0,  "RW", 0, 8'h00, 1, 0, 1);
        dir.configure     (this, 8, 8,  "RW", 0, 8'hFF, 1, 0, 1);
        intr_mask.configure(this, 8, 16, "RW", 0, 8'h00, 1, 0, 1);
        intr_type.configure(this, 8, 24, "RW", 0, 8'h00, 1, 0, 1);
    endfunction

    `uvm_object_utils(gpio_ctrl_reg)
endclass
```

---

## 3. mirror / preload / predict

### 3.1 三个值的概念

```
DUT 寄存器: 硬件实际值（通过总线或后门访问）
mirror:      RAL 模型记录的"DUT当前期望值"（由RAL维护）
desired:     RAL 模型记录的"我们期望它成为的值"（用于update）

update()    将 desired → DUT + mirror
predict()   仅更新 mirror（不访问DUT）
set()       仅更新 desired
get()       获取 mirror 值
```

### 3.2 predict

```systemverilog
class my_scoreboard extends uvm_scoreboard;
    // predict: 只更新mirror，不访问DUT
    // 用于 monitor 监测总线后更新RAL

    virtual function void write_monitor(uvm_sequence_item item);
        my_transaction tr;

        if ($cast(tr, item)) begin
            if (tr.kind == WRITE) begin
                // 预测写操作后的寄存器值
                rgm.ctrl.predict(tr.data);
            end else begin
                // 读操作后，从总线上采样实际值并比价
                rgm.ctrl.predict(tr.data, UVM_PREDICT_READ);
            end
        end
    endfunction
endclass
```

### 3.3 set / update / get

```systemverilog
class reg_test_seq extends uvm_sequence;
    virtual task body();
        uvm_status_e   status;
        uvm_reg_data_t data;

        // === set: 只设置期望值，不写DUT ===
        rgm.ctrl.en.set(1'b1);      // 期望 en=1
        rgm.ctrl.mode.set(2'b10);   // 期望 mode=2

        // === update: 将期望值写入DUT，同时更新mirror ===
        rgm.ctrl.update(status);    // 写DUT: en=1, mode=2

        // === get: 获取mirror值 ===
        data = rgm.ctrl.get();      // 返回当前mirror

        // === mirror: 获取硬件实际值（读DUT）===
        rgm.ctrl.mirror(status);    // 读DUT，更新mirror

        // === mirror with CHECK ===
        rgm.ctrl.mirror(status, UVM_CHECK);  // 读DUT并与mirror比价
    endtask
endclass
```

### 3.4 auto_predict vs 手动 predict

```systemverilog
// 方式1: auto_predict (推荐，简单)
class my_env extends uvm_env;
    virtual function void build_phase(uvm_phase phase);
        rgm.default_map.set_auto_predict(1);  // RAL自动predict
    endfunction
endclass
// 优点: 简单
// 缺点: 总线和RAL解耦，无法捕捉后门访问

// 方式2: 手动predict (推荐用于VIP)
class my_env extends uvm_env;
    virtual function void connect_phase(uvm_phase phase);
        // 连接monitor到RAL adapter
        reg2bus_adapter adapter;
        i_agt.ap.connect(reg2ral_predictor.bus_in);
        reg2ral_predictor.adapter = adapter;
        rgm.default_map.set_auto_predict(0);  // 关闭auto_predict
    endfunction
endclass
// 优点: 与monitor解耦，更精确
// 缺点: 需要额外连接
```

### 3.5 preload

RAL 的 initial 值通过 HDL 路径预设：

```systemverilog
class my_reg_block extends uvm_reg_block;
    virtual function void build();
        // ... add_reg ...

        // 设置初始值（仿真开始前的硬件状态）
        ctrl.en.set('h1);          // 使能默认打开
        ctrl.mode.set('h2);        // mode=2

        // 将初始值写入HDL后门
        ctrl.set_hdl_path_root("tb_top.dut");
        ctrl.reset(UVM_HDL);       // 设置HDL初始值

        lock_model();
    endfunction
endclass
```

---

## 4. 寄存器访问序列

### 4.1 基本读写序列

```systemverilog
class reg_basic_seq extends uvm_sequence #(uvm_sequence_item);
    `uvm_object_utils(reg_basic_seq)

    virtual task body();
        uvm_status_e   status;
        uvm_reg_data_t data;

        // === 写寄存器 ===
        rgm.ctrl.write(status, 'h0003);  // 直接写值
        // 或通过域写
        rgm.ctrl.en.write(status, 'h1);
        rgm.ctrl.mode.write(status, 'h2);

        // === 读寄存器 ===
        rgm.ctrl.read(status, data);
        `uvm_info("REG", $sformatf("read back: 0x%0h", data), UVM_MEDIUM)

        // === 期望值设置 + update ===
        rgm.ctrl.en.set('h0);
        rgm.ctrl.update(status);  // 将期望值写入DUT

        // === mirror + CHECK ===
        rgm.ctrl.mirror(status, UVM_CHECK);
    endtask
endclass
```

### 4.2 寄存器位域访问

```systemverilog
class reg_field_seq extends uvm_sequence;
    `uvm_object_utils(reg_field_seq)

    virtual task body();
        uvm_status_e status;

        // 单独访问位域
        rgm.gpio.en.write(status, 'hFF);      // 只写en字段
        rgm.gpio.dir.write(status, 'h00);     // 只写dir字段

        // 读回单个字段
        uvm_reg_data_t en_val;
        en_val = rgm.gpio.en.get();           // 获取mirror值

        // 读回整个寄存器
        uvm_reg_data_t full_val;
        full_val = rgm.gpio.get();            // 获取整个mirror
    endtask
endclass
```

### 4.3 块读写

```systemverilog
class reg_block_seq extends uvm_sequence;
    `uvm_object_utils(reg_block_seq)

    virtual task body();
        uvm_status_e status;
        uvm_reg_data_t data;

        // 块级读写：所有寄存器
        rgm.write(status, 'h1000_0000, 'hDEAD_BEEF);
        rgm.read(status, 'h1000_0000, data);

        // 通过predictor更新（monitor集成）
    endtask
endclass
```

### 4.4 对齐与突发访问

```systemverilog
// AXI RAL 适配器
class axi_ral_adapter extends uvm_reg_adapter;
    virtual function uvm_sequence_item reg2bus(const ref uvm_reg_bus_op rw);
        axi_item item;
        item = axi_item::type_id::create("item");
        if (rw.kind == UVM_WRITE)
            item.ax_write = 1;
        else
            item.ax_write = 0;
        item.ax_addr  = rw.addr;
        item.ax_len   = 0;        // 单次访问
        item.ax_size  = 3;        // 4 bytes
        item.ax_burst = 2'b01;    // INCR
        item.ax_data  = rw.data;
        return item;
    endfunction

    virtual function void bus2reg(uvm_sequence_item bus_item, ref uvm_reg_bus_op rw);
        axi_item item;
        if (!$cast(item, bus_item)) begin
            `uvm_fatal("CAST", "cannot cast to axi_item")
        end
        rw.kind = item.ax_write ? UVM_WRITE : UVM_READ;
        rw.addr = item.ax_addr;
        rw.data = item.ax_data[31:0];
        rw.status = UVM_IS_OK;
    endfunction
endclass
```

---

## 5. 存取属性（access attribute）

### 5.1 读返回值的意义

```systemverilog
// RO: 读返回硬件值，不改变mirror
uvm_reg_field::configure(..., "RO", ...);
// mirror 期望值 = configure时的 reset值
// 读后: mirror 不变

// WO: 写时更新DUT，读返回0
uvm_reg_field::configure(..., "WO", ...);
// mirror 期望值 = 0 (读不出旧值)
```

### 5.2 RW1 (写1翻转) 实现

```systemverilog
// 状态寄存器（读清除、写1清除）
class intr_status_reg extends uvm_reg;
    rand uvm_reg_field intr_flg;

    virtual function void build();
        intr_flg.configure(this, 8, 0, "RC", 0, 8'h00, 1, 0, 1);
    endfunction
    // RC: 读清除，每次读后硬件清除
    // RAL会自动在读操作后predict=0

    `uvm_object_utils(intr_status_reg)
endclass
```

---

## 6. 前后门访问

### 6.1 后门路径设置

```systemverilog
class my_reg_block extends uvm_reg_block;
    virtual function void build();
        // ... 实例化和配置寄存器 ...

        // 方式1: 单一路径（整个寄存器对应一个HDL信号）
        ctrl.set_hdl_path_root("tb_top.dut");

        // 方式2: 多路径（位域在不同的HDL信号中）
        ctrl.en.set_hdl_path("{tb_top.dut.ctrl_reg, gpio_en}");
        ctrl.mode.set_hdl_path("{tb_top.dut.ctrl_reg, gpio_mode}");

        lock_model();
    endfunction
endclass
```

### 6.2 前门 vs 后门访问

```systemverilog
// 前门: 通过总线协议访问DUT
rgm.ctrl.read(status, data);             // 通过bus发送transaction
rgm.ctrl.read(status, data, UVM_FRONTDOOR);

// 后门: 通过HDL直接访问DUT信号（不消耗仿真时间）
rgm.ctrl.read(status, data, UVM_BACKDOOR);

// 混合：前门带后门预测
rgm.ctrl.read(status, data, UVM_PREDICT, UVM_BACKDOOR);
// 从后门读值，然后predict到mirror
```

### 6.3 BACKDOOR 读写实际场景

```systemverilog
// 初始化场景: 仿真开始前设置寄存器初始值
initial begin
    // 通过force方式设置初始值
    force tb_top.dut.regs.ctrl = 'h03;
    force tb_top.dut.regs.status = 'h00;
end

// 后门预加载
class reg_preload_seq extends uvm_sequence;
    virtual task body();
        // 强制设置后门值
        void'(rgm.ctrl.predict('h03));
        void'(rgm.status.predict('h00));
    endtask
endclass
```

---

## 7. 寄存器模型集成

### 7.1 env 集成RAL

```systemverilog
class my_env extends uvm_env;
    my_reg_block  rgm;
    my_adapter    adapter;
    my_predictor  predictor;

    virtual function void build_phase(uvm_phase phase);
        super.build_phase(phase);

        // 1. 创建RAL模型
        rgm = my_reg_block::type_id::create("rgm", this);
        rgm.build();

        // 2. 创建adapter
        adapter = my_adapter::type_id::create("adapter");

        // 3. 创建bus predictor (连接monitor → RAL)
        predictor = my_predictor::type_id::create("predictor", this);
        predictor.map = rgm.default_map;
        predictor.adapter = adapter;

        // 4. 连接: monitor → predictor → RAL
        i_agent.ap.connect(predictor.bus_in);

        // 5. 关闭auto_predict，手动管理
        rgm.default_map.set_auto_predict(0);
    endfunction

    virtual function void connect_phase(uvm_phase phase);
        // sequencer 连接RAL
        rgm.default_map.set_sequencer(px_sequencer);
    endfunction
endclass
```

### 7.2 sequencer 与 RAL 绑定

```systemverilog
// test 中设置 default_sequence 使用RAL
class ral_test extends uvm_test;
    virtual function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        // 设置RAL test sequences
        uvm_config_db#(uvm_object_wrapper)::set(
            this, "env.sqr.main_phase", "default_sequence",
            reg_exhaustive_seq::type_id::get()
        );
    endfunction
endclass
```

---
