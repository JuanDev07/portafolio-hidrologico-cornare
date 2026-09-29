import streamlit as st

# ------------------------------------------------------------------
# Configuración de la página principal
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Portafolio | Programación Avanzada",
    page_icon="📚",
    layout="wide"
)

# Estilo CSS para fijar el tamaño uniforme de las imágenes
st.markdown("""
    <style>
    [data-testid="stImage"] img {
        height: 180px !important;
        object-fit: cover !important;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# ENCABEZADO
# ------------------------------------------------------------------
st.title("📚 Portafolio de Proyectos y Aplicaciones")
st.subheader("Materia: Programación Avanzada | Institución Universitaria Pascual Bravo")
st.markdown("""
Bienvenido al repositorio interactivo de la materia. Haz clic en **"Abrir Proyecto"** en cualquiera de las tarjetas o navega mediante la barra lateral izquierda para ejecutar la aplicación correspondiente.
""")

st.divider()

# ------------------------------------------------------------------
# CATÁLOGO COMPLETO DE PROYECTOS (RUTAS EXACTAS DE /PAGES)
# ------------------------------------------------------------------
PROYECTOS = [
    {
        "titulo": "🌊 Monitor Hídrico CORNARE",
        "descripcion": "Dashboard para monitoreo de niveles de ríos consumiendo la API REST en tiempo real con auditoría de datos.",
        "imagen": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=600&h=350&fit=crop&q=80",
        "page": "pages/1_Monitor_Cornare.py",
        "tags": "API REST • Plotly • Pandas"
    },
    {
        "titulo": "💨 Predicción de Calidad del Aire",
        "descripcion": "Análisis y modelamiento de variables ambientales para la predicción de calidad del aire.",
        "imagen": "https://images.unsplash.com/photo-1534088568595-a066f410bcda?w=600&h=350&fit=crop&q=80",
        "page": "pages/app_Pred_Aire.py",
        "tags": "Machine Learning • Scikit-Learn"
    },
    {
        "titulo": "📈 Series de Tiempo",
        "descripcion": "Análisis exploratorio, tendencias y pronósticos sobre series temporales hidrológicas y climáticas.",
        "imagen": "https://images.unsplash.com/photo-1642543492481-44e81e3914a7?w=600&h=350&fit=crop&q=80",
        "page": "pages/app_series_tiempo.py",
        "tags": "Statsmodels • Pronósticos"
    },
    {
        "titulo": "📊 Regresión Lineal",
        "descripcion": "Ajuste de modelos de regresión lineal simple y múltiple con evaluación de métricas R² y RMSE.",
        "imagen": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&h=350&fit=crop&q=80",
        "page": "pages/app_regresion.py",
        "tags": "Scikit-Learn • Regresión"
    },
    {
        "titulo": "📐 Conceptos de Regresión",
        "descripcion": "Demostración interactiva sobre supuestos de regresión, residuos y multicolinealidad.",
        "imagen": "https://images.unsplash.com/photo-1509228468518-180dd4864904?w=600&h=350&fit=crop&q=80",
        "page": "pages/regresion_conceptos_app.py",
        "tags": "Estadística • Simulación"
    },
    {
        "titulo": "🌱 Clasificación / Análisis de Suelos",
        "descripcion": "Modelamiento y caracterización de muestras de suelo mediante algoritmos de aprendizaje supervisado.",
        "imagen": "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=600&h=350&fit=crop&q=80",
        "page": "pages/app_Suelos.py",
        "tags": "Machine Learning • Suelos"
    },
    {
        "titulo": "🌐 Monitoreo IoT",
        "descripcion": "Visualización y procesamiento de datos recolectados mediante sensores e infraestructura IoT.",
        "imagen": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&h=350&fit=crop&q=80",
        "page": "pages/app_IoT.py",
        "tags": "IoT • Sensores • Real-time"
    },
    {
        "titulo": "⚡ Descenso de Gradiente",
        "descripcion": "Visualización del algoritmo de optimización por descenso de gradiente en funciones matemáticas.",
        "imagen": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=600&h=350&fit=crop&q=80",
        "page": "pages/app_gradiente.py",
        "tags": "Optimización • Numpy"
    },
    {
        "titulo": "🛠️ Preparación de Datos",
        "descripcion": "Herramienta de limpieza, imputación de faltantes y transformación de conjuntos de datos.",
        "imagen": "https://images.unsplash.com/photo-1543286386-713bdd548da4?w=600&h=350&fit=crop&q=80",
        "page": "pages/App_Prep_Datos.py",
        "tags": "ETL • Data Cleaning"
    },
    {
        "titulo": "🍎 Clasificador de Frutas",
        "descripcion": "Aplicación para clasificación de atributos e imágenes de frutas usando modelos de machine learning.",
        "imagen": "https://images.unsplash.com/photo-1619566636858-adf3ef46400b?w=600&h=350&fit=crop&q=80",
        "page": "pages/frutas_app.py",
        "tags": "Clasificación • ML"
    },
    {
        "titulo": "⚡ Análisis de Complejidad (Big O)",
        "descripcion": "Comparador de eficiencia algorítmica y medición de tiempos de ejecución O(n).",
        "imagen": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=350&fit=crop&q=80",
        "page": "pages/App_Big0.py",
        "tags": "Algoritmos • Estructuras"
    },
    {
        "titulo": "🧪 Mi Primera App Streamlit",
        "descripcion": "Primer laboratorio de pruebas con componentes interactivos y widgets de Streamlit.",
        "imagen": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600&h=350&fit=crop&q=80",
        "page": "pages/My_First_App.py",
        "tags": "Streamlit • Fundamentos"
    }
]

# ------------------------------------------------------------------
# RENDERIZADO EN CUADRÍCULA DE 3 COLUMNAS
# ------------------------------------------------------------------
COLS_POR_FILA = 3

for i in range(0, len(PROYECTOS), COLS_POR_FILA):
    columnas = st.columns(COLS_POR_FILA)
    for idx, col in enumerate(columnas):
        if i + idx < len(PROYECTOS):
            app = PROYECTOS[i + idx]
            with col:
                with st.container(border=True):
                    st.image(app["imagen"], use_container_width=True)
                    st.markdown(f"### {app['titulo']}")
                    st.write(app["descripcion"])
                    st.caption(f"🏷️ `{app['tags']}`")
                    st.divider()
                    st.page_link(app["page"], label="🚀 Abrir Proyecto", icon="📊", use_container_width=True)
