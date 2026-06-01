"""
Verilog Testbench Generator — VLSI Synthesis Studio
Clean dark UI with subtle animations.
"""

import logging
import time
import streamlit as st

from parser import VerilogParser, ParseError
from prompt_builder import PromptBuilder
from generator import TestbenchGenerator, GenerationError, ValidationError
from demo_responses import get_demo_response

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _check_syntax(code: str) -> list:
    warnings = []
    if code.count("(") != code.count(")"):
        warnings.append(f"Unbalanced parentheses ({code.count('(')} open, {code.count(')')} close)")
    bc = len([w for w in code.split() if w.lower() == "begin"])
    ec = len([w for w in code.split() if w.lower() == "end"]) - code.lower().count("endmodule")
    if bc != ec:
        warnings.append(f"Unbalanced begin/end blocks ({bc} begin, {ec} end)")
    return warnings

def _build_fallback_prompt(module_info) -> str:
    ports = ", ".join(f"{p.direction.value} {p.name}" for p in module_info.ports)
    return (
        f"Generate a Verilog testbench for module '{module_info.module_name}'.\n"
        f"Ports: {ports}\nLogic type: {module_info.logic_type.value}\n\n"
        f"Requirements:\n- Module name: tb_{module_info.module_name}\n"
        "- Include `timescale 1ns/1ps\n- Declare inputs as reg, outputs as wire\n"
        f"- Instantiate {module_info.module_name} as dut\n"
        "- Include basic test cases with $display and $finish\n"
        "- Output pure Verilog only, no markdown\n"
    )

def _get_api_key() -> str:
    try:
        return st.secrets["OPENAI_API_KEY"]
    except (KeyError, FileNotFoundError):
        return None


# ─────────────────────────────────────────────────────────────────────────────
# CSS — clean dark theme, minimal animations
# ─────────────────────────────────────────────────────────────────────────────

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&display=swap');

