# UVM 进阶：Factory/Phase/Objection/Config_db/Sequence

> 适用：芯片前端验证，UVM 环境深度定制

---

## 目录

1. [Factory 机制深层用法](#1-factory-机制深层用法)
2. [Phase 机制深层理解](#2-phase-机制深层理解)
3. [Objection 机制与仿真控制](#3-objection-机制与仿真控制)
4. [config_db 深层用法](#4-config_db-深层用法)
5. [sequence 进阶用法](#5-sequence-进阶用法)
6. [layered sequence](#6-layered-sequence)
7. [virtual sequence 最佳实践](#7-virtual-sequence-最佳实践)

---

## 1. Factory 机制深层用法

### 1.1 type override vs instance override

```systemverilog
// ========== type override ==========
// 将所有 MyDriver 替换为 MyNewDriver
factory.set_type_override_by_name("my_driver", "my_new_driver");

// ========== instance override ==========
// 只替换特定路径下的 MyDriver
factory.set_inst_override_by_name("my_driver", "my_new_driver", "top_env.agent1.drv");
```

### 1.2 实例替换 vs 类型替换

```systemverilog
// 原始: my_env.build_phase 中创建 drv
// 方式1: set_type_override — 替换所有实例
class base_test extends uvm_test;
    virtual function void build_phase(uvm_phase phase);
        factory.set_type_override_by_name("my_driver", "my_driver_v1");
    endfunction
endclass

// 方式2: set_inst_override — 只替换特定路径
class test1 extends base_test;
    virtual function void build_phase(uvm_phase phase);
        // 只替换 env1 下的 drv，env2 的不变
        factory.set_inst_override_by_name("my_driver", "my_driver_v2", "uvm_test_top.env1.drv");
    endfunction
endclass
```

### 1.3 通过函数传递替代类型

```systemverilog
// 使用 get_config_object 动态获取类型
class generic_test extends uvm_test;
    uvm_object wrapper;

    virtual function void build_phase(uvm_phase phase);
        if (uvm_config_db#(uvm_object)::get(this, "", "seq_type", wrapper))
            `uvm_info("TEST", $sformatf("got wrapper: %s", wrapper.get_type_name()), UVM_MEDIUM)
    endfunction
endclass

// set 时直接传类型
initial begin
    uvm_config_db#(uvm_object_wrapper)::set(
        this, "env.sqr.*", "default_sequence",
        my_custom_sequence::type_id::get()
    );
end
```

### 1.4 factory 调试

```bash
# 运行时打印 factory 注册表
<sim> +UVM_FACTORY_TRACE
```

---

## 2. Phase 机制深层理解

### 2.1 run_phase 与 12 个子 phase 并行

```systemverilog
// run_phase 与 12 个 runtime phase 并行执行
// 两个 phase 树共享同一时刻轴

class my_test extends uvm_test;
    virtual task run_phase(uvm_phase phase);
        phase.raise_objection(this);
        #1000;
        phase.drop_objection(this);
    endtask

    // reset_phase 等同于 run_phase 的子 phase
    virtual task reset_phase(uvm_phase phase);
        phase.raise_objection(this);
        #100;  // 等复位完成
        phase.drop_objection(this);
    endtask

    virtual task main_phase(uvm_phase phase);
        phase.raise_objection(this);
        #800;  // 主业务
        phase.drop_objection(this);
    endtask
endclass
// reset_phase 先 raise(100ns) 后 drop(100ns)
// 然后 main_phase raise(100ns~800ns) drop(800ns)
// run_phase 整体(0~1000ns)
```

### 2.2 自下而上与自上而下

| Phase 类型 | 执行顺序 | 典型用途 |
|-----------|---------|---------|
| build_phase | 自上而下 | 实例化组件、获取配置 |
| connect_phase | 自下而上 | 连接 TLM 端口、FIFO |
| end_of_elaboration_phase | 自下而上 | 细化配置、打印拓扑 |
| start_of_simulation_phase | 自下而上 | 打印环境信息 |
| extract_phase | 自下而上 | 收集数据 |
| check_phase | 自下而上 | 检查结果 |
| report_phase | 自下而上 | 生成报告 |

### 2.3 phase.wait_for_state

组件可以等待其他组件的 phase：

```systemverilog
class sync_component extends uvm_component;
    virtual task run_phase(uvm_phase phase);
        // 等待 main_phase 开始
        uvm_domain::get_common_domain().wait_for_state(UVM_PHASE_STARTED, UVM_PHASE_MAIN);
        `uvm_info("SYNC", "main_phase started, now running", UVM_MEDIUM)
    endtask
endclass
```

### 2.4 自定义 phase

```systemverilog
// 定义自定义 phase
class my_custom_phase extends uvm_task_phase;
    static bit done[uvm_component];

    virtual task execute(uvm_phase phase, uvm_component comp);
        `uvm_info("PHASE", $sformatf("%s entering my_custom_phase", comp.get_full_name()), UVM_DEBUG)
        // 自定义 phase 逻辑
        #100;
        `uvm_info("PHASE", $sformatf("%s exiting my_custom_phase", comp.get_full_name()), UVM_DEBUG)
    endtask
endclass
```

---

## 3. Objection 机制与仿真控制

### 3.1 objection 的树形结构

所有组件的 objection 形成树，只有**所有叶子节点撤销**才能结束 phase：

```systemverilog
// 典型错误: 在父组件 raise，在子组件 drop
// 如果父组件先 drop，仿真会提前结束

class parent_comp extends uvm_component;
    virtual task main_phase(uvm_phase phase);
        phase.raise_objection(this);  // 父 raise
        fork
            child_comp_run();
            other_work();
        join
        phase.drop_objection(this);   // 如果 child 没有 raise，这里 drop 会立即结束
    endtask
endclass

class child_comp extends uvm_component;
    virtual task main_phase(uvm_phase phase);
        phase.raise_objection(this);  // 子也要 raise
        #500;
        phase.drop_objection(this);
    endtask
endclass
```

### 3.2 set_drain_time 深度理解

```systemverilog
class drain_time_demo extends uvm_test;
    virtual task main_phase(uvm_phase phase);
        // 在 main_phase 结束后，等待额外 200ns 再进入 post_main_phase
        phase.phase_done.set_drain_time(this, 200);
        phase.raise_objection(this);
        #1000;
        phase.drop_objection(this);
    endtask
endclass

// 也可以在组件级别设置
class my_scoreboard extends uvm_scoreboard;
    virtual task main_phase(uvm_phase phase);
        phase.raise_objection(this);
        // drain_time: objection drop 后等待 50ns 清空队列
        uvm_phase::m_current_phase.phase_done.set_drain_time(this, 50);
        // ... 处理数据 ...
        phase.drop_objection(this);
    endtask
endclass
```

### 3.3 objections 状态回调

```systemverilog
// 监控 objection 状态变化
class objection_watcher extends uvm_monitor;
    virtual function void phase_raised(uvm_objection obj, uvm_objection海边 obj_handle, uvm_component comp, int count);
        `uvm_info("OBJ", $sformatf("objection raised by %s, count=%0d", comp.get_full_name(), count), UVM_MEDIUM)
    endfunction

    virtual function void phase_dropped(uvm_objection obj, uvm_objection海边 obj_handle, uvm_component comp, int count);
        `uvm_info("OBJ", $sformatf("objection dropped by %s, count=%0d", comp.get_full_name(), count), UVM_MEDIUM)
    endfunction
endclass
```

### 3.4 超时检测

```systemverilog
// 设置全局超时
class base_test extends uvm_test;
    function new(string name, uvm_component parent);
        super.new(name, parent);
        // 设置 run_phase 超时为 10ms
        uvm_config_db#(time)::set(this, "", "run_timeout", 10ms);
    endfunction

    static time run_timeout = 10ms;  // 默认 9200s 太长，需要设置
endclass

// 或通过命令行
// +UVM_TIMEOUT=10000
```

---

## 4. config_db 深层用法

### 4.1 跨层次传递复杂对象

```systemverilog
// 传递配置对象
class my_config extends uvm_object;
    rand int item_count;
    rand int max_payload;
    rand bit [3:0] priority;

    `uvm_object_utils_begin(my_config)
        `uvm_field_int(item_count, UVM_ALL_ON)
        `uvm_field_int(max_payload, UVM_ALL_ON)
        `uvm_field_int(priority, UVM_ALL_ON)
    `uvm_object_utils_end
endclass

// set (在 test 或 env 中)
class my_test extends uvm_test;
    virtual function void build_phase(uvm_phase phase);
        my_config cfg;
        cfg = my_config::type_id::create("cfg");
        void'(cfg.randomize());  // 随机配置
        uvm_config_db#(my_config)::set(this, "*", "cfg", cfg);
    endfunction
endclass

// get (在任何组件中)
class my_driver extends uvm_driver;
    my_config cfg;
    virtual function void build_phase(uvm_phase phase);
        if (!uvm_config_db#(my_config)::get(this, "", "cfg", cfg))
            `uvm_fatal("CFG", "my_config not set")
    endfunction
endclass
```

### 4.2 通配符路径与精确路径

```systemverilog
// 通配符: 所有组件的 drv 都能收到
uvm_config_db#(virtual my_if)::set(this, "*", "vif", input_if);

// 精确路径: 只设置给特定组件
uvm_config_db#(virtual my_if)::set(this, "env.agent.drv", "vif", input_if);

// 不好的写法: 容易出现路径不匹配
uvm_config_db#(virtual my_if)::set(this, "uvm_test_top.env.agent.drv", "vif", input_if);
```

### 4.3 config_db 的 get 查找机制

```systemverilog
// config_db 从当前组件向上搜索，直到树根
// 如果 get 时 component="drv", path="agent"
// 实际查找: uvm_test_top.agent.drv.*

// 如果 set 时 component=null, path="env.agent.drv"
// get 时 component="drv", path=""
// 查找路径: uvm_test_top.drv.* (找不到!)
// 正确: get 时 path 应为相对于 drv 的路径，即 "agent"
```

### 4.4 config_int / config_string / config_object

```systemverilog
// 简化版: uvm_config_db#(int)
uvm_config_db#(int)::set(this, "slave", "max_pending", 8);

// 简化版: uvm_config_db#(string)
uvm_config_db#(string)::set(this, "env", "mode", "DEBUG");

// 完整版: uvm_config_db#(uvm_object)
uvm_config_db#(my_config)::set(this, "*", "cfg", cfg);
```

---

## 5. sequence 进阶用法

### 5.1 sequence 的四种启动方式

```systemverilog
// 方式1: start() 显式启动（最灵活）
class manual_start_seq extends uvm_sequence #(my_item);
    virtual task body();
        repeat(10) `uvm_do(req)
    endtask
endclass

task my_env::run_test(uvm_phase phase);
    manual_start_seq seq;
    phase.raise_objection(this);
    seq = manual_start_seq::type_id::create("seq");
    seq.start(sqr);  // 传入 sequencer
    phase.drop_objection(this);
endtask

// 方式2: default_sequence (最常用)
virtual function void build_phase(uvm_phase phase);
    super.build_phase(phase);
    uvm_config_db#(uvm_object_wrapper)::set(
        this, "sqr.main_phase", "default_sequence",
        basic_seq::type_id::get()
    );
endfunction

// 方式3: sequence library (随机选择)
class seq_lib extends uvm_sequence_library #(my_item);
    `uvm_sequence_library_utils(seq_lib)
    // 各种 sequence 已通过 `uvm_add_to_seq_lib 注册
endclass

// 方式4: start_phase_sequence (通过 phase 启动)
virtual function void main_phase(uvm_phase phase);
    uvm_config_db#(uvm_sequence_lib_kind)::set(
        this, "sqr.main_phase", "default_sequence",
        seq_lib::type_id::get()
    );
endfunction
```

### 5.2 sequence library 进阶

```systemverilog
// 定义 sequence
class seq_a extends uvm_sequence #(my_item);
    `uvm_object_utils(seq_a)
    virtual task body();
        `uvm_info("SEQ", "seq_a running", UVM_MEDIUM)
        repeat(5) `uvm_do(req)
    endtask
endclass

class seq_b extends uvm_sequence #(my_item);
    `uvm_object_utils(seq_b)
    virtual task body();
        `uvm_info("SEQ", "seq_b running", UVM_MEDIUM)
        repeat(3) `uvm_do(req)
    endtask
endclass

// 创建 library 并注册
class my_seq_lib extends uvm_sequence_library #(my_item);
    function new(string name = "my_seq_lib");
        super.new(name);
        init_sequence_library();  // 初始化时必须调用
    endfunction
    `uvm_object_utils(my_seq_lib)
    `uvm_sequence_library_utils(my_seq_lib)
endclass

// 将 sequence 添加到 library
class add_to_lib;
    `uvm_add_to_seq_lib(seq_a, my_seq_lib)
    `uvm_add_to_seq_lib(seq_b, my_seq_lib)
endclass

// 设置 library 作为 default_sequence
virtual function void build_phase(uvm_phase phase);
    uvm_config_db#(uvm_object_wrapper)::set(
        this, "sqr.main_phase", "default_sequence",
        my_seq_lib::type_id::get()
    );
endfunction
```

### 5.3 sequence 优先级与仲裁

```systemverilog
// sequencer 仲裁模式
class my_sequencer extends uvm_sequencer #(my_item);
    function new(string name, uvm_component parent);
        super.new(name, parent);
        // 默认: UVM_SEQ_ARB_FIFO (FIFO顺序)
        // 可选: UVM_SEQ_ARB_RANDOM (随机)
        // 可选: UVM_SEQ_ARB_STRICT_RR (严格轮询，按优先级)
        // 可选: UVM_SEQ_ARB_WEIGHTED (加权轮询)
    endfunction
endclass

// 在 sequence 中设置优先级
class prio_seq extends uvm_sequence #(my_item);
    function new(string name = "prio_seq");
        super.new(name);
        set_item_priority(100);  // 默认 100，数值越大优先级越高
    endfunction
endclass
```

### 5.4 lock / unlock / grab

```systemverilog
class lock_seq extends uvm_sequence #(my_item);
    virtual task body();
        // 请求 lock: 等待获取 lock 后独占 sequencer
        lock();  // 其他低优先级 sequence 无法执行

        repeat(10) `uvm_do(req)

        // unlock: 释放独占
        unlock();
    endtask
endclass

class grab_seq extends uvm_sequence #(my_item);
    virtual task body();
        // grab: 立即抢占，不需要等待（更激进）
        grab();
        repeat(5) `uvm_do(req)
        ungrab();
    endtask
endclass
```

---

## 6. layered sequence

### 6.1 为什么需要分层 sequence

```
virtual_sequence (场景层)
    ├── axi_wr_seq     (协议层: AXI 写事务)
    │   └── axi_transaction
    └── config_reg_seq (协议层: 寄存器配置)
        └── reg_transaction
```

### 6.2 实际实现

```systemverilog
// ========== Layer 1: 底层 transaction ==========
class low_level_item extends uvm_sequence_item;
    rand bit [31:0] addr;
    rand bit [31:0] data;
    rand bit        wr;
    `uvm_object_utils(low_level_item)
endclass

// ========== Layer 2: 协议层 sequence ==========
class protocol_seq extends uvm_sequence #(low_level_item);
    `uvm_object_utils(protocol_seq)

    // 模拟 AXI 协议层: 发送 addr beat + N 个 data beat
    virtual task body();
        `uvm_info("PROT", "protocol_seq: sending addr", UVM_MEDIUM)
        `uvm_create(req)
        assert(req.randomize() with { addr[31:28] == 4'hA; wr == 1; })
        `uvm_send(req)
    endtask
endclass

// ========== Layer 3: 场景层 virtual sequence ==========
class virtual_layered_seq extends uvm_sequence;
    `uvm_object_utils(virtual_layered_seq)

    // 持有底层 sequencer 的引用
    uvm_sequencer #(low_level_item) sqr;

    protocol_seq proto_seq;

    virtual function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        proto_seq = protocol_seq::type_id::create("proto_seq", this);
    endfunction

    virtual task body();
        `uvm_info("VIRT", "virtual_layered_seq: starting", UVM_MEDIUM)
        // 启动协议层 sequence
        fork
            proto_seq.start(sqr);
        join

        `uvm_info("VIRT", "virtual_layered_seq: done", UVM_MEDIUM)
    endtask
endclass
```

### 6.3 实际应用：网卡验证场景

```systemverilog
// Layer 0: 硬件信号层
class mac_tx_frame extends uvm_sequence_item;
// ... DA, SA, Length/Type, Payload, FCS ...

// Layer 1: MAC 协议层
class mac_tx_seq extends uvm_sequence #(mac_tx_frame);
    virtual task body();
        // 发送 preamble + SFD + MAC header + payload + FCS
        `uvm_do_with(req, { req.preamble == 7'h55; req.sfd == 8'hD5; })
    endtask
endclass

// Layer 2: 网络协议层 (IP/TCP/UDP)
class tcp_ip_seq extends uvm_sequence #(mac_tx_frame);
    virtual task body();
        // 构造完整以太网帧
        `uvm_do_with(req, {
            req.length_type == 16'h0800;  // IPv4
            req.payload.size() inside {[46:1500]};
        })
    endtask
endclass

// Layer 3: 流量场景层
class traffic_scenario_seq extends uvm_sequence;
    tcp_ip_seq tcp_seq;
    udp_ip_seq udp_seq;

    virtual task body();
        fork
            tcp_seq.start(sqr);
            udp_seq.start(sqr);
        join
    endtask
endclass
```

---

## 7. virtual sequence 最佳实践

### 7.1 多 sequencer 协调

```systemverilog
class multi_agent_vseq extends uvm_sequence;
    `uvm_object_utils(multi_agent_vseq)

    uvm_sequencer #(axi_item)  axi_sqr;
    uvm_sequencer #(reg_item)  reg_sqr;
    uvm_sequencer #(cfg_item)  cfg_sqr;

    virtual task body();
        `uvm_info("VSEQ", "starting multi-agent sequence", UVM_MEDIUM)

        // 场景: 先配置寄存器，再发起 AXI 传输
        fork
            // 并行: AXI 和配置同时跑
            begin
                axi_traffic_seq  axi_seq;
                axi_seq = axi_traffic_seq::type_id::create("axi_seq");
                axi_seq.start(axi_sqr);
            end
            begin
                reg_config_seq   reg_seq;
                reg_seq = reg_config_seq::type_id::create("reg_seq");
                reg_seq.start(reg_sqr);
            end
        join

        // 等待完成后再发下一个场景
        `uvm_do_on_with(cfg_seq, cfg_sqr, { delay == 100; })
    endtask
endclass
```

### 7.2 virtual sequencer 连接

```systemverilog
// 定义 virtual sequencer
class my_virtual_sequencer extends uvm_sequencer;
    uvm_sequencer #(axi_item)  axi_sqr;
    uvm_sequencer #(reg_item)  reg_sqr;

    function new(string name, uvm_component parent);
        super.new(name, parent);
    endfunction
    `uvm_component_utils(my_virtual_sequencer)
endclass

// env 中实例化并 connect
class my_env extends uvm_env;
    my_virtual_sequencer v_sqr;

    virtual function void build_phase(uvm_phase phase);
        v_sqr = my_virtual_sequencer::type_id::create("v_sqr", this);
    endfunction

    virtual function void connect_phase(uvm_phase phase);
        // 关键: 将真实 sequencer 绑定到 virtual sequencer
        v_sqr.axi_sqr = i_agt.sqr;
        v_sqr.reg_sqr = r_agt.sqr;
    endfunction
endclass
```

---
