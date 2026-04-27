"""
Demo mode responses for the Verilog Testbench Generator.

Provides predefined, simulation-ready testbench examples for common modules,
used when running in demo mode (no API key required).
"""

from parser import ModuleInfo, LogicType

# ---------------------------------------------------------------------------
# Predefined testbench strings
# ---------------------------------------------------------------------------

AND_GATE_TESTBENCH = """`timescale 1ns/1ps

module tb_and_gate;

    // DUT inputs (reg)
    reg a;
    reg b;

    // DUT outputs (wire)
    wire y;

    // Instantiate Device Under Test
    and_gate dut (
        .a(a),
        .b(b),
        .y(y)
    );

    // Monitor signal changes
    initial begin
        $monitor("Time=%0t | a=%b b=%b | y=%b", $time, a, b, y);
    end

    // Test cases - exhaustive (2^2 = 4 combinations)
    initial begin
        $display("=== AND Gate Testbench ===");
        $display("Testing all input combinations");

        // Test case 1: a=0, b=0 -> expected y=0
        a = 0; b = 0; #10;
        $display("a=%b, b=%b -> y=%b (expected: 0)", a, b, y);

        // Test case 2: a=0, b=1 -> expected y=0
        a = 0; b = 1; #10;
        $display("a=%b, b=%b -> y=%b (expected: 0)", a, b, y);

        // Test case 3: a=1, b=0 -> expected y=0
        a = 1; b = 0; #10;
        $display("a=%b, b=%b -> y=%b (expected: 0)", a, b, y);

        // Test case 4: a=1, b=1 -> expected y=1
        a = 1; b = 1; #10;
        $display("a=%b, b=%b -> y=%b (expected: 1)", a, b, y);

        $display("=== Test Complete ===");
        $finish;
    end

endmodule
"""

ADDER_TESTBENCH = """`timescale 1ns/1ps

module tb_adder;

    // DUT inputs (reg)
    reg  [3:0] a;
    reg  [3:0] b;

    // DUT outputs (wire)
    wire [4:0] sum;   // 5-bit to capture carry

    // Instantiate Device Under Test
    adder dut (
        .a(a),
        .b(b),
        .sum(sum)
    );

    // Monitor signal changes
    initial begin
        $monitor("Time=%0t | a=%0d b=%0d | sum=%0d", $time, a, b, sum);
    end

    // Test cases - representative (8 input bits -> 256 combinations, use representative set)
    initial begin
        $display("=== 4-bit Adder Testbench ===");

        // All-zeros
        a = 4'h0; b = 4'h0; #10;
        $display("a=%0d, b=%0d -> sum=%0d (expected: 0)", a, b, sum);

        // All-ones
        a = 4'hF; b = 4'hF; #10;
        $display("a=%0d, b=%0d -> sum=%0d (expected: 30)", a, b, sum);

        // Boundary: max + 1
        a = 4'hF; b = 4'h1; #10;
        $display("a=%0d, b=%0d -> sum=%0d (expected: 16)", a, b, sum);

        // Alternating bits
        a = 4'b1010; b = 4'b0101; #10;
        $display("a=%0d, b=%0d -> sum=%0d (expected: 15)", a, b, sum);

        // Typical values
        a = 4'd5; b = 4'd3; #10;
        $display("a=%0d, b=%0d -> sum=%0d (expected: 8)", a, b, sum);

        a = 4'd7; b = 4'd8; #10;
        $display("a=%0d, b=%0d -> sum=%0d (expected: 15)", a, b, sum);

        // Carry generation
        a = 4'd9; b = 4'd9; #10;
        $display("a=%0d, b=%0d -> sum=%0d (expected: 18)", a, b, sum);

        // One operand zero
        a = 4'd0; b = 4'd12; #10;
        $display("a=%0d, b=%0d -> sum=%0d (expected: 12)", a, b, sum);

        $display("=== Test Complete ===");
        $finish;
    end

endmodule
"""

