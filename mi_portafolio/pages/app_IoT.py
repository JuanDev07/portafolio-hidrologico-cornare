"""
Predictor de Sensación Térmica — Taller IoT ET0197
Consulta datos reales de InfluxDB (temperatura y humedad de un ESP32),
entrena un modelo de regresión lineal y permite predecir la sensación
térmica de forma interactiva. Pensado para desplegarse en Streamlit
Community Cloud: sin autorefresh, solo librerías estándar del ecosistema
científico de Python (pandas, numpy, scikit-learn, matplotlib) más el
cliente oficial de InfluxDB.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 -- necesario para projection='3d'
import streamlit as st
from influxdb_client import InfluxDBClient
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ────────────────────────────────────────────────────────────────────────────
# Configuración de la página
# ────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Predictor Sensación Térmica", page_icon="🌡️", layout="centered")

COLUMNAS = ["temperatura", "humedad", "sensacion_termica"]


# ────────────────────────────────────────────────────────────────────────────
# Funciones de datos y modelo
# ────────────────────────────────────────────────────────────────────────────
def obtener_datos_crudos(url: str, token: str, org: str, bucket: str, measurement: str, horas: int) -> pd.DataFrame:
    """Consulta InfluxDB y devuelve el DataFrame TAL COMO llega (con posibles NaN).

    Usamos un context manager para que la conexión se cierre apenas termina
    la consulta -- no queremos mantener conexiones abiertas en Streamlit Cloud.
    Sin caché: el botón ya controla cuándo se dispara la consulta, así que
    cada clic debe traer los datos más recientes de InfluxDB.
    """
    query = f'''
    from(bucket: "{bucket}")
      |> range(start: -{horas}h)
      |> filter(fn: (r) => r._measurement == "{measurement}")
      |> filter(fn: (r) => r._field == "temperatura" or r._field == "humedad" or r._field == "sensacion_termica")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    with InfluxDBClient(url=url, token=token, org=org, verify_ssl=False) as client:
        df = client.query_api().query_data_frame(query, org=org)

    if df.empty:
        return df

    df = df[["_time"] + COLUMNAS].copy()
    df["_time"] = pd.to_datetime(df["_time"])
    df = df.set_index("_time").sort_index()
    df.index = df.index.tz_convert("America/Bogota")
    return df


def preparar_datos(df_crudo: pd.DataFrame) -> pd.DataFrame:
    """Interpola y luego promedia las lecturas cada 30 minutos para reducir ruido."""
    df_interp = df_crudo.interpolate(method="time").dropna()
    
    # Agrupa por ventanas de 30 minutos y calcula el promedio
    df_30min = df_interp.resample("30min").mean().dropna()
    
    return df_30min


def detectar_outliers_iqr(serie: pd.Series) -> pd.Series:
    q1, q3 = serie.quantile(0.25), serie.quantile(0.75)
    iqr = q3 - q1
    lim_inf, lim_sup = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return serie[(serie < lim_inf) | (serie > lim_sup)]


@st.cache_data(ttl=300, show_spinner=False)
def entrenar_modelo(df: pd.DataFrame):
    """Entrena la regresión lineal y devuelve el modelo junto a sus métricas."""
    X = df[["temperatura", "humedad"]]
    y = df["sensacion_termica"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    modelo = LinearRegression()
    modelo.fit(X_train, y_train)

    y_pred = modelo.predict(X_test)
    metricas = {
        "mae": mean_absolute_error(y_test, y_pred),
        "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
        "r2": r2_score(y_test, y_pred),
    }
    return modelo, metricas


# ────────────────────────────────────────────────────────────────────────────
# Barra lateral
# ────────────────────────────────────────────────────────────────────────────
st.sidebar.header("Credenciales InfluxDB")
influx_url = st.sidebar.text_input("URL", placeholder="https://<region>.aws.cloud2.influxdata.com")
influx_token = st.sidebar.text_input("Token", type="password", placeholder="Tu token de InfluxDB")
influx_org = st.sidebar.text_input("Organización", placeholder="tu-org o email de la cuenta")
influx_bucket = st.sidebar.text_input("Bucket", placeholder="T_H")
influx_measurement = st.sidebar.text_input("Measurement", placeholder="Sensor 1")

st.sidebar.divider()
st.sidebar.header("Parámetros de consulta")
horas = st.sidebar.slider("Horas de historial a consultar", min_value=1, max_value=12, value=1, step=1)
st.sidebar.caption("Datos tomados del sensor DHT22 (ESP32) vía InfluxDB Cloud.")

credenciales_completas = all([influx_url, influx_token, influx_org, influx_bucket, influx_measurement])
if not credenciales_completas:
    st.sidebar.warning("Completa todos los campos de credenciales para poder consultar.")

consultar = st.sidebar.button("🔄 Consultar datos y entrenar modelo",
                               use_container_width=True, disabled=not credenciales_completas)

# ────────────────────────────────────────────────────────────────────────────
# Cuerpo principal
# ────────────────────────────────────────────────────────────────────────────
st.title("🌡️ Predictor de Sensación Térmica")
st.markdown(
    "Datos reales de temperatura y humedad tomados por un sensor IoT, "
    "usados para entrenar un modelo de regresión lineal que predice la sensación térmica."
)

if consultar:
    error_conexion = None
    with st.spinner("Consultando InfluxDB..."):
        try:
            df_crudo = obtener_datos_crudos(influx_url, influx_token, influx_org,
                                             influx_bucket, influx_measurement, horas)
        except Exception as e:
            error_conexion = str(e)
            df_crudo = pd.DataFrame()

    if error_conexion:
        st.error(f"No se pudo conectar a InfluxDB. Revisa tus credenciales.\n\nDetalle: {error_conexion}")
    elif df_crudo.empty:
        st.error("No se encontraron datos para el rango de horas seleccionado.")
    else:
        df = preparar_datos(df_crudo)
        if df.empty:
            st.error("Los datos consultados no permitieron preparar una serie válida (todo quedó en NaN).")
        else:
            st.session_state["df_crudo"] = df_crudo
            st.session_state["df"] = df
            with st.spinner("Entrenando modelo..."):
                modelo, metricas = entrenar_modelo(df)
            st.session_state["modelo"] = modelo
            st.session_state["metricas"] = metricas

# ────────────────────────────────────────────────────────────────────────────
# Panel con pestañas (solo si ya hay una consulta en sesión)
# ────────────────────────────────────────────────────────────────────────────
if "df" in st.session_state:
    df_crudo = st.session_state["df_crudo"]
    df = st.session_state["df"]
    modelo = st.session_state["modelo"]
    metricas = st.session_state["metricas"]
    ultima = df.iloc[-1]

    st.success(f"{len(df)} lecturas listas — última: {df.index[-1].strftime('%Y-%m-%d %H:%M:%S')}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Temperatura", f"{ultima['temperatura']:.1f} °C")
    col2.metric("Humedad", f"{ultima['humedad']:.1f} %")
    col3.metric("Sensación Térmica (real)", f"{ultima['sensacion_termica']:.1f} °C")

    tab_stats, tab_prep, tab_modelo, tab_pred = st.tabs(
        ["📊 Estadísticos", "🧹 Preparación de datos", "📈 Análisis del modelo", "🔮 Predicción"]
    )

    # ── Pestaña: Estadísticos ────────────────────────────────────────────────
    with tab_stats:
        st.subheader("Histórico de lecturas")
        
        # Gráfico comparativo general
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(df.index, df["temperatura"], label="Temperatura (°C)", color="tab:red")
        ax.plot(df.index, df["humedad"], label="Humedad (%)", color="tab:blue")
        ax.plot(df.index, df["sensacion_termica"], label="Sensación Térmica (°C)", color="tab:green", alpha=0.7)
        ax.legend(loc="upper right", fontsize=8)
        ax.set_xlabel("Tiempo")
        fig.autofmt_xdate()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        # Gráfico individual de Humedad (Sección 5)
        st.subheader("Análisis de Humedad en el tiempo (Sección 5)")
        fig_h, ax_h = plt.subplots(figsize=(8, 3))
        ax_h.plot(df.index, df["humedad"], color="tab:blue", label="Humedad (%)")
        ax_h.set_ylabel("Humedad (%)")
        ax_h.set_xlabel("Tiempo")
        ax_h.set_title("Comportamiento de la Humedad Relativa")
        ax_h.grid(True, linestyle="--", alpha=0.5)
        fig_h.autofmt_xdate()
        st.pyplot(fig_h, use_container_width=True)
        plt.close(fig_h)

    # ── Pestaña: Preparación de datos ────────────────────────────────────────
    with tab_prep:
        st.subheader("1. Tipos de datos")
        st.caption("Verificación de que el índice sea fecha/hora y las variables sean numéricas.")
        tipos = pd.DataFrame({"Tipo de dato": df_crudo.dtypes.astype(str)})
        st.dataframe(tipos, use_container_width=True)

        st.subheader("2. Detección de datos faltantes")
        faltantes = df_crudo.isna().sum()
        porcentaje = (df_crudo.isna().mean() * 100).round(2)
        resumen_faltantes = pd.DataFrame({"Valores Faltantes": faltantes, "Porcentaje (%)": porcentaje})
        st.dataframe(resumen_faltantes, use_container_width=True)

        st.subheader("3. Efecto de la interpolación")
        if df_crudo.isna().any().any():
            col_referencia = st.selectbox(
                "Selecciona la variable a inspeccionar:",
                COLUMNAS,
                index=1,
                key="prep_select_var"
            )
            color_map = {"temperatura": "tab:red", "humedad": "tab:blue", "sensacion_termica": "tab:green"}
            
            fig, ax = plt.subplots(figsize=(8, 3))
            ax.plot(df_crudo.index, df_crudo[col_referencia], marker="o", linestyle="none",
                    color="gray", alpha=0.6, label="Datos originales (con huecos)")
            ax.plot(df.index, df[col_referencia], color=color_map.get(col_referencia, "tab:blue"),
                    alpha=0.8, label="Serie interpolada")
            ax.legend(fontsize=8)
            ax.set_title(f"Interpolación aplicada sobre {col_referencia}")
            fig.autofmt_xdate()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        else:
            st.info("ℹ️ No se encontraron datos faltantes en esta consulta. La serie está completa y no requirió interpolación.")

        st.subheader("4. Valores atípicos (outliers, regla IQR)")
        hay_outliers = False
        for col in COLUMNAS:
            outliers = detectar_outliers_iqr(df[col])
            if not outliers.empty:
                hay_outliers = True
                st.markdown(f"**{col}** — {len(outliers)} outlier(s):")
                st.dataframe(outliers.rename("Valor"), use_container_width=True)
        if not hay_outliers:
            st.info("ℹ️ No se detectaron outliers según la regla del rango intercuartílico (IQR).")

    # ── Pestaña: Análisis del modelo ─────────────────────────────────────────
    with tab_modelo:
        st.subheader("Relación entre variables (gráfico 3D)")
        fig = plt.figure(figsize=(6, 5))
        ax = fig.add_subplot(projection="3d")
        ax.scatter(df["temperatura"], df["humedad"], df["sensacion_termica"], color="green")
        ax.set_xlabel("Temperatura (°C)")
        ax.set_ylabel("Humedad (%)")
        ax.set_zlabel("Sens. Térmica (°C)")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        st.subheader("Ecuación del modelo")
        beta0 = modelo.intercept_
        beta1, beta2 = modelo.coef_
        st.latex(
            r"\text{sensación\_térmica} = %.3f + %.3f \cdot \text{temperatura} + %.3f \cdot \text{humedad}"
            % (beta0, beta1, beta2)
        )
        st.caption("Coeficientes obtenidos por mínimos cuadrados sobre el conjunto de entrenamiento (70% de los datos).")

        st.subheader("Desempeño del modelo")
        m1, m2, m3 = st.columns(3)
        m1.metric("MAE", f"{metricas['mae']:.2f} °C")
        m2.metric("RMSE", f"{metricas['rmse']:.2f} °C")
        m3.metric("R²", f"{metricas['r2']:.3f}")
        st.caption("Calculadas sobre un conjunto de prueba (30% de los datos), no visto durante el entrenamiento.")

    # ── Pestaña: Predicción ───────────────────────────────────────────────────
    with tab_pred:
        st.subheader("Predicción con coeficientes del modelo")
        st.markdown(
            "Los coeficientes se cargan automáticamente a partir del modelo entrenado con los datos de InfluxDB, "
            "pero puedes ajustarlos manualmente si deseas probar otros valores."
        )

        # Carga por defecto de los valores calculados por scikit-learn
        beta0_def = float(modelo.intercept_)
        beta1_def = float(modelo.coef_[0])
        beta2_def = float(modelo.coef_[1])

        bc1, bc2, bc3 = st.columns(3)
        beta0_input = bc1.number_input("β₀ (intercepto)", value=beta0_def, format="%.4f")
        beta1_input = bc2.number_input("β₁ (coef. temperatura)", value=beta1_def, format="%.4f")
        beta2_input = bc3.number_input("β₂ (coef. humedad)", value=beta2_def, format="%.4f")

        pc1, pc2 = st.columns(2)
        temp_manual = pc1.number_input("Temperatura (°C)", value=float(round(ultima["temperatura"], 1)),
                                        step=0.1, key="temp_manual")
        hum_manual = pc2.number_input("Humedad (%)", value=float(round(ultima["humedad"], 1)),
                                       step=0.1, key="hum_manual")

        if st.button("🔮 Predecir sensación térmica", use_container_width=True):
            prediccion_manual = beta0_input + beta1_input * temp_manual + beta2_input * hum_manual
            st.success(f"Sensación térmica estimada: **{prediccion_manual:.2f} °C**")
