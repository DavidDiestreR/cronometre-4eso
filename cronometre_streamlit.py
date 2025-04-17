import streamlit as st

# Paràmetres de cada tram (quilòmetres i m/s²)
TRAMS = {
    "Tram Poble-Riu": {
        "tipo": "MRU",  "v": 25.0,    "rang": (0.0,   120.0)
    },
    "Tram Riu-Muntanya": {
        "tipo": "MRUA", "vo": 25.0,   "a": 1/18,   "rang": (120.0, 130.0)
    },
    "Tram Muntanya-Poble": {
        "tipo": "MRUA", "vo": 125/3,  "a": -1/16,  "rang": (130.0, 220.0)
    },
}

TIEMPO_VUELTA = 4800 + 300 + 2700

def segons_a_hms(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def trams_containment(km):
    return [nom for nom, P in TRAMS.items() if P["rang"][0] <= km <= P["rang"][1]]

def calcula_temps(tram_sel, ki, kf):
    if ki == kf:
        membership = trams_containment(ki)
        if not membership:
            raise ValueError("Els km han d’estar entre 0 i 220.")
        if tram_sel not in membership:
            raise ValueError(f"Per fer aquesta mesura cal que viatgi al tram «{membership[0]}»")
        return segons_a_hms(TIEMPO_VUELTA)

    m_ki = trams_containment(ki)
    m_kf = trams_containment(kf)
    if not m_ki or not m_kf:
        raise ValueError("Els km han d’estar entre 0 i 220.")

    common = set(m_ki) & set(m_kf)
    if not common:
        raise ValueError(
            "Estàs intentant mesurar el temps entre dos punts de diferents trams, "
            "fet que fa impossible trobar un lloc on es vegin tots dos punts alhora"
        )

    tram_real = common.pop()
    if tram_real != tram_sel:
        raise ValueError(f"Per fer aquesta mesura cal que viatgi al tram «{tram_real}»")
    if tram_real == "Tram Muntanya-Poble":
        raise ValueError("La neblina impedeix veure el tren en tots dos punts alhora")

    lo, hi = min(ki, kf), max(ki, kf)
    s = (hi - lo) * 1000.0
    P = TRAMS[tram_real]

    if P["tipo"] == "MRU":
        t = s / P["v"]
    else:
        vo, a = P["vo"], P["a"]
        delta = vo**2 + 2*a*s
        if delta < 0:
            raise ValueError("No hi ha solució real per a aquests paràmetres.")
        t1 = (-vo + delta**0.5) / a
        t2 = (-vo - delta**0.5) / a
        t = max(t1, t2)
        if t <= 0:
            raise ValueError("Temps negatiu: revisa les dades.")

    return segons_a_hms(t)


# === GUI Streamlit ===
st.title("⏱️ Cronòmetre – Física 4t ESO")
st.markdown("Calculadora de temps segons el tram i posicions quilomètriques.")

tram = st.selectbox("Des d'on estàs utilitzant el cronòmetre?", list(TRAMS.keys()))
ki = st.number_input("Kilòmetre Inici", min_value=0.0, max_value=220.0, step=0.1)
kf = st.number_input("Kilòmetre Final", min_value=0.0, max_value=220.0, step=0.1)

if st.button("Calcula"):
    try:
        temps = calcula_temps(tram, ki, kf)
        st.success(f"Temps mesurat: **{temps}**")
    except ValueError as e:
        st.error(str(e))
