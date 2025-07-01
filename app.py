import feedparser
from openai import OpenAI
import streamlit as st

# 🔐 Hae API-avain Streamlitin "Secrets" -asetuksista
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Uutistiivistäjä", layout="wide")
st.title("🗞️ Uutistiivistäjä – RSS-uutisten AI-kooste")

# Syöte: RSS-URL ja kiinnostavat avainsanat
rss_url = st.text_input("Anna RSS-syötteen URL", "https://yle.fi/uutiset/rss/uutiset.rss")
keywords = st.text_input("Kiinnostavat avainsanat (pilkulla eroteltuna)", "tekoäly, talous, ilmasto")
keywords = [kw.strip().lower() for kw in keywords.split(",") if kw.strip()]

if st.button("Hae ja tiivistä uutiset"):
    feed = feedparser.parse(rss_url)

    for entry in feed.entries:
        # 📄 Jos summary puuttuu, käytä tyhjää
        summary = getattr(entry, "summary", "")
        combined_text = (entry.title + " " + summary).lower()

        if any(kw in combined_text for kw in keywords):
            prompt = f"Tiivistä seuraava uutinen suomeksi yhdellä kappaleella:\n\n" \
                     f"Otsikko: {entry.title}\n\n{summary}"

            try:
                # 💬 Kutsu OpenAI APIa uudella tavalla
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
