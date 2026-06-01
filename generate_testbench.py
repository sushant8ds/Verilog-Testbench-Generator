"""
Standalone testbench generator script.
Generates a complete Verilog testbench for the rca4 module.
No API key required - uses built-in exhaustive generation.
"""

from parser import VerilogParser
from prompt_builder import PromptBuilder
from demo_responses import get_demo_response

# ── Your Verilog RTL code ──────────────────────────────────────────────────
# Paste ANY single module here. If you have multiple modules,
# paste only the TOP-LEVEL module you want to test.
VERILOG_CODE = """
module rca4(input [3:0] a, b, input cin, output [3:0] sum, output cout);
    wire c1, c2, c3;
    fa f0(a[0], b[0], cin,  sum[0], c1);
    fa f1(a[1], b[1], c1,   sum[1], c2);
    fa f2(a[2], b[2], c2,   sum[2], c3);
    fa f3(a[3], b[3], c3,   sum[3], cout);
endmodule
"""

# ── Other examples you can swap in ────────────────────────────────────────
# AND gate:
# VERILOG_CODE = "module and_gate(input a, input b, output y); assign y = a & b; endmodule"

# D Flip-Flop:
# VERILOG_CODE = """
# module dff(input clk, input rst, input d, output reg q);
#     always @(posedge clk)
#         if (rst) q <= 0;
#         else q <= d;
# endmodule
# """

# 4-bit counter:
# VERILOG_CODE = """
# module counter(input clk, input rst, input enable, output reg [3:0] count);
#     always @(posedge clk)
#         if (rst) count <= 0;
#         else if (enable) count <= count + 1;
# endmodule
# """

# ── Parse ──────────────────────────────────────────────────────────────────
print("=" * 60)
print("  Verilog Testbench Generator")
print("=" * 60)

parser = VerilogParser()
module_info = parser.parse(VERILOG_CODE)

print(f"\n[PARSER]")
print(f"  Module name  : {module_info.module_name}")
print(f"  Logic type   : {module_info.logic_type.value}")
print(f"  Total inputs : {module_info.total_input_bits} bits")
print(f"  Ports:")
for p in module_info.ports:
    width = f"[{p.range_str}]" if p.is_vector else "1-bit"
    print(f"    {p.direction.value:6s}  {p.name:10s}  {width}")

# ── Build prompt ───────────────────────────────────────────────────────────
pb = PromptBuilder()
prompt = pb.build_prompt(module_info)
strategy = "EXHAUSTIVE" if "EXHAUSTIVE" in prompt else "REPRESENTATIVE"

print(f"\n[PROMPT BUILDER]")
print(f"  Test strategy: {strategy}")
print(f"  Input bits <= 10: {module_info.total_input_bits <= 10}")
print(f"  Expected test vectors: {2**module_info.total_input_bits}")

# ── Generate testbench (Demo mode - no API needed) ─────────────────────────
print(f"\n[GENERATOR]  Using demo mode (no API key required)")
testbench = get_demo_response(module_info)

# ── Print output ───────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  GENERATED TESTBENCH")
print("=" * 60)
print(testbench)

# ── Save to file ───────────────────────────────────────────────────────────
output_file = f"tb_{module_info.module_name}.v"
with open(output_file, "w") as f:
    f.write(testbench)

print("=" * 60)
print(f"  Saved to: {output_file}")
print("=" * 60)
