import pandas as pd
import re
import streamlit as st
from io import BytesIO
from spellchecker import SpellChecker

st.set_page_config(page_title="Spelling Checker", layout="wide")
st.title("🔍 Spelling Error Checker in XML")

file = st.file_uploader("📂 Upload an XML file", type=["xml"])

def is_ignorable(word):
    return (
        word.isupper() or
        any(char.isdigit() for char in word) or
        re.match(r'^[a-zA-Z]:\\|^https?://|^\.\.?\b', word)
    )

if file:
    try:
        file_content = file.read()

        # Parse XML
        data_objects_df = pd.read_xml(BytesIO(file_content), xpath=".//DataObjects", parser="etree")[["Name", "Description"]]
        exception_metadata_df = pd.read_xml(BytesIO(file_content), xpath=".//ExceptionMetadata", parser="etree")[["CorrectiveAction"]]
        merged_df = pd.concat([data_objects_df, exception_metadata_df], axis=1)

        columns_to_check = ["Name", "Description", "CorrectiveAction"]
        all_words = set()

        for _, row in merged_df.iterrows():
            for col in columns_to_check:
                text = row.get(col)
                if pd.notna(text):
                    words = re.findall(r'\b\w+\b', text)
                    for word in words:
                        if not is_ignorable(word):
                            all_words.add(word)

        # Check for spelling mistakes using pyspellchecker
        spell = SpellChecker()
        misspelled = spell.unknown(all_words)

        if misspelled:
            st.success(f"✅ Found {len(misspelled)} unique spelling issues.")
            st.dataframe(pd.DataFrame(sorted(misspelled), columns=["Misspelled Word"]), use_container_width=True)
        else:
            st.info("🎉 No spelling issues found!")

    except Exception as e:
        st.error(f"❌ Error parsing file: {e}")
else:
    st.warning("📄 Please upload an XML file to begin.")
