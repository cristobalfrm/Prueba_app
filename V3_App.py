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
        return pd.read_excel(COOR_FILE)
    except Exception as e:
        st.error(f"Error al cargar coordenadas: {e}")
        return pd.DataFrame()

@st.cache_data
def obtener_imagen_base64(ruta_imagen):
    """Convierte una imagen a base64 para usarla en HTML."""
    if ruta_imagen.exists():
        with open(ruta_imagen, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# Cargar datos de coordenadas
df_sedes = cargar_coordenadas()

# --- FUNCIÓN PARA CREAR MAPA INTERACTIVO ---
def crear_mapa_interactivo(df):
    """Crea un mapa de Folium con marcadores para cada sede."""
    if df.empty:
        return folium.Map(location=[-33.45, -70.67], zoom_start=5)
    centro = [df['Latitud_sede'].mean(), df['Longitud_sede'].mean()]
    mapa = folium.Map(location=centro, zoom_start=5, tiles='CartoDB Positron', control_scale=True)
    logo_base64 = obtener_imagen_base64(LOGO_PATH) if LOGO_PATH.exists() else ""
    for _, row in df.iterrows():
        logo_html = (
            f'<div style="text-align:center;"><img src="data:image/png;base64,{logo_base64}" width="80" '
            'style="margin-bottom:10px;"></div>'
        ) if logo_base64 else ""
        popup_html = (
            f'<div style="font-family: Arial; text-align:center; width:200px;">'
            f'{logo_html}<h4 style="color:#2c3e50;">{row["NombreSede"]}</h4>'
            '<button style="background:#3498db;border:none;color:white;padding:8px 16px;'
            'font-size:14px;border-radius:4px;cursor:pointer;" '
            f'onclick="window.parent.postMessage(\'{row["NombreSede"]}\', \'*\')">'
            'Ver Gráficos</button></div>'
        )
        folium.Marker(
            location=[row['Latitud_sede'], row['Longitud_sede']],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=row['NombreSede'],
            icon=folium.Icon(color="blue", icon="university", prefix="fa")
        ).add_to(mapa)
    return mapa

# --- INTERFAZ DE LA APLICACIÓN ---
st.title("📊 Análisis de Sedes - Admisión 2025")

if df_sedes.empty:
    st.error("No se pudieron cargar las coordenadas de sedes.")
    st.stop()

col1, col2 = st.columns([1, 3])

with col1:
    st.header("⚙️ Configuración")
    st.markdown("1. Explora el mapa\n2. Haz clic en un marcador\n3. Presiona **Ver Gráficos**")
    sedes = sorted(df_sedes['NombreSede'].unique())
    sede_seleccionada = st.selectbox("Selecciona sede", sedes)
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=150)

with col2:
    st.header("📍 Mapa de Sedes")
    mapa = crear_mapa_interactivo(df_sedes)
    evento = st_folium(mapa, width=900, height=600, returned_objects=["last_object_clicked_popup"])
    if evento and evento.get("last_object_clicked_popup"):
        sede_seleccionada = evento["last_object_clicked_popup"]
        st.experimental_rerun()

# --- MOSTRAR IMAGEN ÚNICA ---
st.divider()
st.header(f"📈 Gráfico para: {sede_seleccionada}")
ruta_grafico = GRAFICOS_DIR / f"{sede_seleccionada}_graficos.png"

if ruta_grafico.exists():
    st.image(str(ruta_grafico), use_column_width=True)
    with open(ruta_grafico, "rb") as f:
        st.download_button(
            label="⬇️ Descargar gráfico",
            data=f,
            file_name=f"{sede_seleccionada}_graficos.png",
            mime="image/png"
        )
else:
    st.error(f"No se encontró el gráfico para {sede_seleccionada}.")
    st.info("Asegúrate de que 'graficos_sedes' contenga el archivo correspondiente.")

st.divider()
st.caption("Dashboard desarrollado por Cris | Junio 2025")
