# EDA 工具使用指南 (VCS / Questa / Verdi)

> 适用：芯片前端验证，EDA工具熟练使用

---

## 目录

1. [VCS UVM 编译与仿真](#1-vcs-uvm-编译与仿真)
2. [Questa UVM 编译与仿真](#2-questa-uvm-编译与仿真)
3. [覆盖率收集](#3-覆盖率收集)
4. [调试技巧](#4-调试技巧)
5. [常见问题与解决方案](#5-常见问题与解决方案)
6. [UVM 消息与日志](#6-uvm-消息与日志)

---

## 1. VCS UVM 编译与仿真

### 1.1 编译选项

```bash
# 基础编译
vcs -sverilog -f filelist.f \
    -ntb_opts uvm-1.2 \
    -cm line+branch+fsm+toggle \
    -o simv

# 常用编译选项
# -sverilog         : SystemVerilog 支持
# -ntb_opts uvm-1.2 : UVM 支持 (不需要 -uvm 标志)
# -cm line+...      : 覆盖率选项
# -l compile.log    : 编译日志
# -debug_pp          : 编译时启用调试信息（用于 DVE/Verdi）
# -k                 : 保留编译文件
# -pvalues+"..."    : 指定参数值
# -timescale=1ns/1ps: 指定时间精度
```

### 1.2 完整编译脚本

```bash
#!/bin/bash
# vcs_compile.sh


UVM_HOME=${UVM_HOME:-/path/to/uvm-1.2}
WORK=work
CM_OPTS="-cm line+branch+fsm+toggle+assert"

# 清理
rm -rf ${WORK} csrc ucli.key

vcs -sverilog \
    -f filelist.f \
    -top top_tb \
    +incdir+./include \
    -ntb_opts uvm-1.2 \
    ${CM_OPTS} \
    -cm_dir ./coverage/vcs.cm \
    -debug_pp \
    -l compile.log \
    -o simv \
    -jobs 8 \
    -queue 16
```

### 1.3 仿真运行

```bash
# 基础仿真
./simv +UVM_TESTNAME=my_test +UVM_VERBOSITY=UVM_MEDIUM

# 带覆盖率
./simv +UVM_TESTNAME=my_test \
    -cm line+branch+fsm+toggle \
    -cm_dir ./coverage/simv.cm

# 带 seed 复现
./simv +UVM_TESTNAME=my_test +ntb_random_seed=12345

# 多测试回归
for test in test1 test2 test3; do
    ./simv +UVM_TESTNAME=${test} -l ${test}.log
done
```

### 1.4 UVM 命令行参数

```bash
# 常用 UVM 参数
+UVM_TESTNAME=my_case0           # 指定测试用例
+UVM_VERBOSITY=UVM_MEDIUM        # 消息级别
+UVM_OBJECTION_TRACE             # objection 追踪
+UVM_PHASE_TRACE                 # phase 追踪
+UVM_CONFIG_DB_TRACE             # config_db 追踪
+UVM_TESTNAME=xxx +UVM_SEQUENCE=yyy  # 指定测试+sequence
+ntb_random_seed=12345           # 随机 seed

# UVM_VERBOSITY 可选值
# UVM_NONE     : 无限制打印
# UVM_LOW      : 低冗余
# UVM_MEDIUM   : 默认级别
# UVM_HIGH     : 高冗余
# UVM_DEBUG    : 最高冗余，包含所有信息
```

---

## 2. Questa UVM 编译与仿真

### 2.1 编译

```bash
# 基础编译 (Questa/ModelSim)
vlog -sv -f filelist.f \
    -work work \
    -uvm \
    -uvmhome ${QUESTA_HOME}/uvm-1.2 \
    -mfcu \
    -lint \
    -writetoplevelscompile.log \
    -timescale 1ns/1ps

# 关键选项:
# -sv         : SystemVerilog
# -work work   : 编译库
# -uvm         : 启用 UVM 支持
# -mfcu       : 允许多个编译单元
# -lint       : 额外的 lint 检查
```

### 2.2 仿真

```bash
# 基础仿真
vsim -c -sv_lib work _my_test \
    -do "run -all; quit" \
    top_tb

# GUI 仿真
vsim -gui -do "run -all" top_tb

# 带覆盖率
vsim -coverage \
    -coveropt 3 \
    -coverbc \
    top_tb

# UVM 仿真
vsim -uvm \
    -uvmhome ${QUESTA_HOME}/uvm-1.2 \
    -do "run -all" \
    top_tb
```

### 2.3 UVM 自动化 (vopt + vsim)

```bash
# Questa UVM flow (推荐)
vlog -sv -work work filelist.f
vopt +acc -work work top_tb -o top_tb_optimized
vsim -c -work work top_tb_optimized \
    +UVM_TESTNAME=my_test \
    +UVM_VERBOSITY=UVM_MEDIUM \
    -do "run -all; quit -f"
```

---

## 3. 覆盖率收集

### 3.1 VCS 覆盖率

```bash
# 编译时启用覆盖率
vcs -sverilog -ntb_opts uvm-1.2 \
    -cm line+branch+fsm+toggle+assert \
    -cm_dir ./cov_dir/simv.cm \
    -o simv

# 仿真时启用覆盖率收集
./simv +UVM_TESTNAME=my_test \
    -cm line+branch+fsm+toggle \
    -cm_dir ./cov_dir/simv.cm

# 合并覆盖率数据库
urg -dir ./cov_dir/*.log -dir ./cov_dir/*.db \
    -report ./cov_report

# 打开 HTML 报告
firefox ./cov_report/dashboard.html
```

### 3.2 Questa 覆盖率

```bash
# 编译时启用
vlog -sv -coverage sbfc filelist.f

# 仿真时收集
vsim -coverage -coveropt 3 top_tb \
    +UVM_TESTNAME=my_test \
    -do "coverage save -onexit cov.ucdb; run -all; quit"

# 合并多个 UCDB
vcover merge cov_merged.ucdb cov1.ucdb cov2.ucdb

# 生成报告
vcover report cov_merged.ucdb -detail -hierarchy -file cov_report.txt
```

### 3.3 覆盖率配置示例

```systemverilog
// 在 TB 中设置覆盖率选项
class my_test extends uvm_test;
    virtual function void end_of_elaboration_phase(uvm_phase phase);
        // 打印覆盖率配置
        `uvm_info("COV", "Coverage collection enabled", UVM_MEDIUM)
    endfunction
endclass

// 代码覆盖率配置
// VCS: -cm line+branch+fsm+toggle
// Questa: -coverage bcestf
// 覆盖项:
//   b = branch
//   c = condition
//   e = expression
//   s = statement
//   t = toggle
//   f = fsm
```

---

## 4. 调试技巧

### 4.1 波形转储配置

```systemverilog
// VCS: 编译时加 -debug_pp 以支持波形
// 仿真时可选择:
//   +vcs+fsdb+region   : 单个 fsdb 文件 (推荐)
//   +fsdb+region       : FSDB dump

// 运行时 dump 波形
./simv +verdi+fsdb+log -l sim.log

// Verdi GUI
verdi -ssf top_tb.fsdb &

// 限制 dump 范围
initial begin
    $fsdbDumpfile("wave.fsdb");
    $fsdbDumpvars(0, top_tb);  // 全部
    $fsdbDumpvars("+module", "tb_top");  // 指定模块
    $fsdbDumpvars("+mda", top_tb);  // 包含多个驱动
end
```

### 4.2 单步调试

```bash
# VCS + DVE
./simv -gui &          # 打开 DVE
# DVE: 断点、波形、调试

# VCS + Verdi
verdi -f filelist.f &  # 直接打开 Verdi
```

### 4.3 UVM 信息追踪

```bash
# 追踪 objection 状态
./simv +UVM_OBJECTION_TRACE

# 追踪 phase 顺序
./simv +UVM_PHASE_TRACE

# 追踪 config_db
./simv +UVM_CONFIG_DB_TRACE

# 打开 UVM GUI
./simv -uvm_debug
```

### 4.4 常见调试命令

```systemverilog
// 在 sequence 中打印信息
`uvm_info("ID", "message", UVM_MEDIUM)
// 级别: UVM_NONE/LOW/MEDIUM/HIGH/DEBUG

// 打印对象内容
tr.print();            // 打印 transaction
rgm.print();           // 打印寄存器模型
env.print();           // 打印环境结构

// 打印树形结构
print_topology();      // UVM 内置函数

// 停止仿真（带信息）
`uvm_fatal("ID", "Fatal message")
`uvm_error("ID", "Error message")
`uvm_warning("ID", "Warning message")
```

---

## 5. 常见问题与解决方案

### 5.1 编译错误

```bash
# 错误: undefined reference to uvm_* stuff
# 原因: 缺少 -ntb_opts uvm-1.2
# 解决: vcs -ntb_opts uvm-1.2

# 错误: UVM_HOME not set
# 解决: export UVM_HOME=/path/to/uvm-1.2

# 错误: randomize() failed
# 原因: 约束无解
# 解决: 检查约束，打印失败信息:
assert(tr.randomize()) else
    `uvm_error("RAND", "randomization failed")
```

### 5.2 仿真问题

```bash
# 仿真立即结束，不跑测试
# 原因: objection 未 raise
# 解决: 检查 test 的 objection

# 仿真挂死
# 原因: sequencer/driver handshake 死锁
# 解决: +UVM_OBJECTION_TRACE 查看

# 随机结果不一致
# 原因: seed 不同
# 解决: +ntb_random_seed=固定值
```

### 5.3 覆盖率问题

```bash
# 覆盖率数据库为空
# 原因: 编译和仿真使用不同的 cm_dir
# 解决: 确保一致

# 行覆盖率为0
# 原因: DUT 代码路径不在 filelist 中
# 解决: 检查 filelist
```

---

## 6. UVM 消息与日志

### 6.1 消息宏使用规范

```systemverilog
// 规范用法
`uvm_info("SEQ", $sformatf("send item %0d", i), UVM_MEDIUM)
// ID 格式: 3字母大写，如 REG, AXI, ENV, SEQ

// 消息级别使用场景
UVM_DEBUG: 调试信息（开发时用）
UVM_HIGH:  详细调试信息
UVM_MEDIUM: 一般信息（默认）
UVM_LOW:   少量关键信息
UVM_NONE:  始终打印（重要告警）

// 报告配置
uvm_report_server server;
server = uvm_report_server::get_server();
server.set_max_quit_count(10);  // 10个error后退出
```

### 6.2 日志保存

```bash
# 保存仿真日志
./simv +UVM_TESTNAME=my_test > sim.log 2>&1

# 带时间戳的日志
./simv +UVM_TESTNAME=my_test | tee sim_$(date +%Y%m%d_%H%M%S).log

# 分离 info/warning/error/fatal
./simv +UVM_TESTNAME=my_test \
    +uvm_set_action=uvm_test_top,UVM_INFO,UVM_DEBUG \
    -l detailed.log
```

### 6.3 自动化回归

```bash
#!/bin/bash
# regress.sh


TESTS="test_basic test_random test_constraint test_error"
CM_DIR="./coverage"
LOG_DIR="./logs"

mkdir -p ${CM_DIR} ${LOG_DIR}

for test in ${TESTS}; do
    echo "Running ${test}..."
    ./simv +UVM_TESTNAME=${test} \
        -cm line+branch+fsm+toggle \
        -cm_dir ${CM_DIR}/${test}.cm \
        -l ${LOG_DIR}/${test}.log

    if [ $? -eq 0 ]; then
        echo "  PASS: ${test}"
    else
        echo "  FAIL: ${test}"
    fi
done

# 合并覆盖率
urg -dir ${CM_DIR}/*.cm -report ${CM_DIR}/merged_report
```

---
