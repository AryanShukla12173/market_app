import streamlit as st
import requests

# Load secrets
token = st.secrets['fb_access_token']
ad_account_id = st.secrets['ad_account_id']
def fetchData(url : str ,params):
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

def main():
    st.title("📊 Market Management Dashboard")

    if st.button("Fetch Campaigns"):
        data = fetchData("https://graph.facebook.com/v19.0/me/adaccounts",{
        "access_token": token
        })

        if data and "data" in data:
            st.success(f"✅ Loaded {len(data['data'])} campaigns")
            st.dataframe(data["data"])
            st.dataframe(data['paging'])
        else:
            st.error("❌ No campaign data found or an error occurred.")
            if data:
                st.json(data)  # Show raw API error/response
    if st.button("Fetch Account Metadata"):
        data = fetchData(f"https://graph.facebook.com/v19.0/{ad_account_id}/",{
        "fields": "name,account_status,currency,timezone_name",
        "access_token": token
    })
        if data:
            st.success(f"✅ Loaded Account Metadata")
            st.dataframe(data)
        else:
            st.error("❌ No campaign data found or an error occurred.")
            if data:
                st.json(data)  # Show raw API error/response

if __name__ == "__main__":
    main()
    