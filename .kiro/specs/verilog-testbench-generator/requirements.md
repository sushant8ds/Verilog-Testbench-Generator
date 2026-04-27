# Requirements Document

## Introduction

The Verilog Testbench Generator is a web-based system that automatically analyzes Verilog RTL modules and generates complete, simulation-ready testbenches using GenAI technology. The system provides a user-friendly Streamlit interface where users can upload or paste Verilog code, leverages Large Language Models (LLMs) to generate intelligent testbenches, and delivers properly formatted testbench code that can be executed in standard Verilog simulators without modification. The system uses structured prompt engineering to ensure consistent, high-quality output and supports both cloud-based (OpenAI) and local LLM options.

## Glossary

- **Generator**: The Verilog Testbench Generator system
- **Web_Application**: The Streamlit-based user interface
- **RTL_Module**: A Verilog hardware description module provided as input
- **Testbench**: A Verilog module that instantiates and tests an RTL_Module
- **DUT**: Device Under Test - the RTL_Module being tested
- **Port**: An input or output signal of an RTL_Module
- **Combinational_Logic**: Logic where outputs depend only on current inputs
- **Sequential_Logic**: Logic where outputs depend on clock edges and previous state
- **Test_Case**: A set of input values applied to the DUT with expected outputs
- **Simulator**: A Verilog simulation tool such as ModelSim or Icarus Verilog
- **LLM**: Large Language Model used for testbench generation
- **Parser**: Component that extracts structural information from Verilog code
- **Prompt_Builder**: Component that constructs structured prompts for the LLM
- **Generator_Module**: Component that interfaces with the LLM API

## Requirements

### Requirement 1: Web Application Interface

**User Story:** As a hardware engineer, I want a simple web interface, so that I can easily generate testbenches without command-line tools.

#### Acceptance Criteria

1. THE Web_Application SHALL provide a Streamlit-based user interface
2. THE Web_Application SHALL allow users to upload Verilog files
3. THE Web_Application SHALL allow users to paste Verilog code directly into a text area
4. THE Web_Application SHALL display the input Verilog code in a dedicated panel
5. THE Web_Application SHALL display the generated testbench code in a separate panel side-by-side with the input
6. THE Web_Application SHALL provide a download button to save the generated testbench as a .v file
7. THE Web_Application SHALL use a clean, beginner-friendly interface design
8. WHEN a user uploads a file, THE Web_Application SHALL display the file contents in the input panel
9. WHEN testbench generation completes, THE Web_Application SHALL automatically display the result
10. THE Web_Application SHALL provide clear error messages when generation fails

### Requirement 2: GenAI Integration

**User Story:** As a hardware engineer, I want the system to use AI for intelligent testbench generation, so that I get high-quality, context-aware results.

#### Acceptance Criteria

1. THE Generator SHALL use the OpenAI API as the primary LLM provider
2. THE Generator SHALL support local LLM as an alternative option to OpenAI
3. THE Generator SHALL use structured prompt engineering to ensure consistent output format
4. THE Generator SHALL NOT use hardcoded testbench templates or outputs
5. THE Generator SHALL generate all testbench content dynamically via the LLM
6. WHEN the OpenAI API is unavailable, THE Generator SHALL provide a clear error message
7. THE Generator SHALL include module analysis information in the LLM prompt
8. THE Generator SHALL include test strategy guidance in the LLM prompt
9. THE Generator SHALL request specific output format requirements in the LLM prompt

### Requirement 3: System Architecture

**User Story:** As a developer, I want a modular codebase, so that I can maintain and extend the system easily.

#### Acceptance Criteria

1. THE Generator SHALL be implemented in Python
2. THE Generator SHALL include a parser.py module for Verilog parsing
3. THE Generator SHALL include a prompt_builder.py module for constructing LLM prompts
4. THE Generator SHALL include a generator.py module for LLM integration
5. THE Generator SHALL include an app.py module for the Streamlit application
6. THE Generator SHALL include a requirements.txt file listing all dependencies
7. THE Generator SHALL include setup instructions in a README file
8. THE Generator SHALL include run instructions in the README file
9. THE Parser module SHALL be independently testable
10. THE Prompt_Builder module SHALL be independently testable

### Requirement 4: Parse Verilog Module Definition

**User Story:** As a hardware engineer, I want the system to parse my Verilog module, so that it can understand the module structure.

#### Acceptance Criteria

1. WHEN a valid Verilog RTL_Module is provided, THE Parser SHALL extract the module name
2. WHEN a valid Verilog RTL_Module is provided, THE Parser SHALL extract all Port names, types (input/output/inout), and bit-widths
3. WHEN an invalid or malformed Verilog module is provided, THE Parser SHALL return a descriptive error message
4. THE Parser SHALL identify whether the RTL_Module contains clock signals (signals named clk, clock, or similar)
5. THE Parser SHALL identify whether the RTL_Module contains reset signals (signals named rst, reset, or similar)
6. THE Parser SHALL return structured data containing all extracted information
7. THE Parser SHALL handle single-line and multi-line port declarations

### Requirement 5: Determine Logic Type

**User Story:** As a hardware engineer, I want the system to classify my module's logic type, so that appropriate test strategies are applied.

#### Acceptance Criteria

1. WHEN an RTL_Module contains clock or reset signals, THE Parser SHALL classify it as Sequential_Logic
2. WHEN an RTL_Module contains always blocks with edge-sensitive triggers, THE Parser SHALL classify it as Sequential_Logic
3. WHEN an RTL_Module contains no clock signals and no edge-sensitive always blocks, THE Parser SHALL classify it as Combinational_Logic
4. THE Parser SHALL record the logic type classification for use in test generation
5. THE Parser SHALL include logic type in the structured data output

