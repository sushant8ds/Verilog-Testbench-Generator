# Verilog Testbench Generator

A GenAI-powered web application that automatically generates simulation-ready testbenches for Verilog RTL modules.

## Features

- 🌐 **Web-based Interface**: Simple Streamlit UI for easy interaction
- 🤖 **AI-Powered Generation**: Uses OpenAI GPT models for intelligent testbench creation
- 📝 **Smart Parsing**: Automatically analyzes Verilog modules and extracts structure
- ✅ **Comprehensive Testing**: Generates exhaustive or representative test cases
- 🔄 **Retry Logic**: Automatic retry with fallback strategies for reliability
- 📊 **Performance Monitoring**: Track generation times and performance metrics
- 🎯 **Demo Mode**: Test without API costs using predefined examples
- 📋 **Validation**: Ensures generated testbenches are syntactically correct

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (for AI-powered generation) or use Demo Mode

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd verilog-testbench-generator
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure API key (skip if using Demo Mode):
```bash
mkdir -p .streamlit
```

Create `.streamlit/secrets.toml` with your OpenAI API key:
```toml
OPENAI_API_KEY = "your-api-key-here"
```

To obtain an OpenAI API key:
- Visit https://platform.openai.com/api-keys
- Sign up or log in
- Create a new API key
- Copy and paste it into the secrets.toml file

## Usage

### Running the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### Using the Generator

1. **Input Method**: Choose between uploading a Verilog file or pasting code directly
2. **Upload/Paste**: Provide your Verilog RTL module
3. **Generate**: Click "Generate Testbench" button
4. **Review**: View the generated testbench side-by-side with your input
5. **Download**: Save the testbench as a `.v` file

### Demo Mode

To use the application without an API key:
1. Enable "Demo Mode" in the sidebar
2. Upload or paste a Verilog module
3. The system will use predefined examples instead of calling the API

Demo mode supports:
- Simple combinational logic (AND gates, adders)
- Sequential logic (flip-flops, counters)

## Project Structure

```
verilog-testbench-generator/
├── app.py                  # Streamlit web application
├── parser.py              # Verilog parsing logic
├── prompt_builder.py      # LLM prompt construction
├── generator.py           # LLM integration and generation
├── demo_responses.py      # Mock responses for demo mode
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .streamlit/
│   └── secrets.toml      # API key configuration (not in git)
└── tests/
    ├── test_parser_properties.py
    ├── test_prompt_builder_properties.py
    ├── test_generator_integration.py
    └── test_e2e.py
```

## Testing

Run all tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=. --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html
```

## Architecture

The system follows a modular architecture:

1. **Parser**: Extracts module structure, ports, and signals from Verilog code
2. **Prompt Builder**: Constructs structured prompts with test strategies
3. **Generator**: Interfaces with OpenAI API and validates responses
4. **Web App**: Streamlit UI for user interaction

## Requirements

See `requirements.txt` for full dependency list.

Key dependencies:
- `streamlit`: Web framework
- `openai`: LLM API integration
- `pytest`: Testing framework
- `hypothesis`: Property-based testing

## Configuration

### API Configuration

Configure in `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "your-api-key-here"
```

### Performance Settings

- Expected generation time: 2-10 seconds
- Automatic retry: Up to 2 attempts
- Timeout: 30 seconds per API call

## Troubleshooting

### "No API key found"
- Ensure `.streamlit/secrets.toml` exists with valid API key
- Or enable Demo Mode to test without API

### "Generation failed"
- Check your internet connection
- Verify API key is valid and has credits
- Try Demo Mode to verify the system works

### "Parsing error"
- Ensure your Verilog code is syntactically correct
- Check that module declaration is present
- Verify ports are properly declared

## Future Enhancements

- SystemVerilog assertions (SVA) support
- Multi-module testbench generation
- Coverage-driven verification
- Direct simulator integration (ModelSim)
- Waveform visualization

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Support

For issues and questions, please [open an issue](link-to-issues).
