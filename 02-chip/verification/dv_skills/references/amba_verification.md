# AMBA协议验证指南（AMBA Verification）

## 概述

AMBA（Advanced Microcontroller Bus Architecture）是ARM公司定义的片上互连标准。本文档覆盖APB、AHB、AXI等主要AMBA协议的验证要点。

## AMBA协议家族

```
AMBA协议演进
├── APB (Advanced Peripheral Bus)
│   ├── 简单、低功耗
│   └── 用于外设配置接口
│
├── AHB (Advanced High-performance Bus)
│   ├── 高性能、同步总线
│   └── 用于处理器和DMA
│
├── AXI (Advanced eXtensible Interface)
│   ├── 高性能、非阻塞
│   └── 现代SoC互连标准
│
├── ACE (AXI Coherency Extensions)
│   ├── 缓存一致性
│   └── 用于多核系统
│
└── CHI (Coherent Hub Interface)
    ├── 层次化、复杂
    └── 最新一代互连
```

## APB协议验证

### APB信号

```verilog
// APB接口信号
| Signal     | Direction | Description          |
|-------------|-----------|----------------------|
| PCLK        | Input     | 时钟                 |
| PRESETn     | Input     | 复位（低有效）       |
| PSELx       | Input     | 选择信号             |
| PENABLE     | Input     | 使能信号             |
| PADDR[31:0] | Input     | 地址                 |
| PPROT[2:0]  | Input     | 保护类型             |
| PWRITE      | Input     | 写/读控制            |
| PSTRB[3:0]  | Input     | 字节使能             |
| PWDATA[31:0]| Input     | 写数据               |
| PRDATA[31:0]| Output    | 读数据               |
| PREADY      | Output    | 准备信号（APB3+）    |
| PSLVERR     | Output    | 错误响应（APB3+）    |
```

### APB验证检查点

```verilog
// APB协议检查
property apb_setup_phase;
    @(posedge PCLK) disable iff (!PRESETn)
    $rose(PSELx) |-> ##1 !PENABLE;
endproperty

property apb_access_phase;
    @(posedge PCLK) disable iff (!PRESETn)
    (PSELx && PENABLE) |-> ##1 (PREADY || 1);
endproperty

property apb_write_data_stable;
    @(posedge PCLK) disable iff (!PRESETn)
    (PSELx && PENABLE && PWRITE) |-> $stable(PWDATA) throughout (PSELx && PENABLE);
endproperty
```

### APB验证测试点

```markdown
## APB验证checklist

### 基本功能
- [ ] 单次写事务
- [ ] 单次读事务
- [ ] 连续读写操作
- [ ] PSEL/PENABLE时序

### 边界条件
- [ ] 最大地址边界
- [ ] 最小地址边界
- [ ] PSTRB所有组合

### 错误场景
- [ ] 无PREADY超时（APB3+）
- [ ] PSLVERR响应

### 时序验证
- [ ] Setup phase最小一个周期
- [ ] 访问phase可延长
```

## AHB协议验证

### AHB信号

```verilog
// AHB接口信号
| Signal       | Direction | Description          |
|--------------|-----------|----------------------|
| HCLK         | Input     | 时钟                 |
| HRESETn      | Input     | 复位（低有效）       |
| HADDR[31:0]  | Input     | 地址                 |
| HTRANS[1:0]  | Input     | 传输类型             |
| HWRITE       | Input     | 写/读控制            |
| HSIZE[2:0]   | Input     | 数据宽度             |
| HBURST[2:0]  | Input     | 突发类型             |
| HPROT[3:0]   | Input     | 保护类型             |
| HWDATA[31:0] | Input     | 写数据               |
| HRDATA[31:0] | Output    | 读数据               |
| HREADY       | Output    | 从机准备好           |
| HRESP        | Output    | 响应类型             |
```

### HTRANS类型

```verilog
typedef enum bit [1:0] {
    IDLE    = 2'b00,   // 空闲
    BUSY    = 2'b01,   // 忙（突发中）
    NONSEQ  = 2'b10,   // 非顺序传输
    SEQ     = 2'b11    // 顺序传输（突发中）
} htrans_e;
```

### AHB突发类型

```verilog
typedef enum bit [2:0] {
    SINGLE  = 3'b000,  // 单次传输
    INCR    = 3'b001,  // 增量突发
    WRAP4   = 3'b010,  // 4拍回环突发
    INCR4   = 3'b011,  // 4拍增量突发
    WRAP8   = 3'b100,  // 8拍回环突发
    INCR8   = 3'b101,  // 8拍增量突发
    WRAP16  = 3'b110,  // 16拍回环突发
    INCR16  = 3'b111   // 16拍增量突发
} hburst_e;
```

### AHB验证检查点

