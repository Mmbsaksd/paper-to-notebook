# Paper to Notebook (Modularized)

Convert research paper PDFs into functional Jupyter Notebooks using Gemini 2.0. This tool analyzes papers, designs a toy implementation, generates PyTorch code, and validates the output.

## Features

- **Clean Modular Code**: Core logic resides in `src/paper_to_notebook`.
- **Unified Pipeline**: Supports both CLI and Web interfaces.
- **Local Credentials**: Managed via `.env` file.
- **Improved Entry Points**: Dedicated `main.py` (CLI) and `app.py` (FastAPI).

## Local Setup

1. **Clone the repository**: (You've already done this)
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
### LLM Providers
This tool supports both **Google Gemini** and **Azure OpenAI**. You can configure your preferred provider in the `.env` file.

3. **Configure API Key**:
   - Copy `.env.example` to `.env`.
   - Add your credentials.
   ```bash
   cp .env.example .env
   ```

#### Gemini Setup
```text
GOOGLE_API_KEY=your_key
LLM_PROVIDER=gemini
```

#### Azure OpenAI Setup
```text
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview
LLM_PROVIDER=azure
```

## Usage

### CLI Usage
Run the conversion directly from your terminal:
```bash
python main.py path/to/paper.pdf -o output_notebook.ipynb
```

### Web Usage (FastAPI)
Start the FastAPI server (Modern HTML UI):
```bash
uvicorn app:app --reload
```
Then open `http://localhost:8000` in your browser.

### Streamlit Usage (Alternative UI)
For a more interactive local interface:
```bash
streamlit run streamlit_app.py
```

## Project Structure

```text
paper-to-notebook/
├── src/
│   └── paper_to_notebook/
│       ├── core/
│       │   ├── llm_client.py       # Gemini API interaction
│       │   ├── notebook_builder.py # NB creation logic
│       │   ├── pdf_handler.py      # PDF processing
│       │   └── pipeline.py         # Unified conversion flow
│       ├── config.py               # Constants & Env loading
│       └── prompts.py              # LLM prompt templates
├── static/                         # Web UI assets
├── app.py                          # Web application entry point
├── main.py                         # CLI entry point
├── requirements.txt                # Consolidated dependencies
└── .env.example                    # Template for credentials
```

## License

MIT
