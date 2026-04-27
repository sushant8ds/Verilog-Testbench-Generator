# Implementation Plan: Verilog Testbench Generator

## Overview

This implementation plan breaks down the Verilog Testbench Generator into discrete coding tasks. The system is a Python-based web application using Streamlit for the UI, with modular components for parsing Verilog code, building LLM prompts, and generating testbenches via OpenAI API or local LLM.

The implementation follows a bottom-up approach: data models → parser → prompt builder → generator → UI integration → testing.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create project directory structure (root, tests/, .streamlit/)
  - Create requirements.txt with dependencies: streamlit, openai, hypothesis, pytest, pytest-cov
  - Create README.md with setup and usage instructions
  - Create .gitignore for Python projects
  - _Requirements: 3.1, 3.6, 3.7, 3.8_

- [x] 2. Implement data models and exceptions (parser.py foundation)
  - [x] 2.1 Create enums and dataclasses in parser.py
    - Implement LogicType enum (COMBINATIONAL, SEQUENTIAL)
    - Implement PortDirection enum (INPUT, OUTPUT, INOUT)
    - Implement PortInfo dataclass with fields: name, direction, bit_width, is_vector, range_str
    - Implement ModuleInfo dataclass with fields: module_name, ports, clock_signals, reset_signals, logic_type, total_input_bits, raw_code
    - _Requirements: 4.2, 4.6, 5.4, 5.5_

  - [x] 2.2 Create custom exception classes in parser.py
    - Implement ParseError exception
    - Implement GenerationError exception (in generator.py)
    - Implement ValidationError exception (in generator.py)
    - _Requirements: 4.3, 11.7_

