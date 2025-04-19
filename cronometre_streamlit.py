import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from math import sqrt

# === DADES DEL RECORREGUT ===
TRAMS = {
    "Tram Poble-Riu": {
        "tipo": "MRU",  "v": 25.0,    "rang": (0.0,   120.0)
    },
    "Tram Riu-Muntanya": {
        "tipo": "MRUA", "vo": 25.0,   "a": 1/18,   "rang": (120.0, 130.0)
    },
    "Tram Muntanya-Poble": {
        "tipo": "MRUA", "vo": 125/3,  "a": -1/162,  "rang": (130.0, 220.0)
    },
}

TIEMPO_VUELTA = 4800 + 300 + 2700  # segons

def segons_a_hms(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def trams_containment(km):
    return [nom for nom, P in TRAMS.items() if P["rang"][0] <= km <= P["rang"][1]]

def calcula_temps(tram_sel, ki, kf):
    if ki == kf:
        return segons_a_hms(0)

    m_ki = trams_containment(ki)
    m_kf = trams_containment(kf)
    if not m_ki or not m_kf:
        raise ValueError("Els km han d’estar entre 0 i 220.")
    common = set(m_ki) & set(m_kf)
    if not common:
        raise ValueError("Els punts no són visibles des del mateix tram.")
    tram_real = common.pop()
    if tram_real != tram_sel:
        raise ValueError(f"Mesura incorrecta: cal triar el tram «{tram_real}»")
    if tram_real == "Tram Muntanya-Poble":
        raise ValueError("La neblina impedeix veure aquest tram complet.")

    lo, hi = min(ki, kf), max(ki, kf)
    P = TRAMS[tram_real]

    if P["tipo"] == "MRU":
        t = (hi - lo) * 1000 / P["v"]
    else:
        vo, a = P["vo"], P["a"]

        def temps_absolut(pos):
            d = (pos - P["rang"][0]) * 1000  # m des de l'inici del tram
            discriminant = vo**2 + 2*a*d
            if discriminant < 0:
                raise ValueError("No hi ha solució real per a aquests paràmetres.")
            t = (-vo + sqrt(discriminant)) / a
            if t < 0:
                t = (-vo - sqrt(discriminant)) / a
            if t < 0:
                raise ValueError("Temps negatiu: revisa les dades.")
            return t

        t = abs(temps_absolut(kf) - temps_absolut(ki))

    return segons_a_hms(t)

# === GUI Streamlit ===
st.title("\u23f1\ufe0f Cron\u00f2metre")
st.markdown("Calculadora de temps segons el tram i posicions quilom\u00e8triques.")

tram = st.selectbox("Des d'on est\u00e0s utilitzant el cron\u00f2metre?", list(TRAMS.keys()))
ki = st.number_input("Kil\u00f2metre Inici", min_value=0.0, max_value=220.0, step=0.1)
kf = st.number_input("Kil\u00f2metre Final", min_value=0.0, max_value=220.0, step=0.1)

if st.button("Calcula"):
    try:
        temps = calcula_temps(tram, ki, kf)
        st.success(f"Temps mesurat: **{temps}**")
    except ValueError as e:
        st.error(str(e))

# === GR\u00c0FIQUES ===
def calcula_temps_brut(vo, a, s):
    A = 0.5 * a
    B = vo
    C = -s
    discriminant = B**2 - 4*A*C
    return (-B + sqrt(discriminant)) / (2*A)

def velocitat_vs_posicio():
    x_vals_totals = []
    v_vals_totals = []

    # MRU
    x_mru = np.linspace(0, 120, 200)
    v_mru = np.full_like(x_mru, TRAMS["Tram Poble-Riu"]["v"])
    x_vals_totals.extend(x_mru)
    v_vals_totals.extend(v_mru)

    # MRUA positiva
    vo_rm, a_rm = TRAMS["Tram Riu-Muntanya"]["vo"], TRAMS["Tram Riu-Muntanya"]["a"]
    t_rm = np.linspace(0, calcula_temps_brut(vo_rm, a_rm, 10_000), 100)
    x_rm = vo_rm * t_rm + 0.5 * a_rm * t_rm**2
    v_rm = vo_rm + a_rm * t_rm
    x_vals_totals.extend(120 + x_rm / 1000)
    v_vals_totals.extend(v_rm)

    # MRUA negativa
    vo_mp, a_mp = TRAMS["Tram Muntanya-Poble"]["vo"], TRAMS["Tram Muntanya-Poble"]["a"]
    t_mp = np.linspace(0, calcula_temps_brut(vo_mp, a_mp, 90_000), 100)
    x_mp = vo_mp * t_mp + 0.5 * a_mp * t_mp**2
    v_mp = vo_mp + a_mp * t_mp
    x_vals_totals.extend(130 + x_mp / 1000)
    v_vals_totals.extend(v_mp)

    return x_vals_totals, v_vals_totals

def velocitat_vs_temps():
    t_vals = []
    v_vals = []

    # MRU
    x_mru = np.linspace(0, 120, 200)
    t_mru = (x_mru * 1000) / TRAMS["Tram Poble-Riu"]["v"]
    v_mru = np.full_like(t_mru, TRAMS["Tram Poble-Riu"]["v"])
    t_vals.extend(t_mru)
    v_vals.extend(v_mru)

    # MRUA positiva
    vo_rm, a_rm = TRAMS["Tram Riu-Muntanya"]["vo"], TRAMS["Tram Riu-Muntanya"]["a"]
    t_rm = np.linspace(0, calcula_temps_brut(vo_rm, a_rm, 10_000), 100)
    v_rm = vo_rm + a_rm * t_rm
    t_vals.extend(t_rm + t_vals[-1])
    v_vals.extend(v_rm)

    # MRUA negativa
    vo_mp, a_mp = TRAMS["Tram Muntanya-Poble"]["vo"], TRAMS["Tram Muntanya-Poble"]["a"]
    t_mp = np.linspace(0, calcula_temps_brut(vo_mp, a_mp, 90_000), 100)
    v_mp = vo_mp + a_mp * t_mp
    t_vals.extend(t_mp + t_vals[-1])
    v_vals.extend(v_mp)

    return t_vals, v_vals

# Mostrar gràfiques
x_graph, v_x_graph = velocitat_vs_posicio()
t_graph, v_t_graph = velocitat_vs_temps()

st.subheader("Gràfica de Velocitat vs Posició (v-x)")
fig1, ax1 = plt.subplots()
ax1.plot(x_graph, v_x_graph, label="v(x)")
ax1.set_xlabel("Posició (km)")
ax1.set_ylabel("Velocitat (m/s)")
ax1.grid(True)
ax1.legend()
st.pyplot(fig1)

st.subheader("Gràfica de Velocitat vs Temps (v-t)")
fig2, ax2 = plt.subplots()
ax2.plot(t_graph, v_t_graph, label="v(t)", color="orange")
ax2.set_xlabel("Temps (s)")
ax2.set_ylabel("Velocitat (m/s)")
ax2.grid(True)
ax2.legend()
st.pyplot(fig2)
