"""
Dashboard Interactivo — Nivel de Ríos y Quebradas (CORNARE / MARCO)
--------------------------------------------------------------------
Versión optimizada para portafolio con gráficos interactivos, 
indicadores de tendencia y mapeo de estaciones.

Para correrla:
    streamlit run app_nivel_cornare.py
"""

import requests
import pandas as pd
import streamlit as st
import urllib3
import plotly.express as px

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ------------------------------------------------------------------
# Configuración y Mapeo de Estaciones Conocidas
# ------------------------------------------------------------------
# Diccionario para enriquecer los datos si la API no devuelve nombre o coordenadas
ESTACIONES_INFO = {
    "42": {"nombre": "Quebrada La Mosca - Guarne", "lat": 6.279, "lon": -75.443},
    "12": {"nombre": "Río Nare - Puente", "lat": 6.220, "lon": -75.120},
    # Valor por defecto (Pascual Bravo) si la estación es desconocida
    "default": {"nombre": "Estación Desconocida", "lat": 6.2766, "lon": -75.5901}
}

API_BASE_URL = "https://marco.cornare.gov.co/api/v1/estaciones"
GEOPORTAL_BASE_URL = "https://marco.cornare.gov.co/geoportal"

LLAVE_FECHA = "level_date"
LLAVE_VALOR = "level"
CANDIDATOS_LAT = ["lat", "latitude", "latitud"]
CANDIDATOS_LON = ["lng", "lon", "longitude", "longitud"]

st.set_page_config(page_title="Monitor Hídrico | CORNARE", page_icon="🌊", layout="wide")


# ------------------------------------------------------------------
# Funciones de consulta
# ------------------------------------------------------------------
@st.cache_data(ttl=600) # Caché para no saturar la API en consultas repetidas
def obtener_serie_nivel(codigo_estacion, desde, hasta, calidad=1, timeout=30):
    url = f"{API_BASE_URL}/{codigo_estacion}/nivel"
    params = {"desde": desde, "hasta": hasta, "calidad": calidad}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=timeout, verify=False)
        if resp.status_code == 200:
            return resp.json(), None
        return None, f"HTTP {resp.status_code}"
    except requests.exceptions.RequestException as e:
        return None, f"Error de red: {e}"


def obtener_todas_las_paginas(datos_json, timeout=30):
    registros = list(datos_json.get("values", []))
    siguiente_url = datos_json.get("next")
    while siguiente_url:
        try:
            resp = requests.get(siguiente_url, timeout=timeout, verify=False)
        except requests.exceptions.RequestException:
            break
        if resp.status_code != 200:
            break
        pagina = resp.json()
        registros.extend(pagina.get("values", []))
        siguiente_url = pagina.get("next")
    return registros


def detectar_coordenadas(datos_json, codigo):
    """Busca lat/lon. Si no las encuentra, usa el diccionario de estaciones."""
    lat, lon = None, None
    if isinstance(datos_json, dict):
        lat = next((datos_json[k] for k in CANDIDATOS_LAT if k in datos_json), None)
        lon = next((datos_json[k] for k in CANDIDATOS_LON if k in datos_json), None)

    if lat is not None and lon is not None:
        try:
            return float(lat), float(lon), True
        except (TypeError, ValueError):
            pass
    
    # Fallback al diccionario propio
    info = ESTACIONES_INFO.get(codigo, ESTACIONES_INFO["default"])
    return info["lat"], info["lon"], False


def calcular_indice_calidad(df):
    """Índice simple (0-100) combinando completitud de la serie y proporción de outliers."""
    if df.empty or len(df) < 2:
        return 0.0, 0, 0

    df_idx = df.set_index("fecha")
    frecuencia_tipica = df["fecha"].diff().dropna().mode()
    if len(frecuencia_tipica) == 0:
        return 0.0, 0, 0
    frecuencia_tipica = frecuencia_tipica[0]

    rango_completo = pd.date_range(start=df_idx.index.min(), end=df_idx.index.max(), freq=frecuencia_tipica)
    esperados = len(rango_completo)
    huecos = esperados - len(df_idx)
    completitud = max(0.0, 1 - (huecos / esperados)) if esperados > 0 else 0.0

    Q1, Q3 = df["nivel"].quantile(0.25), df["nivel"].quantile(0.75)
    IQR = Q3 - Q1
    lim_inf, lim_sup = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
    es_outlier = (df["nivel"] < lim_inf) | (df["nivel"] > lim_sup) | (df["nivel"] < 0)
    proporcion_outliers = es_outlier.mean()

    indice = (completitud * 0.7 + (1 - proporcion_outliers) * 0.3) * 100
    return round(indice, 1), int(huecos), int(es_outlier.sum())


