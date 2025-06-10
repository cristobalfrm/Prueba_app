import streamlit as st
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Gráficos por Sede",
    page_icon=":university:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- RUTAS ---
BASE_PATH    = Path(__file__).parent
GRAFICOS_DIR = BASE_PATH / "graficos_sedes"
LOGO_PATH    = BASE_PATH / "logo.png"  # opcional

# Título principal
st.title("📈 Análisis de Gráficos por Sede y Nacional")

# Sidebar: logo y selector
if LOGO_PATH.exists():
    st.sidebar.image(str(LOGO_PATH), use_container_width=True)

st.sidebar.header("🏢 Selecciona una sede")

# Listar archivos existentes
archivos = sorted(GRAFICOS_DIR.glob("*_graficos.png"))
sedes = [f.stem.replace("_graficos", "") for f in archivos]

# Incluir “Nacional” si existe
nacional_path = BASE_PATH / "Nacional.png"
#if nacional_path.exists() and "Nacional" not in sedes:
    #sedes.insert(0, "Nacional")

sede_seleccionada = st.sidebar.selectbox("Sede:", sedes)

# Preparar rutas
ruta_nacional = nacional_path
if sede_seleccionada == "Nacional":
    ruta_sede = nacional_path
else:
    ruta_sede = GRAFICOS_DIR / f"{sede_seleccionada}_graficos.png"

# Crear dos columnas para gráficos
col1, col2 = st.columns(2)

# Columna izquierda: siempre Nacional
with col1:
    st.subheader("Nacional")
    if ruta_nacional.exists():
        st.image(str(ruta_nacional), use_container_width=True)
        with open(ruta_nacional, "rb") as f:
            st.download_button(
                label="⬇️ Descargar Nacional",
                data=f,
                file_name="Nacional.png",
                mime="image/png",
                use_container_width=True
            )
    else:
        st.error("⚠️ No se encontró el gráfico Nacional.png")

# Columna derecha: sede seleccionada
with col2:
    st.subheader(f"Sede: {sede_seleccionada}")
    if ruta_sede.exists():
        st.image(str(ruta_sede), use_container_width=True)
        with open(ruta_sede, "rb") as f:
            st.download_button(
                label=f"⬇️ Descargar {sede_seleccionada}",
                data=f,
                file_name=ruta_sede.name,
                mime="image/png",
                use_container_width=True
            )
    else:
        st.error(f"⚠️ No se encontró el gráfico para «{sede_seleccionada}».")

    # Caption en la columna de la sede
    st.caption("Selecciona otra sede en el menú lateral para actualizar este gráfico.")

# Pie de página
st.markdown("---")
st.caption("Dashboard desarrollado por Cristóbal Reyes M. | Junio 2025")