- [x] 3. Implement VerilogParser class (parser.py)
  - [x] 3.1 Implement module name extraction
    - Write _extract_module_name() method using regex to find "module <name>"
    - Handle edge cases: whitespace variations, comments
    - Raise ParseError if no module declaration found
    - _Requirements: 4.1_

  - [ ]* 3.2 Write property test for module name extraction
    - **Property 1: Module Name Extraction**
    - **Validates: Requirements 4.1**

  - [x] 3.3 Implement port extraction
    - Write _extract_ports() method to parse port declarations
    - Handle single-line port declarations: "input a, output b"
    - Handle multi-line port declarations with proper parsing
    - Extract port direction, name, and bit-width
    - Parse bit ranges like [7:0], [15:8], handle single-bit ports
    - Return List[PortInfo]
    - _Requirements: 4.2, 4.7_

  - [ ]* 3.4 Write property test for port information extraction
    - **Property 2: Port Information Extraction**
    - **Validates: Requirements 4.2**

  - [ ]* 3.5 Write property test for port declaration format independence
    - **Property 7: Port Declaration Format Independence**
    - **Validates: Requirements 4.7**

  - [x] 3.6 Implement clock signal detection
    - Write _detect_clock_signals() method
    - Match patterns: clk, clock, CLK, CLOCK (case-insensitive)
    - Return list of detected clock signal names
    - _Requirements: 4.4_

  - [ ]* 3.7 Write property test for clock signal detection
    - **Property 4: Clock Signal Detection**
    - **Validates: Requirements 4.4**

  - [x] 3.8 Implement reset signal detection
    - Write _detect_reset_signals() method
    - Match patterns: rst, reset, RST, RESET (case-insensitive)
    - Return list of detected reset signal names
    - _Requirements: 4.5_

  - [ ]* 3.9 Write property test for reset signal detection
    - **Property 5: Reset Signal Detection**
    - **Validates: Requirements 4.5**

  - [x] 3.10 Implement logic type classification
    - Write _classify_logic_type() method
    - Check for clock/reset signals → SEQUENTIAL
    - Check for edge-sensitive always blocks (@(posedge/@(negedge) → SEQUENTIAL
    - Otherwise → COMBINATIONAL
    - _Requirements: 5.1, 5.2, 5.3_

  - [ ]* 3.11 Write property tests for logic type classification
    - **Property 8: Sequential Logic Classification - Clock/Reset**
    - **Property 9: Sequential Logic Classification - Edge Sensitivity**
    - **Property 10: Combinational Logic Classification**
    - **Validates: Requirements 5.1, 5.2, 5.3**

  - [x] 3.12 Implement total input bits calculation
    - Write _calculate_total_input_bits() method
    - Sum bit_width for all INPUT ports
    - Handle single-bit and multi-bit ports correctly
    - _Requirements: 6.1, 6.2_

  - [x] 3.13 Implement main parse() method
    - Orchestrate all extraction methods
    - Call _extract_module_name(), _extract_ports(), _detect_clock_signals(), _detect_reset_signals(), _classify_logic_type(), _calculate_total_input_bits()
    - Return populated ModuleInfo object
    - Handle errors and raise ParseError with descriptive messages
    - _Requirements: 4.1, 4.2, 4.3, 4.6_

  - [ ]* 3.14 Write property test for structured data completeness
    - **Property 6: Structured Data Completeness**
    - **Validates: Requirements 4.6**

  - [ ]* 3.15 Write property test for invalid input error handling
    - **Property 3: Invalid Input Error Handling**
    - **Validates: Requirements 4.3**

  - [ ]* 3.16 Write unit tests for parser edge cases
    - Test empty input
    - Test module with no ports
    - Test ports with unusual bit ranges [15:8]
    - Test comments in port declarations
    - Test mixed single-line and multi-line declarations
    - _Requirements: 4.3, 4.7_

- [ ] 4. Checkpoint - Ensure parser tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement PromptBuilder class (prompt_builder.py)
  - [x] 5.1 Implement test strategy determination logic
    - Write _determine_test_strategy() method
    - If total_input_bits <= 10: return "exhaustive" strategy text
    - If total_input_bits > 10: return "representative" strategy text
    - Include standard patterns: all-zeros, all-ones, boundary values, alternating patterns
    - If SEQUENTIAL: add reset behavior and multi-cycle sequences
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8_

  - [ ]* 5.2 Write property test for exhaustive test strategy
    - **Property 11: Exhaustive Test Strategy for Small Inputs**
    - **Validates: Requirements 6.1**

  - [ ]* 5.3 Write property test for representative test strategy
    - **Property 12: Representative Test Strategy for Large Inputs**
    - **Validates: Requirements 6.2**

  - [ ]* 5.4 Write property test for standard test pattern inclusion
    - **Property 13: Standard Test Pattern Inclusion**
    - **Validates: Requirements 6.3, 6.4, 6.7, 6.8**

  - [ ]* 5.5 Write property test for sequential logic test requirements
    - **Property 14: Sequential Logic Test Requirements**
    - **Validates: Requirements 6.5, 6.6**

  - [x] 5.6 Implement build_prompt() method
    - Create structured prompt with sections: MODULE INFORMATION, TEST STRATEGY, REQUIREMENTS, OUTPUT FORMAT
    - Include module name, logic type, ports list, clock/reset signals
    - Include test strategy from _determine_test_strategy()
    - Include specific requirements for testbench structure (timescale, reg/wire declarations, DUT instantiation, clock generation, display statements, etc.)
    - Include output format requirements (pure Verilog, no markdown, simulation-ready)
    - _Requirements: 2.3, 2.7, 2.8, 2.9_

  - [ ]* 5.7 Write property test for module information in prompt
    - **Property 15: Module Information in Prompt**
    - **Validates: Requirements 2.7**

  - [ ]* 5.8 Write property test for test strategy in prompt
    - **Property 16: Test Strategy in Prompt**
    - **Validates: Requirements 2.8**

  - [ ]* 5.9 Write property test for output format requirements in prompt
    - **Property 17: Output Format Requirements in Prompt**
    - **Validates: Requirements 2.9**

  - [ ]* 5.10 Write unit tests for prompt builder edge cases
    - Test module with 0 input bits (only outputs)
    - Test module with exactly 10 input bits (boundary)
    - Test module with 11 input bits (boundary)
    - Test module with very large bit-width ports
    - _Requirements: 6.1, 6.2_

- [ ] 6. Checkpoint - Ensure prompt builder tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement TestbenchGenerator class (generator.py)
  - [x] 7.1 Implement __init__() and OpenAI API configuration
    - Initialize with api_key and use_local parameters
    - Configure OpenAI client with API key
    - Set model (gpt-4 or gpt-3.5-turbo), temperature (0.2), max_tokens (2000)
    - _Requirements: 2.1, 2.2_

  - [x] 7.2 Implement _call_openai_api() method
    - Make API request to OpenAI ChatCompletion endpoint
    - Pass prompt as user message
    - Handle API errors (connection, rate limit, timeout)
    - Set 30-second timeout
    - Return response content
    - _Requirements: 2.1, 13.4_

  - [x] 7.3 Implement _call_local_llm() method (stub for future)
    - Create placeholder method for local LLM support
    - Accept endpoint URL parameter
    - Return mock response or raise NotImplementedError
    - _Requirements: 2.2_

  - [x] 7.4 Implement _extract_verilog_code() method
    - Remove markdown code blocks (```verilog ... ```)
    - Remove explanatory text before/after code
    - Extract pure Verilog code
    - Handle cases where LLM returns plain Verilog without markdown
    - _Requirements: 10.1, 10.2, 10.5_

  - [x] 7.5 Implement _validate_response() method
    - Check for module declaration using regex
    - Check for endmodule keyword
    - Check for DUT instantiation (original module name present)
    - Raise ValidationError with descriptive message if any check fails
    - _Requirements: 11.1, 11.2, 11.3, 11.5, 11.7_

  - [ ]* 7.6 Write property tests for LLM output validation
    - **Property 18: LLM Output Validation - Module Declaration**
    - **Property 19: LLM Output Validation - Module End**
    - **Property 20: LLM Output Validation - DUT Instantiation**
    - **Validates: Requirements 11.2, 11.3, 11.4**

  - [x] 7.7 Implement generate_with_retry() method
    - Implement retry loop with max_retries parameter (default 2)
    - Call _call_openai_api() or _call_local_llm()
    - Call _extract_verilog_code() on response
    - Call _validate_response() on extracted code
    - On failure: log warning, sleep with exponential backoff, retry
    - After all retries fail: raise GenerationError with descriptive message
    - _Requirements: 12.1, 12.2, 12.3, 12.5_

  - [ ]* 7.8 Write property test for retry on validation failure
    - **Property 21: Retry on Validation Failure**
    - **Validates: Requirements 12.1, 12.2, 12.5**

  - [ ]* 7.9 Write property test for final error after retries
    - **Property 22: Final Error After Retries**
    - **Validates: Requirements 12.3**

  - [x] 7.10 Implement main generate() method
    - Call generate_with_retry() with prompt
    - Return validated testbench code
    - _Requirements: 2.1, 2.5_

  - [ ]* 7.11 Write unit tests for generator error handling
    - Mock API connection failure
    - Mock API rate limit error
    - Mock timeout error
    - Mock invalid response (no Verilog code)
    - Test code extraction from markdown
    - Test code extraction from plain text
    - _Requirements: 2.6, 12.5_

- [ ] 8. Checkpoint - Ensure generator tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Implement Streamlit application (app.py)
  - [x] 9.1 Create main UI layout
    - Set page title: "Verilog Testbench Generator"
    - Add description text
    - Create input method radio button (Upload File / Paste Code)
    - _Requirements: 1.1, 1.7_

  - [x] 9.2 Implement file upload functionality
    - Add file_uploader widget for .v and .sv files
    - Read uploaded file content and decode to string
    - Display file content in input panel
    - _Requirements: 1.2, 1.8_

  - [x] 9.3 Implement text area for code input
    - Add text_area widget with height=300
    - Allow users to paste Verilog code directly
    - _Requirements: 1.3_

  - [x] 9.4 Implement Generate button and orchestration logic
    - Add "Generate Testbench" button
    - On click: validate input is not empty
    - Show loading spinner with st.spinner()
    - Instantiate VerilogParser and call parse()
    - Instantiate PromptBuilder and call build_prompt()
    - Instantiate TestbenchGenerator with API key from st.secrets
    - Call generate_with_retry() with max_retries=2
    - Display success message on completion
    - _Requirements: 1.9, 2.1, 13.2, 13.3_

  - [x] 9.5 Implement error handling and display
    - Catch ParseError and display with st.error()
    - Catch ValidationError and display with st.error()
    - Catch GenerationError and display with st.error()
    - Catch generic Exception and display with st.error()
    - Display retry status during retry attempts
    - Preserve user input on error for manual retry
    - _Requirements: 1.10, 11.6, 12.3, 12.6, 12.7_

  - [x] 9.6 Implement side-by-side display panels
    - Create two columns using st.columns(2)
    - Left column: display input Verilog code with st.code()
    - Right column: display generated testbench code with st.code()
    - Use language='verilog' for syntax highlighting
    - _Requirements: 1.4, 1.5_

  - [x] 9.7 Implement download button
    - Add st.download_button() in right column
    - Set file name to "testbench.v"
    - Set file content to generated testbench code
    - _Requirements: 1.6_

  - [x] 9.8 Add configuration sidebar (optional)
    - Add sidebar with st.sidebar
    - Option to toggle between OpenAI and local LLM
    - Display API key status (configured/not configured)
    - _Requirements: 2.2_

- [x] 10. Create Streamlit configuration
  - [x] 10.1 Create .streamlit/secrets.toml file
    - Add OPENAI_API_KEY placeholder
    - Add instructions in comments for users to add their API key
    - _Requirements: 2.1_

  - [x] 10.2 Update README.md with configuration instructions
    - Document how to set up .streamlit/secrets.toml
    - Document how to obtain OpenAI API key
    - Document how to run the application: streamlit run app.py
    - _Requirements: 3.7, 3.8_

- [x] 11. Implement logging system
  - [x] 11.1 Configure logging in all modules
    - Add logging configuration in each module (parser.py, prompt_builder.py, generator.py, app.py)
    - Use Python logging module with appropriate log levels (INFO, WARNING, ERROR)
    - Configure log format: timestamp, module name, level, message
    - _Requirements: Error Handling (Logging section in design)_

  - [x] 11.2 Add logging for parser operations
    - Log successful parsing with module name and port count
    - Log parsing failures with error details
    - Log parsing time for performance monitoring
    - _Requirements: Error Handling (Logging section in design)_

  - [x] 11.3 Add logging for generator operations
    - Log API calls (without sensitive data like API keys)
    - Log retry attempts with attempt number
    - Log validation failures with details
    - Log generation success with timing
    - _Requirements: Error Handling (Logging section in design), 12.6_

  - [x] 11.4 Add logging for errors
    - Log full exception details for debugging
    - Include stack traces for unexpected errors
    - Log user-facing error messages
    - _Requirements: Error Handling (Logging section in design)_

- [x] 12. Implement performance monitoring
  - [x] 12.1 Add timing measurements
    - Measure parsing time using time.time() or time.perf_counter()
    - Measure prompt building time
    - Measure LLM generation time (including retries)
    - Measure total end-to-end time
    - _Requirements: 13.1, 13.6, 13.7_

  - [x] 12.2 Display performance metrics in UI
    - Show generation time in success message: "Testbench generated successfully in X.XX seconds"
    - Optionally display breakdown (parsing, generation) in expandable section
    - Log performance metrics for monitoring
    - _Requirements: 13.1_

  - [x] 12.3 Add performance logging
    - Log all timing measurements at INFO level
    - Track performance trends over time
    - Identify slow operations for optimization
    - _Requirements: Error Handling (Logging section in design)_

- [x] 13. Implement enhanced validation (basic syntax checks)
  - [x] 13.1 Add syntax validation to _validate_response()
    - Check balanced parentheses: count '(' and ')' match
    - Check balanced begin/end blocks
    - Check semicolon presence in key statements
    - Verify basic Verilog syntax patterns
    - _Requirements: 11.2, 11.3, 11.4_

  - [x] 13.2 Add validation error details
    - Provide specific error messages for each validation failure
    - Example: "Unbalanced parentheses detected (5 open, 4 close)"
    - Example: "Missing semicolons in testbench code"
    - Help users understand what went wrong
    - _Requirements: 11.6_

  - [ ]* 13.3 Write unit tests for syntax validation
    - Test balanced parentheses check
    - Test unbalanced parentheses detection
    - Test semicolon validation
    - Test begin/end block validation
    - _Requirements: 11.2, 11.3, 11.4_

- [x] 14. Implement fallback prompt strategy
  - [x] 14.1 Create simplified prompt template
    - Design a simpler, more direct prompt for fallback
    - Remove complex instructions that might confuse LLM
    - Focus on essential requirements only
    - Store as separate template in prompt_builder.py
    - _Requirements: 2.3, 12.1_

  - [x] 14.2 Modify retry logic to use fallback prompt
    - On first retry: use original prompt
    - On second retry: use simplified fallback prompt
    - Log when fallback prompt is used
    - Track success rate of fallback vs original prompt
    - _Requirements: 12.1, 12.2_

  - [x] 14.3 Add fallback prompt configuration
    - Allow users to customize fallback behavior
    - Option to skip fallback and retry with same prompt
    - Document fallback strategy in README
    - _Requirements: 2.3_

- [x] 15. Implement demo mode (offline mode)
  - [x] 15.1 Create mock testbench responses
    - Create predefined testbench examples for common modules
    - Store in demo_responses.py or JSON file
    - Include examples: AND gate, adder, D flip-flop, counter
    - Ensure examples are high-quality and realistic
    - _Requirements: 2.2 (alternative to LLM)_

  - [x] 15.2 Add demo mode toggle in UI
    - Add checkbox in sidebar: "Demo Mode (No API required)"
    - When enabled, use mock responses instead of API calls
    - Display notice: "Running in demo mode with predefined examples"
    - _Requirements: 1.1, 2.2_

  - [x] 15.3 Implement demo mode logic in generator
    - Add demo_mode parameter to TestbenchGenerator.__init__()
    - In generate() method: if demo_mode, return mock response
    - Match mock response to input module type (combinational/sequential)
    - Add slight randomization to make it feel realistic
    - _Requirements: 2.2_

  - [x] 15.4 Document demo mode in README
    - Explain how to enable demo mode
    - List available demo examples
    - Clarify that demo mode is for testing/demonstration only
    - _Requirements: 3.7, 3.8_

- [ ]* 11. Write integration tests (tests/test_generator_integration.py)
  - Test generator with mocked OpenAI API
  - Test full workflow with mocked LLM responses
  - Verify prompt format and response parsing
  - Test retry mechanism with mocked failures
  - Test fallback prompt strategy
  - Test demo mode functionality
  - _Requirements: 2.1, 12.1, 12.2_

- [ ]* 12. Write end-to-end tests (tests/test_e2e.py)
  - Test complete workflow for simple combinational module (AND gate)
  - Test complete workflow for small combinational module (4-bit adder)
  - Test complete workflow for sequential module (D flip-flop)
  - Use real parser and prompt builder, mocked generator
  - Verify output is valid Verilog (basic syntax check)
  - Test performance monitoring (timing measurements)
  - _Requirements: 4.1, 4.2, 5.1, 6.1, 6.5, 13.1_

- [x] 13. Final checkpoint - Run all tests and verify application
  - Run pytest with coverage: pytest --cov=. --cov-report=html
  - Verify coverage >= 85%
  - Run manual UI tests with example modules
  - Test file upload with .v file
  - Test paste code functionality
  - Test error handling with invalid input
  - Test demo mode with and without API key
  - Test performance monitoring display
  - Verify logging output in console/file
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property-based tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- Integration and E2E tests verify the complete workflow
- The implementation uses Python with Streamlit, OpenAI API, and Hypothesis for property-based testing
- API keys should be configured in .streamlit/secrets.toml before running the application

## Production-Ready Features

The following tasks add production-ready capabilities:

1. **Logging System (Task 11)**: Comprehensive logging for debugging and monitoring
2. **Performance Monitoring (Task 12)**: Track and display generation times
3. **Enhanced Validation (Task 13)**: Basic syntax checks beyond structural validation
4. **Fallback Prompt Strategy (Task 14)**: Advanced GenAI technique for improved reliability
5. **Demo Mode (Task 15)**: Offline mode for testing and demonstration without API costs

These features make the system more robust, reliable, and professional.
