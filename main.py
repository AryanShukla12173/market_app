import streamlit as st
import requests
import pandas as pd

# Load secrets with error handling
try:
    token = st.secrets['fb_access_token']
    ad_account_id = st.secrets['ad_account_id']
except KeyError as e:
    st.error(f"❌ Missing secret: {e}")
    st.info("Please add the missing secrets to your Streamlit app settings or secrets.toml file")
    st.stop()

def fetchData(url: str, params):
    try:
        response = requests.get(url, params=params)
        print(response.json())
        response.raise_for_status()  # Raise error for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Request error: {e}")
        return None
    except ValueError:
        st.error("⚠️ Response was not valid JSON.")
        return None

def safe_dataframe_display(data, label="Data"):
    """Safely display data as DataFrame with type conversion"""
    try:
        if isinstance(data, dict):
            # Convert dict to DataFrame
            df = pd.DataFrame([data])
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame(data)
        
        # Convert mixed-type columns to strings to avoid Arrow serialization issues
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str)
        
        st.dataframe(df)
        
    except Exception as e:
        st.warning(f"⚠️ Could not display {label} as DataFrame: {e}")
        st.json(data)  # Fallback to JSON display

def main():
    st.title("📊 Market Management Dashboard")
    
    if st.button("Fetch Campaigns"):
        data = fetchData("https://graph.facebook.com/v19.0/me/adaccounts", {
            "access_token": token
        })
        
        if data and "data" in data:
            st.success(f"✅ Loaded {len(data['data'])} campaigns")
            safe_dataframe_display(data["data"], "Campaigns")
            
            # Handle paging data separately
            if "paging" in data:
                st.subheader("Paging Information")
                safe_dataframe_display(data['paging'], "Paging")
        else:
            st.error("❌ No campaign data found or an error occurred.")
            if data:
                st.json(data)  # Show raw API error/response
    
    if st.button("Fetch Account Metadata"):
        data = fetchData(f"https://graph.facebook.com/v19.0/{ad_account_id}/", {
            "fields": "name,account_status,currency,timezone_name",
            "access_token": token
        })
        
        if data:
            st.success(f"✅ Loaded Account Metadata")
            safe_dataframe_display(data, "Account Metadata")
        else:
            st.error("❌ No account metadata found or an error occurred.")
            if data:
                st.json(data)  # Show raw API error/response

if __name__ == "__main__":
    main()