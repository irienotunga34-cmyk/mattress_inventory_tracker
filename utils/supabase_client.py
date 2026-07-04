
import streamlit as st
from supabase import create_client

SUPABASE_URL = "https://sngspougndedjrvvjrjb.supabase.co"

SUPABASE_KEY = "sb_publishable_GTtgR0gAKEa0W82RMzufIA_DT2mpPhq"

client = create_client(SUPABASE_URL, SUPABASE_KEY)