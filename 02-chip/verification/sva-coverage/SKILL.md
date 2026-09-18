---
name: sva-coverage
description: SVA (SystemVerilog Assertions) and Functional Coverage guidelines — immediate/concurrent assertions, property/sequence definitions, covergroups, coverpoints, cross coverage, and coverage-driven verification methodology.
---

# SVA Assertions & Functional Coverage

You are an expert in SVA (SystemVerilog Assertions) and functional coverage for ASIC/FPGA verification. Follow these conventions for writing assertions and coverage models.

## SystemVerilog Assertions (SVA)

### Immediate Assertions

Used inside procedural code (`always`/`initial`/`task`/`function`) — evaluated immediately at execution time.

```systemverilog
// Simple condition check
always_ff @(posedge clk) begin
  if (valid) begin
    assert (data !== 'x) else $error("Data is X when valid=1");
    assert (addr < MAX_ADDR) else $error("Address overflow: %0d", addr);
  end
end

// With pass/fail actions
assert (result == expected)
  pass_cnt++;
else begin
  fail_cnt++;
  $error("Check failed at time %0t: got %0d, expected %0d", $time, result, expected);
end
```

### Concurrent Assertions

Used outside procedural code for temporal behavior checking over multiple clock cycles.

#### Sequence Definition
```systemverilog
// Basic sequence: request followed by grant within 1-4 cycles
sequence req_grant_seq;
  req ##[1:4] gnt;
endsequence

// Sequence with data
sequence read_handshake_seq;
  rd_req ##1 rd_ack ##0 (rd_data === expected_data);
endsequence

// Repetition operators
sequence burst_write_seq;
  wr_req ##1 wr_ack[=1] ##1 wr_data[*4] ##1 wr_done;
endsequence
```

#### Property Definition
```systemverilog
// Overlapping implication: if antecedent matches, consequent must follow
property req_grant_prop;
  @(posedge clk) disable iff (rst_n)
    req |-> ##[1:4] gnt;
endproperty

// Non-overlapping implication: consequent starts one cycle after antecedent
property req_grant_next_prop;
  @(posedge clk) disable iff (rst_n)
    req |=> gnt;
endproperty

// Window-based property
property fifo_no_overflow_prop;
  @(posedge clk) disable iff (rst_n)
    (wr_en && (fifo_count == DEPTH)) |-> !full;
endproperty
```

#### Assert/Cover/Assume
```systemverilog
// Assert: must always hold (fail = bug)
assert_req_grant: assert property (req_grant_prop)
  else $error("Grant not received for request");

// Cover: must be observed at least once (no cover = coverage gap)
cover_req_grant: cover property (req_grant_prop);

// Assume: constraint for formal verification (input behavior assumption)
assume_stable_input: assume property (
  @(posedge clk) $stable(cfg_signal)
);
```

### Common Assertion Patterns

| Pattern | Code |
|---------|------|
| One-hot | `$onehot(signal)` or `$onehot0(signal)` |
| Mutex | `!(grant1 && grant2)` |
| No X/Z | `!$isunknown(data) when valid` |
| Stability | `$stable(addr) throughout (burst_cnt > 0)` |
| Handshake | `valid ##1 ready ##0 valid` |
| No overflow | `(wr_ptr + 1 != rd_ptr)` |
| State machine | `$rose(state == A) \|-> ##[1:N] state == B` |
| Data hold | `valid \|=> $stable(data) until_with ack` |

### SVA System Functions

```systemverilog
$rose(expr)      // True when LSB changes 0→1
$fell(expr)      // True when LSB changes 1→0
$stable(expr)    // True when expression didn't change
$past(expr, N)   // Value of expr N cycles ago
$onehot(expr)    // True if exactly one bit is 1
$onehot0(expr)   // True if at most one bit is 1
$isunknown(expr) // True if any bit is X or Z
$countones(expr) // Number of 1 bits
```