```verilog
// AHB协议检查
property ahb_address_phase;
    @(posedge HCLK) disable iff (!HRESETn)
    (HTRANS != IDLE && HTRANS != BUSY) |-> $stable(HADDR) throughout (HREADY);
endproperty

property ahb_hready_response;
    @(posedge HCLK)
    HREADY == 1 |-> (HRESP inside {OKAY, ERROR});
endproperty

property ahb_burst_alignment;
    @(posedge HCLK) disable iff (!HRESETn)
    (HBURST == WRAP4 && HSIZE == WORD) |-> (HADDR[2:0] == 0);
endproperty
```

### AHB验证测试用例

```verilog
// AHB基本测试序列
class ahb_basic_test extends uvm_sequence;
    task body();
        // SINGLE传输
        single_read_write();
        
        // 增量突发
        incr_burst_test();
        
        // 回环突发
        wrap_burst_test();
        
        // 错误响应
        error_response_test();
    endtask
    
    task single_read_write();
        `uvm_do_with(req, {
            req.trans == NONSEQ;
            req.burst == SINGLE;
            req.write == 1;
            req.size == WORD;
        })
    endtask
    
    task incr_burst_test();
        `uvm_do_with(req, {
            req.trans == NONSEQ;
            req.burst == INCR4;
            req.len == 4;
            req.write == 1;
        })
    endtask
endclass
```

## AXI协议验证（重点）

### AXI通道

```
AXI架构
├── 写地址通道 (AW)
├── 写数据通道 (W)
├── 写响应通道 (B)
├── 读地址通道 (AR)
└── 读数据通道 (R)
```

### AXI信号定义

```verilog
// 全局信号
| Signal  | Description |
|---------|-------------|
| ACLK    | 时钟       |
| ARESETn | 复位       |

// 写地址通道
| Signal     | Width | Description          |
|------------|-------|----------------------|
| AWID       | 4     | 事务ID               |
| AWADDR     | 32    | 地址                 |
| AWLEN      | 8     | 突发长度             |
| AWSIZE     | 3     | 突发尺寸             |
| AWBURST    | 2     | 突发类型             |
| AWLOCK     | 1     | 锁类型               |
| AWCACHE    | 4     | 缓存属性             |
| AWPROT     | 3     | 保护属性             |
| AWQOS      | 4     | QoS                  |
| AWVALID    | 1     | 地址有效             |
| AWREADY    | 1     | 地址准备好           |

// 写数据通道
| Signal   | Width | Description   |
|----------|-------|---------------|
| WID      | 4     | 数据ID        |
| WDATA    | 32    | 写数据        |
| WSTRB    | 4     | 字节使能      |
| WLAST    | 1     | 最后数据拍    |
| WVALID   | 1     | 数据有效      |
| WREADY   | 1     | 数据准备好    |

// 写响应通道
| Signal  | Width | Description   |
|---------|-------|---------------|
| BID     | 4     | 响应ID        |
| BRESP   | 2     | 响应类型      |
| BVALID  | 1     | 响应有效      |
| BREADY  | 1     | 响应准备好    |
```

### AXI突发类型

```verilog
typedef enum bit [1:0] {
    FIXED   = 2'b00,  // 固定突发
    INCR    = 2'b01,  // 增量突发
    WRAP    = 2'b10   // 回环突发
} axi_burst_e;

// AWSIZE编码
| Value | Size  | Bytes |
|-------|-------|-------|
| 000   | 1B    | 1     |
| 001   | 2B    | 2     |
| 010   | 4B    | 4     |
| 011   | 8B    | 8     |
| 100   | 16B   | 16    |
| 101   | 32B   | 32    |
| 110   | 64B   | 64    |
| 111   | 128B  | 128   |
```

### AXI验证重点

#### 1. 握手时序

```verilog
// VALID/READY时序规则
// 1. VALID在READY之前或同时拉高
// 2. VALID拉高后必须保持直到READY
// 3. 不得依赖READY的上升沿

property axi_write_addr_handshake;
    @(posedge ACLK) disable iff (!ARESETn)
    AWVALID |-> ##[0:$] AWREADY;
endproperty

property axi_write_data_handshake;
    @(posedge ACLK) disable iff (!ARESETn)
    WVALID && !WLAST |-> ##[0:$] WREADY;
endproperty

property axi_write_resp_handshake;
    @(posedge ACLK) disable iff (!ARESETn)
    BVALID |-> ##[0:$] BREADY;
endproperty
```

#### 2. 地址对齐

```verilog
// 地址对齐检查
property axi_addr_alignment;
    @(posedge ACLK) disable iff (!ARESETn)
    AWVALID && AWREADY |-> 
        (AWADDR % (2**AWSIZE) == 0) ||
        (AWBURST == FIXED);
endproperty
```

#### 3. 突发长度约束

