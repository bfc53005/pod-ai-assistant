import streamlit as st
import openai
import os
import csv
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials
import pyperclip
import json

st.set_page_config(page_title="POD AI Assistant", layout="wide")
st.title("👕 Print-on-Demand AI Assistant")

openai.api_key = st.secrets.get("OPENAI_API_KEY", "")
SAVE_FILE = "saved_designs.csv"

# Google Sheets Setup
gsheet_enabled = "GOOGLE_SHEET_ID" in st.secrets
if gsheet_enabled:
    gs_credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    gc = gspread.authorize(gs_credentials)
    sheet = gc.open_by_key(st.secrets["GOOGLE_SHEET_ID"]).sheet1

# Helper: GPT prompt call
def generate_text(prompt, temperature=0.7):
    if not openai.api_key:
        return "Missing OpenAI API key."
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Helper: Save to CSV
def save_to_csv(data_dict):
    file_exists = os.path.isfile(SAVE_FILE)
    with open(SAVE_FILE, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=data_dict.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data_dict)

# Helper: Save to Google Sheets
def save_to_gsheet(data_dict):
    if gsheet_enabled:
        row = [data_dict.get(k, "") for k in data_dict.keys()]
        sheet.append_row(row)

# Load Saved Designs
def load_saved_designs():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, newline="") as file:
            return list(csv.DictReader(file))
    return []

# Tabs for each major function
tabs = st.tabs(["🎨 Design Prompt Generator", "📝 Slogan/Text Generator", "🛒 Listing Generator", "🗂️ Saved Designs"])

# --- Design Prompt Generator ---
with tabs[0]:
    st.header("🎨 AI Design Prompt Generator")
    st.markdown("Generate image prompts for Ideogram, Midjourney, or DALL·E")

    col1, col2 = st.columns(2)
    with col1:
        subject = st.text_input("Subject (e.g., Process Operator)")
        tool = st.text_input("Tool or Item (e.g., Pipe Wrench)")
        mood = st.selectbox("Mood", ["Funny", "Sarcastic", "Serious", "Heroic"])
    with col2:
        style = st.selectbox("Art Style", ["Sketch", "Cartoon", "Flat 2D", "Vintage", "Stencil"])
        phrase = st.text_input("Text to Include on Design")
        platform = st.selectbox("Target Platform", ["Ideogram", "Midjourney", "DALL·E"])

    if st.button("⚡ Generate Prompt"):
        user_prompt = (
            f"Create a visual prompt for a T-shirt design featuring a {subject} holding a {tool}. "
            f"The mood should be {mood.lower()} and the style should be {style}. "
            f"Include the text: '{phrase}'. Format it for {platform}."
        )
        ai_result = generate_text(user_prompt)
        st.text_area("Generated Prompt:", ai_result, height=100)

        if st.button("📋 Copy Prompt"):
            pyperclip.copy(ai_result)
            st.success("Prompt copied to clipboard!")

        if st.button("💾 Save Design Prompt"):
            record = {
                "type": "design",
                "subject": subject,
                "tool": tool,
                "mood": mood,
                "style": style,
                "phrase": phrase,
                "platform": platform,
                "output": ai_result,
                "timestamp": datetime.now().isoformat()
            }
            save_to_csv(record)
            if gsheet_enabled:
                save_to_gsheet(record)
            st.success("Saved successfully!")

        if platform.lower() == "ideogram":
            st.markdown(f"[Open Ideogram](https://ideogram.ai/?prompt={ai_result.replace(' ', '%20')})")

# --- Slogan/Text Generator ---
with tabs[1]:
    st.header("📝 Slogan & Text Generator")
    st.markdown("Create shirt slogans based on role, tone, and context.")

    role = st.text_input("Job Role or Industry (e.g., Chemical Operator)")
    tone = st.selectbox("Tone", ["Funny", "Sarcastic", "Inspirational", "Tough"], key="tone")
    theme = st.text_input("Optional Theme (e.g., Night Shift, Maintenance)")

    if st.button("🧠 Generate Slogan"):
        user_prompt = f"Create a {tone.lower()} slogan for a shirt for a {role}. Theme: {theme}"
        slogan = generate_text(user_prompt)
        st.text_area("Generated Slogan:", slogan, height=80)

        if st.button("💾 Save Slogan"):
            record = {
                "type": "slogan",
                "role": role,
                "tone": tone,
                "theme": theme,
                "output": slogan,
                "timestamp": datetime.now().isoformat()
            }
            save_to_csv(record)
            if gsheet_enabled:
                save_to_gsheet(record)
            st.success("Saved successfully!")

# --- Listing Generator ---
with tabs[2]:
    st.header("🛒 Listing Generator")
    st.markdown("Generate Etsy/Redbubble listings: titles, descriptions, and tags.")

    product_type = st.text_input("Product Type (e.g., T-shirt, Hoodie)")
    design_summary = st.text_area("Design Summary (describe the shirt/image)")
    niche_keywords = st.text_input("Keywords (comma-separated)")

    if st.button("🛍️ Generate Listing"):
        user_prompt = (
            f"Write an Etsy listing for a {product_type} with this description: {design_summary}. "
            f"Include a catchy title, SEO-optimized tags using these keywords: {niche_keywords}."
        )
        response = generate_text(user_prompt)
        st.text_area("AI-Generated Listing:", response, height=200)

        if st.button("💾 Save Listing"):
            record = {
                "type": "listing",
                "product": product_type,
                "summary": design_summary,
                "keywords": niche_keywords,
                "output": response,
                "timestamp": datetime.now().isoformat()
            }
            save_to_csv(record)
            if gsheet_enabled:
                save_to_gsheet(record)
            st.success("Saved successfully!")

# --- Saved Designs Tab ---
with tabs[3]:
    st.header("🗂️ Saved Designs")
    saved = load_saved_designs()
    if saved:
        search_type = st.selectbox("Filter by type", ["All", "design", "slogan", "listing"])
        for row in reversed(saved):
            if search_type != "All" and row["type"] != search_type:
                continue
            with st.expander(f"{row['type'].capitalize()} @ {row['timestamp']}"):
                for k, v in row.items():
                    if k not in ["timestamp", "type"]:
                        st.markdown(f"**{k}**: {v}")
    else:
        st.info("No saved prompts yet. Generate something and save it!")
