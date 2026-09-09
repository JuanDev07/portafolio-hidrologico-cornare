import streamlit as st

# Configuración de la página principal
st.set_page_config(
    page_title="Portafolio | Programación Avanzada",
    page_icon="📚",
    layout="wide"
)

# --- ENCABEZADO DE LA MATERIA ---
st.title("📚 Portafolio de Proyectos")
st.subheader("Materia: Programación Avanzada | Institución Universitaria Pascual Bravo")
st.markdown("""
Bienvenido al repositorio interactivo de la materia. A continuación se presentan las implementaciones 
y aplicaciones desarrolladas durante el curso. Seleccione un proyecto para explorar su funcionalidad en tiempo real.
""")

st.divider()

# --- SECCIÓN DE CARTAS (CARDS) ---
# Usamos columnas para organizar las cartas una al lado de la otra
col1, col2, col3 = st.columns(3)

# Carta 1: Proyecto Cornare
with col1:
    with st.container(border=True):
        st.markdown("### 🌊 Monitor Hídrico CORNARE")
        st.write("Dashboard interactivo para el monitoreo de niveles de ríos y quebradas consumiendo la API REST del Geoportal en tiempo real. Incluye auditoría de calidad de datos.")
        # El st.page_link es el botón que te lleva directamente al proyecto
        st.page_link("pages/1_Monitor_Cornare.py", label="Abrir Aplicación", icon="📊")

# Carta 2: Espacio para el próximo proyecto (Plantilla)
with col2:
    with st.container(border=True):
        st.markdown("### ⚙️ Proyecto 2 (Próximamente)")
        st.write("Espacio reservado para la siguiente implementación de algoritmos o procesamiento de datos que se desarrolle en la materia.")
        st.button("No disponible", disabled=True, key="btn_2")

# Carta 3: Espacio para otro proyecto (Plantilla)
with col3:
    with st.container(border=True):
        st.markdown("### 🚀 Proyecto 3 (Próximamente)")
        st.write("Espacio reservado para el proyecto final del curso. Aquí se desplegará la integración completa de los temas vistos.")
        st.button("No disponible", disabled=True, key="btn_3")