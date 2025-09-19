import streamlit as st
from streamlit_split_button import split_button

# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run split_button/example.py`

import streamlit as st
from streamlit_split_button import split_button

# Create a split button with primary action and alternatives
result = split_button(
    label="Save",
    options=["Save As Copy", "Save As Template", "Export PDF"],
    icon=":material/save:"
)

st.write("")

if result == "Save":
    st.write("Document saved!")
elif result == "Save As Copy":
    st.write("Document saved as copy")
elif result == "Save As Template":
    st.write("Document saved as template")
elif result == "Export PDF":
    st.write("Document exported as PDF")
