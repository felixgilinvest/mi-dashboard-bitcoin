import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Dashboard Pro", page_icon="📊", layout="centered")

st.title("📊 Centro de Mando: Inversión Bitcoin")
st.caption(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")
st.markdown("---")

# --- FUNCIONES DE DATOS ---
@st.cache_data(ttl=60) # Guarda datos 60 seg para no bloquear la API
def get_market_data():
    """Obtiene datos enriquecidos de CoinGecko"""
    try:
        # Pedimos más datos: ATH (Máximo histórico) y Precios
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=eur&ids=bitcoin,ethereum&order=market_cap_desc&per_page=2&page=1&sparkline=false"
        data = requests.get(url).json()
        return data
    except:
        return []

def get_fear_greed():
    try:
        url = "https://api.alternative.me/fng/"
        data = requests.get(url).json()['data'][0]
        return int(data['value']), data['value_classification']
    except:
        return 0, "Error"

# --- CARGA DE DATOS ---
coins = get_market_data()
fg_value, fg_label = get_fear_greed()

if not coins:
    st.error("⚠️ No se pudieron cargar los datos. Espera 1 minuto y recarga.")
    st.stop()

btc = coins[0] # Datos de Bitcoin
eth = coins[1] # Datos de Ethereum

# --- CÁLCULO DE DESCUENTO ATH ---
btc_ath_drop = btc['ath_change_percentage'] # Cuánto ha caído desde el máximo

# --- INTERFAZ VISUAL ---

# 1. KPI PRINCIPALES
st.subheader("1. Precios y Descuentos")
c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Precio Bitcoin", f"{btc['current_price']:,.2f} €", f"{btc['price_change_percentage_24h']:.2f}%")

with c2:
    # Muestra qué tan lejos estamos del precio máximo histórico
    st.metric("Caída desde Máx (ATH)", f"{btc_ath_drop:.2f}%", delta_color="inverse")

with c3:
    st.metric("Miedo y Codicia", f"{fg_value}/100", fg_label)

# 2. ANÁLISIS AUTOMÁTICO (Lógica de Inversión)
st.subheader("2. Análisis del Asistente IA")

analisis = ""
tipo_aviso = "info" # info, success, warning, error

# Lógica del análisis
if fg_value < 25:
    analisis = "✅ **MOMENTO DE OPORTUNIDAD:** El mercado tiene 'Miedo Extremo'. Históricamente, comprar Bitcoin cuando este indicador está bajo 25 ha sido la estrategia más rentable a largo plazo. Mantén la disciplina del DCA."
    tipo_aviso = "success"
elif fg_value > 75:
    analisis = "🛑 **PRECAUCIÓN:** El mercado está en 'Codicia Extrema'. Hay euforia. No es recomendable hacer compras grandes de golpe (Lump Sum), ya que el riesgo de corrección es alto. Limítate a tu compra pequeña recurrente."
    tipo_aviso = "error"
else:
    analisis = "⚖️ **ZONA NEUTRA:** El mercado está indeciso. Es el terreno ideal para el DCA (compras automáticas) sin estrés. No intentes adivinar la dirección del precio."

# Añadir comentario sobre el ATH
if btc_ath_drop < -50:
    analisis += "\n\n💎 **Nota:** Bitcoin está con un descuento superior al 50% de su máximo. Es zona de acumulación."

# Mostrar el cuadro de análisis
if tipo_aviso == "success":
    st.success(analisis)
elif tipo_aviso == "error":
    st.error(analisis)
else:
    st.info(analisis)


st.markdown("---")

# 3. SECCIÓN EDUCATIVA (Desplegable)
with st.expander("📚 Glosario: ¿Qué estoy mirando? (Clic para abrir)"):
    st.markdown("""
    * **ATH (All Time High):** Es el precio más alto que ha tocado Bitcoin en su historia. Si la "Caída desde Máx" es -20%, significa que está un 20% más barato que en su mejor momento.
    * **Fear & Greed Index:** Mide el sentimiento.
        * 0-25: Miedo extremo (Suelen ser suelos de mercado).
        * 75-100: Euforia (Suelen ser techos de mercado).
    * **DCA (Dollar Cost Averaging):** Estrategia de comprar siempre la misma cantidad (ej. 50€) sin importar el precio.
    """)

# Botón para refrescar manual
if st.button('🔄 Actualizar Datos Ahora'):
    st.rerun()