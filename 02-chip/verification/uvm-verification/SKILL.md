---
name: uvm-verification
description: UVM (Universal Verification Methodology) testbench development — agent, driver, monitor, scoreboard, sequences, factory, TLM, register model, and coverage-driven verification. Use when writing UVM testbenches, creating sequences, or building verification environments.
---

# UVM Verification Methodology

You are an expert in UVM-based verification for ASIC/FPGA designs. Follow these conventions and patterns when building UVM testbenches or writing UVM-related code.

## UVM Architecture Overview

### Standard UVM Testbench Hierarchy
```
uvm_test
  └── uvm_env (top-level)
        ├── uvm_agent (active: driver + sequencer + monitor)
        │     ├── uvm_driver (drives DUT signals)
        │     ├── uvm_sequencer (routes sequences to driver)
        │     └── uvm_monitor (observes interface signals)
        ├── uvm_agent (passive: monitor only, for output checking)
        ├── uvm_scoreboard (compares actual vs expected)
        └── uvm_subscriber (coverage collection)
```

### File Structure
- One agent per directory: `agent_name/{agent.sv, driver.sv, monitor.sv, sequencer.sv, sequence_lib.sv, cfg.sv, pkg.sv}`
- Interface file: `if/if_name.sv`
- Test files: `tests/test_name.sv`
- Environment: `env/env_name.sv`
- Top: `tb/tb_top.sv`

## UVM Component Guidelines

### Driver (`uvm_driver`)
```systemverilog
class my_driver extends uvm_driver #(my_item);
  `uvm_component_utils(my_driver)
  virtual my_if vif;
  
  // Run phase: get items from sequencer and drive
  task run_phase(uvm_phase phase);
    forever begin
      seq_item_port.get_next_item(req);
      drive_item(req);   // Drive to DUT interface
      seq_item_port.item_done();
    end
  endtask
  
  task drive_item(my_item item);
    // Apply reset handling at beginning
    // Drive signals on clock edges with proper timing
    // Use non-blocking assignments for synchronous drives
  endtask
endclass
```

- Always use `seq_item_port.get_next_item()` / `item_done()` pattern
- Handle reset gracefully — check reset before driving
- Drive on the correct clock edge with proper setup/hold timing

### Monitor (`uvm_monitor`)
```systemverilog
class my_monitor extends uvm_monitor;
  `uvm_component_utils(my_monitor)
  uvm_analysis_port #(my_item) item_collected_port;
  
  task run_phase(uvm_phase phase);
    forever begin
      @(posedge vif.clk);
      collect_transaction(item);
      item_collected_port.write(item);
    end
  endtask
endclass
```

- Collect transactions on every relevant clock edge
- Detect protocol start/end conditions
- Write collected items to analysis port for scoreboard/coverage subscribers

### Sequencer & Sequences

```systemverilog
// Sequences should be parameterized for reusability
class my_sequence extends uvm_sequence #(my_item);
  `uvm_object_utils(my_sequence)
  
  rand int num_transactions;
  constraint valid_count { num_transactions inside {[1:100]}; }
  
  task body();
    repeat(num_transactions) begin
      my_item item = my_item::type_id::create("item");
      start_item(item);
      if (!item.randomize()) `uvm_fatal("SEQ", "Randomization failed")
      finish_item(item);
      get_response(rsp);  // Optional: wait for response
    end
  endtask
endclass
```

- Use `uvm_do` / `uvm_do_with` macros for simple cases, manual start/finish for complex flows
- Parameterize sequence count and constraints
- Support both directed and constrained-random sequences
- Implement interrupt/error injection sequences

### Scoreboard
```systemverilog
class my_scoreboard extends uvm_scoreboard;
  `uvm_component_utils(my_scoreboard)
  
  uvm_analysis_imp #(my_item, my_scoreboard) input_imp;
  uvm_analysis_imp #(my_item, my_scoreboard) output_imp;
  
  // Compare predicted output against actual
  function void write_output(my_item item);
    my_item expected = expected_queue.pop_front();
    if (!expected.compare(item))
      `uvm_error("SB", $sformatf("Mismatch: expected %s, got %s",
                   expected.convert2str(), item.convert2str()))
  endfunction
endclass
```

- Always use Queue/FIFO for in-order comparison; associative arrays for out-of-order
- Report mismatches with clear, human-readable messages
- Support in-order and out-of-order checking modes

## UVM Factory & Configuration

