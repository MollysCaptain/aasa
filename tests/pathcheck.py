import sys, os
import streamlit as st
st.write("cwd: " + os.getcwd())
st.write("sys.path[0]: " + sys.path[0])
st.write(sys.path[:5])
