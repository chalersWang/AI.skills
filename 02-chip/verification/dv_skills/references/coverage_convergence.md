# 覆盖率收敛方法论

> 适用：芯片前端验证，覆盖率sign-off

---

## 目录

1. [覆盖率类型体系](#1-覆盖率类型体系)
2. [代码覆盖率](#2-代码覆盖率)
3. [功能覆盖率](#3-功能覆盖率)
4. [覆盖率收敛四阶段](#4-覆盖率收敛四阶段)
5. [覆盖点分析与缺口填补](#5-覆盖点分析与缺口填补)
6. [漏洞密度与质量评估](#6-漏洞密度与质量评估)
7. [实际案例：覆盖率收敛流程](#7-实际案例覆盖率收敛流程)

---

## 1. 覆盖率类型体系

```
覆盖率
├── 代码覆盖率 (Code Coverage)
│   ├── 行覆盖率 (Line/Statement)
│   ├── 分支覆盖率 (Branch)
│   ├── 条件覆盖率 (Condition/Toggle)
│   ├── 翻转覆盖率 (FSM/Toggle)
│   └── 路径覆盖率 (Path)
│
└── 功能覆盖率 (Functional Coverage)
    ├── 覆盖组 (covergroup)
    ├── 覆盖点 (coverpoint)
    ├── 交叉覆盖 (cross)
    └── 过渡覆盖 (transition)
```

### 1.1 各类型覆盖率的关注点

| 类型 | 目标 | 工具支持 | 局限性 |
|------|------|---------|--------|
| 行覆盖 | >95% | VCS/Questa | 无法反映设计意图 |
| 分支覆盖 | >90% | VCS/Questa | case语句覆盖 |
| 条件覆盖 | >80% | VCS/Questa | 组合逻辑覆盖 |
| 翻转覆盖 | >95% | VCS/Questa | 寄存器/信号翻转 |
| FSM覆盖 | 100% | VCS/Questa | 状态机状态+转换 |
| 功能覆盖 | 100% | VCS/Questa | 需要人工建模 |

---

## 2. 代码覆盖率

### 2.1 行覆盖率 (Line/Statement Coverage)

```systemverilog
// 统计每一行可执行代码是否被触发
// 目标: >95%
// 低于100%通常说明有死代码或未覆盖分支

// 示例: 覆盖率工具会标记哪些行未被执行
always @(posedge clk) begin
    if (req) begin           // Branch: req==0 时跳过
        if (grant) begin    // Branch: grant==0 时跳过
            data_out = data_in;  // Line: 未覆盖如果 grant==0
        end else begin
            data_out = 8'hFF;   // Line: 未覆盖如果 grant==1
        end
    end
end
```

### 2.2 分支覆盖率 (Branch Coverage)

```systemverilog
// if/else, case 语句的每个分支是否执行
// 三项式覆盖 ( condition coverage ): A, B, A&&B, A||B 各分支

// 关键: 条件覆盖与分支覆盖的区别
always @(*) begin
    case (state)
        IDLE:   next = READ;     // branch 1
        READ:   next = WRITE;    // branch 2
        WRITE:  next = IDLE;     // branch 3
        default:next = IDLE;     // branch 4
    endcase
end
// 分支覆盖: 4个分支都要触发
// 行覆盖: 所有语句都要执行
```

### 2.3 翻转覆盖率 (Toggle Coverage)

```systemverilog
// 统计每个信号是否从 0->1 和 1->0 都发生过
// 目标: >95% (关键信号 100%)
// 重要: 时钟和复位信号通常不计入toggle覆盖

// 示例: module 级别的 toggle 覆盖率
module toggle_monitor;
    // 单比特信号: 必须 0->1 和 1->0
    // 多比特信号: 每个 bit 都需要翻转
    // 静态信号: 不翻转不算覆盖率问题
endmodule
```

### 2.4 FSM 覆盖率

```systemverilog
// FSM 覆盖要求:
// 1. 每个状态都被进入
// 2. 每条状态转换都被触发
// 3. 状态机重置路径

// 状态覆盖组
covergroup fsm_cov @(posedge clk);
    state: coverpoint state {
        bins s_idle   = {IDLE};
        bins s_read   = {READ};
        bins s_write  = {WRITE};
        bins s_error  = {ERROR};
    }

    trans: coverpoint $past(state) {
        bins idle_to_read  = (IDLE => READ);
        bins read_to_write = (READ => WRITE);
        bins write_to_idle = (WRITE => IDLE);
        bins any_to_idle   = (IDLE, READ, WRITE, ERROR => IDLE);
    }
endgroup
```

---

## 3. 功能覆盖率

### 3.1 covergroup 基础

```systemverilog
// 覆盖组定义
class my_coverage extends uvm_subscriber #(my_transaction);
    covergroup my_cg;
        // 单点覆盖
        option.per_instance = 1;
        option.name = "my_coverage";

        cp_addr: coverpoint tr.addr {
            bins zero     = {32'h00000000};
            bins low      = {[32'h00000001:32'h0000FFFF]};
            bins mid      = {[32'h00010000:32'h0FFFFFFF]};
            bins high     = {[32'h10000000:32'hFFFFFFFF]};
            bins others   = default;  // 捕获未匹配值
        }

        cp_len: coverpoint tr.len {
            bins short    = {[0:7]};
            bins medium   = {[8:63]};
            bins long     = {[64:255]};
            bins special  = {7, 15, 31, 63, 127, 255};  // 关键值
        }

        // 交叉覆盖
        cross cp_addr, cp_len;
    endgroup

    function new(string name, uvm_component parent);
        super.new(name, parent);
        my_cg = new();  // 覆盖组实例化
    endfunction

    function void write(my_transaction tr);
        this.tr = tr;   // 更新副本
        my_cg.sample();  // 触发采样
    endfunction
endclass
```

### 3.2 覆盖点选项

```systemverilog
covergroup cg_options;
    // 覆盖点 bins 数量限制
    cp_auto: coverpoint tr.val {
        bins small[]  = {[0:15]};      // 自动bins，16个
        bins big      = {[16:255]};   // 单个bins
    }

    // 长度覆盖 bins
    cp_len_banks: coverpoint tr.len {
        bins legal_len[] = {[1:255]};  // 每个值一个bin
        illegal_len      = {0};         // 0是非法值，但被捕获
    }
endgroup

// 类型选项
covergroup cg_type_option;
    option.name = "global_cg";     // 覆盖组名
    option.per_instance = 0;        // 0: 全局共享; 1: 每个实例单独统计
    option.comment = "my coverage"; // 注释
    option.goal = 90;               // 目标 90%
endgroup
```

### 3.3 过渡覆盖 (transition coverage)

```systemverilog
// 时序相关，覆盖值之间的转换
covergroup trans_cov;
    coverpoint tr.cmd {
        // 单值序列: a -> b -> c
        bins seq_abc = (REQ => ACK => DONE);
        // 范围序列: idle 之后任何值
        bins idle_any = (IDLE => READ, WRITE, IDLE);
        // 重复: r1 -> r1 -> r1
        bins repeat_3 = (READ [*3]);
        // goto: READ 之后跳到 IDLE
        bins goto_idle = (READ => IDLE);
    }
endgroup

// 多比特跳转
covergroup toggle_cov;
    coverpoint tr.status {
        bins power_on  = (4'b0000 => 4'b0001);
        bins init      = (4'b0001 => 4'b0010);
        bins running   = (4'b0010 => 4'b0100);
        bins sleep     = (4'b0100 => 4'b0000);
    }
endgroup
```

### 3.4 忽略与非法bins

```systemverilog
covergroup filter_cov;
    // 忽略: 不计入覆盖率计算
    cp_data: coverpoint tr.data {
        bins valid[]    = {[0:99]};
        bins ignore_val = {100};    // 忽略100
        bins ignore_range = {[200:255]};
        ignore_bins ignore_vals = {100, [200:255]};
    }

    // 非法: 遇到时报错（适用于设计保证不会出现的情况）
    cp_op: coverpoint tr.op {
        bins legal_op = {READ, WRITE, IDLE};
        illegal_bins illegal = {RESERVED};  // 非法值出现则报错
    }
endgroup
```

### 3.5 covergroup 采样触发

```systemverilog
// 方式1: 事件触发
covergroup cg_event @(posedge clk);
    cp_data: coverpoint tr.data;
endgroup

// 方式2: 手动采样
covergroup cg_manual;
    cp_data: coverpoint tr.data;
endgroup

class my_monitor extends uvm_monitor;
    function void build_phase(uvm_phase phase);
        // 方式3: 配合 sequence 采样
        cg_manual = new();
    endfunction

    virtual protected task process_item(my_transaction tr);
        // 事件触发: @(event) 隐含采样
        // 手动采样: sample() 调用
        cg_manual.sample();
    endtask
endclass

// 方式3: 条件采样 (with)
covergroup conditional_cg @(posedge clk);
    cp_addr: coverpoint tr.addr with (tr.valid == 1);  // 只采样有效数据
endgroup
```

---

## 4. 覆盖率收敛四阶段

```
阶段1: 定向覆盖 (0→60%)
├── 定向测试用例
├── 核心功能点
└── 快速建立基线

阶段2: 随机扩展 (60→80%)
├── 约束随机验证
├── 随机化边界条件
└── 发现corner case

阶段3: 缺口填补 (80→95%)
├── 覆盖率报告分析
├── 未覆盖bins识别
└── 定向补充测试

阶段4: 边界强化 (95→100%)
├── corner case 枚举
├── 错误注入
└── 极端条件
```

### 4.1 阶段1：定向用例 (Directed Tests)

```systemverilog
// 快速达到基础覆盖
// 每个用例覆盖特定功能点

test_basic_read():
    配置寄存器
    发起单次读
    检查数据正确性
    预期: 基础路径 60%+

test_burst_write():
    配置burst参数
    发起突发写
    检查数据一致性
    预期: burst路径覆盖
```

### 4.2 阶段2：约束随机扩展

```systemverilog
// 使用约束随机大幅扩展覆盖空间
class coverage_driven_seq extends uvm_sequence;
    // 宽约束: 尽可能覆盖大范围
    constraint c_wide {
        addr inside {[0x0000:0xFFFF]};
        len inside {[1:256]};
        size inside {[0:3]};
    }

    // 特定bins: 确保关键值出现
    constraint c_critical {
        // 确保关键值在随机中优先出现
        solve addr before len;
        (addr[15:12] == 4'hA) -> (len inside {[1, 4, 16, 64]});
    }
endclass
```

---

## 5. 覆盖点分析与缺口填补

### 5.1 覆盖率报告解读

```bash
# VCS 生成覆盖率报告
vcs -cm line+branch+fsm+toggle -cm_dir ./cov_work -lca
# 仿真
./simv -cm line+branch -cm_dir ./cov_work
# 合并报告
urg -dir ./cov_work/*.dat -report ./cov_report
# 查看 HTML 报告
firefox ./cov_report/dashboard.html
```

### 5.2 未覆盖bins的处理

```systemverilog
// 覆盖率报告发现: cp_len bins long 未覆盖
// 原因: len 随机到 [64:255] 的概率低

covergroup len_analysis_cg;
    cp_len: coverpoint tr.len {
        // 分析发现: [64:127] 未覆盖，[128:255] 已覆盖
        // 说明 64~127 的测试用例不足
        bins low_mid   = {[64:127]};  // 需要新用例
        bins high      = {[128:255]}; // 已覆盖
        bins short     = {[1:63]};    // 已覆盖
    }
endgroup

// 解决方案1: 调整权重
constraint c_prefer_mid {
    len dist {
        [64:127] := 60,  // 增加权重
        [128:255] := 40
    };
}

// 解决方案2: 添加定向用例
class len_mid_test extends uvm_sequence;
    virtual task body();
        repeat(100) begin
            `uvm_do_with(req, { req.len inside {[64:127]}; })
        end
    endtask
endclass
```

### 5.3 waiver 管理

```systemverilog
// 不可达代码: 设计中保证不会出现的情况
// 需要申请 waiver 并附上说明

// 功能覆盖 waiver 申请格式:
// 文件: coverage_waivers.txt
// Line 100: unreachable - state FSM guarantees this path
// Branch 50: condition `(a && b)` - design constraint a==0 => b==0

// VCS waiver 语法
//urg - waivers:
//  line: ./src/design.v:100 "unreachable code verified by assertion"
//  branch: ./src/design.v:50 "condition impossible by protocol"
```

---

## 6. 漏洞密度与质量评估

### 6.1 漏洞密度指标

```python
# 漏洞密度 = 发现的bug数 / 代码行数 (KLOC)
# 行业参考值:
#   入门项目: 5-10 bugs/KLOC
#   成熟项目: 1-3 bugs/KLOC
#   优秀项目: < 1 bug/KLOC

coverage_report = {
    "total_lines": 50000,           # 代码行数
    "covered_lines": 48500,         # 已覆盖行
    "line_coverage": 97.0,          # 行覆盖率 97%
    "branch_coverage": 91.5,         # 分支覆盖率 91.5%
    "bugs_found": 48,               # 发现的bug数
    "bug_density": 48/50,           # 0.96 bugs/KLOC
    "severity": {
        "critical": 2,              # 严重bug
        "major": 12,                # 主要bug
        "minor": 34                 # 次要bug
    }
}
```

### 6.2 覆盖率质量关系

```
覆盖率 vs 发现bug数 (典型曲线)
100%|           ___
    |          /    ---\  ← 后期增加覆盖率，边际收益急剧下降
 80%|---------/          \____
    |       /                     ← 80-90% 区间收益最高
 60%|------/                          
    |    /
 40%|---/   ← 初期投入大，但快速发现大量bug
    |
  0%|________________________
     0%   50%   80%   90%   100%
              覆盖率
```

### 6.3 覆盖率sign-off标准

| 指标 | 目标 | 说明 |
|------|------|------|
| 行覆盖 | >95% | 核心逻辑必须覆盖 |
| 分支覆盖 | >90% | 所有分支路径 |
| 条件覆盖 | >80% | 组合逻辑 |
| FSM覆盖 | 100% | 状态机全状态+转换 |
| 功能覆盖 | 100% | 所有功能点+cross |
| 翻转覆盖 | >95% | 关键寄存器/信号 |

---

## 7. 实际案例：覆盖率收敛流程

### 7.1 DDR 控制器验证覆盖率收敛

```systemverilog
// DDR 控制器覆盖组设计
class ddr_cov extends uvm_subscriber #(ddr_transaction);
    covergroup ddr_cg @(posedge aclk);
        // 地址覆盖
        cp_addr: coverpoint tr.addr {
            bins row_bank_col = (tr.addr_type == ROW_BANK_COL);
            bins bank_row_col = (tr.addr_type == BANK_ROW_COL);
            // 基于 DDR 地址映射
        }

        // 命令覆盖
        cp_cmd: coverpoint {tr.act, tr.read, tr.write} {
            bins activate = {3'b100};
            bins read     = {3'b010};
            bins write    = {3'b001};
            bins precharge= {3'b001};  // 需要具体定义
            bins refresh  = {3'bxxx};
        }

        // 时序参数覆盖
        cp_timing: coverpoint tr.timing_param {
            bins t_rcd_min  = {tRCD_MIN};   // 关键时序
            bins t_rcd_max  = {tRCD_MAX};
            bins t_cl_min   = {CL_MIN};
            bins t_cl_max   = {CL_MAX};
        }

        // 交叉覆盖: 命令x地址
        cross cp_cmd, cp_addr;
    endgroup
endclass
```

### 7.2 收敛分析示例

```systemverilog
// 覆盖率缺口分析
// 报告: cp_timing.t_rcd_max bin 未覆盖
// 原因: max 值只在压力测试下出现
// 解决方案: 添加压力测试序列

class stress_seq extends uvm_sequence;
    virtual task body();
        // 连续发起最小间隔的 activate 命令
        repeat(100) begin
            `uvm_do_with(req, {
                req.cmd == ACTIVATE;
                req.timing_param inside {[tRCD_MAX:tRCD_MAX+10]};
            })
        end
    endtask
endclass
```

---