### Factory Registration
```systemverilog
// Component: use `uvm_component_utils
class my_agent extends uvm_agent;
  `uvm_component_utils(my_agent)
endclass

// Object/Transaction/Sequence: use `uvm_object_utils
class my_item extends uvm_sequence_item;
  `uvm_object_utils(my_item)
endclass
```

### Override with Factory
```systemverilog
// Type override: replace all instances of old_type with new_type
my_old_driver::type_id::set_type_override(my_new_driver::get_type());
// Instance override: replace at specific path
my_old_monitor::type_id::set_inst_override(my_new_monitor::get_type(), "env.agent.monitor");
```

### Configuration Database
```systemverilog
// Set in test or env
uvm_config_db #(virtual my_if)::set(this, "env.agent.*", "vif", my_if);
// Set configuration object
uvm_config_db #(my_cfg)::set(this, "*", "cfg", my_cfg);

// Get in component
if (!uvm_config_db #(virtual my_if)::get(this, "", "vif", vif))
  `uvm_fatal("CFG", "Virtual interface not set")
```

- Always check return value of `uvm_config_db::get()` — fatal if not set
- Use simple wildcards `*` carefully; prefer explicit paths

## TLM Communication

| Port Type | Direction | Use Case |
|-----------|-----------|----------|
| `uvm_analysis_port` | broadcast (1→N) | Monitor → scoreboard/coverage |
| `uvm_blocking_put_port` | blocking 1→1 | Sequence → scoreboard (prediction) |
| `uvm_nonblocking_put_port` | non-blocking 1→1 | High-speed data transfer |
| `uvm_blocking_get_port` | blocking pull | Pull-based data retrieval |
| `uvm_tlm_fifo` | buffered channel | Decoupled producer/consumer |

## UVM Phases

```
build_phase → connect_phase → end_of_elaboration_phase → start_of_simulation_phase
→ run_phase (12 parallel sub-phases: reset → configure → main → shutdown)
→ extract_phase → check_phase → report_phase → final_phase
```

- Build: create components, get config
- Connect: connect TLM ports, get virtual interfaces
- Run: all test activity (only phase with `task` by default)
- Report: print pass/fail summary

## Register Model (UVM RAL)

```systemverilog
class my_reg_block extends uvm_reg_block;
  `uvm_object_utils(my_reg_block)
  
  rand my_reg reg_ctrl;
  rand my_reg reg_status;
  
  function void build();
    default_map = create_map("default_map", 0, 4, UVM_LITTLE_ENDIAN);
    reg_ctrl.configure(this);
    reg_ctrl.build();
    default_map.add_reg(reg_ctrl, 'h00, "RW");
    lock_model();
  endfunction
endclass
```

- Use `uvm_reg::randomize()` with constraints for randomized register testing
- Frontdoor: access via bus interface; Backdoor: direct DUT signal access
- Implement predictor: `uvm_reg_predictor` connected to monitor analysis port

## Logging & Reporting

```systemverilog
`uvm_info("TAG", "Informational message", UVM_MEDIUM)     // Info (filter with verbosity)
`uvm_warning("TAG", "Warning message")                     // Warning (counted)
`uvm_error("TAG", "Error message")                         // Error (counted, fails test)
`uvm_fatal("TAG", "Fatal message")                         // Fatal (immediate $finish)
```

- Verbosity levels: `UVM_NONE`(0) < `UVM_LOW`(100) < `UVM_MEDIUM`(200) < `UVM_HIGH`(300) < `UVM_FULL`(400) < `UVM_DEBUG`(500)
- Keep UVM_LOW for key events, UVM_HIGH for debug detail
- Count errors: test should fail if `error_count > 0`

## Best Practices

1. **Testbench topology**: Keep agents plug-and-play with is_active=UVM_ACTIVE/UVM_PASSIVE
2. **Sequence library**: Organize into basic sequences (read/write) and complex scenarios (burst, stress)
3. **Reuse**: Design environment to be reusable at subsystem and full-chip levels
4. **Simulation termination**: Use phase objections or `uvm_top.stop_request()`
5. **Random stability**: Use `$urandom()`, `std::randomize()` with consistent seeds
6. **Timeout**: Always add watchdog timer in test `run_phase`:
   ```systemverilog
   fork
     run_test_sequence();
     begin
       #100us;
       `uvm_fatal("TIMEOUT", "Test timed out")
     end
   join_any
   ```
