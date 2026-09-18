---
name: vcs-simulation
description: VCS compilation, simulation, and Verdi debugging workflow — compile options, simulation runtime, waveform dumping, coverage collection, debug flags, and Synopsys VCS/Verdi tool integration.
---

# VCS Simulation & Verdi Debugging

You are an expert in Synopsys VCS simulation and Verdi debugging for ASIC/FPGA verification. Follow these workflows and guidelines when working with VCS/Verdi.

## VCS Compilation Flow

### Three-Step Flow (Recommended)

```bash
# Step 1: Analysis (vlogan)
vlogan -sverilog -assert sva +v2k \
  -f flist.f \
  -kdb -l vlogan.log

# Step 2: Elaboration (vcs)
vcs -top tb_top \
  -debug_access+all \
  -lca -kdb \
  -l vcs_elab.log

# Step 3: Simulation (simv)
./simv \
  +UVM_TESTNAME=my_test \
  +UVM_VERBOSITY=UVM_MEDIUM \
  +vcs+fsdbon \
  -l simv.log
```

### One-Step Flow (Simpler)

```bash
vcs -sverilog -full64 \
  -f flist.f \
  -top tb_top \
  -debug_access+all \
  -kdb \
  -l vcs.log
```

### Key Compile Options

| Option | Description |
|--------|-------------|
| `-sverilog` | Enable SystemVerilog |
| `-full64` | 64-bit compilation |
| `-ntb_opts uvm-1.2` | Enable UVM 1.2 |
| `-assert sva` | Enable SVA assertions |
| `-assert dve` | Enable assertion debug in DVE/Verdi |
| `-cm line+cond+fsm+tgl+branch` | Coverage metrics |
| `-lca` | Limited Customer Availability features |
| `-kdb` | Knowledge Database (for Verdi) |
| `-debug_access+all` | Full debug access (waveform, trace) |
| `-debug_access+class` | Class-level debug only (faster) |
| `-debug_access+pp` | Post-process debug (fastest compile) |
| `-debug_region=lib+cell` | Debug external libraries |
| `+define+MACRO=value` | Define macros |
| `+incdir+<dir>` | Include directory |
| `-timescale=1ns/1ps` | Default timescale |

### Debug Access Tradeoffs

```
-debug_access+pp      → fastest compile, waveform only (post-process)
-debug_access+class   → class debug, moderate speed
-debug_access+all     → full debug, slowest compile (use for active debug)
-debug_access+cbk     → callback debug for UVM
```

## VCS Simulation Options

| Option | Description |
|--------|-------------|
| `+UVM_TESTNAME=<test>` | Select UVM test class |
| `+UVM_VERBOSITY=<level>` | UVM verbosity (UVM_LOW/MEDIUM/HIGH/FULL) |
| `+UVM_MAX_QUIT_COUNT=N` | Max errors before exit |
| `+ntb_random_seed=<seed>` | Set random seed (repeatable tests) |
| `+ntb_solver_seed=<seed>` | Set constraint solver seed |
| `+vcs+fsdbon` | Enable FSDB dumping |
| `+fsdb+delta` | Dump delta cycles |
| `+fsdb+region` | Dump UVM phase info |
| `+fsdb+sva_success` | Log assertion successes |

### FSDB Dumping Control

```bash
# Command-line control
./simv +fsdbfile+wave.fsdb +fsdb+fsdbon

# Procedural control in testbench
$fsdbDumpfile("wave.fsdb");
$fsdbDumpvars(0, tb_top);         // Dump all signals (0 = all levels)
$fsdbDumpvars(1, tb_top.dut);    // Dump 1 level under DUT
$fsdbDumpvars(0, tb_top, "all+no_cell");  // All except standard cells
$fsdbDumpSVA(0, tb_top);          // Dump SVA assertions
$fsdbDumpon();                    // Start dumping
$fsdbDumpoff();                   // Stop dumping
```

## Coverage Collection

```bash
# Compile with coverage
vcs -cm line+cond+fsm+tgl+branch -cm_dir cov.vdb

# Run simulation
./simv -cm line+cond+fsm+tgl+branch -cm_dir cov.vdb -cm_name test1

# Merge coverage from multiple tests
urg -dir cov*.vdb -dbname merged_cov -report merged_report

# Generate HTML/XML report
urg -dir merged_cov.vdb -report merged_report -format both
```

| Coverage Type | Flag | Description |
|---------------|------|-------------|
| Line | `-cm line` | Statement/line execution |
| Condition | `-cm cond` | Condition expression coverage |
| FSM | `-cm fsm` | State machine coverage |
| Toggle | `-cm tgl` | Signal toggle 0→1/1→0 |
| Branch | `-cm branch` | Branch coverage (if/case) |
| Assertion | `-cm assert` | SVA assertion coverage |

