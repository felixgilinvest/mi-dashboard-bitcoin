import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Terminal Crypto Pro", page_icon="🦅", layout="wide")
st.title("🦅 Terminal de Inversión Integral")
st.markdown("---")

@st.cache_data(ttl=300)
def get_detailed_data():
    ids = "bitcoin,ethereum,solana,chainlink"
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=eur&ids={ids}&order=market_cap_desc&sparkline=false"
    try:
        return requests.get(url).json()
    except:
        return []

def get_fear_greed():
    try:
        url = "https://api.alternative.me/fng/"
        data = requests.get(url).json()['data'][0]
        return int(data['value']), data['value_classification']
    except:
        return 0, "Error"

coins = get_detailed_data()
fg_value, fg_label = get_fear_greed()

if not coins:
    st.error("⚠️ Error de conexión. Recarga la página.")
    st.stop()

# Cálculos auxiliares
btc_price = coins[0]['current_price']
eth_price = coins[1]['current_price']
eth_btc_ratio = eth_price / btc_price

# SECCIÓN 1: SENTIMIENTO
st.subheader("🌡️ Contexto de Mercado")
c_fg1, c_fg2 = st.columns([1, 4])
with c_fg1:
    color_fg = "red" if fg_value < 25 else "green" if fg_value > 75 else "orange"
    st.markdown(f"<h2 style='text-align: center; color: {color_fg};'>{fg_value} ({fg_label})</h2>", unsafe_allow_html=True)
with c_fg2:
    st.info("El sentimiento dicta la tendencia general. Miedo = Oportunidad DCA.")

st.markdown("---")

# SECCIÓN 2: PESTAÑAS
tabs = st.tabs(["🟠 Bitcoin (BTC)", "🔵 Ethereum (ETH)", "🟣 Solana (SOL)", "Ez Chainlink (LINK)"])

for i, tab in enumerate(tabs):
    coin = coins[i]
    with tab:
        # CABECERA
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Precio", f"{coin['current_price']:,.2f} €", f"{coin['price_change_percentage_24h']:.2f}%")
        c2.metric("Min 24h", f"{coin['low_24h']:,.2f} €")
        c3.metric("Max 24h", f"{coin['high_24h']:,.2f} €")
        c4.metric("Rank", f"#{coin['market_cap_rank']}")
        
        st.markdown("---")

        # --- ANÁLISIS PREDICTIVO ESPECÍFICO (INTELIGENCIA) ---
        
        # 1. BITCOIN: MVRV & RESERVAS
        if coin['id'] == 'bitcoin':
            st.subheader("🔮 Inteligencia Predictiva: MVRV Z-Score")
            st.write("El indicador más preciso para detectar Techos y Suelos de mercado.")
            
            p1, p2 = st.columns([3, 1])
            with p1:
                st.info("""
                **¿Cómo leerlo?** (Tienes que consultarlo en el enlace de la derecha)
                * **Zona Roja (> 3.5):** Mercado sobrecalentado. Probabilidad de caída alta. -> **VENDER/ESPERAR**.
                * **Zona Verde (< 1.0):** Mercado infravalorado. Probabilidad de subida alta. -> **COMPRA FUERTE**.
                * **Zona actual:** Si está entre 1 y 2, es zona de acumulación sostenible.
                """)
            with p2:
                st.link_button("👉 Ver Gráfico MVRV", "https://www.lookintobitcoin.com/charts/mvrv-zscore/")
                st.caption("Fuente: LookIntoBitcoin")

        # 2. ETHEREUM: RATIO ETH/BTC
        elif coin['id'] == 'ethereum':
            st.subheader("⚖️ Inteligencia Predictiva: Ratio ETH/BTC")
            r1, r2 = st.columns([1, 3])
            with r1:
                st.metric("Ratio ETH/BTC", f"{eth_btc_ratio:.5f}")
            with r2:
                if eth_btc_ratio < 0.035:
                    st.success("✅ **ZONA DE OPORTUNIDAD:** ETH está históricamente barato vs BTC.")
                elif eth_btc_ratio > 0.055:
                    st.error("🛑 **ETH CARO:** Bitcoin domina. Riesgo alto.")
                else:
                    st.warning("⚖️ **ZONA NEUTRA:** Ethereum se mueve con el mercado.")

        # 3. SOLANA & LINK: Volatilidad
        else:
            st.subheader("⚡ Inteligencia de Riesgo")
            st.write(f"Al ser una Altcoin, su movimiento depende de Bitcoin x2.")
            if fg_value < 30:
                st.success(f"Con el 'Miedo' actual, {coin['name']} tiene un potencial de rebote agresivo.")
            else:
                st.warning(f"Vigila la dominancia de Bitcoin. Si BTC cae, {coin['name']} caerá más fuerte.")

        st.markdown("---")
        
        # ANÁLISIS CICLO (ATH)
        ath_drop = coin['ath_change_percentage']
        try: ath_date = datetime.strptime(coin['ath_date'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%m/%Y")
        except: ath_date = "N/A"
        
        st.subheader("📉 Descuento vs Máximos (ATH)")
        ac1, ac2 = st.columns([1, 2])
        ac1.metric("Caída desde ATH", f"{ath_drop:.2f}%", delta_color="inverse")
        with ac2:
            st.write(f"Máximo: **{coin['ath']:,.2f} €** ({ath_date})")

st.markdown("---")
if st.button('🔄 Actualizar'): st.rerun()
