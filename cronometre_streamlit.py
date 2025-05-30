import streamlit as st
from math import sqrt

# === PARÀMETRES DELS TRAMS ===

TRAMS = {
    "Poble-Riu": {
        "tipo": "MRU",  "v": 20,    "rang": (0.0,   120.0)
    },
    "Riu-Mines": {
        "tipo": "MRUA", "vo": 20,   "a": 0.16,   "rang": (120.0, 130.0)
    },
    "Mines-Poble": {
        "tipo": "MRUA", "vo": 60,  "a": -0.02,  "rang": (130.0, 220.0)
    },
}

TIEMPO_VUELTA = 6000 + 250 + 2000  # 2h 17min 30s en segons

# === FUNCIONS ===

def segons_a_hms(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    return f"{h:02d} h : {m:02d} m : {s:02d} s"

def trams_containment(km):
    return [nom for nom, P in TRAMS.items() if P["rang"][0] <= km <= P["rang"][1]]

def calcula_temps(tram_sel, ki, kf):
    # Cas especial: mateixa posició
    if ki == kf:
        membership = trams_containment(ki)
        if not membership:
            raise ValueError("Els km han d’estar entre 0 i 220.")
        if tram_sel not in membership:
            suggerit = membership[0]
            raise ValueError(f"Per fer aquesta mesura cal que viatgi al tram «{suggerit}»")
        return segons_a_hms(TIEMPO_VUELTA)

    # Cas especial: volta completa
    if (ki == 0.0 and kf == 220.0) or (ki == 220.0 and kf == 0.0):
        membership = trams_containment(0.0)
        if not membership:
            raise ValueError("Els km han d’estar entre 0 i 220.")
        if tram_sel not in membership:
            suggerit = membership[0]
            raise ValueError(f"Per fer aquesta mesura cal que viatgi al tram «{suggerit}»")
        return segons_a_hms(TIEMPO_VUELTA)

    # Cas normal
    m_ki = trams_containment(ki)
    m_kf = trams_containment(kf)
    if not m_ki or not m_kf:
        raise ValueError("Els km han d’estar entre 0 i 220.")

    common = set(m_ki) & set(m_kf)
    if not common:
        raise ValueError("Els punts no són visibles des del mateix tram.")
    tram_real = common.pop()
    if tram_real != tram_sel:
        raise ValueError(f"Per fer aquesta mesura cal que viatgi al tram «{tram_real}»")
    if tram_real == "Mines-Poble":
        raise ValueError("La neblina impedeix veure aquest tram complet.")

    P = TRAMS[tram_real]
    lo, hi = min(ki, kf), max(ki, kf)

    if P["tipo"] == "MRU":
        s = (hi - lo) * 1000.0
        t = s / P["v"]
    else:
        vo, a = P["vo"], P["a"]
        x0 = P["rang"][0]

        def temps_absolut(pos_km):
            d = (pos_km - x0) * 1000  # metres des de l’inici del tram
            discriminant = vo**2 + 2*a*d
            if discriminant < 0:
                raise ValueError("No hi ha solució real per a aquests paràmetres.")
            t1 = (-vo + sqrt(discriminant)) / a
            t2 = (-vo - sqrt(discriminant)) / a
            t = max(t1, t2)
            if t < 0:
                raise ValueError("Temps negatiu.")
            return t

        t = abs(temps_absolut(kf) - temps_absolut(ki))

    return segons_a_hms(t)

# === INTERFÍCIE STREAMLIT ===

st.title("⏱️ Cronòmetre")
st.markdown("Útil per calcular el temps segons el tram en el que ens trobem i les posicions quilomètriques des d'on començem a comptar fins on parem el cronòmetre.")

tram = st.selectbox("Des d'on estàs utilitzant el cronòmetre?", list(TRAMS.keys()))
ki = st.number_input("Kilòmetre Inici", min_value=0.0, max_value=220.0, step=0.1)
kf = st.number_input("Kilòmetre Final", min_value=0.0, max_value=220.0, step=0.1)

if st.button("Calcula Temps"):
    try:
        temps = calcula_temps(tram, ki, kf)
        st.success(f"Temps mesurat: **{temps}**")
    except ValueError as e:
        st.error(str(e))
