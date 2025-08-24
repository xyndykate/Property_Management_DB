import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path
from document_processor import PropertyDocumentProcessor, create_sample_documents
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Property Document Processor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'processor' not in st.session_state:
    st.session_state.processor = PropertyDocumentProcessor()
if 'results' not in st.session_state:
    st.session_state.results = []
if 'processing' not in st.session_state:
    st.session_state.processing = False

# Create necessary directories
Path("uploads").mkdir(exist_ok=True)
Path("processed_results").mkdir(exist_ok=True)
Path("documents").mkdir(exist_ok=True)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        background-color: #f8f9fa;
        margin-bottom: 1rem;
    }
    .entity-badge {
        background-color: #e3f2fd;
        padding: 0.3rem 0.6rem;
        border-radius: 0.25rem;
        margin: 0.2rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("📄 Document Processor")
    st.markdown("---")
    
    # File upload
    uploaded_files = st.file_uploader(
        "Upload documents",
        type=['pdf', 'txt', 'jpg', 'jpeg', 'png'],
        accept_multiple_files=True
    )
    
    # Process button
    if st.button("🚀 Process Documents", type="primary", use_container_width=True):
        if uploaded_files:
            st.session_state.processing = True
            st.session_state.results = []
            
            # Save uploaded files
            for uploaded_file in uploaded_files:
                file_path = os.path.join("uploads", uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            # Process files
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, uploaded_file in enumerate(uploaded_files):
                file_path = os.path.join("uploads", uploaded_file.name)
                status_text.text(f"Processing {uploaded_file.name}...")
                
                try:
                    result = st.session_state.processor.process_document(file_path)
                    st.session_state.results.append(result)
                except Exception as e:
                    st.session_state.results.append({
                        "error": str(e),
                        "file_name": uploaded_file.name
                    })
                
                progress_bar.progress((i + 1) / len(uploaded_files))
                time.sleep(0.1)  # Simulate processing time
            
            progress_bar.empty()
            status_text.empty()
            st.session_state.processing = False
            st.rerun()
        else:
            st.warning("Please upload at least one document")
    
    # Create sample documents
    if st.button("📋 Create Sample Documents", use_container_width=True):
        create_sample_documents()
        st.success("Sample documents created in 'documents' folder!")
    
    st.markdown("---")
    st.info("""
    **Supported formats:**
    - PDF documents
    - Images (JPG, PNG)
    - Text files
    """)

# Main content
st.markdown('<h1 class="main-header">🏠 Property Document Processor</h1>', unsafe_allow_html=True)

# Display results
if st.session_state.results:
    st.header("📊 Processing Results")
    
    for result in st.session_state.results:
        with st.expander(f"📄 {result.get('file_name', 'Unknown')}", expanded=True):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("Document Info")
                st.write(f"**Type:** {result.get('document_type', 'Unknown')}")
                st.write(f"**Processed:** {result.get('processing_date', 'N/A')}")
                st.write(f"**Text Length:** {result.get('text_length', 0)} characters")
                
                if 'error' in result:
                    st.error(f"Error: {result['error']}")
            
            with col2:
                if 'entities' in result and result['entities']:
                    st.subheader("📋 Extracted Entities")
                    entities_df = pd.DataFrame(
                        [(k.replace('_', ' ').title(), v) for k, v in result['entities'].items()],
                        columns=['Field', 'Value']
                    )
                    st.dataframe(entities_df, use_container_width=True, hide_index=True)
                else:
                    st.warning("No entities extracted")
            
            # Show extracted text preview
            if 'extracted_text' in result:
                st.subheader("📝 Extracted Text Preview")
                st.text_area(
                    "Full Text",
                    result['extracted_text'],
                    height=200,
                    disabled=True,
                    label_visibility="collapsed"
                )
            
            # Download results
            json_str = json.dumps(result, indent=2)
            st.download_button(
                label="📥 Download JSON Results",
                data=json_str,
                file_name=f"results_{result.get('file_name', 'document')}.json",
                mime="application/json",
                key=f"download_{result.get('file_name', 'unknown')}"
            )
    
    # Summary statistics
    st.header("📈 Summary")
    col1, col2, col3 = st.columns(3)
    
    successful = len([r for r in st.session_state.results if 'error' not in r])
    errors = len([r for r in st.session_state.results if 'error' in r])
    total_entities = sum(len(r.get('entities', {})) for r in st.session_state.results if 'error' not in r)
    
    col1.metric("Documents Processed", len(st.session_state.results))
    col2.metric("Successful", successful)
    col3.metric("Total Entities", total_entities)
    
    # Export all results
    if st.button("💾 Export All Results"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"all_results_{timestamp}.json"
        
        with open(os.path.join("processed_results", filename), "w") as f:
            json.dump(st.session_state.results, f, indent=2)
        
        st.success(f"All results exported to processed_results/{filename}")

elif st.session_state.processing:
    st.info("🔄 Processing documents... Please wait.")
    
else:
    # Welcome screen
    st.info("""
    👋 Welcome to the Property Document Processor!
    
    **How to use:**
    1. Upload documents using the sidebar
    2. Click 'Process Documents'
    3. View extracted information and download results
    
    **Supported document types:**
    - Leases and rental agreements
    - Invoices and bills
    - ID documents
    - Any text-based property documents
    """)
    
    # Quick start section
    st.header("🚀 Quick Start")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Upload Your Documents")
        st.write("Use the sidebar to upload PDFs, images, or text files containing property documents.")
    
    with col2:
        st.subheader("Try Sample Documents")
        st.write("Click 'Create Sample Documents' in the sidebar to generate test files and see how the system works.")

# Footer
st.markdown("---")
st.caption("Built with Streamlit, TensorFlow, and Transformers | Property Management Document Processing System")