# ------------------------------------------------------------------
# Sidebar — parámetros de la consulta
# ------------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3262/3262973.png", width=80)
    st.header("Parámetros de Consulta")
    nombre_estudiante = st.text_input("Analista de Datos", "Juan Alberto Rojas Mesa")
    codigo_estacion = st.text_input("Código de estación", "42")
    fecha_desde = st.date_input("Desde", pd.to_datetime("2026-08-23")).strftime("%Y-%m-%d")
    fecha_hasta = st.date_input("Hasta", pd.to_datetime("2026-08-30")).strftime("%Y-%m-%d")
    calidad = st.selectbox("Calidad de Datos", [1, 0], index=0, format_func=lambda x: "Validados (1)" if x==1 else "Crudos (0)")
    consultar = st.button("🔍 Iniciar Análisis", type="primary", use_container_width=True)

# ------------------------------------------------------------------
# Layout Principal
# ------------------------------------------------------------------
nombre_est = ESTACIONES_INFO.get(codigo_estacion, ESTACIONES_INFO["default"])["nombre"]
st.title(f"🌊 Análisis Hídrico: {nombre_est}")
st.markdown(f"**Analista:** {nombre_estudiante} | **Estación ID:** {codigo_estacion}")
st.divider()

if consultar:
    with st.spinner("Extrayendo telemetría de la API de Cornare..."):
        datos_crudos, error = obtener_serie_nivel(codigo_estacion, fecha_desde, fecha_hasta, calidad)

    if error:
        st.error(f"❌ Error al conectar con la fuente de datos: {error}")
    else:
        registros = obtener_todas_las_paginas(datos_crudos)

        if not registros:
            st.warning("No hay registros para esta estación en el rango seleccionado. Intenta ampliar las fechas.")
        else:
            df = pd.DataFrame(registros)
            df = df.rename(columns={LLAVE_FECHA: "fecha", LLAVE_VALOR: "nivel"})
            df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
            df["nivel"] = pd.to_numeric(df["nivel"], errors="coerce")
            df = df.dropna(subset=["fecha", "nivel"]).sort_values("fecha").reset_index(drop=True)

            lat, lon, coords_reales = detectar_coordenadas(datos_crudos, codigo_estacion)
            indice_calidad, huecos, n_outliers = calcular_indice_calidad(df)

            # --- Cálculos para métricas avanzadas ---
            nivel_promedio = df["nivel"].mean()
            ultimo_nivel = df["nivel"].iloc[-1]
            delta_nivel = ultimo_nivel - nivel_promedio

            # --- Panel de Métricas ---
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Lecturas", len(df), help="Número de puntos de datos recuperados.")
            col2.metric("Nivel Promedio (m)", f"{nivel_promedio:.2f}")
            col3.metric("Último Nivel (m)", f"{ultimo_nivel:.2f}", delta=f"{delta_nivel:.2f} vs Promedio", delta_color="inverse")
            col4.metric("Score de Calidad", f"{indice_calidad}%", help="Calculado en base a completitud y valores atípicos.")

            st.write("") # Espaciador

            # --- Gráfico Interactivo de la serie ---
            st.subheader("📈 Evolución Temporal del Nivel")
            fig = px.line(
                df, x="fecha", y="nivel", 
                labels={"fecha": "Fecha de Medición", "nivel": "Nivel (metros)"},
                color_discrete_sequence=["#1f77b4"]
            )
            fig.update_layout(hovermode="x unified", margin=dict(l=0, r=0, t=30, b=0))
            fig.add_hline(y=nivel_promedio, line_dash="dot", annotation_text="Promedio", annotation_position="bottom right")
            st.plotly_chart(fig, use_container_width=True)

            # --- Mapa de la estación y Enlaces ---
            col_mapa, col_info = st.columns([2, 1])
            
            with col_mapa:
                st.subheader("📍 Ubicación de Monitoreo")
                if not coords_reales:
                    st.caption(f"Usando coordenadas de referencia de la base de datos interna para: {nombre_est}.")
                st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=12)
            
            with col_info:
                st.subheader("⚙️ Opciones de Exportación")
                st.write("Verifica el entorno oficial del geoportal o exporta la serie de datos limpia para realizar entrenamientos o modelos predictivos externos.")
                
                # Botón de enlace al Geoportal de Cornare
                link_geoportal = f"{GEOPORTAL_BASE_URL}/{codigo_estacion}"
                st.link_button("🗺️ Ver en Geoportal Oficial", link_geoportal, use_container_width=True)
                
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Exportar CSV (Limpiado)", csv, file_name=f"dataset_estacion_{codigo_estacion}.csv", mime="text/csv", use_container_width=True)

            # --- Detalle de calidad (Expandible) ---
            with st.expander("🛠️ Auditoría y Calidad de Datos"):
                st.write(f"- **Huecos de reporte (Gaps):** {huecos} detectados basándose en la frecuencia modal.")
                st.write(f"- **Valores Atípicos (Outliers):** {n_outliers} registros fuera del rango intercuartílico (1.5 IQR).")
                st.dataframe(df, use_container_width=True)
else:
    # Estado vacío (Splash screen)
    st.info("👈 Configura los parámetros en el panel lateral e inicia el análisis.")
    st.markdown("""
    ### Bienvenido al Monitor Hídrico
    Esta herramienta permite extraer, limpiar y visualizar información en tiempo real de las estaciones hidrológicas de CORNARE. Ideal para el monitoreo de cuencas y la prevención de riesgos.
    """)