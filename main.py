import streamlit as st
import requests
import pandas as pd

# Load secrets with error handling and fallback to environment variables
import os

try:
    token = st.secrets['fb_access_token']
    ad_account_id = st.secrets['ad_account_id']
except KeyError as e:
    # Fallback to environment variables
    token = os.getenv('fb_access_token')
    ad_account_id = os.getenv('ad_account_id')
    
    if not token or not ad_account_id:
        st.error(f"❌ Missing secret: {e}")
        st.info("Please add the missing secrets to your Streamlit Cloud app settings or environment variables")
        st.stop()

def fetchData(url: str, params):
    try:
        response = requests.get(url, params=params)
        # Remove sensitive data logging - don't print full response
        response.raise_for_status()  # Raise error for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Request error: {e}")
        return None
    except ValueError:
        st.error("⚠️ Response was not valid JSON.")
        return None

def safe_dataframe_display(data, label="Data", hide_sensitive=True):
    """Safely display data as DataFrame with type conversion and sensitive data masking"""
    try:
        if isinstance(data, dict):
            # Convert dict to DataFrame
            df = pd.DataFrame([data])
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame(data)
        
        # Hide sensitive fields
        if hide_sensitive:
            sensitive_fields = [
                'access_token', 'token', 'secret', 'key', 'password', 'auth',
                'id', 'account_id', 'user_id', 'email', 'phone', 'credit_card',
                'payment', 'billing', 'personal', 'private'
            ]
            
            for col in df.columns:
                if any(field in col.lower() for field in sensitive_fields):
                    if col in df.columns:
                        df[col] = '***HIDDEN***'
        
        # Convert mixed-type columns to strings to avoid Arrow serialization issues
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str)
        
        st.dataframe(df)
        
    except Exception as e:
        st.warning(f"⚠️ Could not display {label} as DataFrame: {e}")
        # Don't show raw JSON for sensitive data - just show structure
        if hide_sensitive:
            if isinstance(data, dict):
                safe_keys = {k: "***HIDDEN***" if any(field in k.lower() for field in ['token', 'secret', 'key', 'id', 'auth']) else str(type(v).__name__) for k, v in data.items()}
                st.json(safe_keys)
            else:
                st.info(f"Data type: {type(data).__name__}, Length: {len(data) if hasattr(data, '__len__') else 'N/A'}")
        else:
            st.json(data)

def main():
    st.title("📊 Market Management Dashboard")
    
    # Add security notice
    st.sidebar.info("🔒 Sensitive data is automatically hidden for security")
    
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
                safe_dataframe_display(data['paging'], "Paging", hide_sensitive=False)
        else:
            st.error("❌ No campaign data found or an error occurred.")
            if data:
                # Only show error structure, not full data
                error_info = {
                    "error_type": data.get("error", {}).get("type", "Unknown"),
                    "error_code": data.get("error", {}).get("code", "Unknown"),
                    "error_message": data.get("error", {}).get("message", "Unknown error"),
                    "response_keys": list(data.keys()) if isinstance(data, dict) else "Not a dict"
                }
                st.json(error_info)
    
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
                # Only show error structure, not full data
                error_info = {
                    "error_type": data.get("error", {}).get("type", "Unknown"),
                    "error_code": data.get("error", {}).get("code", "Unknown"),
                    "error_message": data.get("error", {}).get("message", "Unknown error"),
                    "response_keys": list(data.keys()) if isinstance(data, dict) else "Not a dict"
                }
                st.json(error_info)

if __name__ == "__main__":
    main()