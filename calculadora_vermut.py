# app.py  – Calculadora de mezcla para vermut (con % de vino)
import streamlit as st

# ─────────────────────────────────────────────────────────────
# ► CONSTANTES
DENS_SYRUP_2TO1 = 1.47     # g/mL  (almíbar 2:1 a 20 °C)
SYRUP_VOL_PER_G_SUGAR = (1.5 / DENS_SYRUP_2TO1) / 1000   # L por gramo de azúcar ≈ 0.00102 L

SUGAR_CLASSES = [
    (0,   30,  "extra seco"),
    (30,  50,  "seco"),
    (50,  90,  "semi-seco"),
    (90, 130,  "semi-dulce"),
    (130,180,  "dulce"),
    (180,1e9,  "extra dulce"),
]
def sugar_label(g_per_L: float) -> str:
    for low, high, name in SUGAR_CLASSES:
        if low <= g_per_L < high:
            return name
    return "sin clasificar"

# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Mezcla para Vermut", page_icon="🍷")

# Banner superior
st.markdown(
    """
    <div style="background-color:#f5f5f5;padding:0.6rem 1rem;border-radius:6px;">
        <a href="https://www.nosoynormalcerveceria.com" target="_blank"
           style="text-decoration:none;color:#0066cc;font-weight:600;">
           Mirá más calculadoras para productores de bebidas en www.nosoynormalcerveceria.com
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

st.title("🍷 Calculadora de Mezcla para Vermut")

st.markdown(
    "Completá los datos, presioná **Calcular vermut** y obtené volumen final, "
    "graduación alcohólica, dulzor y % de vino."
)

# ─── Selector de unidades ───────────────────────────────────
unidad = st.radio("Unidad de los volúmenes", ("Mililitros", "Litros"), horizontal=True)
factor_in  = 1 if unidad == "Mililitros" else 1000   # → mL
factor_out = 1 if unidad == "Mililitros" else 1/1000 # ← para mostrar
suf = "mL" if unidad == "Mililitros" else "L"

# ─── Entradas ───────────────────────────────────────────────
st.header("1) Vino base")
V_vino   = st.number_input(f"Volumen de vino ({suf})", 0.0, value=750.0, step=0.1)
ABV_vino = st.number_input("Graduación alcohólica del vino (%)", 0.0, 20.0, 12.0, 0.1)

st.header("2) Macerado de hierbas")
V_mac  = st.number_input(f"Volumen de macerado ({suf})", 0.0, value=120.0, step=0.1)
ABV_mac = st.number_input("Graduación alcohólica del macerado (%)", 0.0, 96.0, 60.0, 0.1)

st.header("3) Solución hidroalcohólica para reforzar alcohol")
V_sol  = st.number_input(f"Volumen de solución ({suf})", 0.0, value=10.0, step=0.1)
ABV_sol = st.number_input("Graduación alcohólica de la solución (%)", 0.0, 96.0, 96.0, 0.1)

st.header("4) Azúcar (se considerará para el volumen un almíbar 1:1)")
sugar_g = st.number_input("Azúcar (g)", 0.0, value=100.0, step=10.0)

# ─── Cálculos ───────────────────────────────────────────────
if st.button("Calcular vermut"):
    # Volúmenes a mL
    V_vino_mL = V_vino * factor_in
    V_mac_mL  = V_mac  * factor_in
    V_sol_mL  = V_sol  * factor_in

    # Volumen almíbar
    V_syr_L  = sugar_g * SYRUP_VOL_PER_G_SUGAR
    V_syr_mL = V_syr_L * 1000

    # Volumen total
    V_total_mL = V_vino_mL + V_mac_mL + V_sol_mL + V_syr_mL

    # Etanol total
    EtOH_mL = (
        V_vino_mL * ABV_vino/100 +
        V_mac_mL  * ABV_mac /100 +
        V_sol_mL  * ABV_sol /100
    )
    ABV_final = (EtOH_mL / V_total_mL) * 100 if V_total_mL else 0

    # Azúcar g/L y Brix
    V_total_L = V_total_mL / 1000
    sugar_g_L = sugar_g / V_total_L if V_total_L else 0
    brix = sugar_g_L / 10
    etiqueta = sugar_label(sugar_g_L)

    # Porcentaje de vino en el vermut
    perc_vino = (V_vino_mL / V_total_mL) * 100 if V_total_mL else 0

    # ─── Resultados ────────────────────────────────────────
    st.subheader("Resultado")
    st.write(f"**Volumen final:** `{V_total_mL * factor_out:.2f} {suf}`")
    st.write(f"**Graduación alcohólica final:** `{ABV_final:.2f} % v/v`")
    st.write(f"**Azúcar:** `{brix:.1f} °Bx`  → *{etiqueta}* ({sugar_g_L:.0f} g/L)")
    st.write(f"**Vino en la mezcla:** `{perc_vino:.1f} %`")

    if perc_vino < 75:
        st.warning(
            "⚠️ En muchas legislaciones, el vermut no se considera tal si no contiene "
            "al menos un **75 % de vino** en su composición."
        )

    st.caption(
        "Almíbar 1:1 asumido con densidad ≈ 1,33 g mL⁻¹. Sin corrección de contracción "
        "ni densidad real de la mezcla."
    )
