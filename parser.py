"""
Verilog Parser module for extracting structural information from Verilog RTL modules.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class LogicType(Enum):
    """Classification of module logic type."""
    COMBINATIONAL = "combinational"
    SEQUENTIAL = "sequential"


class PortDirection(Enum):
    """Port direction types."""
    INPUT = "input"
    OUTPUT = "output"
    INOUT = "inout"


@dataclass
class PortInfo:
    """Information about a single port."""
    name: str
    direction: PortDirection  # INPUT, OUTPUT, INOUT
    bit_width: int            # 1 for single bit, N for [N-1:0]
    is_vector: bool           # True if multi-bit
    range_str: str            # e.g., "[7:0]" or "" for single bit


@dataclass
class ModuleInfo:
    """Structured information about a Verilog module."""
    module_name: str
    ports: List[PortInfo]
    clock_signals: List[str]
    reset_signals: List[str]
    logic_type: LogicType
    total_input_bits: int
    raw_code: str             # Original Verilog code


class ParseError(Exception):
    """Raised when Verilog parsing fails."""
    pass


import re
import logging
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


class VerilogParser:
    """Parser for extracting structural information from Verilog RTL modules."""

    def _strip_comments(self, code: str) -> str:
        """Remove // and /* */ comments from Verilog code."""
        # Remove block comments /* ... */
        code = re.sub(r'/\*.*?\*/', ' ', code, flags=re.DOTALL)
        # Remove line comments // ...
        code = re.sub(r'//[^\n]*', '', code)
        return code

    def _extract_module_name(self, code: str) -> str:
        """
        Extract module name from Verilog code.

        Args:
            code: Verilog source code (comments already stripped)

        Returns:
            Module name string

        Raises:
            ParseError: If no module declaration is found
        """
        match = re.search(r'\bmodule\s+(\w+)', code)
        if not match:
            raise ParseError("No module declaration found in Verilog code")
        return match.group(1)

    def _extract_ports(self, code: str) -> List[PortInfo]:
        """
        Extract port declarations from Verilog code.

        Handles both ANSI-style (ports in module header) and old-style
        (port declarations in module body).

        Args:
            code: Verilog source code (comments already stripped)

        Returns:
            List of PortInfo objects
        """
        ports: List[PortInfo] = []

        # Try ANSI-style: ports declared inline in module header
        # e.g. module foo(input a, output [3:0] b, inout c);
        ansi_ports = self._parse_ansi_ports(code)
        if ansi_ports:
            return ansi_ports

        # Fall back to old-style: separate port declarations in module body
        return self._parse_old_style_ports(code)

    def _parse_ansi_ports(self, code: str) -> List[PortInfo]:
        """Parse ANSI-style port declarations from module header."""
        # Match the module header port list
        header_match = re.search(
            r'\bmodule\s+\w+\s*\(([^;]*?)\)\s*;',
            code,
            re.DOTALL
        )
        if not header_match:
            return []

        port_list_str = header_match.group(1)

        # Check if this is ANSI style (contains direction keywords)
        if not re.search(r'\b(input|output|inout)\b', port_list_str):
            return []

        ports: List[PortInfo] = []
        # Split by comma, but be careful with ranges like [7:0]
        # We'll process token by token
        port_entries = self._split_port_list(port_list_str)

        current_direction: Optional[PortDirection] = None
        current_range: str = ""
        current_width: int = 1

        for entry in port_entries:
            entry = entry.strip()
            if not entry:
                continue

            port = self._parse_single_port_declaration(entry)
            if port:
                ports.append(port)

        return ports

    def _parse_old_style_ports(self, code: str) -> List[PortInfo]:
        """Parse old-style port declarations from module body."""
        ports: List[PortInfo] = []

        # Find all input/output/inout declarations in the module body
        # Pattern: (input|output|inout) [range] name1, name2, ...;
        decl_pattern = re.compile(
            r'\b(input|output|inout)\s*(?:wire\s*|reg\s*)?((?:\[\s*\d+\s*:\s*\d+\s*\])\s*)?(\w+(?:\s*,\s*\w+)*)\s*;',
            re.MULTILINE
        )

        for match in decl_pattern.finditer(code):
            direction_str = match.group(1).lower()
            range_str = (match.group(2) or "").strip()
            names_str = match.group(3)

            direction = PortDirection(direction_str)
            bit_width, is_vector, range_str_clean = self._parse_range(range_str)

            for name in re.split(r'\s*,\s*', names_str):
                name = name.strip()
                if name:
                    ports.append(PortInfo(
                        name=name,
                        direction=direction,
                        bit_width=bit_width,
                        is_vector=is_vector,
                        range_str=range_str_clean,
                    ))

        return ports

    def _split_port_list(self, port_list_str: str) -> List[str]:
        """Split a port list string by commas, respecting brackets."""
        entries = []
        depth = 0
        current = []
        for ch in port_list_str:
            if ch == '[':
                depth += 1
                current.append(ch)
            elif ch == ']':
                depth -= 1
                current.append(ch)
            elif ch == ',' and depth == 0:
                entries.append(''.join(current))
                current = []
            else:
                current.append(ch)
        if current:
            entries.append(''.join(current))
        return entries

    def _parse_single_port_declaration(self, decl: str) -> Optional[PortInfo]:
        """
        Parse a single port declaration string like:
          "input a", "input [7:0] data", "output [3:0] result", "inout bus"
        """
        decl = decl.strip()
        # Match: (input|output|inout) [wire|reg] [[range]] name
        match = re.match(
            r'\b(input|output|inout)\s*(?:wire\s*|reg\s*)?((?:\[\s*\d+\s*:\s*\d+\s*\])\s*)?(\w+)\s*$',
            decl,
            re.IGNORECASE
        )
        if not match:
            return None

        direction_str = match.group(1).lower()
        range_str = (match.group(2) or "").strip()
        name = match.group(3)

        direction = PortDirection(direction_str)
        bit_width, is_vector, range_str_clean = self._parse_range(range_str)

        return PortInfo(
            name=name,
            direction=direction,
            bit_width=bit_width,
            is_vector=is_vector,
            range_str=range_str_clean,
        )

    def _parse_range(self, range_str: str) -> Tuple[int, bool, str]:
        """
        Parse a bit range string like "[7:0]" or "[15:8]".

        Returns:
            Tuple of (bit_width, is_vector, range_str_clean)
        """
        range_str = range_str.strip()
        if not range_str:
            return 1, False, ""

        match = re.match(r'\[\s*(\d+)\s*:\s*(\d+)\s*\]', range_str)
        if match:
            high = int(match.group(1))
            low = int(match.group(2))
            bit_width = abs(high - low) + 1
            is_vector = bit_width > 1
            return bit_width, is_vector, f"[{high}:{low}]"

        return 1, False, ""

    def _detect_clock_signals(self, ports: List[PortInfo]) -> List[str]:
        """
        Detect clock signals from port list.

        Matches: clk, clock, CLK, CLOCK (case-insensitive, partial match allowed)

        Args:
            ports: List of PortInfo objects

        Returns:
            List of clock signal names
        """
        clock_pattern = re.compile(r'\b(clk|clock)\b', re.IGNORECASE)
        return [p.name for p in ports if clock_pattern.search(p.name)]

    def _detect_reset_signals(self, ports: List[PortInfo]) -> List[str]:
        """
        Detect reset signals from port list.

        Matches: rst, reset, RST, RESET (case-insensitive, partial match allowed)

        Args:
            ports: List of PortInfo objects

        Returns:
            List of reset signal names
        """
        reset_pattern = re.compile(r'\b(rst|reset)\b', re.IGNORECASE)
        return [p.name for p in ports if reset_pattern.search(p.name)]

    def _classify_logic_type(
        self,
        code: str,
        clock_signals: List[str],
        reset_signals: List[str],
    ) -> LogicType:
        """
        Classify module as SEQUENTIAL or COMBINATIONAL.

        SEQUENTIAL if:
          - Has clock or reset signals, OR
          - Contains posedge/negedge triggers in always blocks

        Args:
            code: Verilog source code (comments stripped)
            clock_signals: Detected clock signal names
            reset_signals: Detected reset signal names

        Returns:
            LogicType enum value
        """
        if clock_signals or reset_signals:
            return LogicType.SEQUENTIAL

        if re.search(r'@\s*\(\s*(posedge|negedge)', code, re.IGNORECASE):
            return LogicType.SEQUENTIAL

        return LogicType.COMBINATIONAL

    def _calculate_total_input_bits(self, ports: List[PortInfo]) -> int:
        """
        Calculate total number of input bits across all INPUT ports.

        Args:
            ports: List of PortInfo objects

        Returns:
            Sum of bit_width for all INPUT ports
        """
        return sum(p.bit_width for p in ports if p.direction == PortDirection.INPUT)

    def parse(self, verilog_code: str) -> ModuleInfo:
        """
        Parse Verilog code and extract module information.

        Args:
            verilog_code: Raw Verilog source code

        Returns:
            ModuleInfo object containing extracted data

        Raises:
            ParseError: If Verilog code is invalid or malformed
        """
        if not verilog_code or not verilog_code.strip():
            raise ParseError("No Verilog code provided")

        # Strip comments before parsing
        clean_code = self._strip_comments(verilog_code)

        # Extract module name
        module_name = self._extract_module_name(clean_code)
        logger.info(f"Parsing module: {module_name}")

        # Extract ports
        ports = self._extract_ports(clean_code)
        logger.info(f"Extracted {len(ports)} ports from module '{module_name}'")

        # Detect clock and reset signals
        clock_signals = self._detect_clock_signals(ports)
        reset_signals = self._detect_reset_signals(ports)

        # Classify logic type
        logic_type = self._classify_logic_type(clean_code, clock_signals, reset_signals)

        # Calculate total input bits
        total_input_bits = self._calculate_total_input_bits(ports)

        return ModuleInfo(
            module_name=module_name,
            ports=ports,
            clock_signals=clock_signals,
            reset_signals=reset_signals,
            logic_type=logic_type,
            total_input_bits=total_input_bits,
            raw_code=verilog_code,
        )
