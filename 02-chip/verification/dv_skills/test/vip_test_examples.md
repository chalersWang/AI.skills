# VIP测试示例（VIP Test Examples）

## 概述

本文档提供VIP使用和测试的实践示例，帮助验证工程师快速掌握VIP应用。

## AXI4 VIP测试示例

### 基本读写测试

```verilog
// AXI4基本读写测试
class axi4_basic_rw_test extends uvm_sequence;
    `uvm_object_utils(axi4_basic_rw_test)
    
    axi_transaction req;
    
    task body();
        // 单次写事务
        `uvm_do_with(req, {
            req.trans_kind == WRITE;
            req.addr == 'h1000;
            req.len == 0;     // 突发长度1
            req.size == 2;    // 4字节
            req.burst == INCR;
        })
        
        // 单次读事务
        `uvm_do_with(req, {
            req.trans_kind == READ;
            req.addr == 'h1000;
            req.len == 0;
        })
    endtask
endclass
```

### 突发传输测试

```verilog
// AXI4突发传输测试
class axi4_burst_test extends uvm_sequence;
    `uvm_object_utils(axi4_burst_test)
    
    task body();
        // INCR4突发
        `uvm_do_with(req, {
            req.trans_kind == WRITE;
            req.addr == 'h1000;
            req.len == 3;      // 4拍
            req.size == 2;     // 4字节
            req.burst == INCR;
        })
        
        // WRAP4突发
        `uvm_do_with(req, {
            req.trans_kind == WRITE;
            req.addr == 'h1000;
            req.len == 3;      // 4拍
            req.size == 2;     // 4字节
            req.burst == WRAP;
        })
    endtask
endclass
```

### Outstanding测试

```verilog
// AXI4 Outstanding测试
class axi4_outstanding_test extends uvm_sequence;
    `uvm_object_utils(axi4_outstanding_test)
    
    task body();
        // 发送多个读请求，不等待响应
        fork
            begin
                `uvm_do_with(req, { req.id == 0; req.addr == 'h1000; })
            end
            begin
                `uvm_do_with(req, { req.id == 1; req.addr == 'h2000; })
            end
            begin
                `uvm_do_with(req, { req.id == 2; req.addr == 'h3000; })
            end
        join
    endtask
endclass
```

## DDR VIP测试示例

### 初始化测试

```verilog
// DDR初始化序列测试
class ddr_init_test extends uvm_sequence;
    `uvm_object_utils(ddr_init_test)
    
    ddr_cmd cmd;
    
    task body();
        // 等待时钟稳定
        #100us;
        
        // CKE使能
        cmd = ddr_cmd::type_id::create("cmd");
        `uvm_do_with(cmd, { cmd.cmd == CKE_ON; })
        
        // MR0配置
        `uvm_do_with(cmd, { cmd.cmd == MRS; cmd.mr_addr == 0; })
        
        // MR1配置
        `uvm_do_with(cmd, { cmd.cmd == MRS; cmd.mr_addr == 1; })
        
        // ZQ校准
        `uvm_do_with(cmd, { cmd.cmd == ZQ_CALIB; })
    endtask
endclass
```

### 读写测试

```verilog
// DDR读写测试
class ddr_rw_test extends uvm_sequence;
    `uvm_object_utils(ddr_rw_test)
    
    ddr_transaction req;
    
    task body();
        // 激活行
        `uvm_do_with(req, {
            req.cmd == ACT;
            req.bank == 0;
            req.row == 'h100;
        })
        
        // 写突发
        `uvm_do_with(req, {
            req.cmd == WRITE;
            req.col == 0;
            req.data.size() == 8;  // BL8
        })
        
        // 读突发
        `uvm_do_with(req, {
            req.cmd == READ;
            req.col == 0;
        })
    endtask
endclass
```

## APB VIP测试示例

```verilog
// APB基本测试
class apb_basic_test extends uvm_sequence;
    `uvm_object_utils(apb_basic_test)
    
    apb_transaction req;
    
    task body();
        // 写寄存器
        `uvm_do_with(req, {
            req.pwrite == 1;
            req.paddr == 'h1000;
            req.pwdata == 'hABCD;
            req.pstrb == 4'b1111;
        })
        
        // 读寄存器
        `uvm_do_with(req, {
            req.pwrite == 0;
            req.paddr == 'h1000;
        })
        
        // 验证读回数据
        assert(req.prdata == 'hABCD) else
            `uvm_error("APB_TEST", "Readback mismatch")
    endtask
endclass
```

## 错误注入测试

```verilog
// VIP错误注入测试
class vip_error_injection_test extends uvm_sequence;
    `uvm_object_utils(vip_error_injection_test)
    
    task body();
        // 注入AXI协议错误
        inject_axi_protocol_error();
        
        // 注入超时错误
        inject_timeout_error();
        
        // 注入错误响应
        inject_error_response();
    endtask
    
    task inject_axi_protocol_error();
        axi_transaction req;
        
        // 发送非对齐地址（当size=3即8字节时）
        req = axi_transaction::type_id::create("req");
        start_item(req);
        assert(req.randomize() with {
            req.addr[2:0] != 0;  // 非对齐
            req.size == 3;       // 8字节
        });
        finish_item(req);
        
        // 期望收到SLVERR或DECERR
    endtask
    
    task inject_timeout_error();
        cfg.vip_timeout_cycles = 100;
        `uvm_do_with(req, { req.wait_response == 1; })
    endtask
endclass
```

## 覆盖率收集

```verilog
// VIP覆盖率收集器
class vip_coverage_collector extends uvm_subscriber;
    `uvm_component_utils(vip_coverage_collector)
    
    // AXI协议覆盖组
    covergroup axi_protocol_cov @(posedge aclk);
        // 传输类型覆盖
        trans_type: coverpoint req.trans_type {
            bins read = {READ};
            bins write = {WRITE};
        }
        
        // 突发类型覆盖
        burst_type: coverpoint req.burst {
            bins fixed = {FIXED};
            bins incr = {INCR};
            bins wrap = {WRAP};
        }
        
        // 突发长度覆盖
        burst_len: coverpoint req.len {
            bins single = {0};
            bins short = {[1:4]};
            bins medium = {[5:16]};
            bins long = {[17:256]};
        }
        
        // 响应覆盖
        resp: coverpoint rsp.resp {
            bins okay = {OKAY};
            bins exokay = {EXOKAY};
            bins slverr = {SLVERR};
            bins decerr = {DECERR};
        }
        
        // 交叉覆盖
        trans_x_resp: cross trans_type, resp;
    endgroup
    
    function new(string name, uvm_component parent);
        super.new(name, parent);
        axi_protocol_cov = new();
    endfunction
    
    function void write(T t);
        req = t;
        axi_protocol_cov.sample();
    endfunction
endclass
```

## 测试配置

```verilog
// VIP测试配置
class vip_test_cfg extends uvm_object;
    `uvm_object_utils(vip_test_cfg)
    
    // AXI配置
    int max_outstanding_write = 8;
    int max_outstanding_read = 8;
    bit enable_protocol_checker = 1;
    
    // DDR配置
    string mem_type = "DDR4";
    int mem_size = 1GB;
    real freq_mhz = 3200;
    
    // APB配置
    bit enable_psel_check = 1;
    bit enable_timeout = 1;
    int timeout_cycles = 1000;
endclass
```

## 总结

VIP测试要点：

1. **基础测试** - 基本读写、突发传输
2. **边界测试** - 地址边界、协议边界
3. **错误注入** - 协议错误、超时、错误响应
4. **覆盖率** - 协议覆盖、功能覆盖
5. **配置管理** - 统一配置、参数化测试
