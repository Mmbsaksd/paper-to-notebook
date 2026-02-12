import streamlit as st
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add src to path for package imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from paper_to_notebook.core.pipeline import run_pipeline
from paper_to_notebook.config import DEFAULT_MODEL

load_dotenv()

st.set_page_config(
    page_title="Paper to Notebook (Azure)",
    page_icon="📓",
    layout="wide"
)

st.title("📓 Paper to Notebook")
st.markdown("Convert research papers (PDF) into functional Jupyter Notebooks using **Azure OpenAI**.")

# Sidebar for configuration
with st.sidebar:
    st.header("Azure Settings")
    st.success("✅ Azure OpenAI Connected")
    st.info(f"Deployment: {os.environ.get('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4o')}")
    
    st.divider()
    model_override = st.text_input("Override Deployment Name", value=DEFAULT_MODEL)

uploaded_file = st.file_uploader("Upload a Research Paper (PDF)", type="pdf")

if uploaded_file is not None:
    if st.button("Generate Notebook"):
        status_placeholder = st.empty()
        progress_bar = st.progress(0)
        
        try:
            with st.spinner("Generating notebook... This may take a few minutes."):
                pdf_bytes = uploaded_file.read()
                
                def on_progress(step, name, detail, extra=None):
                    progress_bar.progress(step * 25 if step <= 4 else 100)
                    status_placeholder.write(f"**Step {step}: {name}** - {detail}")

                nb_bytes = run_pipeline(
                    pdf_source=pdf_bytes,
                    model=model_override,
                    on_progress=on_progress
                )
            
            st.success("Notebook generated successfully!")
            
            # Download button
            st.download_button(
                label="Download Notebook (.ipynb)",
                data=nb_bytes,
                file_name="generated_notebook.ipynb",
                mime="application/x-ipynb+json"
            )
            
        except Exception as e:
            st.error(f"An error occurred: {e}")

st.divider()
st.markdown("### How it works")
st.markdown("""
1. **Analysis**: Azure OpenAI reads the paper context and extracts key algorithms.
2. **Design**: A toy implementation plan is created (synthetic data, mock models).
3. **Generation**: PyTorch code and markdown cells are written.
4. **Validation**: The LLM reviews the code for consistency and errors.
""")
