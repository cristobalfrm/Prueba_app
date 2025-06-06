import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd
import os
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Sedes",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar rutas
BASE_PATH = r"C:\Users\Cristobal Reyes\Documents\Admisión 2025\Análisis_Venta_Abril_2025\Por_Sede"
COOR_FILE = Path(BASE_PATH) / "Coordenadas_Sedes.xlsx"
GRAFICOS_DIR = Path(BASE_PATH) / "graficos_sedes"

# Cargar coordenadas de sedes
@st.cache_data
def cargar_coordenadas():
    return pd.read_excel(COOR_FILE)

df_sedes = cargar_coordenadas()

# Función para crear mapa interactivo
def crear_mapa_interactivo(df):
    # Centro del mapa (promedio de coordenadas)
    centro = [df['Latitud_sede'].mean(), df['Longitud_sede'].mean()]
    
    # Crear mapa base
    mapa = folium.Map(
        location=centro, 
        zoom_start=5,
        tiles='CartoDB Positron',
        control_scale=True
    )
    
    # Agregar marcadores para cada sede
    for _, row in df.iterrows():
        # HTML personalizado para el popup
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; text-align: center; width: 200px;">
            <h4 style="margin-bottom: 10px; color: #2c3e50;">{row['NombreSede']}</h4>
            <button style="
                background-color: #3498db;
                border: none;
                color: white;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 14px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 4px;
                transition: background-color 0.3s;"
                onmouseover="this.style.backgroundColor='#2980b9'"
                onmouseout="this.style.backgroundColor='#3498db'"
                onclick="window.parent.postMessage('{row['NombreSede']}', '*')">
                Ver Gráficos
            </button>
        </div>
        """
        
        # Agregar marcador
        folium.Marker(
            location=[row['Latitud_sede'], row['Longitud_sede']],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"Click para {row['NombreSede']}",
            icon=folium.Icon(color="blue", icon="university", prefix="fa")
        ).add_to(mapa)
    
    return mapa

# =====================================================================
# INTERFAZ DE LA APLICACIÓN
# =====================================================================

# Título principal
st.title("📊 Análisis de Sedes - Admisión 2025")

# Crear columnas para el layout
col1, col2 = st.columns([1, 3])

# Panel lateral
with col1:
    st.header("Configuración")
    st.markdown("""
    **Instrucciones:**
    1. Explora el mapa de sedes
    2. Haz clic en un marcador
    3. Presiona "Ver Gráficos"
    """)
    
    # Mostrar lista de sedes
    st.subheader("Sedes Disponibles")
    for sede in df_sedes['NombreSede']:
        st.markdown(f"- {sede}")
    
    # Información adicional
    st.divider()
    st.markdown("**Periodos de Admisión:**")
    st.markdown("- PSU (2016-2019)")
    st.markdown("- PDT (2020-2022)")
    st.markdown("- PAES (2023-2025)")

# Mapa principal
with col2:
    st.header("Ubicación de Sedes")
    
    # Crear y mostrar mapa
    mapa = crear_mapa_interactivo(df_sedes)
    evento = st_folium(
        mapa, 
        width=900, 
        height=600,
        returned_objects=["last_object_clicked_popup"]
    )
    
    # Manejar selección de sede
    sede_seleccionada = st.session_state.get('sede_activa', None)
    
    if evento and evento.get("last_object_clicked_popup"):
        sede_seleccionada = evento["last_object_clicked_popup"]
        st.session_state.sede_activa = sede_seleccionada
        st.experimental_rerun()

# Mostrar gráficos si hay sede seleccionada
if sede_seleccionada:
    st.divider()
    st.header(f"📈 Análisis de: {sede_seleccionada}")
    
    # Ruta al archivo PNG
    ruta_grafico = GRAFICOS_DIR / f"{sede_seleccionada}_graficos.png"
    
    if os.path.exists(ruta_grafico):
        # Mostrar gráficos
        st.image(str(ruta_grafico), use_column_width=True)
        
        # Descargar gráficos
        with open(ruta_grafico, "rb") as file:
            btn = st.download_button(
                label="Descargar gráficos",
                data=file,
                file_name=f"{sede_seleccionada}_graficos.png",
                mime="image/png"
            )
    else:
        st.error(f"No se encontraron gráficos para {sede_seleccionada}")
        st.info(f"Ejecuta primero 'generar_graficos.py' para crear los gráficos")
else:
    st.info("Selecciona una sede del mapa para ver sus gráficos")

# Pie de página
st.divider()
st.caption("Dashboard desarrollado por Cris | Actualizado: Junio 2025")