import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Terminal Crypto", page_icon="📈", layout="wide")

st.title("📈 Terminal de Análisis Financiero")
st.markdown("---")

# --- MOTOR DE DATOS (API) ---
@st.cache_data(ttl=300) # Guarda datos 5 minutos
def get_detailed_data():
    # Pedimos datos extendidos de las 4 monedas
    ids = "bitcoin,ethereum,solana,chainlink"
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=eur&ids={ids}&order=market_cap_desc&sparkline=false"
    try:
        return requests.get(url).json()
    except:
        return []

data = get_detailed_data()

if not data:
    st.error("⚠️ Error de conexión con la API. Espera unos segundos y recarga.")
    st.stop()

# --- INTERFAZ POR PESTAÑAS ---
# Creamos una pestaña para cada moneda disponible
tabs = st.tabs(["🟠 Bitcoin (BTC)", "🔵 Ethereum (ETH)", "🟣 Solana (SOL)", "Ez Chainlink (LINK)"])

# Iteramos para rellenar cada pestaña con sus datos únicos
for i, tab in enumerate(tabs):
    coin = data[i] # Datos de la moneda actual
    
    with tab:
        # CABECERA: Precio y Cambio
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Precio Actual", f"{coin['current_price']:,.2f} €", f"{coin['price_change_percentage_24h']:.2f}%")
        c2.metric("Rango 24h (Min)", f"{coin['low_24h']:,.2f} €")
        c3.metric("Rango 24h (Max)", f"{coin['high_24h']:,.2f} €")
        c4.metric("Ranking Mercado", f"#{coin['market_cap_rank']}")
        
        st.markdown("---")
        
        # CUERPO: Datos Financieros Profundos
        st.subheader("📊 Fundamental & Tokenomics")
        
        fc1, fc2, fc3 = st.columns(3)
        
        with fc1:
            st.markdown("**Capitalización de Mercado (Size)**")
            st.info(f"{coin['market_cap']:,.0f} €")
            st.caption("Tamaño total de la empresa/red. Más grande = Menos volátil.")
            
        with fc2:
            st.markdown("**Volumen 24h (Liquidez)**")
            st.warning(f"{coin['total_volume']:,.0f} €")
            st.caption("Dinero que se ha movido hoy. Alto volumen = Saludable.")
            
        with fc3:
            st.markdown("**Suministro (Escasez)**")
            circulante = coin['circulating_supply']
            total = coin['total_supply'] if coin['total_supply'] else circulante
            porcentaje = (circulante / total) * 100 if total else 100
            
            st.progress(porcentaje / 100)
            st.write(f"Emitido: {porcentaje:.1f}%")
            st.caption(f"{circulante:,.0f} monedas en circulación.")

        st.markdown("---")

        # PIE: Análisis de Riesgo / Oportunidad (ATH)
        st.subheader("📉 Análisis de Ciclo (All Time High)")
        
        ath_price = coin['ath']
        ath_drop = coin['ath_change_percentage']
        ath_date = datetime.strptime(coin['ath_date'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%m/%Y")
        
        ac1, ac2 = st.columns([1, 2])
        
        with ac1:
            st.metric("Caída desde Máximos", f"{ath_drop:.2f}%", delta_color="inverse")
        
        with ac2:
            st.write(f"El precio máximo histórico fue de **{ath_price:,.2f} €** el día **{ath_date}**.")
            
            if ath_drop < -70:
                st.success("✅ **Oportunidad Histórica:** El activo está a precio de saldo (Descuento > 70%). Riesgo alto, potencial alto.")
            elif ath_drop < -40:
                st.success("⚖️ **Zona de Acumulación:** Buen punto de entrada para largo plazo.")
            elif ath_drop > -20:
                st.warning("⛔ **Cerca de Máximos:** Esperar corrección o entrar con precaución (DCA).")

# Botón de recarga manual abajo del todo
st.markdown("---")
if st.button('🔄 Actualizar todos los datos'):
    st.rerun()
    
