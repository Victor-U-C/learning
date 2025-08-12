import streamlit as st
import requests
import pandas as pd
import openai
import re

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

# ———— Function to get 2025 population ————
def get_2025_population(country_name):
    try:
        openai.api_key = st.secrets["OPENAI_API_KEY"]

        prompt = f"What is the current 2025 population of {country_name}? Please provide only the numerical value without any additional text or formatting."

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0
        )

        population_text = response.choices[0].message.content.strip()
        numbers = re.findall(r'[\d,]+', population_text)
        if numbers:
            return int(numbers[0].replace(',', ''))
    except Exception as e:
        print(f"Error fetching 2025 population data: {e}")
    return None

# ———— Country Info Search ————
country_name = st.text_input("Enter a country name", "")

if country_name:
    try:
        r = requests.get(f"https://restcountries.com/v3.1/name/{country_name}?fullText=true")
        if r.status_code == 200:
            data = r.json()[0]
            name = data['name']['common']

            st.subheader(f"Information about {name}")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"Capital: {', '.join(data.get('capital', ['N/A']))}")
                st.markdown(f"Region: {data.get('region','N/A')}")
                st.markdown(f"Subregion: {data.get('subregion','N/A')}")
                st.markdown(f"Area: {data.get('area',0):,} km²")
            with col2:
                langs = data.get('languages', {})
                st.markdown(f"Languages: {', '.join(langs.values())}")
                if len(langs) == 1:
                    st.markdown("Note: Only official languages are shown.")
                currencies = ", ".join(v['name'] for v in data.get('currencies', {}).values())
                st.markdown(f"Currency: {currencies}")
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

            population_2025 = get_2025_population(name)
            if population_2025:
                st.markdown(f"📊 2025 Population: **{population_2025:,}**")
            else:
                fallback_pop = data.get('population')
                if fallback_pop:
                    st.markdown(f"📊 Population: **{fallback_pop:,}** (estimate)")
                else:
                    st.markdown(f"📊 Population data not available.")

        else:
            st.error("Country not found. Please check spelling.")
    except requests.RequestException:
        st.error("Error connecting to country data service. Please try again.")

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

        total = 0
        for c in subset:
            country_name = c.get('name', {}).get('common', '')
            pop_2025 = get_2025_population(country_name)
            if pop_2025:
                total += pop_2025
            else:
                total += c.get('population', 0)

        largest = max(subset, key=lambda c: c.get('area', 0), default={})
        largest_name = largest.get('name', {}).get('common', 'Unknown')
        st.markdown(f"👥 Total population in {selected}: **{total:,}**")
        st.markdown(f"📏 Largest country by area: {largest_name}")

        coords = [c.get('latlng') for c in subset if c.get('latlng')]
        if coords:
            df = pd.DataFrame(coords, columns=["lat", "lon"])
            st.map(df)
else:
    st.error("Failed to fetch continent data.")
