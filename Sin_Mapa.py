import streamlit as st
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Sedes - Admisión 2025",
    page_icon=":university:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- RUTAS ---
BASE_PATH     = Path(__file__).parent
GRAFICOS_DIR  = BASE_PATH / "graficos_sedes"
LOGO_PATH     = BASE_PATH / "logo.png"  # si no lo usas, déjalo en blanco o quítalo

# Título principal
st.title("📈 Análisis de Gráficos por Sede")

# Sidebar con menú desplegable de sedes
st.sidebar.header("🏢 Selecciona una sede")
# Buscar automáticamente todos los archivos *_graficos.png
archivos = sorted(GRAFICOS_DIR.glob("*_graficos.png"))
sedes = [f.stem.replace("_graficos", "") for f in archivos]
sede_seleccionada = st.sidebar.selectbox("Sede:", sedes)

# Mostrar logo opcional en sidebar
if LOGO_PATH.exists():
    st.sidebar.image(str(LOGO_PATH), use_column_width=True)

# Sección principal: gráfico de la sede seleccionada
st.header(f"Gráfico de la sede: {sede_seleccionada}")

ruta_grafico = GRAFICOS_DIR / f"{sede_seleccionada}_graficos.png"
if ruta_grafico.exists():
    st.image(str(ruta_grafico), use_column_width=True)
    with open(ruta_grafico, "rb") as file:
        st.download_button(
            label="⬇️ Descargar gráfico",
            data=file,
            file_name=f"{sede_seleccionada}_graficos.png",
            mime="image/png"
        )
else:
    st.error(f"No se encontró el gráfico para «{sede_seleccionada}».")
    st.info("Verifica que en la carpeta `graficos_sedes` exista el archivo correspondiente.")

# Pie de página
st.markdown("---")
st.caption("Dashboard desarrollado por Cris | Junio 2025")
