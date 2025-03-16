"""### gif from local file"""
import streamlit as st
import base64

file_ = open("kindly-bounce.gif", "rb")
contents = file_.read()
data_url = base64.b64encode(contents).decode("utf-8")
file_.close()
st.markdown(
    f'<img style="height: 260px; width: 250px;" src="data:image/gif;base64,{data_url}" alt="cat gif">',
unsafe_allow_html = True,)

