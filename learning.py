import streamlit as st
import requests
import pandas as pd

# ———— Page config ————
st.set_page_config(page_title="Country Info Finder", page_icon="🌍", layout="centered")

# ———— Custom CSS ————
st.markdown("""
<style>
.stApp {
    background-image: url("https://i.imgur.com/BpJLWrg.jpeg");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
    color: white;
}

.custom-box {
    background-color: rgba(0, 0, 0, 0.6);
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
}

.custom-title {
    font-size: 2rem;
    font-weight: bold;
    text-align: center;
    text-shadow: 2px 2px 4px #000000;
    color: white;
}

.stTextInput label, .stSelectbox label {
    font-weight: bold;
    font-size: 1rem;
    background-color: rgba(0, 0, 0, 0.6);
    padding: 5px 10px;
    border-radius: 5px;
    color: white !important;
    text-shadow: 1px 1px 2px black;
}

.stTextInput > div > div > input,
.stSelectbox > div > div > div {
    background-color: rgba(255, 255, 255, 0.8) !important;
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

# ———— Title & Description ————
st.markdown("""
<div class="custom-box">
    <h1 class="custom-title">🌍 Country Info Finder</h1>
    <div style="
        background-color: rgba(0, 0, 0, 0.6);
        color: white;
        padding: 10px 15px;
        border-radius: 10px;
        font-size: 1rem;
        text-shadow: 1px 1px 2px black;
        margin-top: 10px;
    ">
        Enter a country name to get details, or explore by continent.
    </div>
</div>
""", unsafe_allow_html=True)

# ———— Country Info Search ————
country_name = st.text_input("Enter a country name", "")

if country_name:
    r = requests.get(f"https://restcountries.com/v3.1/name/{country_name}?fullText=true")
    if r.status_code == 200:
        data = r.json()[0]
        name = data['name']['common']
        st.subheader(f"Information about {name}")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Capital:** {', '.join(data.get('capital', ['N/A']))}")
            st.markdown(f"**Region:** {data.get('region','N/A')}")
            st.markdown(f"**Subregion:** {data.get('subregion','N/A')}")
            st.markdown(f"**Area:** {data.get('area',0):,} km²")
        with col2:
            langs = data.get('languages', {})
            st.markdown(f"**Languages:** {', '.join(langs.values())}")
            if len(langs) == 1:
                st.markdown("_Note: Only official languages are shown. Some speak many more._")
            currencies = ", ".join(v['name'] for v in data.get('currencies', {}).values())
            st.markdown(f"**Currency:** {currencies}")
            maplink = data.get('maps', {}).get('googleMaps', "")
            if maplink:
                st.markdown(f"[📍 View on Google Maps]({maplink})")

        flag = data['flags']['png']
        st.markdown(
            f"""
            <div style="background-color: rgba(255,255,255,0.8); padding:10px; display:inline-block; border-radius:8px;">
                <img src="{flag}" width="200"><br><strong>{name}</strong>
            </div>
            """, unsafe_allow_html=True
        )

        pop = data.get('population', 0)
        st.markdown(f"📊 Based on last census, **{name}**'s population is **{pop:,}**.")
    else:
        st.error("Country not found. Please check spelling.")

# ———— Continent Explorer ————
st.markdown("---")
st.header("🌐 Continent Explorer")

resp = requests.get("https://restcountries.com/v3.1/all?fields=name,region,area,population,latlng")
if resp.status_code == 200:
    countries = resp.json()
    continents = sorted({c.get('region') for c in countries if c.get('region')})
    selected = st.selectbox("Choose a continent", [""] + continents)
    if selected:
        subset = [c for c in countries if c.get('region') == selected]
        total = sum(c.get('population', 0) for c in subset)
        largest = max(subset, key=lambda c: c.get('area', 0), default={})
        largest_name = largest.get('name', {}).get('common', 'Unknown')
        st.markdown(f"👥 Total population in **{selected}**: **{total:,}**")
        st.markdown(f"📏 Largest country by area: **{largest_name}**")

        coords = [c.get('latlng') for c in subset if c.get('latlng')]
        if coords:
            df = pd.DataFrame(coords, columns=["lat", "lon"])
            st.map(df)
else:
    st.error("Failed to fetch continent data.")