DFF_TESTBENCH = """`timescale 1ns/1ps

module tb_dff;

    // DUT inputs (reg)
    reg clk;
    reg rst;
    reg d;

    // DUT outputs (wire)
    wire q;

    // Instantiate Device Under Test
    dff dut (
        .clk(clk),
        .rst(rst),
        .d(d),
        .q(q)
    );

    // Clock generation: 10ns period (100 MHz)
    initial clk = 0;
    always #5 clk = ~clk;

    // Monitor signal changes
    initial begin
        $monitor("Time=%0t | clk=%b rst=%b d=%b | q=%b", $time, clk, rst, d, q);
    end

    // Test cases
    initial begin
        $display("=== D Flip-Flop Testbench ===");

        // --- Reset behavior ---
        $display("-- Testing reset --");
        rst = 1; d = 1;
        @(posedge clk); #1;
        $display("After reset: rst=%b, d=%b -> q=%b (expected: 0)", rst, d, q);

        // --- Release reset, capture d=0 ---
        $display("-- Testing d=0 capture --");
        rst = 0; d = 0;
        @(posedge clk); #1;
        $display("d=%b -> q=%b (expected: 0)", d, q);

        // --- Capture d=1 ---
        $display("-- Testing d=1 capture --");
        d = 1;
        @(posedge clk); #1;
        $display("d=%b -> q=%b (expected: 1)", d, q);

        // --- Hold value when d changes between edges ---
        $display("-- Testing hold between edges --");
        d = 0; #3;  // change d mid-cycle
        $display("d changed to 0 mid-cycle: q=%b (expected: 1, not yet captured)", q);
        @(posedge clk); #1;
        $display("After next edge: d=%b -> q=%b (expected: 0)", d, q);

        // --- Multi-cycle sequence ---
        $display("-- Multi-cycle sequence --");
        d = 1; @(posedge clk); #1;
        $display("Cycle 1: d=%b -> q=%b (expected: 1)", d, q);
        d = 0; @(posedge clk); #1;
        $display("Cycle 2: d=%b -> q=%b (expected: 0)", d, q);
        d = 1; @(posedge clk); #1;
        $display("Cycle 3: d=%b -> q=%b (expected: 1)", d, q);

        // --- Reset mid-operation ---
        $display("-- Reset mid-operation --");
        d = 1; rst = 1;
        @(posedge clk); #1;
        $display("Reset asserted: q=%b (expected: 0)", q);
        rst = 0;

        $display("=== Test Complete ===");
        $finish;
    end

endmodule
"""

COUNTER_TESTBENCH = """`timescale 1ns/1ps

module tb_counter;

    // DUT inputs (reg)
    reg clk;
    reg rst;
    reg enable;

    // DUT outputs (wire)
    wire [3:0] count;

    // Instantiate Device Under Test
    counter dut (
        .clk(clk),
        .rst(rst),
        .enable(enable),
        .count(count)
    );

    // Clock generation: 10ns period (100 MHz)
    initial clk = 0;
    always #5 clk = ~clk;

    // Monitor signal changes
    initial begin
        $monitor("Time=%0t | clk=%b rst=%b en=%b | count=%0d", $time, clk, rst, enable, count);
    end

    // Test cases
    initial begin
        $display("=== 4-bit Counter Testbench ===");

        // --- Reset behavior ---
        $display("-- Testing reset --");
        rst = 1; enable = 0;
        @(posedge clk); #1;
        $display("After reset: count=%0d (expected: 0)", count);

        // --- Count disabled ---
        $display("-- Testing count disabled --");
        rst = 0; enable = 0;
        repeat(3) @(posedge clk);
        #1;
        $display("After 3 cycles with enable=0: count=%0d (expected: 0)", count);

        // --- Count enabled ---
        $display("-- Testing count enabled --");
        enable = 1;
        repeat(4) begin
            @(posedge clk); #1;
            $display("count=%0d", count);
        end

        // --- Disable mid-count ---
        $display("-- Testing disable mid-count --");
        enable = 0;
        @(posedge clk); #1;
        $display("After disable: count=%0d (should hold)", count);
        @(posedge clk); #1;
        $display("One more cycle disabled: count=%0d (should still hold)", count);

        // --- Re-enable and continue ---
        $display("-- Re-enable and continue --");
        enable = 1;
        repeat(4) begin
            @(posedge clk); #1;
            $display("count=%0d", count);
        end

        // --- Count to rollover (0 -> 15 -> 0) ---
        $display("-- Testing rollover --");
        rst = 1; @(posedge clk); #1; rst = 0;
        enable = 1;
        repeat(17) begin
            @(posedge clk); #1;
        end
        $display("After 17 counts from 0: count=%0d (expected: 1 after rollover)", count);

        // --- Reset during counting ---
        $display("-- Reset during counting --");
        enable = 1;
        repeat(5) @(posedge clk);
        rst = 1; @(posedge clk); #1;
        $display("Reset during count: count=%0d (expected: 0)", count);
        rst = 0;

        $display("=== Test Complete ===");
        $finish;
    end

endmodule
"""