## Functional Coverage

### Covergroup Basics

```systemverilog
// Declare inside class (UVM subscriber) or module
covergroup my_cg @(posedge clk);
  option.per_instance = 1;       // Track per instance
  option.goal = 95;              // Coverage goal percentage
  option.at_least = 3;           // Min hits per bin for "covered"
  
  // Coverpoint: variable or expression to track
  cp_opcode: coverpoint opcode {
    bins reads  = {READ, READX};
    bins writes = {WRITE, WRITEX};
    bins others = default;
    ignore_bins invalid = {4'bxxxx, 4'bzzzz};   // Don't track
    illegal_bins reserved = {4'b1111};           // Error if hit
  }
  
  // Cross coverage
  cross_opcode_addr: cross cp_opcode, cp_addr {
    bins valid_combos = binsof(cp_opcode.reads) && binsof(cp_addr) intersect {[0:1023]};
    ignore_bins unused = binsof(cp_opcode.others);
  }
endgroup
```

### Coverpoint Bin Types

```systemverilog
coverpoint signal {
  // Value bins
  bins zero  = {0};
  bins small = {[1:127]};
  bins large = {[128:255]};
  
  // Transition bins
  bins inc = (0 => 1), (1 => 2), (2 => 3);        // Single-step increments
  bins dec = (3 => 2), (2 => 1), (1 => 0);
  bins jump = (0 => 255), (255 => 0);              // Extreme transitions
  
  // Wildcard bins
  wildcard bins even = {4'b???0};
  wildcard bins odd  = {4'b???1};
  
  // Default: catch all un-binned values
  bins others = default;
}
```

### Coverage-Driven Verification Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ Write Tests  │────▶│ Run Sim      │────▶│ Review      │
│ + Sequences  │     │ + Collect    │     │ Coverage    │
└─────────────┘     └──────────────┘     └─────────────┘
                                                 │
                                    ┌────────────┴──────┐
                                    │ Holes found?      │
                                    │ Yes → Add tests   │
                                    │ No  → Sign off    │
                                    └───────────────────┘
```

### Coverage in UVM

```systemverilog
class my_coverage extends uvm_subscriber #(my_item);
  `uvm_component_utils(my_coverage)
  
  my_item item;
  
  covergroup my_cg;
    cp_len: coverpoint item.length {
      bins short  = {[1:16]};
      bins medium = {[17:64]};
      bins long   = {[65:256]};
    }
    cp_dir: coverpoint item.direction;
    cross_len_dir: cross cp_len, cp_dir;
  endgroup
  
  function new(string name, uvm_component parent);
    super.new(name, parent);
    my_cg = new();
  endfunction
  
  function void write(my_item t);
    item = t;
    my_cg.sample();
  endfunction
endclass
```

### Coverage Best Practices

1. **Sample at the right time**: Use `@(posedge clk)` or explicit `sample()` in subscriber
2. **Cross with care**: Cross of N coverpoints creates N-dimensional space — keep crosses focused on meaningful combinations
3. **Set `at_least`**: Default is 1 — set to 3-5 for signals with random variation
4. **Weight goals**: Use `option.weight` to prioritize critical coverpoints
5. **Threshold-based closure**: 100% of key metrics, 95% of cross-coverage is typical signoff
6. **Use `get_coverage()`**: Query coverage at end of test to drive adaptive testing
7. **Illegal bins**: Use `illegal_bins` to catch protocol violations; simulation errors on hit

### Coverage Closure Hints

```systemverilog
// Add directed test to hit specific bin
// Use constraint to narrow randomization toward uncovered bins
// Use urm_sequence with coverage-driven control
task hit_uncovered_bins(cp_opcode uncovered_bins);
  repeat (100) begin
    item = my_item::type_id::create("item");
    start_item(item);
    item.opcode = uncovered_bins.sample_value();  // Force value
    finish_item(item);
  end
endtask
```
