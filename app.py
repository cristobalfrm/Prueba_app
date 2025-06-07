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
LOGO_PATH = BASE_PATH / "logo.png"  # Opcional: si tienes un logo

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
        st.error(f"Error al cargar coordenadas: {str(e)}")
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
    
    # Configurar mapa base
    mapa = folium.Map(
        location=centro, 
        zoom_start=5,
        tiles='CartoDB Positron',
        control_scale=True,
        attr='Mapa de Sedes'
    )
    
    # Cargar logo en base64 (si existe)
    logo_base64 = obtener_imagen_base64(LOGO_PATH) if LOGO_PATH else ""
    
    # Añadir marcadores
    for _, row in df.iterrows():
        # HTML personalizado para el popup
        logo_html = f"""
        <div style="text-align:center;">
            <img src="data:image/png;base64,{logo_base64}" width="80" style="margin-bottom:10px;">
        </div>
        """ if logo_base64 else ""
        
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; text-align: center; width: 200px;">
            {logo_html}
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
        
        # Añadir marcador al mapa
        folium.Marker(
            location=[row['Latitud_sede'], row['Longitud_sede']],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"Click para {row['NombreSede']}",
            icon=folium.Icon(color="blue", icon="university", prefix="fa")
        ).add_to(mapa)
    
    return mapa

# --- INTERFAZ DE LA APLICACIÓN ---
st.title("📊 Análisis de Sedes - Admisión 2025")

# Verificar si se cargaron datos
if df_sedes.empty:
    st.error("""
        **Error crítico:** No se pudieron cargar los datos de las sedes. 
        Verifica que el archivo `Coordenadas_Sedes.xlsx` esté en la raíz del repositorio.
    """)
    st.stop()

# Crear columnas para el layout
col1, col2 = st.columns([1, 3])

# Panel lateral
with col1:
    st.header("⚙️ Configuración")
    st.markdown("""
    **Instrucciones:**
    1. Explora el mapa de sedes
    2. Haz clic en un marcador
    3. Presiona **Ver Gráficos**
    """)
    
    st.subheader("🏢 Sedes Disponibles")
    for sede in df_sedes['NombreSede'].unique():
        st.markdown(f"- {sede}")
    
    st.divider()
    st.markdown("**📅 Periodos de Admisión:**")
    st.markdown("- PSU (2016-2019)")
    st.markdown("- PDT (2020-2022)")
    st.markdown("- PAES (2023-2025)")
    
    # Espacio para logo (opcional)
    if LOGO_PATH and LOGO_PATH.exists():
        st.divider()
        st.image(str(LOGO_PATH), width=150)

# Mapa principal
with col2:
    st.header("📍 Ubicación de Sedes")
    
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
        
        # CORRECCIÓN: Usar st.rerun() en lugar de st.experimental_rerun()
        st.rerun()

# Mostrar gráficos si hay sede seleccionada
if sede_seleccionada:
    st.divider()
    st.header(f"📈 Análisis de: {sede_seleccionada}")
    
    # Ruta al archivo PNG
    ruta_grafico = GRAFICOS_DIR / f"{sede_seleccionada}_graficos.png"
    
    try:
        # Verificar si existe el gráfico
        if ruta_grafico.exists():
            # Mostrar gráficos
            st.image(str(ruta_grafico), use_column_width=True)
            
            # Botón de descarga
            with open(ruta_grafico, "rb") as file:
                btn = st.download_button(
                    label="⬇️ Descargar gráficos",
                    data=file,
                    file_name=f"{sede_seleccionada}_graficos.png",
                    mime="image/png",
                    use_container_width=True
                )
        else:
            st.error(f"⚠️ No se encontraron gráficos para {sede_seleccionada}")
            st.info("""
            **Solución:** 
            - Ejecuta localmente `generar_graficos.py` para crear los gráficos
            - Sube la carpeta `graficos_sedes` a GitHub
            """)
            
    except Exception as e:
        st.error(f"❌ Error al cargar gráficos: {str(e)}")

# Pie de página
st.divider()
st.caption("Dashboard desarrollado por Cris | Actualizado: Junio 2025")
