import feedparser
from openai import OpenAI
import streamlit as st

# 🔐 Hae OpenAI API Key Streamlitin "Secrets" -järjestelmästä
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Uutistiivistäjä", layout="wide")
st.title("🗞️ Uutistiivistäjä – RSS-uutisten AI-kooste")

# ➕ Käyttäjä voi antaa monta RSS-syötettä (yksi per rivi)
rss_urls_input = st.text_area(
    "Anna RSS-syötteiden URL-osoitteet (yksi per rivi)",
    "https://www.marinetechnologynews.com/rss/\nhttps://www.marinelog.com/feed/\nhttps://www.ship-technology.com/feed/\nhttps://sea-technology.com/feed"
)
rss_urls = [url.strip() for url in rss_urls_input.splitlines() if url.strip()]

# Avainsanat kiinnostuksen kohteita varten
keywords = st.text_input("Kiinnostavat avainsanat (pilkulla eroteltuna)", "autonomy, remote, unmanned, nacos, wärtsilä, kongsberg, orca, avikus, mahi, massterly")
keywords = [kw.strip().lower() for kw in keywords.split(",") if kw.strip()]

if st.button("Hae ja tiivistä uutiset"):
    for rss_url in rss_urls:
        st.markdown(f"## 📡 {rss_url}")
        feed = feedparser.parse(rss_url)

        if not feed.entries:
            st.warning("Ei uutisia tai syötettä ei voitu lukea.")
            continue

        for entry in feed.entries:
            summary = getattr(entry, "summary", "")
            combined_text = (entry.title + " " + summary).lower()

            if any(kw in combined_text for kw in keywords):
                prompt = f"Tiivistä seuraava uutinen suomeksi yhdellä kappaleella:\n\n" \
                         f"Otsikko: {entry.title}\n\n{summary}"

                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Olet suomenkielinen uutistiivistäjä."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                    )

                    tiivistelma = response.choices[0].message.content.strip()

                    st.subheader(entry.title)
                    st.write(tiivistelma)
                    st.markdown(f"[Lue alkuperäinen uutinen]({entry.link})")

                except Exception as e:
                    st.error(f"Tiivistys epäonnistui:\n\n{e}")

          
