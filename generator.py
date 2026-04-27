"""
Generator module for interfacing with LLM services to generate Verilog testbenches.
"""

import re
import time
import logging

logger = logging.getLogger(__name__)


class GenerationError(Exception):
    """Raised when testbench generation fails."""
    pass


class ValidationError(Exception):
    """Raised when LLM output validation fails."""
    pass


class TestbenchGenerator:
    """Interfaces with LLM services to generate Verilog testbenches."""

    def __init__(self, api_key: str = None, use_local: bool = False, demo_mode: bool = False):
        """
        Initialize generator with API configuration.

        Args:
            api_key: OpenAI API key (if using OpenAI)
            use_local: Use local LLM instead of OpenAI
            demo_mode: Use demo/mock responses without API calls
        """
        self.api_key = api_key
        self.use_local = use_local
        self.demo_mode = demo_mode
        self.model = "gpt-3.5-turbo"
        self.temperature = 0.2
        self.max_tokens = 2000

        # Initialize OpenAI client
        if not use_local and not demo_mode:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key)
            except ImportError:
                logger.warning("openai package not installed; API calls will fail")
                self.client = None
        else:
            self.client = None

        logger.info(
            f"TestbenchGenerator initialized (model={self.model}, "
            f"use_local={use_local}, demo_mode={demo_mode})"
        )

    def _call_openai_api(self, prompt: str, module_name: str) -> str:
        """
        Make an OpenAI ChatCompletion request.

        Args:
            prompt: The user prompt to send
            module_name: Module name (used for logging, not sent to API)

        Returns:
            Response content string from the LLM

        Raises:
            GenerationError: If the API call fails for any reason
        """
        logger.info(f"Calling OpenAI API for module '{module_name}' (model={self.model})")

        system_message = "You are a Verilog testbench generation expert. Output only pure Verilog code."

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=30,
            )
            content = response.choices[0].message.content
            logger.info(f"OpenAI API call succeeded for module '{module_name}'")
            return content

        except Exception as e:
            error_type = type(e).__name__
            # Avoid logging the full exception which may contain sensitive data
            logger.error(f"OpenAI API call failed for module '{module_name}': {error_type}")
            raise GenerationError(
                f"OpenAI API call failed ({error_type}): {e}"
            ) from e

    def _call_local_llm(self, prompt: str, endpoint_url: str) -> str:
        """
        Stub method for future local LLM support.

        Args:
            prompt: The prompt to send
            endpoint_url: URL of the local LLM endpoint

        Raises:
            NotImplementedError: Always, as this is a stub for future implementation
        """
        raise NotImplementedError(
            "Local LLM support is not yet implemented. "
            "To use a local LLM, configure an endpoint URL and implement this method. "
            "Compatible services include Ollama (https://ollama.ai) and LM Studio."
        )

    def _extract_verilog_code(self, response: str) -> str:
        """
        Extract pure Verilog code from an LLM response.

        Strips markdown code fences, removes text before the first Verilog
        construct, and removes text after the last endmodule.

        Args:
            response: Raw LLM response string

        Returns:
            Clean Verilog code string
        """
        code = response.strip()

        # Strip ```verilog ... ``` or ``` ... ``` fences
        code = re.sub(r'```verilog\s*', '', code, flags=re.IGNORECASE)
        code = re.sub(r'```\s*', '', code)

        # Remove any text before `timescale or before first "module" keyword
        timescale_match = re.search(r'`timescale\b', code)
        module_match = re.search(r'\bmodule\b', code)

        start_pos = None
        if timescale_match:
            start_pos = timescale_match.start()
        elif module_match:
            start_pos = module_match.start()

        if start_pos is not None:
            code = code[start_pos:]

        # Remove any text after the last "endmodule"
        last_endmodule = code.rfind('endmodule')
        if last_endmodule != -1:
            code = code[:last_endmodule + len('endmodule')]

        return code.strip()

    def _validate_response(self, code: str, module_name: str) -> None:
        """
        Validate that generated testbench contains critical elements.

        Args:
            code: Generated Verilog code
            module_name: Name of the module being tested (for DUT instantiation check)

        Raises:
            ValidationError: If any critical element is missing
        """
        # Check for module declaration
        if not re.search(r'module\s+\w+', code):
            logger.warning(f"Validation failed for '{module_name}': missing module declaration")
            raise ValidationError("Generated code is missing a module declaration")

        # Check for endmodule keyword
        if 'endmodule' not in code:
            logger.warning(f"Validation failed for '{module_name}': missing endmodule keyword")
            raise ValidationError("Generated code is missing the endmodule keyword")

        # Check for DUT instantiation (module_name appears in code)
        if module_name not in code:
            logger.warning(
                f"Validation failed: DUT instantiation of '{module_name}' not found in generated code"
            )
            raise ValidationError(
                f"Generated code is missing DUT instantiation of '{module_name}'"
            )

        logger.info(f"Validation passed for module '{module_name}'")

    def generate_with_retry(
        self,
        prompt: str,
        module_name: str,
        max_retries: int = 2,
        fallback_prompt: str = None,
    ) -> str:
        """
        Generate testbench with automatic retry on failure.

        Args:
            prompt: Structured prompt for LLM
            module_name: Name of the module being tested
            max_retries: Maximum number of retry attempts (default 2)
            fallback_prompt: Optional simplified prompt to use on last attempt

        Returns:
            Validated testbench Verilog code

        Raises:
            GenerationError: If all retry attempts fail
        """
        total_attempts = max_retries + 1
        last_error = None

        for attempt in range(total_attempts):
            # Choose prompt: use fallback on last attempt if provided
            if attempt == total_attempts - 1 and fallback_prompt is not None:
                current_prompt = fallback_prompt
                logger.info(f"Attempt {attempt + 1}/{total_attempts}: using fallback prompt")
            else:
                current_prompt = prompt
                logger.info(f"Attempt {attempt + 1}/{total_attempts}: using original prompt")

            try:
                # Call the appropriate API
                if self.use_local:
                    response = self._call_local_llm(current_prompt, endpoint_url="")
                else:
                    response = self._call_openai_api(current_prompt, module_name)

                # Extract and validate
                code = self._extract_verilog_code(response)
                self._validate_response(code, module_name)

                logger.info(
                    f"Generation succeeded for module '{module_name}' on attempt {attempt + 1}"
                )
                return code

            except (GenerationError, ValidationError) as e:
                last_error = e
                if attempt < total_attempts - 1:
                    backoff = 1 * attempt  # 0s, 1s, 2s, ...
                    logger.warning(
                        f"Generation attempt {attempt + 1} failed for '{module_name}': {e}. "
                        f"Retrying in {backoff}s..."
                    )
                    if backoff > 0:
                        time.sleep(backoff)
                else:
                    logger.error(
                        f"All {total_attempts} generation attempts failed for '{module_name}': {e}"
                    )

        raise GenerationError(
            f"Testbench generation failed after {total_attempts} attempt(s): {last_error}"
        )

    def generate(self, prompt: str, module_name: str, fallback_prompt: str = None) -> str:
        """
        Generate a testbench for the given module.

        Args:
            prompt: Structured prompt from PromptBuilder
            module_name: Name of the module being tested
            fallback_prompt: Optional simplified prompt for last retry attempt

        Returns:
            Validated testbench Verilog code

        Raises:
            GenerationError: If generation fails after all retries
        """
        start_time = time.perf_counter()
        logger.info(f"Starting testbench generation for module '{module_name}'")

        result = self.generate_with_retry(
            prompt=prompt,
            module_name=module_name,
            fallback_prompt=fallback_prompt,
        )

        elapsed = time.perf_counter() - start_time
        logger.info(
            f"Testbench generation completed for '{module_name}' in {elapsed:.2f}s"
        )
        return result
