"""Configuration constants optimized for Azure OpenAI."""
import os
from dotenv import load_dotenv

load_dotenv()

# Azure OpenAI Deployment
DEFAULT_MODEL = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")

# Token limits per pipeline step (Azure GPT-4o typically supports up to 16k completion tokens)
MAX_TOKENS_ANALYSIS = 4096
MAX_TOKENS_DESIGN = 4096
MAX_TOKENS_GENERATE = 16000
MAX_TOKENS_VALIDATE = 16000
MAX_TOKENS_FIX = 16000

# Notebook execution
EXECUTE_TIMEOUT = 300  # seconds per cell
MAX_FIX_ATTEMPTS = 2   # max times to retry fixing errors

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAYS = [5, 15, 30]  # seconds

# PDF constraints (Local processing)
MAX_PDF_SIZE_MB = 30
MAX_PDF_PAGES = 100

# Required notebook sections (in order)
REQUIRED_SECTIONS = [
    "Title & Paper Overview",
    "Problem Intuition",
    "Imports & Setup",
    "Dataset & Tokenization",
    "Model Architecture",
    "Loss Function & Training Utilities",
    "Baseline Implementation",
    "Paper's Main Algorithm — Training",
    "Inference / Generation",
    "Full Experiment & Evaluation",
    "Visualizations",
    "Summary & Next Steps",
]