```verilog
// AXI4突发长度约束
property axi_burst_len_incr;
    @(posedge ACLK) disable iff (!ARESETn)
    AWVALID && AWREADY && (AWBURST == INCR) |->
        (AWLEN inside {[0:255]});
endproperty

property axi_burst_len_wrap;
    @(posedge ACLK) disable iff (!ARESETn)
    AWVALID && AWREADY && (AWBURST == WRAP) |->
        (AWLEN inside {1, 2, 4, 8, 16});
endproperty
```

#### 4. WLAST信号

```verilog
// WLAST必须在突发最后一拍拉高
property axi_wlast_assertion;
    @(posedge ACLK) disable iff (!ARESETn)
    WVALID && WLAST |-> WLAST;  // WLAST只能为1
endproperty

property axi_wlast_timing;
    @(posedge ACLK) disable iff (!ARESETn)
    WVALID && !WLAST |-> ##[0:$] (WVALID && WLAST);
endproperty
```

### AXI验证测试用例

```verilog
// AXI验证测试序列
class axi_vip_seq extends uvm_sequence;
    
    // 1. 基本读写测试
    task basic_rw_test();
        // 单次写
        `uvm_do_with(wr_req, {
            wr_req.addr == 'h1000;
            wr_req.len == 0;
            wr_req.size == 2;
            wr_req.burst == INCR;
        })
        
        // 单次读
        `uvm_do_with(rd_req, {
            rd_req.addr == 'h1000;
            rd_req.len == 0;
        })
    endtask
    
    // 2. 突发传输测试
    task burst_test();
        // INCR4突发
        `uvm_do_with(wr_req, {
            wr_req.addr == 'h1000;
            wr_req.len == 3;  // 4拍
            wr_req.size == 2; // 4字节
            wr_req.burst == INCR;
        })
        
        // WRAP4突发
        `uvm_do_with(wr_req, {
            wr_req.addr == 'h1000;
            wr_req.len == 3;
            wr_req.size == 2;
            wr_req.burst == WRAP;
        })
    endtask
    
    // 3. Outstanding测试
    task outstanding_test();
        // 发送多个不相关的读请求
        fork
            `uvm_do_with(rd_req, { rd_req.addr == 'h1000; rd_req.id == 0; })
            `uvm_do_with(rd_req, { rd_req.addr == 'h2000; rd_req.id == 1; })
            `uvm_do_with(rd_req, { rd_req.addr == 'h3000; rd_req.id == 2; })
        join
    endtask
    
    // 4. 边界测试
    task boundary_test();
        // 4KB边界测试
        `uvm_do_with(wr_req, {
            wr_req.addr == 'h0FFC;  // 接近4KB边界
            wr_req.len == 3;
            wr_req.burst == INCR;
        })
    endtask
    
    // 5. 错误注入测试
    task error_injection_test();
        // 写非法地址
        `uvm_do_with(wr_req, {
            wr_req.addr == 'hFFFF_0000; // 非法地址
            wr_req.len == 0;
        })
        
        // 检查错误响应
        get_response(rsp);
        assert(rsp.resp inside {SLVERR, DECERR});
    endtask
endclass
```

### AXI响应类型

```verilog
// AXI响应编码
typedef enum bit [1:0] {
    OKAY   = 2'b00,   // 正常成功
    EXOKAY = 2'b01,   // Exclusive成功
    SLVERR = 2'b10,   // 从机错误
    DECERR = 2'b11    // 解码错误
} axi_resp_e;
```

### AXI ID约束

```verilog
// ReadID和WriteID关系
// - AWID和ARID独立编址
// - WID必须与AWID匹配
// - BID响应与AWID匹配
// - RID响应与ARID匹配

property axi_write_id_consistency;
    @(posedge ACLK) disable iff (!ARESETn)
    (WVALID && WREADY) |-> (WID == 0);  // 假设AWID=0
endproperty
```

## AMBA验证Checklist

### APB验证
- [ ] Setup/Access phase时序
- [ ] PWRITE/PREAD信号
- [ ] PSTRB字节使能
- [ ] PREADY延长（APB3+）
- [ ] PSLVERR错误响应（APB3+）

### AHB验证
- [ ] HTRANS传输类型
- [ ] 突发传输连续性
- [ ] HREADY响应时序
- [ ] HRESP错误响应
- [ ] 边界地址对齐

### AXI验证
- [ ] VALID/READY握手
- [ ] 地址对齐
- [ ] 突发长度/尺寸
- [ ] WLAST信号
- [ ] 响应顺序
- [ ] 事务ID一致性
- [ ] 4KB边界
- [ ] Outstanding/Outstanding
- [ ] Exclusive访问
- [ ] 错误响应处理

## 总结

AMBA验证核心要点：

1. **理解协议** - 时序图、信号定义、约束条件
2. **验证时序** - 握手协议、边界条件
3. **覆盖驱动** - 覆盖模型设计、覆盖率收敛
4. **错误注入** - 协议错误、边界错误
5. **系统集成** - 多Master/Slave互连验证