@keyframes pulse-border {
  0%, 100% { box-shadow: 0 0 0 0 rgba(0,255,200,0.0); }
  50%       { box-shadow: 0 0 0 3px rgba(0,255,200,0.15); }
}
@keyframes fade-in {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes ping {
  75%, 100% { transform: scale(2); opacity: 0; }
}
@keyframes grid-drift {
  0%   { background-position: 0 0; }
  100% { background-position: 40px 40px; }
}

/* Base */
html, body, [data-testid="stAppViewContainer"], .stApp {
  background-color: #0d1117 !important;
  color: #e6edf3 !important;
  font-family: 'JetBrains Mono', monospace !important;
}

/* Subtle animated grid background */
[data-testid="stAppViewContainer"] {
  background-image:
    linear-gradient(rgba(0,255,200,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,255,200,0.03) 1px, transparent 1px) !important;
  background-size: 40px 40px !important;
  animation: grid-drift 20s linear infinite !important;
}

/* Main content */
.main .block-container {
  padding: 2rem 2.5rem !important;
  max-width: 1600px !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
  background-color: #0d1117 !important;
  border-right: 1px solid #21262d !important;
}
[data-testid="stSidebar"] * {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.78rem !important;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {
  color: #8b949e !important;
}

/* Headings */
h1 {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 1.3rem !important;
  font-weight: 700 !important;
  color: #00ffc8 !important;
  letter-spacing: 0.05em !important;
  text-shadow: 0 0 20px rgba(0,255,200,0.3) !important;
}
h2, h3 {
  font-family: 'JetBrains Mono', monospace !important;
  color: #8b949e !important;
  font-size: 0.75rem !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
}

/* Primary button */
.stButton > button[kind="primary"] {
  background: #00ffc8 !important;
  color: #0d1117 !important;
  border: none !important;
  border-radius: 6px !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.8rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.1em !important;
  padding: 0.7rem 2rem !important;
  width: 100% !important;
  transition: all 0.2s ease !important;
  animation: pulse-border 3s ease-in-out infinite !important;
}
.stButton > button[kind="primary"]:hover {
  background: #00e6b4 !important;
  box-shadow: 0 0 20px rgba(0,255,200,0.4) !important;
  transform: translateY(-1px) !important;
}

/* Secondary buttons */
.stButton > button:not([kind="primary"]) {
  background: transparent !important;
  color: #8b949e !important;
  border: 1px solid #21262d !important;
  border-radius: 6px !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.75rem !important;
}

/* Text area */
.stTextArea textarea {
  background: #161b22 !important;
  border: 1px solid #21262d !important;
  border-radius: 6px !important;
  color: #79c0ff !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.75rem !important;
  line-height: 1.7 !important;
  caret-color: #00ffc8 !important;
  transition: border-color 0.2s !important;
}
.stTextArea textarea:focus {
  border-color: #00ffc8 !important;
  box-shadow: 0 0 0 2px rgba(0,255,200,0.1) !important;
}

/* Code blocks */
.stCode, pre, code {
  background: #161b22 !important;
  border: 1px solid #21262d !important;
  border-radius: 6px !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.75rem !important;
  color: #7ee787 !important;
}

/* Selectbox */
.stSelectbox > div > div {
  background: #161b22 !important;
  border: 1px solid #21262d !important;
  border-radius: 6px !important;
  color: #c9d1d9 !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.75rem !important;
}

/* Radio */
.stRadio label { color: #8b949e !important; font-size: 0.75rem !important; }

/* Checkbox */
.stCheckbox label { color: #8b949e !important; font-size: 0.75rem !important; }

/* Text input */
.stTextInput input {
  background: #161b22 !important;
  border: 1px solid #21262d !important;
  border-radius: 6px !important;
  color: #c9d1d9 !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.75rem !important;
}

/* Alerts — animated fade in */
[data-testid="stAlert"] {
  animation: fade-in 0.35s ease !important;
  border-radius: 6px !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.75rem !important;
}

/* Download button */
.stDownloadButton > button {
  background: #161b22 !important;
  border: 1px solid #238636 !important;
  color: #3fb950 !important;
  border-radius: 6px !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.75rem !important;
  transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
  background: rgba(35,134,54,0.1) !important;
  box-shadow: 0 0 12px rgba(63,185,80,0.2) !important;
}

/* Divider */
hr { border-color: #21262d !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #21262d; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #30363d; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="stToolbar"] { display: none !important; }
</style>
"""


DEFAULT_VERILOG = """\
module alu_8bit (
    input  wire        clk,
    input  wire        rst,
    input  wire [7:0]  a,
    input  wire [7:0]  b,
    input  wire [2:0]  op,
    output reg  [7:0]  result,
    output reg         carry,
    output reg         zero
);
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            result <= 8'b0;
            carry  <= 1'b0;
            zero   <= 1'b0;
        end else begin
            case (op)
                3'b000: {carry, result} <= a + b;
                3'b001: {carry, result} <= a - b;
                3'b010: result <= a & b;
                3'b011: result <= a | b;
                3'b100: result <= a ^ b;
                3'b101: result <= ~a;
                3'b110: result <= a << 1;
                3'b111: result <= a >> 1;
            endcase
            zero <= (result == 8'b0);
        end
    end
endmodule"""

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="VLSI Synthesis Studio",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CSS, unsafe_allow_html=True)

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### ⚙️ Settings")

        demo_mode = st.checkbox("Demo Mode (no API key)", value=False)

        st.markdown("---")
        llm_backend = st.radio(
            "LLM Backend",
            options=["OpenAI", "Ollama (Local)"],
            index=1,
            disabled=demo_mode,
        )

        if not demo_mode:
            if llm_backend == "OpenAI":
                api_key = _get_api_key()
                if api_key and not api_key.startswith("PASTE"):
                    st.success("✅ OpenAI key configured")
                else:
                    st.warning("⚠️ Add OPENAI_API_KEY to secrets.toml")
                model_choice = st.selectbox("Model", ["gpt-3.5-turbo", "gpt-4"])
            else:
                st.success("✅ Ollama — no key needed")
                model_choice = st.selectbox("Ollama Model",
                                            ["llama3.2", "llama3.2:1b", "qwen2.5-coder:1.5b", "llama3", "mistral", "codellama"])
                ollama_url = st.text_input("Ollama URL", value="http://localhost:11434")
        else:
            model_choice = "llama3.2"
            ollama_url   = "http://localhost:11434"

        st.markdown("---")
        st.selectbox("Target Simulator",
                     ["Icarus Verilog (iverilog)", "ModelSim / EDA Playground"])
        st.selectbox("Test Architecture",
                     ["Directed Exhaustive", "Randomized Constraints"])
        max_retries = st.selectbox("Max Retries", [1, 2, 3], index=1, disabled=demo_mode)

        st.markdown("---")
        with st.expander("ℹ️ About"):
            st.markdown("""
**VLSI Synthesis Studio**
AI-powered Verilog testbench generator.

**Backends:** OpenAI · Ollama · Demo

**Pipeline:**
1. Parse RTL → extract ports
2. Build LLM prompt
3. Generate testbench
4. Syntax check
            """)

    # ── Header ───────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:0.5rem;">
          <span style="font-size:1.4rem;">⚡</span>
          <span style="font-family:'JetBrains Mono',monospace;font-size:1.2rem;font-weight:700;
                       color:#00ffc8;text-shadow:0 0 20px rgba(0,255,200,0.4);letter-spacing:0.05em;">
            Verilog Testbench Generator
          </span>
          <span style="
            font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#3fb950;
            border:1px solid #238636;border-radius:4px;padding:2px 8px;
            display:flex;align-items:center;gap:5px;
          ">
            <span style="display:inline-block;width:6px;height:6px;border-radius:50%;
                         background:#3fb950;box-shadow:0 0 6px #3fb950;
                         animation:ping 2s cubic-bezier(0,0,0.2,1) infinite;"></span>
            ONLINE
          </span>
        </div>
        <p style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;color:#8b949e;
                  margin-bottom:1.5rem;">
          // VLSI Synthesis Studio &nbsp;·&nbsp; v1.2 &nbsp;·&nbsp; AI-Powered RTL Analysis
        </p>
        """,
        unsafe_allow_html=True,
    )

    # ── Input toggle ─────────────────────────────────────────────────────────
    input_method = st.radio(
        "Input method",
        options=["✏️ Paste Code", "📁 Upload File"],
        horizontal=True,
        label_visibility="collapsed",
    )

    verilog_code = ""

    # ── Dual panel ────────────────────────────────────────────────────────────
    col_in, col_out = st.columns(2, gap="large")

    with col_in:
        st.markdown(
            "<p style='font-family:JetBrains Mono,monospace;font-size:0.7rem;"
            "color:#8b949e;letter-spacing:0.1em;text-transform:uppercase;"
            "margin-bottom:4px;'>📄 DUT_Module.v</p>",
            unsafe_allow_html=True,
        )
        if "Upload" in input_method:
            uploaded = st.file_uploader("Upload .v / .sv", type=["v", "sv"],
                                        label_visibility="collapsed")
            if uploaded:
                verilog_code = uploaded.read().decode("utf-8", errors="replace")
                st.code(verilog_code, language="verilog")
        else:
            verilog_code = st.text_area(
                "verilog_input",
                value="",
                height=480,
                label_visibility="collapsed",
            )

    with col_out:
        st.markdown(
            "<p style='font-family:JetBrains Mono,monospace;font-size:0.7rem;"
            "color:#3fb950;letter-spacing:0.1em;text-transform:uppercase;"
            "margin-bottom:4px;'>🧪 DUT_tb.v — Generated</p>",
            unsafe_allow_html=True,
        )
        testbench_code = st.session_state.get("testbench_code", "")
        if testbench_code:
            st.code(testbench_code, language="verilog")
        else:
            st.markdown(
                """
                <div style="height:480px;display:flex;align-items:center;justify-content:center;
                  background:#161b22;border:1px solid #21262d;border-radius:6px;">
                  <span style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;
                               color:#30363d;">// output will appear here</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── Generate button ───────────────────────────────────────────────────────
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    if st.button("⚡ COMPILE AND GENERATE", type="primary"):
        if not verilog_code or not verilog_code.strip():
            st.error("No input — paste Verilog code or upload a .v file.")
        elif "module" not in verilog_code.lower():
            st.error("No `module` declaration found. Ensure your code contains `module <name>(...);`")
        else:
            _run_generation(
                verilog_code=verilog_code,
                demo_mode=demo_mode,
                llm_backend=llm_backend if not demo_mode else "Demo",
                model_choice=model_choice,
                max_retries=max_retries,
                ollama_url=ollama_url if not demo_mode else "http://localhost:11434",
            )

    # ── Post-generation info ──────────────────────────────────────────────────
    if testbench_code:
        module_name  = st.session_state.get("module_name", "module")
        gen_time     = st.session_state.get("gen_total_time", 0.0)
        is_demo      = st.session_state.get("demo_mode", False)
        backend      = st.session_state.get("llm_backend", "")
        syntax_warns = st.session_state.get("syntax_warnings", [])

        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            st.success(f"✅ Generated `tb_{module_name}.v` in {gen_time:.2f}s")
        with c2:
            if is_demo:
                st.info("🎭 Demo mode — predefined example")
            elif backend == "Ollama (Local)":
                st.info("🦙 Generated via Ollama (local)")
        with c3:
            st.download_button(
                label="⬇ Download .v",
                data=testbench_code,
                file_name=f"tb_{module_name}.v",
                mime="text/plain",
            )

        for w in syntax_warns:
            st.warning(f"⚠️ {w}")


# ─────────────────────────────────────────────────────────────────────────────
# Generation pipeline
# ─────────────────────────────────────────────────────────────────────────────

def _run_generation(verilog_code, demo_mode, llm_backend,
                    model_choice, max_retries, ollama_url):
    total_start = time.perf_counter()
    with st.spinner("⚡ Running synthesis model..."):
        try:
            parser      = VerilogParser()
            module_info = parser.parse(verilog_code)

            pb              = PromptBuilder()
            prompt          = pb.build_prompt(module_info)
            fallback_prompt = _build_fallback_prompt(module_info)

            if demo_mode:
                testbench_code = get_demo_response(module_info)
            elif llm_backend == "Ollama (Local)":
                gen = TestbenchGenerator(use_local=True)
                gen.ollama_model = model_choice
                gen.ollama_url   = ollama_url
                testbench_code   = gen.generate_with_retry(
                    prompt=prompt, module_name=module_info.module_name,
                    max_retries=max_retries, fallback_prompt=fallback_prompt)
            else:
                gen = TestbenchGenerator(api_key=_get_api_key())
                gen.model      = model_choice
                testbench_code = gen.generate(
                    prompt=prompt, module_name=module_info.module_name,
                    fallback_prompt=fallback_prompt)

            total_time = time.perf_counter() - total_start

            st.session_state["testbench_code"]  = testbench_code
            st.session_state["module_name"]     = module_info.module_name
            st.session_state["demo_mode"]       = demo_mode
            st.session_state["llm_backend"]     = llm_backend
            st.session_state["gen_total_time"]  = total_time
            st.session_state["syntax_warnings"] = _check_syntax(testbench_code)

            logger.info(f"Done in {total_time:.2f}s — '{module_info.module_name}'")
            st.rerun()

        except ParseError as e:
            st.error(f"Parse Error: {e}")
        except ValidationError as e:
            st.error(f"Validation Error: {e}")
        except GenerationError as e:
            st.error(f"Generation Error: {e}")
        except Exception as e:
            logger.exception(e)
            st.error(f"Unexpected Error: {e}")


if __name__ == "__main__":
    main()
