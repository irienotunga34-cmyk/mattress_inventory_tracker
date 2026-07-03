import streamlit as st
from supabase import create_client

st.write("URL exists:", "SUPABASE_URL" in st.secrets)
st.write("KEY exists:", "SUPABASE_KEY" in st.secrets)

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

st.write("URL:", SUPABASE_URL)
st.write("Key length:", len(SUPABASE_KEY))

client = create_client(SUPABASE_URL, SUPABASE_KEY)
