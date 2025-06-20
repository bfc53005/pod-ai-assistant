# POD AI Assistant

An AI-powered tool to generate print-on-demand T-shirt prompts, slogans, and Etsy listings. Built with Streamlit, OpenAI GPT-4, and Google Sheets integration.

## Features

- 🎨 Design prompt generator (Ideogram, Midjourney, DALL·E)
- 📝 AI-generated slogans (funny, sarcastic, tough, etc.)
- 🛒 Full Etsy-style listing generator
- 💾 Save to CSV and Google Sheets
- 📋 Copy prompt to clipboard + one-click link to Ideogram

## Deployment (Streamlit Cloud)

1. Push to GitHub.
2. Add a `secrets.toml` under **Settings > Secrets** on Streamlit Cloud:

```toml
OPENAI_API_KEY = "sk-..."

GOOGLE_SHEET_ID = "your-google-sheet-id"

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

3. Deploy your app from the main file: `pod_ai_assistant.py`.