# ---------------------------------------------------------------------------
# Generic fallback templates
# ---------------------------------------------------------------------------

GENERIC_COMBINATIONAL_TESTBENCH = """`timescale 1ns/1ps

module tb_{module_name};

    // DUT inputs (reg)
{reg_declarations}

    // DUT outputs (wire)
{wire_declarations}

    // Instantiate Device Under Test
    {module_name} dut (
{port_connections}
    );

    // Monitor signal changes
    initial begin
        $monitor("Time=%0t{monitor_fmt}", $time{monitor_sigs});
    end

    // Test cases
    initial begin
        $display("=== {module_name} Testbench ===");

        // All-zeros
{zero_assignments}
        #10;
        $display("All-zeros test complete");

        // All-ones
{ones_assignments}
        #10;
        $display("All-ones test complete");

        // Alternating bits
{alt_assignments}
        #10;
        $display("Alternating bits test complete");

        $display("=== Test Complete ===");
        $finish;
    end

endmodule
"""

GENERIC_SEQUENTIAL_TESTBENCH = """`timescale 1ns/1ps

module tb_{module_name};

    // DUT inputs (reg)
{reg_declarations}

    // DUT outputs (wire)
{wire_declarations}

    // Instantiate Device Under Test
    {module_name} dut (
{port_connections}
    );

    // Clock generation: 10ns period (100 MHz)
    initial {clock_signal} = 0;
    always #5 {clock_signal} = ~{clock_signal};

    // Monitor signal changes
    initial begin
        $monitor("Time=%0t{monitor_fmt}", $time{monitor_sigs});
    end

    // Test cases
    initial begin
        $display("=== {module_name} Testbench ===");

        // Reset behavior
        $display("-- Testing reset --");
{reset_assert}
        @(posedge {clock_signal}); #1;
        $display("After reset complete");

        // Release reset
{reset_deassert}

        // Multi-cycle test sequence
        $display("-- Multi-cycle test --");
        repeat(8) @(posedge {clock_signal});
        #1;
        $display("Multi-cycle test complete");

        $display("=== Test Complete ===");
        $finish;
    end

endmodule
"""

# ---------------------------------------------------------------------------
# Predefined response registry
# ---------------------------------------------------------------------------

_DEMO_REGISTRY = {
    "and_gate": AND_GATE_TESTBENCH,
    "adder":    ADDER_TESTBENCH,
    "dff":      DFF_TESTBENCH,
    "counter":  COUNTER_TESTBENCH,
}

# Name fragments that map to a known demo key
_NAME_HINTS = {
    "and":     "and_gate",
    "adder":   "adder",
    "add":     "adder",
    "dff":     "dff",
    "flip":    "dff",
    "flop":    "dff",
    "counter": "counter",
    "cnt":     "counter",
}


