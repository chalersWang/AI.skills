# UVM 核心技术文档

> 提取自 /tmp/dv_docs/uvm_shizhan.pdf

---

## 目录

1. [UVM组件（component）与UVM object](#1-uvm组件component与uvm-object)
2. [factory机制](#2-factory机制)
3. [phase机制](#3-phase机制)
4. [objection机制](#4-objection机制)
5. [sequence机制](#5-sequence机制)
6. [TLM通信](#6-tlm通信)
7. [field automation机制](#7-field-automation机制)
8. [config_db机制](#8-config_db机制)
9. [callback机制](#9-callback机制)
10. [寄存器模型](#10-寄存器模型register-model)

---

## 1. UVM组件（component）与UVM object

### 1.1 核心概念

UVM中有两个基类：**uvm_object** 和 **uvm_component**。

```
uvm_object
    └── uvm_sequence_item (transaction的基类)
    └── 其他uvm_object派生类

uvm_component (派生自uvm_object)
    ├── uvm_driver
    ├── uvm_monitor
    ├── uvm_sequencer
    ├── uvm_agent
    ├── uvm_env
    ├── uvm_scoreboard
    └── uvm_test (测试用例的基类)
```

### 1.2 uvm_component的特点

- **一直存在**：在整个仿真过程中存活
- **参与树形结构**：通过parent参数构建UVM树
- **使用`uvm_component_utils宏注册**：实现factory功能

### 1.3 uvm_object的特点

- **生命周期有限**：用完即可销毁
- **不参与树形结构**：没有parent参数
- **使用`uvm_object_utils宏注册**

### 1.4 常用宏

```systemverilog
// component注册
`uvm_component_utils(MyDriver)

// object注册
`uvm_object_utils(MyTransaction)

// 带field automation的object注册
`uvm_object_utils_begin(MyTransaction)
`uvm_field_int(dmac, UVM_ALL_ON)
`uvm_field_int(smac, UVM_ALL_ON)
`uvm_field_array_int(pload, UVM_ALL_ON)
`uvm_object_utils_end
```

### 1.5 UVM树的构建

```systemverilog
class my_env extends uvm_env;
    my_driver drv;
    
    virtual function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        drv = my_driver::type_id::create("drv", this);  // 必须用create
    endfunction
    
    `uvm_component_utils(my_env)
endclass
```

**重要**：所有uvm_component的实例化**必须**使用`type_id::create()`方式，不能用new()。

---

## 2. factory机制

### 2.1 什么是factory

Factory是UVM的核心机制，允许：
- 根据字符串类名创建类的实例
- 在不修改原有代码的情况下替换类的行为（重载）

### 2.2 Factory注册

```systemverilog
class my_driver extends uvm_driver;
    `uvm_component_utils(my_driver)  // 将类注册到factory表
endclass

class my_transaction extends uvm_sequence_item;
    `uvm_object_utils(my_transaction)  // object使用object_utils
endclass
```

### 2.3 使用factory创建实例

```systemverilog
// 错误方式
drv = new("drv", this);

// 正确方式（factory机制）
drv = my_driver::type_id::create("drv", this);
```

### 2.4 Factory重载

可以在不改变原有代码的情况下替换类的行为：

```systemverilog
// 定义基类
class my_driver extends uvm_driver;
    `uvm_component_utils(my_driver)
endclass

// 派生新类实现重载
class my_new_driver extends my_driver;
    `uvm_component_utils(my_new_driver)
endclass

// 在test中重载
class my_test extends base_test;
    virtual function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        // 将原有的my_driver替换为my_new_driver
        factory.set_type_override_by_name("my_driver", "my_new_driver");
    endfunction
endclass
```

### 2.5 factory的本质

Factory机制的核心是一张**注册表**，记录了类名与类的映射关系。当调用`type_id::create()`时，UVM根据类名在这张表中查找并创建实例。

---

## 3. phase机制

### 3.1 phase的分类

| 类型 | phase | 说明 |
|------|-------|------|
| **Function Phase** | build_phase | 实例化组件 |
| | connect_phase | 连接端口 |
| | end_of_elaboration_phase | 细化配置 |
| | start_of_simulation_phase | 仿真开始 |
| | extract_phase | 收集数据 |
| | check_phase | 检查结果 |
| | report_phase | 报告结果 |
| | final_phase | 结束清理 |
| **Task Phase** | run_phase | 主运行phase |
| | reset_phase | 复位 |
| | configure_phase | 配置 |
| | main_phase | 主业务 |
| | shutdown_phase | 关闭 |

### 3.2 phase执行顺序

```
build_phase (自上而下)
    ↓
connect_phase (自下而上)
    ↓
end_of_elaboration_phase
    ↓
start_of_simulation_phase
    ↓
[12个runtime phase并行运行]
    └── pre_reset_phase
    └── reset_phase
    └── post_reset_phase
    └── pre_configure_phase
    └── configure_phase
    └── post_configure_phase
    └── pre_main_phase
    └── main_phase
    └── post_main_phase
    └── pre_shutdown_phase
    └── shutdown_phase
    └── post_shutdown_phase
    ↓
run_phase (与12个runtime phase并行)
    ↓
extract_phase
    ↓
check_phase
    ↓
report_phase
    ↓
final_phase
```

### 3.3 常用phase示例

```systemverilog
class my_driver extends uvm_driver;
    // build_phase: 实例化成员变量、获取config配置
    virtual function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        if(!uvm_config_db#(virtual my_if)::get(this, "", "vif", vif))
            `uvm_fatal("my_driver", "virtual interface must be set")
    endfunction
    
    // connect_phase: 连接端口
    virtual function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
    endfunction
    
    // main_phase: 主要任务（task phase，消耗仿真时间）
    virtual task main_phase(uvm_phase phase);
        while(1) begin
            seq_item_port.get_next_item(req);
            drive_one_pkt(req);
            seq_item_port.item_done();
        end
    endtask
    
    `uvm_component_utils(my_driver)
endclass
```

### 3.4 build_phase执行顺序

build_phase按照**自上而下**（从父到子）的顺序执行。这是为了保证在实例化子组件时，父组件已经存在。

---

## 4. objection机制

### 4.1 基本概念

Objection用于**控制仿真何时结束**。UVM会监视所有objection，只有当所有objection都被撤销后，才会进入下一个phase。

### 4.2 基本使用

```systemverilog
task main_phase(uvm_phase phase);
    phase.raise_objection(this);  // 提起异议
    // ... 执行测试代码 ...
    phase.drop_objection(this);   // 撤销异议
endtask
```

**重要**：`raise_objection`和`drop_objection`必须**成对出现**。

### 4.3 objection与仿真时间

- 如果某phase没有任何objection被提起，UVM会**立即跳过**这个phase
- 如果有objection，UVM会等待所有objection被撤销后才进入下一个phase

### 4.4 在sequence中控制objection

```systemverilog
virtual task body();
    // 推荐方式：在sequence中控制objection
    if(starting_phase != null)
        starting_phase.raise_objection(this);
    
    repeat(10) begin
        `uvm_do(m_trans)
    end
    
    if(starting_phase != null)
        starting_phase.drop_objection(this);
endtask
```

### 4.5 drain_time

设置drain_time可以延长objection撤销后的等待时间：

```systemverilog
task base_test::main_phase(uvm_phase phase);
    phase.phase_done.set_drain_time(this, 200);  // 等待200时间单位
endtask
```

### 4.6 objection调试

```bash
<sim command> +UVM_OBJECTION_TRACE
```

---

## 5. sequence机制

### 5.1 sequence基础

Sequence用于**产生激励**，是UVM中最强大的机制之一。

```systemverilog
class my_sequence extends uvm_sequence #(my_transaction);
    my_transaction m_trans;
    
    virtual task body();
        repeat(10) begin
            `uvm_do(m_trans)  // 创建、随机化、发送transaction
        end
    endfunction
    
    `uvm_object_utils(my_sequence)
endclass
```

### 5.2 sequencer

Sequencer负责管理sequence的仲裁和调度：

```systemverilog
class my_sequencer extends uvm_sequencer #(my_transaction);
    function new(string name, uvm_component parent);
        super.new(name, parent);
    endfunction
    `uvm_component_utils(my_sequencer)
endclass
```

### 5.3 driver与sequencer的连接

```systemverilog
// 在agent中连接
function void my_agent::connect_phase(uvm_phase phase);
    super.connect_phase(phase);
    if (is_active == UVM_ACTIVE) begin
        drv.seq_item_port.connect(sqr.seq_item_export);
    end
endfunction

// driver从sequencer获取transaction
task my_driver::main_phase(uvm_phase phase);
    while(1) begin
        seq_item_port.get_next_item(req);
        drive_one_pkt(req);
        seq_item_port.item_done();
    end
endtask
```

### 5.4 启动sequence

**方式一**：手动启动
```systemverilog
task my_env::main_phase(uvm_phase phase);
    my_sequence seq;
    phase.raise_objection(this);
    seq = my_sequence::type_id::create("seq");
    seq.start(i_agt.sqr);
    phase.drop_objection(this);
endtask
```

**方式二**：default_sequence（推荐）
```systemverilog
virtual function void build_phase(uvm_phase phase);
    super.build_phase(phase);
    uvm_config_db#(uvm_object_wrapper)::set(this,
        "i_agt.sqr.main_phase",
        "default_sequence",
        my_sequence::type_id::get());
endfunction
```

### 5.5 常用sequence宏

| 宏 | 说明 |
|----|------|
| `uvm_do(tr) | 创建、随机化、发送transaction |
| `uvm_do_with(tr, {constraints}) | 带约束的uvm_do |
| `uvm_create(tr) | 仅创建transaction |
| `uvm_send(tr) | 发送已创建的transaction |
| `uvm_rand_send(tr) | 随机化后发送 |
| `uvm_rand_send_with(tr, {constraints}) | 带约束的随机发送 |

### 5.6 start_item与finish_item

不使用宏，手动控制transaction发送：

```systemverilog
virtual task body();
    repeat(10) begin
        tr = new("tr");
        start_item(tr);
        assert(tr.randomize() with {tr.pload.size == 200;});
        finish_item(tr);
    end
endtask
```

### 5.7 pre_do、mid_do、post_do

在uvm_do过程中插入自定义代码：

```systemverilog
class case0_sequence extends uvm_sequence #(my_transaction);
    virtual task pre_do(bit is_item);
        #100;
    endtask
    
    virtual function void mid_do(uvm_sequence_item this_item);
        // 在transaction发送前做处理
    endfunction
    
    virtual function void post_do(uvm_sequence_item this_item);
        // 在transaction发送后做处理
    endfunction
endclass
```

### 5.8 嵌套sequence

在一个sequence中启动其他sequence：

```systemverilog
class case0_sequence extends uvm_sequence #(my_transaction);
    virtual task body();
        crc_seq cseq;
        long_seq lseq;
        repeat(10) begin
            `uvm_do(cseq)
            `uvm_do(lseq)
        end
    endfunction
endclass
```

### 5.9 virtual sequence

用于协调多个sequencer：

```systemverilog
class virtual_sequence extends uvm_sequence;
    virtual task body();
        // 启动多个sequencer上的sequence
        fork
            seq1.start(sequencer1);
            seq2.start(sequencer2);
        join
    endfunction
endclass
```

### 5.10 sequence library

将多个sequence组合成一个可随机选择的库：

```systemverilog
class simple_seq_library extends uvm_sequence_library#(my_transaction);
    function new(string name= "simple_seq_library");
        super.new(name);
        init_sequence_library();
    endfunction
    `uvm_object_utils(simple_seq_library)
    `uvm_sequence_library_utils(simple_seq_library)
endclass

// 将sequence加入library
class seq0 extends uvm_sequence#(my_transaction);
    `uvm_object_utils(seq0)
    `uvm_add_to_seq_lib(seq0, simple_seq_library)
endclass
```

---

## 6. TLM通信

### 6.1 TLM端口类型

| 类型 | 说明 |
|------|------|
| uvm_blocking_put_port | 阻塞发送 |
| uvm_nonblocking_put_port | 非阻塞发送 |
| uvm_blocking_get_port | 阻塞获取 |
| uvm_nonblocking_get_port | 非阻塞获取 |
| uvm_analysis_port | 广播式发送 |
| uvm_analysis_export | 广播式接收 |
| uvm_analysis_imp | 实现analysis接收（需定义write函数） |

### 6.2 基本连接示例

```systemverilog
// component A 发送
class A extends uvm_component;
    uvm_blocking_put_port #(my_transaction) A_port;
    
    virtual function void build_phase(uvm_phase phase);
        A_port = new("A_port", this);
    endfunction
    
    task main_phase(uvm_phase phase);
        repeat(10) begin
            tr = new("tr");
            assert(tr.randomize());
            A_port.put(tr);
        end
    endfunction
endclass

// component B 接收
class B extends uvm_component;
    uvm_blocking_put_export #(my_transaction) B_export;
    
    virtual function void build_phase(uvm_phase phase);
        B_export = new("B_export", this);
    endfunction
    
    task main_phase(uvm_phase phase);
        my_transaction tr;
        B_export.get(tr);
    endfunction
endclass

// 连接
function void my_env::connect_phase(uvm_phase phase);
    A_inst.A_port.connect(B_inst.B_export);
endfunction
```

### 6.3 FIFO通信

使用FIFO进行解耦：

```systemverilog
class my_env extends uvm_env;
    uvm_tlm_analysis_fifo #(my_transaction) agt_mdl_fifo;
    
    virtual function void build_phase(uvm_phase phase);
        agt_mdl_fifo = new("agt_mdl_fifo", this);
    endfunction
    
    virtual function void connect_phase(uvm_phase phase);
        i_agt.ap.connect(agt_mdl_fifo.analysis_export);
        mdl.port.connect(agt_mdl_fifo.blocking_get_export);
    endfunction
endclass
```

### 6.4 analysis_port广播

一个analysis_port可以连接多个IMP：

```systemverilog
// 定义多个接收者
class B extends uvm_component;
    uvm_analysis_imp #(my_transaction, B) B_imp;
    function void write(my_transaction tr);
        // 处理transaction
    endfunction
endclass

class C extends uvm_component;
    uvm_analysis_imp #(my_transaction, C) C_imp;
    function void write(my_transaction tr);
        // 处理transaction
    endfunction
endclass

// 连接（广播）
function void my_env::connect_phase(uvm_phase phase);
    A_inst.A_ap.connect(B_inst.B_imp);
    A_inst.A_ap.connect(C_inst.C_imp);
endfunction
```

### 6.5 多个IMP的处理

使用`uvm_analysis_imp_decl`宏处理多个analysis端口：

```systemverilog
`uvm_analysis_imp_decl(_monitor)
`uvm_analysis_imp_decl(_model)

class my_scoreboard extends uvm_scoreboard;
    uvm_analysis_imp_monitor#(my_transaction, my_scoreboard) monitor_imp;
    uvm_analysis_imp_model#(my_transaction, my_scoreboard) model_imp;
    
    extern function void write_monitor(my_transaction tr);
    extern function void write_model(my_transaction tr);
endclass

function void my_scoreboard::write_model(my_transaction tr);
    expect_queue.push_back(tr);
endfunction

function void my_scoreboard::write_monitor(my_transaction tr);
    // 比较逻辑
endfunction
```

---

## 7. field automation机制

### 7.1 目的

自动实现`copy`、`compare`、`print`、`pack`、`unpack`等函数，无需手动编写。

### 7.2 常用宏

```systemverilog
`uvm_object_utils_begin(T)
`uvm_field_int(var, flags)
`uvm_field_real(var, flags)
`uvm_field_string(var, flags)
`uvm_field_array_int(array, flags)
`uvm_field_queue_int(queue, flags)
`uvm_object_utils_end
```

### 7.3 示例

```systemverilog
class my_transaction extends uvm_sequence_item;
    rand bit[47:0] dmac;
    rand bit[47:0] smac;
    rand bit[15:0] ether_type;
    rand byte pload[];
    rand bit[31:0] crc;
    
    `uvm_object_utils_begin(my_transaction)
        `uvm_field_int(dmac, UVM_ALL_ON)
        `uvm_field_int(smac, UVM_ALL_ON)
        `uvm_field_int(ether_type, UVM_ALL_ON)
        `uvm_field_array_int(pload, UVM_ALL_ON)
        `uvm_field_int(crc, UVM_ALL_ON)
    `uvm_object_utils_end
endclass
```

### 7.4 使用自动生成的函数

```systemverilog
my_transaction tr1, tr2;
tr1 = new("tr1");
tr2 = new("tr2");

// 复制
tr2.copy(tr1);

// 比较
if(tr1.compare(tr2))
    `uvm_info("PASS", "compare passed", UVM_LOW)

// 打印
tr1.print();

// 打包/解包
byte unsigned data_q[];
tr1.pack_bytes(data_q);      // 打包
tr2.unpack_bytes(data_q);    // 解包
```

### 7.5 flags说明

| Flag | 说明 |
|------|------|
| UVM_ALL_ON | 默认值，所有操作都使能 |
| UVM_NOPACK | 不打包 |
| UVM_NOCOMPARE | 不比较 |
| UVM_NOPRINT | 不打印 |
| UVM_NORECOPY | 不重新复制 |
| UVM_NOREFLARE | 不反射 |

---

## 8. config_db机制

### 8.1 用途

Config_db用于在不同组件之间传递配置参数，特别是virtual interface。

### 8.2 set和get

```systemverilog
// 在top_tb中设置
initial begin
    uvm_config_db#(virtual my_if)::set(null, "uvm_test_top.drv", "vif", input_if);
end

// 在driver中获取
virtual function void build_phase(uvm_phase phase);
    super.build_phase(phase);
    if(!uvm_config_db#(virtual my_if)::get(this, "", "vif", vif))
        `uvm_fatal("my_driver", "virtual interface must be set for vif!!!")
endfunction
```

### 8.3 set/get参数说明

```systemverilog
// set(component, path, field_name, value)
// get(component, path, field_name, variable)

// component: 设置或获取数据的组件的指针
// path: 相对于component的路径
// field_name: 字段名（字符串）
// value: 要设置的值或存放获取值的变量
```

### 8.4 路径规则

- `null`作为第一个参数表示从树根(uvm_test_top)开始查找
- 路径是相对于set的第一个参数的
- get的第一个参数是获取者的指针，路径相对于获取者

### 8.5 通配符支持

```systemverilog
// 使用通配符
uvm_config_db#(virtual my_if)::set(null, "uvm_test_top.*", "vif", input_if);
```

### 8.6 跨层次设置

```systemverilog
// 在env中设置，driver中获取
virtual function void build_phase(uvm_phase phase);
    super.build_phase(phase);
    uvm_config_db#(int)::set(this, "drv", "var", 100);
endfunction

// 在driver中获取
virtual function void build_phase(uvm_phase phase);
    int var;
    super.build_phase(phase);
    if(!uvm_config_db#(int)::get(this, "", "var", var))
        `uvm_warning("my_driver", "var not set")
endfunction
```

---

## 9. callback机制

### 9.1 为什么需要callback

在不修改原始类的情况下，向其添加自定义行为，用于：
- 测试用例扩展
- VIP定制
- 异常用例构建

### 9.2 callback实现步骤

**VIP开发者**：
```systemverilog
// 1. 定义callback类
class A extends uvm_callback;
    virtual task pre_tran(my_driver drv, ref my_transaction tr);
    endtask
endclass

// 2. 声明callback池
typedef uvm_callbacks#(my_driver, A) A_pool;

// 3. 在目标类中注册
class my_driver extends uvm_driver;
    `uvm_component_utils(my_driver)
    `uvm_register_cb(my_driver, A)
    
    task main_phase(uvm_phase phase);
        while(1) begin
            seq_item_port.get_next_item(req);
            `uvm_do_callbacks(my_driver, A, pre_tran(this, req))
            drive_one_pkt(req);
            seq_item_port.item_done();
        end
    endtask
endclass
```

**VIP使用者**：
```systemverilog
// 1. 派生callback类
class my_callback extends A;
    virtual task pre_tran(my_driver drv, ref my_transaction tr);
        `uvm_info("my_callback", "this is pre_tran task", UVM_MEDIUM)
    endtask
    `uvm_object_utils(my_callback)
endclass

// 2. 在test中实例化并添加到池
function void my_case0::connect_phase(uvm_phase phase);
    my_callback my_cb;
    super.connect_phase(phase);
    my_cb = my_callback::type_id::create("my_cb");
    A_pool::add(env.i_agt.drv, my_cb);
endfunction
```

### 9.3 callback与factory的关系

- **Factory**：替换整个类
- **Callback**：在类的特定位置插入代码

两者可以结合使用，实现更强的扩展性。

---

## 10. 寄存器模型（register model）

### 10.1 为什么需要寄存器模型

- 方便配置DUT寄存器
- 支持前门和后门访问
- 与reference model集成

### 10.2 简单寄存器模型

```systemverilog
class my_reg extends uvm_reg;
    rand uvm_reg_field reg_data;
    
    virtual function void build();
        reg_data = uvm_reg_field::type_id::create("reg_data");
        reg_data.configure(this, 32, 0, "RW", 0, 'h0, 1, 0, 0);
    endfunction
    
    `uvm_object_utils(my_reg)
endclass

class my_reg_block extends uvm_reg_block;
    my_reg r0;
    
    virtual function void build();
        r0 = my_reg::type_id::create("r0");
        r0.configure(this);
        r0.build();
        
        default_map.add_reg(r0, 'h9, "RW");
        default_map.configure(this, 0, 0);
    endfunction
    
    `uvm_object_utils(my_reg_block)
endclass
```

### 10.3 前门访问

通过总线协议访问寄存器：

```systemverilog
// 在sequence中使用
class reg_sequence extends uvm_sequence;
    virtual task body();
        // 读寄存器
        rgm.r0.read(status, value);
        // 写寄存器
        rgm.r0.write(status, 'h55);
    endtask
endclass
```

### 10.4 后门访问

通过DPI/VPI直接访问DUT信号：

```systemverilog
// 设置hdl路径
rgm.r0.add_hdl_path("tb_top.dut.reg");

// 后门写
rgm.r0.write(status, 'hFF, UVM_BACKDOOR);

// 后门读
rgm.r0.read(status, value, UVM_BACKDOOR);
```

### 10.5 寄存器模型的集成

```systemverilog
class my_env extends uvm_env;
    my_reg_block rgm;
    
    virtual function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        rgm = my_reg_block::type_id::create("rgm", this);
        rgm.build();
        rgm.set_hdl_path_root("tb_top");
    endfunction
endclass
```

### 10.6 期望值与镜像值

- **期望值(desired)**：通过randomize期望寄存器达到的值
- **镜像值(mirrored)**：当前DUT中实际的值

```systemverilog
// 更新镜像值
rgm.r0.predict('h55);

// 更新期望值
rgm.r0.set('hFF);

// 将期望值更新到DUT并同步镜像值
rgm.r0.update(status);
```

---

## 附录：关键概念速查

### UVM树的构建原则
1. 所有component使用`type_id::create()`实例化
2. build_phase按自上而下顺序执行
3. connect_phase按自下而上顺序执行

### 宏速查
| 宏 | 用途 |
|----|------|
| `uvm_component_utils | 注册component到factory |
| `uvm_object_utils | 注册object到factory |
| `uvm_object_utils_begin/end | 注册object并启用field automation |
| `uvm_do | 创建并发送transaction |
| `uvm_register_cb | 注册callback |
| `uvm_do_callbacks | 调用callback |

### Phase执行顺序
- **Function phase**：build(自上而下) → connect(自下而上) → 其他
- **Task phase**：12个runtime phase并行运行

---

*文档生成于 2026-05-09，从《UVM实战》提取关键章节内容*