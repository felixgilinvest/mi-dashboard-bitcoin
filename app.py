import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Terminal Crypto Pro", page_icon="🦅", layout="wide")

st.title("🦅 Terminal de Inversión Integral")
st.markdown("---")

# --- MOTOR DE DATOS (API) ---
@st.cache_data(ttl=300) # 5 min cache
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

# Cargar datos
coins = get_detailed_data()
fg_value, fg_label = get_fear_greed()

if not coins:
    st.error("⚠️ Error de conexión. Espera unos segundos y recarga.")
    st.stop()

# --- SECCIÓN 1: SENTIMIENTO DEL MERCADO (GLOBAL) ---
st.subheader("🌡️ Contexto de Mercado (Global)")

c_fg1, c_fg2 = st.columns([1, 4])

with c_fg1:
    if fg_value < 25:
        color_fg = "red"
        emoji_fg = "🟢 Oportunidad"
    elif fg_value > 75:
        color_fg = "green"
        emoji_fg = "🔴 Precaución"
    else:
        color_fg = "orange"
        emoji_fg = "🟡 Neutral"
        
    st.markdown(f"<h1 style='text-align: center; color: {color_fg};'>{fg_value}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'><b>{fg_label}</b><br>{emoji_fg}</p>", unsafe_allow_html=True)

with c_fg2:
    st.info(f"""
    **¿Cómo afecta esto a mis monedas?**
    * El índice actual es **{fg_value}/100 ({fg_label})**.
    * Cuando Bitcoin tiene 'Miedo' (Bajo 25), **Solana y Chainlink** suelen ofrecer descuentos aún mayores.
    * Cuando hay 'Euforia' (Sobre 75), vigila posibles correcciones.
    """)

st.markdown("---")

# --- SECCIÓN 2: ANÁLISIS POR ACTIVO (PESTAÑAS) ---
tabs = st.tabs(["🟠 Bitcoin (BTC)", "🔵 Ethereum (ETH)", "🟣 Solana (SOL)", "Ez Chainlink (LINK)"])

# AQUÍ ESTABA EL ERROR: Ahora usamos 'coins' correctamente
for i, tab in enumerate(tabs):
    coin = coins[i]  # <--- CORREGIDO
    with tab:
        # CABECERA
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Precio Actual", f"{coin['current_price']:,.2f} €", f"{coin['price_change_percentage_24h']:.2f}%")
        c2.metric("Rango 24h (Min)", f"{coin['low_24h']:,.2f} €")
        c3.metric("Rango 24h (Max)", f"{coin['high_24h']:,.2f} €")
        c4.metric("Ranking", f"#{coin['market_cap_rank']}")
        
        st.markdown("---")
        
        # FUNDAMENTALES
        st.subheader("📊 Fundamental & Tokenomics")
        fc1, fc2, fc3 = st.columns(3)
        
        with fc1:
            st.markdown("**Capitalización (Size)**")
            st.info(f"{coin['market_cap']:,.0f} €")
        with fc2:
            st.markdown("**Volumen 24h**")
            st.warning(f"{coin['total_volume']:,.0f} €")
        with fc3:
            st.markdown("**Suministro Emitido**")
            circ = coin['circulating_supply']
            total = coin['total_supply'] if coin['total_supply'] else circ
            pct = (circ / total) * 100 if total else 100
            st.progress(pct / 100)
            st.caption(f"{pct:.1f}% en circulación")

        st.markdown("---")

        # CICLO Y ATH
        st.subheader("📉 Análisis de Ciclo (ATH)")
        ath_drop = coin['ath_change_percentage']
        try:
            ath_date = datetime.strptime(coin['ath_date'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%m/%Y")
        except:
            ath_date = "N/A"
        
        ac1, ac2 = st.columns([1, 2])
        ac1.metric("Caída desde Máximos", f"{ath_drop:.2f}%", delta_color="inverse")
        
        with ac2:
            st.write(f"Máximo histórico: **{coin['ath']:,.2f} €** ({ath_date})")
            
            if ath_drop < -70: 
                st.success(f"✅ **Oportunidad Agresiva:** Descuento masivo (>70%).")
            elif ath_drop < -40: 
                st.success("⚖️ **Zona de Acumulación:** Buen punto de entrada DCA.")
            elif ath_drop > -20: 
                st.warning("⛔ **Cerca de Máximos:** Precaución.")

st.markdown("---")
if st.button('🔄 Actualizar Datos'):
    st.rerun()
    