### Requirement 6: Generate Test Strategy

**User Story:** As a hardware engineer, I want the system to create an appropriate test strategy, so that my module is thoroughly tested.

#### Acceptance Criteria

1. WHEN an RTL_Module has total input bits <= 10, THE Prompt_Builder SHALL specify exhaustive test cases covering all input combinations
2. WHEN an RTL_Module has total input bits > 10, THE Prompt_Builder SHALL specify representative test cases including edge cases
3. THE Prompt_Builder SHALL specify test cases for all-zeros input values
4. THE Prompt_Builder SHALL specify test cases for all-ones input values
5. WHEN an RTL_Module is classified as Sequential_Logic, THE Prompt_Builder SHALL specify test cases that exercise reset behavior
6. WHEN an RTL_Module is classified as Sequential_Logic, THE Prompt_Builder SHALL specify test cases spanning multiple clock cycles
7. THE Prompt_Builder SHALL specify test cases for boundary values (maximum and minimum values for each input port)
8. THE Prompt_Builder SHALL specify alternating bit pattern test cases

### Requirement 7: Generate Testbench Structure

**User Story:** As a hardware engineer, I want the system to generate a complete testbench module, so that I can run simulations immediately.

#### Acceptance Criteria

1. THE LLM SHALL create a testbench module named "tb_<module_name>" where <module_name> is the RTL_Module name
2. THE LLM SHALL include a timescale directive at the beginning of the testbench
3. THE LLM SHALL declare all input ports as reg type signals
4. THE LLM SHALL declare all output ports as wire type signals
5. THE LLM SHALL instantiate the DUT with correct port mapping
6. WHEN the RTL_Module is Sequential_Logic, THE LLM SHALL include clock generation logic with configurable period
7. THE LLM SHALL include an initial block containing test case execution logic
8. THE LLM SHALL include proper signal declarations for all testbench variables

### Requirement 8: Generate Verification Logic

**User Story:** As a hardware engineer, I want the testbench to display test results, so that I can verify correct operation.

#### Acceptance Criteria

1. THE LLM SHALL include $display statements showing input values for each Test_Case
2. THE LLM SHALL include $display statements showing output values for each Test_Case
3. THE LLM SHALL include comments indicating expected output values for each Test_Case
4. THE LLM SHALL include $monitor statements to track signal changes during simulation
5. WHEN the RTL_Module is Sequential_Logic, THE LLM SHALL include appropriate delay statements between test cases
6. THE LLM SHALL include a $finish statement to end simulation

### Requirement 9: Ensure Code Quality

**User Story:** As a hardware engineer, I want the generated testbench to be clean and readable, so that I can understand and modify it easily.

#### Acceptance Criteria

1. THE Generator SHALL produce Verilog code with consistent indentation (2 or 4 spaces per level)
2. THE Generator SHALL produce syntactically correct Verilog code
3. THE Generator SHALL produce code that compiles without errors in standard Simulators
4. THE Generator SHALL use descriptive signal names matching the RTL_Module port names
5. THE Generator SHALL include comments explaining the test strategy and test cases
6. THE Generator SHALL produce properly formatted code ready for simulation

### Requirement 10: Output Format

**User Story:** As a hardware engineer, I want the output to be pure Verilog code, so that I can directly save it to a file and run simulations.

#### Acceptance Criteria

1. THE Generator SHALL output pure Verilog code without markdown formatting
2. THE Generator SHALL output code without explanatory text outside of Verilog comments
3. THE Generator SHALL produce output that can be saved directly to a .v or .sv file
4. THE Generator SHALL produce simulation-ready code requiring no manual modifications
5. THE Web_Application SHALL extract only Verilog code from LLM responses for display and download

### Requirement 11: LLM Output Validation

**User Story:** As a hardware engineer, I want the system to validate generated testbenches, so that I receive only complete and correct outputs.

#### Acceptance Criteria

1. THE Generator SHALL treat LLM output as non-deterministic
2. THE Generator SHALL validate the presence of a module declaration in generated code
3. THE Generator SHALL validate the presence of an endmodule keyword in generated code
4. THE Generator SHALL validate the presence of DUT instantiation in generated code
5. WHEN critical elements are missing from generated code, THE Generator SHALL reject the output
6. WHEN validation fails, THE Generator SHALL display a clear error message to the user
7. THE Generator SHALL raise a ValidationError when critical elements are missing

### Requirement 12: Retry Strategy

**User Story:** As a hardware engineer, I want the system to automatically retry on failures, so that temporary issues don't prevent successful generation.

#### Acceptance Criteria

1. WHEN generation fails, THE Generator SHALL retry up to 2 times
2. THE Generator SHALL use exponential backoff between retry attempts
3. WHEN all retry attempts fail, THE Generator SHALL display a final error message
4. THE Generator SHALL NOT retry on parse errors (user input issues)
5. THE Generator SHALL retry on validation failures, API failures, and timeouts
6. THE Web_Application SHALL display retry status to the user during retry attempts
7. THE Generator SHALL preserve user input for manual retry after all attempts fail

### Requirement 13: Performance and Responsiveness

**User Story:** As a hardware engineer, I want fast generation with responsive UI, so that I can work efficiently.

#### Acceptance Criteria

1. THE Generator SHALL complete testbench generation within 2-10 seconds under normal conditions
2. THE Web_Application SHALL display a loading indicator during generation
3. THE Web_Application SHALL remain responsive during generation
4. THE Generator SHALL use a 30-second timeout for LLM API calls
5. THE Web_Application SHALL display retry status during retry attempts
6. THE Parser SHALL complete parsing in less than 100 milliseconds
7. THE Prompt_Builder SHALL complete prompt construction in less than 50 milliseconds
