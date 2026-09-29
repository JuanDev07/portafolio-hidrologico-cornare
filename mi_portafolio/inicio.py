import streamlit as st

# ------------------------------------------------------------------
# Configuración de la página principal
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Portafolio | Programación Avanzada",
    page_icon="📚",
    layout="wide"
)

# ------------------------------------------------------------------
# ENCABEZADO DE LA MATERIA
# ------------------------------------------------------------------
st.title("📚 Portafolio de Proyectos y Aplicaciones")
st.subheader("Materia: Programación Avanzada | Institución Universitaria Pascual Bravo")
st.markdown("""
Bienvenido al repositorio interactivo de la materia. A continuación se presentan las implementaciones, 
análisis de datos y modelos desarrollados durante el curso. Selecciona cualquiera de los proyectos para explorar su funcionalidad en tiempo real.
""")

st.divider()

# ------------------------------------------------------------------
# CATÁLOGO DE APLICACIONES (11 PROYECTOS)
# ------------------------------------------------------------------
PROYECTOS = [
    {
        "titulo": "🌊 Monitor Hídrico CORNARE",
        "descripcion": "Dashboard para monitoreo de niveles de ríos consumiendo la API REST en tiempo real con auditoría de calidad de datos.",
        "imagen": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=600&q=80",
        "tipo": "interno",  # Página interna en folder /pages
        "target": "pages/1_Monitor_Cornare.py",
        "tags": "Python • API REST • Plotly"
    },
    {
        "titulo": "💨 Predicción de Calidad del Aire",
        "descripcion": "Análisis y modelamiento de variables ambientales para la predicción de calidad del aire.",
        "imagen": "https://images.unsplash.com/photo-1534088568595-a066f410bcda?w=600&q=80",
        "tipo": "externo",
        "target": "https://prediccion-aire.streamlit.app/",
        "tags": "Machine Learning • Pandas"
    },
    {
        "titulo": "📈 Series de Tiempo",
        "descripcion": "Análisis exploratorio, tendencias y pronósticos sobre series temporales hidrológicas y climáticas.",
        "imagen": "https://images.unsplash.com/photo-1642543492481-44e81e3914a7?w=600&q=80",
        "tipo": "externo",
        "target": "https://series-de-tiempo.streamlit.app/",
        "tags": "Statsmodels • Time Series"
    },
    {
        "titulo": "📊 Regresión Lineal",
        "descripcion": "Ajuste de modelos de regresión lineal simple y múltiple con evaluación de métricas R² y RMSE.",
        "imagen": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&q=80",
        "tipo": "externo",
        "target": "https://regresion-lineal.streamlit.app/",
        "tags": "Scikit-Learn • Regresión"
    },
    {
        "titulo": "📐 Conceptos de Regresión",
        "descripcion": "Demostración interactiva sobre supuestos de regresión, residuos y multicolinealidad.",
        "imagen": "https://images.unsplash.com/photo-1509228468518-180dd4864904?w=600&q=80",
        "tipo": "externo",
        "target": "https://regresion-conceptos-app.streamlit.app/",
        "tags": "Estadística • Simulación"
    },
    {
        "titulo": "⚡ Descenso de Gradiente",
        "descripcion": "Visualización del algoritmo de optimización por descenso de gradiente en funciones matematicas.",
        "imagen": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=600&q=80",
        "tipo": "externo",
        "target": "https://gradiente.streamlit.app/",
        "tags": "Optimización • Numpy"
    },
    {
        "titulo": "🛠️ Preparación de Datos",
        "descripcion": "Herramienta de limpieza, imputación de faltantes y transformación de conjuntos de datos.",
        "imagen": "https://images.unsplash.com/photo-1543286386-713bdd548da4?w=600&q=80",
        "tipo": "externo",
        "target": "https://app-preparacion-datos.streamlit.app/",
        "tags": "ETL • Data Wrangling"
    },
    {
        "titulo": "🍎 Clasificador de Frutas",
        "descripcion": "Aplicación para clasificación de atributos e imágenes de frutas usando modelos de machine learning.",
        "imagen": "https://images.unsplash.com/photo-1619566636858-adf3ef46400b?w=600&q=80",
        "tipo": "externo",
        "target": "https://app-frutas.streamlit.app/",
        "tags": "Clasificación • ML"
    },
    {
        "titulo": "⚡ Análisis de Complejidad (Big O)",
        "descripcion": "Comparador de eficiencia algorítmica y medición de tiempos de ejecución $O(n)$.",
        "imagen": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&q=80",
        "tipo": "externo",
        "target": "https://app-big0.streamlit.app/",
        "tags": "Algoritmos • Estructuras"
    },
    {
        "titulo": "🧪 Mi Primera App Streamlit",
        "descripcion": "Primer laboratorio de pruebas con componentes interactivos y widgets de Streamlit.",
        "imagen": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600&q=80",
        "tipo": "externo",
        "target": "https://my-first-app.streamlit.app/",
        "tags": "Streamlit • Fundamentos"
    }
]

# ------------------------------------------------------------------
# RENDERIZADO DE TARJETAS (CARTAS) EN CUADRÍCULA (3 COLUMNAS)
# ------------------------------------------------------------------
COLS_POR_FILA = 3

for i in range(0, len(PROYECTOS), COLS_POR_FILA):
    columnas = st.columns(COLS_POR_FILA)
    for idx, col in enumerate(columnas):
        if i + idx < len(PROYECTOS):
            app = PROYECTOS[i + idx]
            with col:
                with st.container(border=True):
                    # Imagen de portada
                    st.image(app["imagen"], use_container_width=True)
                    
                    # Título y Descripción
                    st.markdown(f"### {app['titulo']}")
                    st.write(app["descripcion"])
                    st.caption(f"🏷️ `{app['tags']}`")
                    
                    st.divider()
                    
                    # Botón según si es una página interna o app externa
                    if app["tipo"] == "interno":
                        st.page_link(app["target"], label="Abrir Aplicación", icon="📊", use_container_width=True)
                    else:
                        st.link_button("🚀 Abrir en Streamlit Cloud", app["target"], use_container_width=True)
