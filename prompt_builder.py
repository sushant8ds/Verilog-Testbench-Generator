"""
Prompt Builder module for constructing structured LLM prompts with test strategies.
"""

import logging
from parser import ModuleInfo, LogicType, PortDirection

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Constructs structured prompts for LLM-based testbench generation."""

    def _determine_test_strategy(self, module_info: ModuleInfo) -> str:
        """
        Determine the appropriate test strategy based on module characteristics.

        Args:
            module_info: Parsed module information

        Returns:
            Test strategy text to include in the LLM prompt
        """
        lines = []

        if module_info.total_input_bits <= 10:
            lines.append(
                f"Generate EXHAUSTIVE test cases covering all 2^{module_info.total_input_bits} "
                f"input combinations ({2 ** module_info.total_input_bits} total test vectors)."
            )
        else:
            lines.append(
                "Generate REPRESENTATIVE test cases including edge cases "
                f"(total input bits = {module_info.total_input_bits}, exhaustive coverage not feasible)."
            )

        # Standard patterns always included
        lines.append("Include the following standard test patterns:")
        lines.append("  - All-zeros: set all inputs to 0")
        lines.append("  - All-ones: set all inputs to their maximum value")
        lines.append("  - Boundary values: minimum and maximum value for each input port individually")
        lines.append("  - Alternating bit patterns: e.g., 10101010 and 01010101")

        # Sequential-specific additions
        if module_info.logic_type == LogicType.SEQUENTIAL:
            lines.append("  - Reset behavior: assert reset signal and verify outputs go to known state")
            lines.append("  - Multi-cycle sequences: apply sequences of inputs across multiple clock cycles")

        return "\n".join(lines)

    def build_prompt(self, module_info: ModuleInfo) -> str:
        """
        Build a structured LLM prompt with test strategy for testbench generation.

        Args:
            module_info: Parsed module information

        Returns:
            Formatted prompt string for the LLM
        """
        # --- MODULE INFORMATION section ---
        port_lines = []
        for port in module_info.ports:
            direction = port.direction.value
            width_desc = f"{port.bit_width} bit{'s' if port.bit_width > 1 else ''}"
            range_part = f" {port.range_str}" if port.range_str else ""
            port_lines.append(f"  - {port.name} ({direction},{range_part} {width_desc})")

        clock_str = ", ".join(module_info.clock_signals) if module_info.clock_signals else "None"
        reset_str = ", ".join(module_info.reset_signals) if module_info.reset_signals else "None"
        logic_type_str = module_info.logic_type.value.capitalize()

        module_info_section = f"""MODULE INFORMATION:
- Name: {module_info.module_name}
- Logic Type: {logic_type_str}
- Ports:
{chr(10).join(port_lines)}
- Clock Signals: {clock_str}
- Reset Signals: {reset_str}"""

        # --- TEST STRATEGY section ---
        test_strategy_section = f"TEST STRATEGY:\n{self._determine_test_strategy(module_info)}"

        # --- REQUIREMENTS section ---
        req_lines = [
            "REQUIREMENTS:",
            f'1. Create a testbench module named "tb_{module_info.module_name}"',
            "2. Include a `timescale directive at the top (e.g., `timescale 1ns/1ps)",
            "3. Declare all input ports as reg type signals",
            "4. Declare all output ports as wire type signals",
            f"5. Instantiate the DUT ({module_info.module_name}) with correct named port mapping",
        ]

        req_num = 6
        if module_info.logic_type == LogicType.SEQUENTIAL:
            req_lines.append(
                f"{req_num}. Include clock generation logic using an always block "
                "(e.g., always #5 clk = ~clk; for a 10ns period)"
            )
            req_num += 1
            req_lines.append(
                f"{req_num}. Initialize the clock signal to 0 in the initial block before starting tests"
            )
            req_num += 1

        req_lines += [
            f"{req_num}. Include an initial block containing all test case execution logic",
            f"{req_num + 1}. Use $display statements to show input and output values for each test case",
            f"{req_num + 2}. Use $monitor to track signal changes throughout simulation",
            f"{req_num + 3}. Add inline comments indicating expected output values for each test case",
            f"{req_num + 4}. End the simulation with a $finish statement",
            f"{req_num + 5}. Use consistent indentation (2 or 4 spaces per level)",
            f"{req_num + 6}. Include a comment block at the top describing the test strategy used",
        ]

        if module_info.logic_type == LogicType.SEQUENTIAL:
            req_lines.append(
                f"{req_num + 7}. Include appropriate @(posedge clk) or #delay statements between test cases"
            )

        requirements_section = "\n".join(req_lines)

        # --- OUTPUT FORMAT section ---
        output_format_section = """OUTPUT FORMAT:
- Output PURE Verilog code only — no markdown formatting, no code fences (no ```verilog)
- Do NOT include any explanatory text outside of Verilog comments
- The output must be simulation-ready and compile without errors in standard simulators (Icarus Verilog, ModelSim)
- Do NOT include any text before the `timescale directive or after the endmodule keyword"""

        # Assemble full prompt
        prompt = f"""You are a Verilog testbench generation expert.

{module_info_section}

{test_strategy_section}

{requirements_section}

{output_format_section}"""

        logger.info(
            f"Built prompt for module '{module_info.module_name}' "
            f"({logic_type_str}, {module_info.total_input_bits} input bits)"
        )
        return prompt
