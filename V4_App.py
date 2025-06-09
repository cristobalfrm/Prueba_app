import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd
import os
from pathlib import Path
import base64

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Sedes - Admisión 2025",
    page_icon=":university:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONFIGURACIÓN DE RUTAS ---
BASE_PATH = Path(__file__).parent
COOR_FILE = BASE_PATH / "Coordenadas_Sedes.xlsx"
GRAFICOS_DIR = BASE_PATH / "graficos_sedes"
LOGO_PATH = BASE_PATH / "logo.png"

# --- FUNCIONES AUXILIARES ---
@st.cache_data
def cargar_coordenadas():
    """Carga el archivo de coordenadas y maneja errores."""
    try:
        if not COOR_FILE.exists():
            st.error(f"Archivo no encontrado: {COOR_FILE}")
            return pd.DataFrame()
        df = pd.read_excel(COOR_FILE)
        # Aseguramos tipos correctos
        df['Latitud_sede'] = pd.to_numeric(df['Latitud_sede'], errors='coerce')
        df['Longitud_sede'] = pd.to_numeric(df['Longitud_sede'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error al cargar coordenadas: {e}")
        return pd.DataFrame()

@st.cache_data
def obtener_imagen_base64(ruta_imagen):
    """Convierte una imagen a base64 para usarla en HTML."""
    if ruta_imagen.exists():
        return base64.b64encode(ruta_imagen.read_bytes()).decode()
    return ""

def crear_mapa_interactivo(df):
    """Crea un mapa de Folium con marcadores para cada sede."""
    centro = [-33.45, -70.67]
    if not df.empty:
        centro = [df['Latitud_sede'].mean(), df['Longitud_sede'].mean()]

    mapa = folium.Map(
        location=centro,
        zoom_start=5,
        tiles='CartoDB Positron',
        control_scale=True
    )

    logo_b64 = obtener_imagen_base64(LOGO_PATH) if LOGO_PATH.exists() else ""

    for _, row in df.iterrows():
        # Simple popup con el nombre
        popup_html = (
            f"<b>{row['NombreSede']}</b>"
        )
        folium.Marker(
            location=[row['Latitud_sede'], row['Longitud_sede']],
            popup=popup_html,
            tooltip=row['NombreSede'],
            icon=folium.Icon(color="blue", icon="university", prefix="fa")
        ).add_to(mapa)

    return mapa

# --- INTERFAZ DE LA APLICACIÓN ---
st.title("📊 Análisis de Sedes - Admisión 2025")

# Cargamos coordenadas
df_sedes = cargar_coordenadas()
if df_sedes.empty:
    st.error("No se pudieron cargar las coordenadas de sedes.")
    st.stop()

# Layout
col1, col2 = st.columns([1, 3])
with col1:
    st.header("⚙️ Configuración")
    st.markdown("1. Explora el mapa\n2. Haz clic en un marcador\n3. Verás el gráfico al pie")
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=150)

with col2:
    st.header("📍 Mapa de Sedes")
    mapa = crear_mapa_interactivo(df_sedes)
    evento = st_folium(
        mapa,
        width=900,
        height=600,
        returned_objects=["last_clicked"]
    )
    # Capturamos coordenadas de clic
    latlon = evento.get("last_clicked")
    sede_seleccionada = None
    if latlon:
        # Buscamos la sede cuyo par (lat, lon) coincide
        lat, lon = latlon
        match = df_sedes[
            (df_sedes['Latitud_sede'] == lat) &
            (df_sedes['Longitud_sede'] == lon)
        ]
        if not match.empty:
            sede_seleccionada = match.iloc[0]['NombreSede']

# --- MOSTRAR IMAGEN FINAL ---
st.divider()
if sede_seleccionada:
    st.header(f"📈 Gráfico para: {sede_seleccionada}")
    ruta = GRAFICOS_DIR / f"{sede_seleccionada}_graficos.png"
    if ruta.exists():
        st.image(str(ruta), use_column_width=True)
        with open(ruta, "rb") as f:
            st.download_button(
                label="⬇️ Descargar gráfico",
                data=f,
                file_name=f"{sede_seleccionada}_graficos.png",
                mime="image/png"
            )
    else:
        st.error(f"No se encontró el gráfico para {sede_seleccionada}.")
        st.info("Verifica que en 'graficos_sedes' exista el archivo.")

else:
    st.info("Haz clic en un marcador del mapa para ver su gráfico.")

st.divider()
st.caption("Dashboard desarrollado por Cris | Junio 2025")