# ---------------------------------------------------------------------------
# Helper: build a generic testbench from ModuleInfo
# ---------------------------------------------------------------------------

def _build_generic_testbench(module_info: ModuleInfo) -> str:
    """Build a generic simulation-ready testbench from a ModuleInfo object."""
    from parser import PortDirection

    inputs  = [p for p in module_info.ports if p.direction == PortDirection.INPUT]
    outputs = [p for p in module_info.ports if p.direction == PortDirection.OUTPUT]

    def _decl(port, keyword):
        if port.is_vector:
            return f"    {keyword} {port.range_str} {port.name};"
        return f"    {keyword} {port.name};"

    reg_decls  = "\n".join(_decl(p, "reg")  for p in inputs)
    wire_decls = "\n".join(_decl(p, "wire") for p in outputs)

    connections = "\n".join(
        f"        .{p.name}({p.name}){',' if i < len(module_info.ports) - 1 else ''}"
        for i, p in enumerate(module_info.ports)
    )

    monitor_fmt  = "".join(f" | {p.name}=%b" for p in module_info.ports)
    monitor_sigs = "".join(f", {p.name}" for p in module_info.ports)

    if module_info.logic_type == LogicType.SEQUENTIAL:
        clock_sig = module_info.clock_signals[0] if module_info.clock_signals else "clk"
        reset_sig = module_info.reset_signals[0] if module_info.reset_signals else None

        reset_assert   = f"        {reset_sig} = 1;" if reset_sig else "        // no reset signal detected"
        reset_deassert = f"        {reset_sig} = 0;" if reset_sig else ""

        return GENERIC_SEQUENTIAL_TESTBENCH.format(
            module_name=module_info.module_name,
            reg_declarations=reg_decls,
            wire_declarations=wire_decls,
            port_connections=connections,
            clock_signal=clock_sig,
            monitor_fmt=monitor_fmt,
            monitor_sigs=monitor_sigs,
            reset_assert=reset_assert,
            reset_deassert=reset_deassert,
        )

    # Combinational fallback
    def _zero(p):
        return f"        {p.name} = {p.bit_width}'b0;"

    def _ones(p):
        return f"        {p.name} = {p.bit_width}'b{'1' * p.bit_width};"

    def _alt(p):
        pattern = "10" * (p.bit_width // 2 + 1)
        return f"        {p.name} = {p.bit_width}'b{pattern[:p.bit_width]};"

    zero_assigns = "\n".join(_zero(p) for p in inputs)
    ones_assigns = "\n".join(_ones(p) for p in inputs)
    alt_assigns  = "\n".join(_alt(p)  for p in inputs)

    return GENERIC_COMBINATIONAL_TESTBENCH.format(
        module_name=module_info.module_name,
        reg_declarations=reg_decls,
        wire_declarations=wire_decls,
        port_connections=connections,
        monitor_fmt=monitor_fmt,
        monitor_sigs=monitor_sigs,
        zero_assignments=zero_assigns,
        ones_assignments=ones_assigns,
        alt_assignments=alt_assigns,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_demo_response(module_info: ModuleInfo) -> str:
    """
    Return the best matching demo testbench for the given ModuleInfo.

    Matching priority:
    1. Exact module name match in the registry (e.g. "and_gate", "adder").
    2. Partial name hint match (e.g. "my_adder" -> adder demo).
    3. Generic combinational or sequential template built from ModuleInfo.

    Args:
        module_info: Parsed module information from VerilogParser.

    Returns:
        A simulation-ready Verilog testbench string.
    """
    name_lower = module_info.module_name.lower()

    # 1. Exact match
    if name_lower in _DEMO_REGISTRY:
        return _DEMO_REGISTRY[name_lower]

    # 2. Partial / hint match
    for hint, key in _NAME_HINTS.items():
        if hint in name_lower:
            return _DEMO_REGISTRY[key]

    # 3. Generic fallback based on logic type
    return _build_generic_testbench(module_info)
