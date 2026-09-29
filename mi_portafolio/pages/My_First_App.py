import streamlit as st

st.title("Mi primera app de streamlit")

st.subheader("Este es un encabezado")

if st.button("▶️ Ejecutar benchmark", type="primary"):
        # 1. CORRECCIÓN: Desempaquetar los 3 valores (agregando fds_b)
        temps_b, hums_b, fds_b = generar_datos(n_bench)

        repeticiones_loop = 1
        repeticiones_vec = 20

        inicio = time.perf_counter()
        for _ in range(repeticiones_loop):
            # 2. CORRECCIÓN: Agregar fds_b a la llamada de la función
            alarma_logica_loop(temps_b, hums_b, fds_b, temp_umbral_b, hum_umbral_b)
        t_loop = (time.perf_counter() - inicio) / repeticiones_loop

        inicio = time.perf_counter()
        for _ in range(repeticiones_vec):
            # 3. CORRECCIÓN: Agregar fds_b a la llamada de la función
            alarma_logica_vectorizada(temps_b, hums_b, fds_b, temp_umbral_b, hum_umbral_b)
        t_vec = (time.perf_counter() - inicio) / repeticiones_vec

        col1, col2, col3 = st.columns(3)
        col1.metric("Tiempo con loop", f"{t_loop*1000:.3f} ms")
        col2.metric("Tiempo con NumPy", f"{t_vec*1000:.3f} ms")

        if t_vec > 0:
            speedup = t_loop / t_vec
            col3.metric("NumPy es más rápido por", f"{speedup:,.0f}x")
        else:
            col3.metric("NumPy es más rápido por", "demasiado rápido para medir")

        st.caption(
            f"Tiempo con loop promediado sobre {repeticiones_loop} corrida(s); "
            f"tiempo con NumPy promediado sobre {repeticiones_vec} corridas, "
            "para reducir el ruido de la medición."
        )

        fig3, ax3 = plt.subplots(figsize=(5, 3.5))
        ax3.bar(["Loop (Python)", "NumPy (vectorizado)"],
                [t_loop * 1000, t_vec * 1000],
                color=["indianred", "seagreen"])
        ax3.set_ylabel("Tiempo (milisegundos)")
        ax3.grid(alpha=0.3, axis="y")
        st.pyplot(fig3)