## Verdi Debugging

### Launching Verdi

```bash
# With FSDB
verdi -ssf wave.fsdb -f flist.f -top tb_top &

# With VCS KDB (source-level debug)
verdi -dbdir simv.daidir -ssf wave.fsdb &
```

### Verdi Workflow Script (vrdi.sh)

```bash
#!/bin/bash
# Load VCS-generated KDB
verdi -dbdir ./simv.daidir \
  -ssf wave.fsdb \
  -top tb_top \
  -f flist.f \
  -nologo \
  +UVM_HIDE_CHILDREN=1 \
  &
```

### Common Verdi Tasks

| Task | Shortcut/Method |
|------|-----------------|
| Open waveform | `nWave` window / File → Open FSDB |
| Search signal | Ctrl+Shift+F → enter signal name |
| Add to waveform | Select signal → Ctrl+W |
| Trace driver | Right-click → Trace Driver (Ctrl+D) |
| Trace load | Right-click → Trace Load (Ctrl+L) |
| Schematic view | Tools → New Schematic → Hierarchy |
| Path view | Tools → Path View |
| UVM hierarchy | UVM Debug → UVM Tree |
| Assertion debug | Assertion → Assertion Report |
| Temporal flow | Right-click → Temporal Flow View |
| Signal value radix | Right-click → Radix → Hex/Bin/Dec |

### Verdi TCL Commands

```tcl
# Automate common tasks
wvOpenWindow -win $_nWave2
wvAddSignal -win $_nWave2 tb_top.clk tb_top.rst_n tb_top.valid
wvSetCursor -win $_nWave2 -snap {200ns}
wvZoomIn -start 0 -end 500ns
wvSaveSignal -win $_nWave2 -file signals.rc
wvRestoreSignal -win $_nWave2 -file signals.rc
```

## Regression & Batch Simulation

### Makefile Template

```makefile
SEED ?= random
TEST ?= my_base_test
COV_DIR ?= cov

comp:
	vcs -sverilog -full64 -ntb_opts uvm-1.2 -assert sva \
	    -f flist.f -top tb_top -kdb -debug_access+pp \
	    -cm line+cond+fsm+tgl -cm_dir $(COV_DIR).vdb -l comp.log

sim:
	./simv +UVM_TESTNAME=$(TEST) +ntb_random_seed=$(SEED) \
	    +UVM_VERBOSITY=UVM_LOW +fsdbfile+wave.fsdb \
	    -cm $(COV_DIR).vdb -cm_name $(TEST)_$(SEED) -l sim.log

clean:
	rm -rf simv* csrc *.log *.fsdb *.vdb DVEfiles verdiLog
```

### Regression Script

```bash
#!/bin/bash
SEED_LIST="1 42 123 4567 99999"
TESTS="test_smoke test_sanity test_stress test_error"

for test in $TESTS; do
  for seed in $SEED_LIST; do
    echo "Running $test with seed $seed"
    make sim TEST=$test SEED=$seed
    if [ $? -ne 0 ]; then
      echo "FAIL: $test seed=$seed" >> regression.log
    else
      echo "PASS: $test seed=$seed" >> regression.log
    fi
  done
done
```

## Common Issues & Debugging

### Compilation Errors

| Error | Solution |
|-------|----------|
| `Undefined macro 'UVM_*'` | Add `-ntb_opts uvm-1.2` |
| `Multiple driver on signal` | Check for conflicting assignments; use `-assert sva` |
| `Package not found` | Check include order, add `+incdir+` |
| `Timescale not specified` | Add `` `timescale 1ns/1ps `` at top of files |

### Simulation Issues

| Issue | Debug Step |
|-------|-----------|
| Zero simulation time | Check that `run_test()` exists; check phase objections |
| X propagation | Use Verdi to trace driver of X; check reset conditions |
| Race conditions | Check NBA (#0) usage; review clock-vs-signal edges |
| Random seed not reproducible | Use `+ntb_random_seed` + `+ntb_solver_seed` |
| FSDB empty | Check `+vcs+fsdbon` or `$fsdbDumpon()` call |

### UVM-Specific

| Issue | Debug |
|-------|-------|
| `uvm_fatal: item not found in factory` | Check `uvm_object_utils` / `uvm_component_utils` |
| `uvm_fatal: virtual interface not set` | Check `uvm_config_db::set()` before `build_phase` |
| Topology issues | Open UVM Tree in Verdi to verify hierarchy |
| Sequence not starting | Check sequencer assignment and `default_sequence` in test |
