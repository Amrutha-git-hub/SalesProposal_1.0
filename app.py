# streamlit_app.py
import streamlit as st
from proposal_service import generate_section_content, slide_section_mapping
from proposal_generator import generate_proposal_ppt_data
from docx_generator import generate_proposal_docx_data

st.title("Proposal Generator")

st.write("Enter the following details to generate your proposal:")

with st.form("proposal_form"):
    firm = st.text_input("Consultancy Firm")
    client = st.text_input("Client")
    product = st.text_input("Product")
    proposal_date = st.text_input("Proposal Date (DD-MM-YYYY)", value="TBD")
    output_format = st.selectbox("Select output format", options=["PPTX", "DOCX", "Both"])
    submit_button = st.form_submit_button("Generate Proposal")

if submit_button:
    if not (firm and client and product):
        st.error("Please fill in all required fields!")
    else:
        st.info("Generating proposal. This may take a few moments...")
        # Generate and preview PPTX file if applicable
        if output_format in ["PPTX", "Both"]:
            ppt_bytes = generate_proposal_ppt_data(
                generate_section_content,
                slide_section_mapping,
                firm,
                client,
                product,
                proposal_date
            )
            st.download_button(
                label="Download PPT Proposal",
                data=ppt_bytes,
                file_name=f"{product.replace(' ', '_')}_Proposal.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
            st.success("PPT proposal generated successfully!")
        
        # Generate and preview DOCX file if applicable
        if output_format in ["DOCX", "Both"]:
            docx_bytes = generate_proposal_docx_data(
                generate_section_content,
                {},  # SECTION_GUIDELINES dictionary; empty dict uses default values in the generator.
                firm,
                client,
                product,
                proposal_date
            )
            st.download_button(
                label="Download DOCX Proposal",
                data=docx_bytes,
                file_name=f"{product.replace(' ', '_')}_Proposal.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            st.success("DOCX proposal generated successfully!")
