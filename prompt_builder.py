"""
Prompt Builder module for constructing structured LLM prompts with test strategies.
"""

import logging
from parser import ModuleInfo, LogicType, PortDirection

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Constructs structured prompts for LLM-based testbench generation."""

    def _determine_test_strategy(self, module_info: ModuleInfo) -> str:
        lines = ["Include these test patterns:"]
        lines.append("  - All-zeros, all-ones, boundary values, alternating bits (0xAA, 0x55)")
        if module_info.logic_type == LogicType.SEQUENTIAL:
            lines.append("  - Assert reset, verify outputs go to known state")
            lines.append("  - Apply 3-5 representative input sequences across clock cycles")
        else:
            if module_info.total_input_bits <= 8:
                lines.append(f"  - Exhaustive: all {2**module_info.total_input_bits} input combinations")
            else:
                lines.append("  - Representative edge cases (exhaustive not feasible)")
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
            "REQUIREMENTS (follow exactly):",
            f'1. Testbench module name: "tb_{module_info.module_name}"',
            "2. Start with `timescale 1ns/1ps",
            "3. Inputs as reg, outputs as wire",
            f"4. Instantiate {module_info.module_name} with named port mapping",
        ]

        req_num = 5
        if module_info.logic_type == LogicType.SEQUENTIAL:
            req_lines.append(f"{req_num}. Clock gen: always #5 clk = ~clk; initialize clk=0")
            req_num += 1

        req_lines += [
            f"{req_num}. initial block with test cases, $display for each, $finish at end",
            f"{req_num+1}. Output ONLY Verilog — no markdown, no explanations outside comments",
        ]

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
