import streamlit as st
import feedparser
import openai
import os
from datetime import datetime

st.set_page_config(page_title="Uutistiivistäjä", layout="wide")

# OpenAI API-avain (haetaan Streamlitin secrettien kautta)
openai.api_key = os.getenv("OPENAI_API_KEY")

st.title("📰 Älykäs Uutistiivistäjä")

rss_urls_input = st.text_area(
    "Anna RSS-syötteiden URL-osoitteet (yksi per rivi)",
    """https://sea-technology.com/feed
https://www.marinetechnologynews.com/rss
https://www.ship-technology.com/feed
https://feeds.feedburner.com/gcaptain
https://www.marineinsight.com/category/tech/feed
https://www.marinelog.com/news/rss"""
)

aihessanat_input = st.text_input("Aihesanat (AI arvioi osuvuuden)", "Artificial intelligence, Remote operations, autonomy, unmanned vessels, situational awareness")
pakolliset_input = st.text_input("Pakolliset avainsanat (jos mainitaan, näytetään)", "Wärtsilä, ABB, Kongsberg, Nacos, Orca, Avikus, Mitsubishi, Groke, Mahi, Marubeni")

aihessanat = [a.strip().lower() for a in aihessanat_input.split(",") if a.strip()]
pakolliset_avainsanat = [p.strip().lower() for p in pakolliset_input.split(",") if p.strip()]

rss_urls = [url.strip() for url in rss_urls_input.split("\n") if url.strip()]

st.write("\n")
st.markdown("### 🔍 Tiivistykset")

@st.cache_data(ttl=3600)
def tarkista_aiheen_osuvuus(otsikko, teksti, aihesanat):
    prompt = f"Tässä on uutinen. Vastaako se johonkin seuraavista aiheista:\n" \
             f"{', '.join(aihesanat)}?\n\n" \
             f"Otsikko: {otsikko}\n\nSisältö: {teksti}\n\n" \
             f"Vastaa muodossa: KYLLÄ tai EI. Jos KYLLÄ, kerro lyhyesti miksi."

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Olet avustaja, joka arvioi uutisten aiheiden osuvuutta käyttäjän kiinnostuksen kohteisiin."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"VIRHE: {e}"

def muodosta_tiivistelma(otsikko, teksti):
    prompt = f"Tiivistä seuraava uutinen 2-3 lauseeseen ytimekkäästi ja informatiivisesti.\n\nOtsikko: {otsikko}\n\nSisältö: {teksti}"

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Olet tiivistämiseen erikoistunut avustaja."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"(Tiivistys epäonnistui: {e})"

for url in rss_urls:
    feed = feedparser.parse(url)
    st.subheader(f"🔗 {feed.feed.get('title', 'Tuntematon syöte')}")

    for entry in feed.entries[:10]:
        otsikko = entry.title
        yhteenveto = getattr(entry, 'summary', '')
        linkki = entry.link

        combined_text = (otsikko + " " + yhteenveto).lower()

        if any(av in combined_text for av in pakolliset_avainsanat):
            tiivis = muodosta_tiivistelma(otsikko, yhteenveto)
            with st.expander(otsikko):
                st.markdown(tiivis)
                st.markdown(f"[Lue koko uutinen]({linkki})")
        else:
            arvio = tarkista_aiheen_osuvuus(otsikko, yhteenveto, aihessanat)
            if arvio.startswith("KYLLÄ"):
                tiivis = muodosta_tiivistelma(otsikko, yhteenveto)
                with st.expander(otsikko):
                    st.markdown(tiivis)
                    st.markdown(f"**GPT perustelu:** {arvio}")
                    st.markdown(f"[Lue koko uutinen]({linkki})")
