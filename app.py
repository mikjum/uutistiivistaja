import streamlit as st
import feedparser
import openai
import os

# OpenAI API-avain Streamlitin secrets-muuttujista
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Uutistiivistäjä", page_icon="🗞️")
st.title("🗞️ Uutistiivistäjä")
st.markdown("""
Tämä sovellus lukee RSS-syötteitä, suodattaa uutiset kiinnostuksen mukaan ja tiivistää ne sinulle helposti luettavaan muotoon.
""")

# RSS-syötteen URL
feed_url = st.text_input("Anna RSS-syötteen URL", "https://yle.fi/uutiset/rss")

# Käyttäjän kiinnostuksen kohteet
keywords = st.text_input("Kiinnostavat aiheet (pilkulla eroteltuna)", "tekoäly, ilmastonmuutos")

# Aloita prosessointi napista
if st.button("Hae ja tiivistä uutiset"):
    with st.spinner("Haetaan ja tiivistetään uutisia..."):
        feed = feedparser.parse(feed_url)
        keyword_list = [k.strip().lower() for k in keywords.split(",")]
        articles = []

        for entry in feed.entries:
            summary = getattr(entry, "summary", "")
            combined_text = (entry.title + " " + summary).lower()
            if any(k in combined_text for k in keyword_list):
                prompt = f"""
Tiivistä seuraava uutinen suomeksi yhdellä kappaleella:

Otsikko: {entry.title}

{summary}
"""
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    summary = response.choices[0].message.content.strip()
                except Exception as e:
                    summary = f"(Tiivistys epäonnistui: {e})"

                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "summary": summary
                })

    # Näytetään tulokset
    if articles:
        for article in articles:
            st.subheader(article["title"])
            st.markdown(f"[Lue alkuperäinen uutinen]({article['link']})")
            st.write(article["summary"])
            st.markdown("---")
    else:
        st.info("Ei löytynyt uutisia annetuilla avainsanoilla.")
