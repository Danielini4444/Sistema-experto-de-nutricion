"""
Sistema Experto de Nutricion (Mexico) — Interfaz Grafica
Base de conocimiento: base_conocimiento_nutricion.json
Fuentes: ENSANUT, NOM-043-SSA2-2012, SMAE 4a ed., FAO/OMS, DRI (IOM)
"""

import json
import random
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# ══════════════════════════════════════════════════════════════════════════════
#  CARGA DE BASE DE CONOCIMIENTO
# ══════════════════════════════════════════════════════════════════════════════
def cargar_base_conocimiento():
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "base_conocimiento_nutricion.json")
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)

BC = cargar_base_conocimiento()

# ══════════════════════════════════════════════════════════════════════════════
#  COLORES Y ESTILOS
# ══════════════════════════════════════════════════════════════════════════════
COLOR_FONDO        = "#F5F7F0"
COLOR_PANEL        = "#FFFFFF"
COLOR_PRIMARIO     = "#2E7D32"
COLOR_PRIMARIO_H   = "#388E3C"
COLOR_SECUNDARIO   = "#F57F17"
COLOR_ACENTO       = "#1565C0"
COLOR_ALERTA       = "#C62828"
COLOR_TEXTO        = "#212121"
COLOR_TEXTO_SEC    = "#616161"
COLOR_BORDE        = "#C8E6C9"
COLOR_INPUT_BG     = "#FAFAFA"
COLOR_SIDEBAR      = "#E8F5E9"
COLOR_SIDEBAR_ACT  = "#C8E6C9"
COLOR_VERDE_CLARO  = "#A5D6A7"
COLOR_AMARILLO_C   = "#FFF9C4"
COLOR_ROJO_CLARO   = "#FFCDD2"

FONT_TITULO   = ("Segoe UI", 16, "bold")
FONT_SUBTIT   = ("Segoe UI", 13, "bold")
FONT_NORMAL   = ("Segoe UI", 10)
FONT_SMALL    = ("Segoe UI", 9)
FONT_MONO     = ("Consolas", 10)
FONT_LABEL    = ("Segoe UI", 10, "bold")
FONT_GRANDE   = ("Segoe UI", 22, "bold")

# ══════════════════════════════════════════════════════════════════════════════
#  MOTOR DE INFERENCIA  (logica pura, sin GUI)
# ══════════════════════════════════════════════════════════════════════════════
ALIMENTOS_POR_GRUPO = {
    "verduras": [
        ("Nopales cocidos", "1 taza"), ("Brocoli cocido", "1/2 taza"),
        ("Calabaza cocida", "1/2 taza"), ("Chayote cocido", "1/2 taza"),
        ("Espinacas cocidas", "1/2 taza"), ("Jitomate crudo", "1 pieza"),
        ("Lechuga", "1 taza"), ("Zanahoria rallada", "1/2 taza"),
        ("Chile poblano", "1 pieza"), ("Flor de calabaza", "1 taza"),
        ("Quelites/Verdolagas", "1/2 taza"), ("Ejotes cocidos", "1/2 taza"),
    ],
    "frutas": [
        ("Guayaba", "2 piezas"), ("Papaya picada", "1 taza"),
        ("Manzana", "1 pieza mediana"), ("Platano", "1/2 pieza"),
        ("Naranja", "1 pieza"), ("Mango", "1/2 pieza"),
        ("Melon picado", "1 taza"), ("Fresa", "1 taza"),
        ("Mandarina", "2 piezas"),
    ],
    "cereales": [
        ("Tortilla de maiz", "1 pieza"), ("Arroz cocido", "1/3 taza"),
        ("Avena en hojuelas", "1/3 taza"), ("Pan integral", "1 rebanada"),
        ("Bolillo sin migajon", "1/2 pieza"), ("Elote cocido", "1/2 pieza"),
        ("Camote cocido", "1/3 taza"), ("Pasta cocida", "1/2 taza"),
        ("Amaranto", "1/4 taza"),
    ],
    "leguminosas": [
        ("Frijol negro cocido", "1/2 taza"), ("Lenteja cocida", "1/2 taza"),
        ("Garbanzo cocido", "1/2 taza"), ("Habas cocidas", "1/2 taza"),
        ("Alubia cocida", "1/2 taza"),
    ],
    "aoa": [
        ("Pechuga de pollo s/piel", "30 g"), ("Atun en agua", "30 g"),
        ("Huevo entero", "1 pieza"), ("Queso panela", "40 g"),
        ("Sardina en aceite", "30 g"), ("Carne de res magra", "30 g"),
        ("Pescado blanco", "30 g"),
    ],
    "aoa_vegetariano": [
        ("Huevo entero", "1 pieza"), ("Queso panela", "40 g"),
        ("Queso cottage", "1/4 taza"), ("Yogurt griego natural", "3/4 taza"),
    ],
    "leche": [
        ("Leche semidescremada", "1 taza (240 mL)"),
        ("Yogurt natural", "1 taza"),
        ("Leche descremada", "1 taza (240 mL)"),
    ],
    "aceites": [
        ("Aceite de oliva", "1 cucharadita"), ("Aguacate", "1/3 pieza"),
        ("Almendras", "14 piezas"), ("Nuez", "4 mitades"),
        ("Cacahuate", "10 piezas"), ("Semillas de chia", "1 cucharada"),
    ],
    "azucares": [
        ("Miel de abeja", "1 cucharadita"),
        ("Azucar mascabado", "2 cucharaditas"),
    ],
}

MAPA_OBJETIVO = {
    "Perdida de grasa":                  "Perdida de grasa",
    "Mantenimiento":                     "Mantenimiento",
    "Ganancia muscular":                 "Ganancia muscular",
    "Rendimiento deportivo (resistencia)": "Rendimiento deportivo (resistencia)",
    "Control glucemico (diabetes/prediabetes)": "Control glucemico (diabetes/prediabetes)",
}

OBJETIVOS_KEYS = {
    "Perdida de grasa": "perdida",
    "Mantenimiento": "mantenimiento",
    "Ganancia muscular": "ganancia",
    "Rendimiento deportivo (resistencia)": "rendimiento",
    "Control glucemico (diabetes/prediabetes)": "control_glucemico",
}

def _regla_objetivo_bc(nombre_objetivo):
    """Busca la regla en la BC mapeando texto sin tildes."""
    reglas = BC["reglas_sistema_experto"]["reglas_distribucion_por_objetivo"]
    mapa = {
        "Perdida de grasa": "Pérdida de grasa",
        "Mantenimiento": "Mantenimiento",
        "Ganancia muscular": "Ganancia muscular",
        "Rendimiento deportivo (resistencia)": "Rendimiento deportivo (resistencia)",
        "Control glucemico (diabetes/prediabetes)": "Control glucémico (diabetes/prediabetes)",
    }
    nombre_bc = mapa.get(nombre_objetivo, "Mantenimiento")
    for r in reglas:
        if r["objetivo"] == nombre_bc:
            return r
    return reglas[1]


def evaluar_condicion_imc(imc, condicion):
    cond = condicion.replace("IMC", "").strip()
    if cond.startswith("< "):
        return imc < float(cond[2:])
    elif cond.startswith(">=") or cond.startswith("\u2265"):
        return imc >= float(cond[1:].replace("=", "").strip())
    elif "\u2013" in cond:
        partes = cond.split("\u2013")
        return float(partes[0]) <= imc <= float(partes[1])
    elif "-" in cond:
        partes = cond.split("-")
        try:
            return float(partes[0]) <= imc <= float(partes[1])
        except ValueError:
            return False
    return False


def motor_inferencia(sexo, edad, peso, talla_cm, actividad, objetivo,
                     condiciones, trimestre, preferencia, alergias_lista):
    """Ejecuta toda la cadena de inferencia y devuelve un dict con resultados."""
    datos = {}
    talla_m = talla_cm / 100

    # 1 — IMC
    imc = round(peso / (talla_m ** 2), 1)
    clasificacion_imc = "Normal"
    accion_imc = ""
    for regla in BC["reglas_sistema_experto"]["reglas_clasificacion_IMC"]:
        if evaluar_condicion_imc(imc, regla["condicion"]):
            clasificacion_imc = regla["clasificacion"]
            accion_imc = regla["accion"]
            break

    # 2 — Peso ideal (Lorentz) y corregido
    if sexo == "Masculino":
        peso_ideal = talla_cm - 100 - ((talla_cm - 150) / 4)
    else:
        peso_ideal = talla_cm - 100 - ((talla_cm - 150) / 2.5)
    peso_ideal = round(max(peso_ideal, 40), 1)

    if imc >= 30:
        peso_calc = round((peso - peso_ideal) * 0.25 + peso_ideal, 1)
        usa_corregido = True
    else:
        peso_calc = peso
        usa_corregido = False

    # 3 — GEB
    sexo_key_fa = "hombres" if sexo == "Masculino" else "mujeres"
    if imc >= 25:
        if sexo == "Masculino":
            geb = (10 * peso_calc) + (6.25 * talla_cm) - (5 * edad) + 5
        else:
            geb = (10 * peso_calc) + (6.25 * talla_cm) - (5 * edad) - 161
        formula_geb = "Mifflin-St Jeor"
    else:
        if sexo == "Masculino":
            geb = 66.47 + (13.75 * peso_calc) + (5.0 * talla_cm) - (6.74 * edad)
        else:
            geb = 655.1 + (9.56 * peso_calc) + (1.85 * talla_cm) - (4.68 * edad)
        formula_geb = "Harris-Benedict"
    geb = round(geb, 0)

    # 4 — GET
    act_map = {"Sedentario": "sedentario", "Ligera": "ligera",
               "Moderada": "moderada", "Intensa": "intensa"}
    act_key = act_map.get(actividad, "sedentario")
    factores = BC["calculo_requerimientos_energeticos"]["factores_actividad_fisica_FAO"]
    fa = factores[act_key][sexo_key_fa]
    get_base = round(geb * fa, 0)

    regla_obj = _regla_objetivo_bc(objetivo)
    ajuste = 0
    if "deficit_kcal" in regla_obj:
        r = regla_obj["deficit_kcal"].split("-")
        ajuste = -(int(r[0]) + int(r[1])) / 2
    elif "superavit_kcal" in regla_obj:
        r = regla_obj["superavit_kcal"].split("-")
        ajuste = (int(r[0]) + int(r[1])) / 2

    if "Embarazo" in condiciones and trimestre:
        extras = BC["condiciones_especiales"]["embarazo"]["energia_extra_kcal"]
        trim_map = {1: "primer_trimestre", 2: "segundo_trimestre", 3: "tercer_trimestre"}
        ajuste += extras[trim_map[trimestre]]
    if "Lactancia" in condiciones:
        ajuste += BC["condiciones_especiales"]["lactancia"]["energia_extra_kcal"]

    get_final = round(get_base + ajuste, 0)
    alerta_cal_baja = False
    minimo = 1500 if sexo == "Masculino" else 1200
    if get_final < minimo:
        alerta_cal_baja = True
        get_final = minimo

    # 5 — Macronutrientes
    def prom_rango(s):
        p = s.split("-")
        return (float(p[0]) + float(p[1])) / 2

    cho_pct = prom_rango(regla_obj["carbohidratos_pct"])
    prot_pct = prom_rango(regla_obj["proteinas_pct"])
    lip_pct = prom_rango(regla_obj["lipidos_pct"])
    cho_g = round((get_final * cho_pct / 100) / 4, 1)
    prot_g = round((get_final * prot_pct / 100) / 4, 1)
    lip_g = round((get_final * lip_pct / 100) / 9, 1)

    prot_min_gkg = 0.8
    if edad >= 60: prot_min_gkg = 1.1
    obj_key = OBJETIVOS_KEYS.get(objetivo, "mantenimiento")
    if obj_key == "ganancia": prot_min_gkg = 1.8
    if obj_key == "rendimiento": prot_min_gkg = 1.3
    prot_min = peso_calc * prot_min_gkg
    if prot_g < prot_min:
        prot_g = round(prot_min, 1)
        kcal_prot = prot_g * 4
        kcal_rest = get_final - kcal_prot
        lip_g = round((kcal_rest * lip_pct / (cho_pct + lip_pct)) / 9, 1)
        cho_g = round((kcal_rest - lip_g * 9) / 4, 1)

    fibra_g = max(25, round(14 * get_final / 1000, 0))
    agua_l = BC["distribucion_macronutrientes"]["agua"][
        "hombres_AI_litros_dia" if sexo == "Masculino" else "mujeres_AI_litros_dia"]

    # 6 — Equivalentes SMAE
    kcal = get_final
    if kcal <= 1400:
        eq = {"verduras": 3, "frutas": 2, "cereales": 4, "leguminosas": 1,
              "aoa": 3, "leche": 1, "aceites": 3, "azucares": 0}
    elif kcal <= 1800:
        eq = {"verduras": 4, "frutas": 3, "cereales": 6, "leguminosas": 1,
              "aoa": 4, "leche": 1, "aceites": 4, "azucares": 0}
    elif kcal <= 2200:
        eq = {"verduras": 5, "frutas": 3, "cereales": 8, "leguminosas": 2,
              "aoa": 5, "leche": 2, "aceites": 5, "azucares": 1}
    elif kcal <= 2600:
        eq = {"verduras": 5, "frutas": 4, "cereales": 10, "leguminosas": 2,
              "aoa": 6, "leche": 2, "aceites": 6, "azucares": 1}
    else:
        eq = {"verduras": 6, "frutas": 4, "cereales": 12, "leguminosas": 2,
              "aoa": 7, "leche": 2, "aceites": 7, "azucares": 2}

    if preferencia == "Vegetariano":
        eq["leguminosas"] += 2; eq["aoa"] = max(0, eq["aoa"] - 2); eq["leche"] += 1
    elif preferencia == "Vegano":
        eq["leguminosas"] += 3; eq["aoa"] = 0; eq["leche"] = 0
        eq["cereales"] += 2; eq["aceites"] += 1

    conds_set = set(condiciones)
    if "Diabetes / Prediabetes" in conds_set or obj_key == "control_glucemico":
        eq["azucares"] = 0; eq["frutas"] = min(eq["frutas"], 2)

    # 7 — Menu
    tiempos = {
        "Desayuno": {
            "verduras": max(1, eq["verduras"] // 4),
            "frutas": max(1, eq["frutas"] // 3),
            "cereales": max(1, eq["cereales"] // 4),
            "aoa": max(1, eq["aoa"] // 3),
            "leche": max(0, eq["leche"] // 2),
            "aceites": max(1, eq["aceites"] // 4),
        },
        "Colacion AM": {"frutas": 1, "aceites": (1 if eq["aceites"] > 3 else 0)},
        "Comida": {
            "verduras": max(1, eq["verduras"] // 3),
            "cereales": max(1, eq["cereales"] // 3),
            "leguminosas": max(1, eq["leguminosas"]),
            "aoa": max(1, eq["aoa"] // 3),
            "aceites": max(1, eq["aceites"] // 3),
        },
        "Colacion PM": {"verduras": 1, "leche": max(0, (eq["leche"] + 1) // 2)},
        "Cena": {
            "verduras": max(1, eq["verduras"] // 3),
            "cereales": max(1, eq["cereales"] // 4),
            "aoa": max(1, eq["aoa"] // 3),
            "aceites": max(1, eq["aceites"] // 4),
        },
    }

    menu = {}
    for tiempo, grupos in tiempos.items():
        platos = []
        for grupo, cant in grupos.items():
            if cant <= 0:
                continue
            if grupo == "aoa" and preferencia == "Vegano":
                continue
            if grupo == "leche" and preferencia == "Vegano":
                platos.append(("Bebida de soya", "1 taza", cant))
                continue
            clave_g = "aoa_vegetariano" if (grupo == "aoa" and preferencia == "Vegetariano") else grupo
            opciones = ALIMENTOS_POR_GRUPO.get(clave_g, [])
            if not opciones:
                continue
            filt = [o for o in opciones if not any(a in o[0].lower() for a in alergias_lista)]
            if not filt:
                filt = opciones
            sel = random.choice(filt)
            porcion = f"{cant} eq. -> {sel[1]} c/u" if cant > 1 else sel[1]
            platos.append((sel[0], porcion, cant))
        menu[tiempo] = platos

    # 8 — Alertas
    alertas = []
    if alerta_cal_baja:
        alertas.append(f"El calculo resulto en calorias muy bajas. Se ajusto al minimo seguro ({minimo} kcal). Requiere supervision medica.")
    if imc >= 35:
        alertas.append(f"{clasificacion_imc} (IMC {imc}). Se recomienda derivacion a equipo multidisciplinario.")
    if "Diabetes / Prediabetes" in conds_set:
        alertas.append("Paciente con diabetes/prediabetes. Priorizar carbohidratos de bajo IG. Distribuir CHO uniformemente. Monitorear glucosa.")
    if "Hipertension arterial" in conds_set:
        alertas.append("Hipertension arterial. Dieta DASH: sodio <2300 mg/dia (ideal <1500), potasio ~4700 mg/dia.")
    if "Embarazo" in conds_set:
        nc = BC["condiciones_especiales"]["embarazo"]["nutrientes_criticos"]
        alertas.append(f"Embarazo (trimestre {trimestre}). Ac. folico >= {nc['acido_folico_ug_DFE']} ug, hierro >= {nc['hierro_mg']} mg, calcio >= {nc['calcio_mg']} mg, DHA >= {nc['omega_3_DHA_mg_dia']} mg/dia.")
    if "Lactancia" in conds_set:
        alertas.append("Lactancia. Energia extra: +500 kcal/dia. Asegurar calcio, ac. folico y B12.")
    if edad >= 60:
        alertas.append("Adulto mayor. Proteina >= 1.0 g/kg/dia. Vit D: 20 ug/dia. Calcio: 1200 mg/dia. Considerar suplementacion de B12.")
    if "Enfermedad renal cronica" in conds_set:
        alertas.append("Enfermedad renal cronica. REQUIERE supervision de nefrologo y nutriologo. Restriccion de proteina, sodio, potasio y fosforo segun estadio.")
    if sexo == "Femenino" and edad < 50 and "Embarazo" not in conds_set:
        alertas.append("Mujer premenopausica. Hierro: 18 mg/dia. Incluir fuentes de hierro hemo + vitamina C.")

    # 9 — IG
    ig_info = None
    if "Diabetes / Prediabetes" in conds_set or obj_key == "control_glucemico":
        ig_data = BC["indice_glucemico_referencia"]["alimentos_comunes"]
        ig_info = {
            "preferir": [a for a in ig_data if a["categoria"] == "bajo"][:8],
            "limitar": [a for a in ig_data if a["categoria"] == "alto"][:5],
        }

    # 10 — Deporte
    deporte_info = None
    if obj_key == "rendimiento" or act_key == "intensa":
        hid = BC["nutricion_deportiva_CONADE"]["hidratacion_deportiva"]
        platos_dep = BC["nutricion_deportiva_CONADE"]["platos_nutricionales"]
        plato_sel = platos_dep[1] if act_key != "intensa" else platos_dep[2]
        td = BC["reglas_sistema_experto"]["reglas_tiempos_comida"]["deportista"]
        deporte_info = {"hidratacion": hid, "plato": plato_sel, "tiempos": td}

    return {
        "imc": imc, "clasificacion_imc": clasificacion_imc, "accion_imc": accion_imc,
        "peso_ideal": peso_ideal, "peso_calc": peso_calc, "usa_corregido": usa_corregido,
        "geb": geb, "formula_geb": formula_geb, "fa": fa, "get_base": get_base,
        "ajuste": round(ajuste, 0), "get_final": get_final,
        "cho_g": cho_g, "prot_g": prot_g, "lip_g": lip_g,
        "cho_pct": round(cho_pct), "prot_pct": round(prot_pct), "lip_pct": round(lip_pct),
        "fibra_g": fibra_g, "agua_l": agua_l,
        "equivalentes": eq, "menu": menu, "alertas": alertas,
        "ig_info": ig_info, "deporte_info": deporte_info,
    }


# ══════════════════════════════════════════════════════════════════════════════
#  WIDGETS AUXILIARES
# ══════════════════════════════════════════════════════════════════════════════
class PlaceholderEntry(ttk.Entry):
    """Entry con texto placeholder gris."""
    def __init__(self, master, placeholder="", **kw):
        super().__init__(master, **kw)
        self.placeholder = placeholder
        self._ph_active = False
        self._show_placeholder()
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

    def _show_placeholder(self):
        if not self.get():
            self._ph_active = True
            self.insert(0, self.placeholder)
            self.configure(foreground="#9E9E9E")

    def _on_focus_in(self, _):
        if self._ph_active:
            self.delete(0, tk.END)
            self.configure(foreground=COLOR_TEXTO)
            self._ph_active = False

    def _on_focus_out(self, _):
        if not self.get():
            self._show_placeholder()

    def get_value(self):
        if self._ph_active:
            return ""
        return self.get()


class CardFrame(tk.Frame):
    """Frame con aspecto de tarjeta (bordes redondeados simulados)."""
    def __init__(self, master, titulo="", color_acento=COLOR_PRIMARIO, **kw):
        super().__init__(master, bg=COLOR_PANEL, highlightbackground=COLOR_BORDE,
                         highlightthickness=1, **kw)
        if titulo:
            barra = tk.Frame(self, bg=color_acento, height=4)
            barra.pack(fill="x")
            lbl = tk.Label(self, text=titulo, font=FONT_SUBTIT,
                           bg=COLOR_PANEL, fg=color_acento, anchor="w")
            lbl.pack(fill="x", padx=14, pady=(8, 2))


# ══════════════════════════════════════════════════════════════════════════════
#  APLICACION PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Experto de Nutricion - Mexico")
        self.configure(bg=COLOR_FONDO)
        self.minsize(1100, 720)
        self.state("zoomed")

        self._build_styles()
        self._build_layout()
        self._show_page("formulario")

    # ──────── estilos ttk ────────
    def _build_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("TFrame", background=COLOR_FONDO)
        s.configure("Card.TFrame", background=COLOR_PANEL)
        s.configure("TLabel", background=COLOR_FONDO, foreground=COLOR_TEXTO, font=FONT_NORMAL)
        s.configure("Card.TLabel", background=COLOR_PANEL, foreground=COLOR_TEXTO, font=FONT_NORMAL)
        s.configure("Header.TLabel", background=COLOR_PANEL, foreground=COLOR_PRIMARIO,
                     font=FONT_SUBTIT)
        s.configure("TButton", font=FONT_NORMAL)
        s.configure("Green.TButton", font=("Segoe UI", 11, "bold"))
        s.configure("TCombobox", font=FONT_NORMAL)
        s.configure("TCheckbutton", background=COLOR_PANEL, font=FONT_NORMAL)
        s.configure("Sidebar.TButton", font=FONT_NORMAL, anchor="w")

    # ──────── layout principal ────────
    def _build_layout(self):
        # Sidebar
        self.sidebar = tk.Frame(self, bg=COLOR_SIDEBAR, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo_frame = tk.Frame(self.sidebar, bg=COLOR_PRIMARIO)
        logo_frame.pack(fill="x", ipady=18)
        tk.Label(logo_frame, text="NutriExperto MX", font=FONT_TITULO,
                 bg=COLOR_PRIMARIO, fg="white").pack(pady=(8, 0))
        tk.Label(logo_frame, text="Sistema Experto de Nutricion",
                 font=FONT_SMALL, bg=COLOR_PRIMARIO, fg="#C8E6C9").pack()

        self.sidebar_btns = {}
        pages = [
            ("formulario", "  Nuevo Plan"),
            ("resultados", "  Resultados"),
            ("alimentos",  "  Alimentos"),
            ("epidemio",   "  Epidemiologia"),
            ("nom043",     "  NOM-043"),
            ("acerca",     "  Acerca de"),
        ]
        for key, label in pages:
            btn = tk.Button(
                self.sidebar, text=label, font=FONT_NORMAL, anchor="w",
                bg=COLOR_SIDEBAR, fg=COLOR_TEXTO, bd=0, padx=18, pady=10,
                activebackground=COLOR_SIDEBAR_ACT, cursor="hand2",
                command=lambda k=key: self._show_page(k))
            btn.pack(fill="x")
            self.sidebar_btns[key] = btn

        tk.Frame(self.sidebar, bg=COLOR_BORDE, height=1).pack(fill="x", pady=10)
        tk.Label(self.sidebar, text="Fuentes: NOM-043, SMAE,\nFAO/OMS, DRI, ENSANUT",
                 font=("Segoe UI", 8), bg=COLOR_SIDEBAR, fg=COLOR_TEXTO_SEC,
                 justify="left").pack(padx=18, anchor="w")

        # Area principal
        self.main_area = tk.Frame(self, bg=COLOR_FONDO)
        self.main_area.pack(side="left", fill="both", expand=True)

        self.pages = {}
        self._build_formulario()
        self._build_resultados()
        self._build_alimentos()
        self._build_epidemio()
        self._build_nom043()
        self._build_acerca()

        self.resultado_data = None

    def _show_page(self, name):
        for key, btn in self.sidebar_btns.items():
            btn.configure(bg=COLOR_SIDEBAR_ACT if key == name else COLOR_SIDEBAR,
                          fg=COLOR_PRIMARIO if key == name else COLOR_TEXTO)
        for page in self.pages.values():
            page.pack_forget()
        self.pages[name].pack(fill="both", expand=True)

    # ══════════════════════════════════════════════════════════════════════════
    #  PAGINA: FORMULARIO
    # ══════════════════════════════════════════════════════════════════════════
    def _build_formulario(self):
        container = tk.Frame(self.main_area, bg=COLOR_FONDO)
        self.pages["formulario"] = container

        canvas = tk.Canvas(container, bg=COLOR_FONDO, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=COLOR_FONDO)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        pad = {"padx": 20, "pady": 8}
        inner = tk.Frame(scroll_frame, bg=COLOR_FONDO)
        inner.pack(fill="x", padx=30, pady=20)

        # Titulo
        tk.Label(inner, text="Generar Plan Nutricional", font=FONT_TITULO,
                 bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(anchor="w", **pad)

        # --- Card datos personales ---
        card1 = CardFrame(inner, "Datos Personales")
        card1.pack(fill="x", **pad)
        f1 = tk.Frame(card1, bg=COLOR_PANEL)
        f1.pack(fill="x", padx=14, pady=10)

        self.entries = {}
        row = 0
        for label, key, ph in [("Nombre", "nombre", "Ej: Maria"),
                                ("Edad (anios)", "edad", "Ej: 35"),
                                ("Peso (kg)", "peso", "Ej: 72"),
                                ("Estatura (cm)", "talla", "Ej: 165")]:
            tk.Label(f1, text=label, font=FONT_LABEL, bg=COLOR_PANEL,
                     fg=COLOR_TEXTO).grid(row=row, column=0, sticky="w", padx=5, pady=5)
            e = PlaceholderEntry(f1, placeholder=ph, width=25)
            e.grid(row=row, column=1, padx=10, pady=5, sticky="w")
            self.entries[key] = e
            row += 1

        tk.Label(f1, text="Sexo", font=FONT_LABEL, bg=COLOR_PANEL,
                 fg=COLOR_TEXTO).grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.combo_sexo = ttk.Combobox(f1, values=["Masculino", "Femenino"],
                                       state="readonly", width=22)
        self.combo_sexo.set("Masculino")
        self.combo_sexo.grid(row=row, column=1, padx=10, pady=5, sticky="w")
        self.combo_sexo.bind("<<ComboboxSelected>>", self._on_sexo_changed)

        # --- Card actividad y objetivo ---
        card2 = CardFrame(inner, "Actividad y Objetivo", color_acento=COLOR_SECUNDARIO)
        card2.pack(fill="x", **pad)
        f2 = tk.Frame(card2, bg=COLOR_PANEL)
        f2.pack(fill="x", padx=14, pady=10)

        tk.Label(f2, text="Nivel de actividad", font=FONT_LABEL,
                 bg=COLOR_PANEL).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.combo_act = ttk.Combobox(
            f2, values=["Sedentario", "Ligera", "Moderada", "Intensa"],
            state="readonly", width=30)
        self.combo_act.set("Sedentario")
        self.combo_act.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        tk.Label(f2, text="Objetivo", font=FONT_LABEL,
                 bg=COLOR_PANEL).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.combo_obj = ttk.Combobox(
            f2, values=list(MAPA_OBJETIVO.keys()), state="readonly", width=40)
        self.combo_obj.set("Mantenimiento")
        self.combo_obj.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # --- Card condiciones ---
        card3 = CardFrame(inner, "Condiciones Medicas", color_acento=COLOR_ALERTA)
        card3.pack(fill="x", **pad)
        f3 = tk.Frame(card3, bg=COLOR_PANEL)
        f3.pack(fill="x", padx=14, pady=10)

        self.cond_vars = {}
        self.cond_widgets = {}
        # Condiciones generales (siempre visibles)
        condiciones_generales = ["Diabetes / Prediabetes", "Hipertension arterial",
                                 "Enfermedad renal cronica"]
        for i, cond in enumerate(condiciones_generales):
            var = tk.BooleanVar()
            cb = tk.Checkbutton(f3, text=cond, variable=var, bg=COLOR_PANEL,
                                font=FONT_NORMAL, activebackground=COLOR_PANEL)
            cb.grid(row=i // 2, column=i % 2, sticky="w", padx=10, pady=3)
            self.cond_vars[cond] = var

        # Condiciones femeninas (solo visibles si sexo == Femenino)
        self.cond_fem_frame = tk.Frame(f3, bg=COLOR_PANEL)
        # Se ubica debajo de las generales
        self.cond_fem_frame.grid(row=2, column=0, columnspan=2, sticky="w")
        self.cond_fem_frame.grid_remove()  # oculto por defecto

        condiciones_fem = ["Embarazo", "Lactancia"]
        for i, cond in enumerate(condiciones_fem):
            var = tk.BooleanVar()
            cb = tk.Checkbutton(self.cond_fem_frame, text=cond, variable=var,
                                bg=COLOR_PANEL, font=FONT_NORMAL,
                                activebackground=COLOR_PANEL,
                                command=self._on_embarazo_changed)
            cb.grid(row=0, column=i, sticky="w", padx=10, pady=3)
            self.cond_vars[cond] = var
            self.cond_widgets[cond] = cb

        # Trimestre (solo visible si Embarazo esta marcado)
        self.trim_frame = tk.Frame(f3, bg=COLOR_PANEL)
        self.trim_frame.grid(row=3, column=0, columnspan=2, sticky="w")
        self.trim_frame.grid_remove()  # oculto por defecto

        tk.Label(self.trim_frame, text="Trimestre de embarazo:", font=FONT_NORMAL,
                 bg=COLOR_PANEL).pack(side="left", padx=(10, 5), pady=5)
        self.combo_trim = ttk.Combobox(self.trim_frame, values=["1", "2", "3"],
                                       state="readonly", width=5)
        self.combo_trim.set("1")
        self.combo_trim.pack(side="left", padx=5, pady=5)

        # --- Card preferencias ---
        card4 = CardFrame(inner, "Preferencias Alimentarias", color_acento=COLOR_ACENTO)
        card4.pack(fill="x", **pad)
        f4 = tk.Frame(card4, bg=COLOR_PANEL)
        f4.pack(fill="x", padx=14, pady=10)

        tk.Label(f4, text="Tipo de alimentacion", font=FONT_LABEL,
                 bg=COLOR_PANEL).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.combo_pref = ttk.Combobox(
            f4, values=["Omnivoro", "Vegetariano", "Vegano"],
            state="readonly", width=22)
        self.combo_pref.set("Omnivoro")
        self.combo_pref.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        tk.Label(f4, text="Alergias (separar con coma)", font=FONT_LABEL,
                 bg=COLOR_PANEL).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_alergias = PlaceholderEntry(f4, placeholder="Ej: lactosa, cacahuate", width=30)
        self.entry_alergias.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Boton generar
        btn_frame = tk.Frame(inner, bg=COLOR_FONDO)
        btn_frame.pack(fill="x", **pad)
        btn_gen = tk.Button(
            btn_frame, text="  GENERAR PLAN NUTRICIONAL  ", font=("Segoe UI", 13, "bold"),
            bg=COLOR_PRIMARIO, fg="white", activebackground=COLOR_PRIMARIO_H,
            activeforeground="white", bd=0, padx=30, pady=12, cursor="hand2",
            command=self._on_generar)
        btn_gen.pack(pady=10)

    # ──────── eventos de visibilidad condicional ────────
    def _on_sexo_changed(self, event=None):
        """Muestra/oculta Embarazo y Lactancia segun el sexo seleccionado."""
        if self.combo_sexo.get() == "Femenino":
            self.cond_fem_frame.grid()
        else:
            # Ocultar y desmarcar
            self.cond_fem_frame.grid_remove()
            self.cond_vars["Embarazo"].set(False)
            self.cond_vars["Lactancia"].set(False)
            self._on_embarazo_changed()

    def _on_embarazo_changed(self):
        """Muestra/oculta el selector de trimestre segun el check de Embarazo."""
        if self.cond_vars["Embarazo"].get():
            self.trim_frame.grid()
        else:
            self.trim_frame.grid_remove()
            self.combo_trim.set("1")

    # ══════════════════════════════════════════════════════════════════════════
    #  PAGINA: RESULTADOS
    # ══════════════════════════════════════════════════════════════════════════
    def _build_resultados(self):
        container = tk.Frame(self.main_area, bg=COLOR_FONDO)
        self.pages["resultados"] = container
        self.result_text = scrolledtext.ScrolledText(
            container, font=FONT_MONO, bg=COLOR_PANEL, fg=COLOR_TEXTO,
            wrap="word", bd=0, padx=20, pady=20, state="disabled")
        self.result_text.pack(fill="both", expand=True, padx=15, pady=15)

        # Tag styles
        self.result_text.tag_configure("titulo", font=FONT_TITULO, foreground=COLOR_PRIMARIO)
        self.result_text.tag_configure("subtitulo", font=FONT_SUBTIT, foreground=COLOR_PRIMARIO)
        self.result_text.tag_configure("alerta", font=("Consolas", 10, "bold"), foreground=COLOR_ALERTA)
        self.result_text.tag_configure("valor", font=("Consolas", 10, "bold"), foreground=COLOR_ACENTO)
        self.result_text.tag_configure("seccion", font=("Segoe UI", 11, "bold"), foreground=COLOR_SECUNDARIO)
        self.result_text.tag_configure("normal", font=FONT_MONO, foreground=COLOR_TEXTO)

    # ══════════════════════════════════════════════════════════════════════════
    #  PAGINA: ALIMENTOS
    # ══════════════════════════════════════════════════════════════════════════
    def _build_alimentos(self):
        container = tk.Frame(self.main_area, bg=COLOR_FONDO)
        self.pages["alimentos"] = container

        tk.Label(container, text="Tabla de Composicion de Alimentos Mexicanos",
                 font=FONT_TITULO, bg=COLOR_FONDO, fg=COLOR_PRIMARIO
                 ).pack(anchor="w", padx=20, pady=(20, 5))
        tk.Label(container, text="Valores por 100 g de porcion comestible  |  Fuente: SMAE + USDA FoodData Central (CC0)",
                 font=FONT_SMALL, bg=COLOR_FONDO, fg=COLOR_TEXTO_SEC
                 ).pack(anchor="w", padx=20, pady=(0, 10))

        cols = ("Alimento", "Energia (kcal)", "Proteina (g)", "Lipidos (g)",
                "CHO (g)", "Fibra (g)")
        tree = ttk.Treeview(container, columns=cols, show="headings", height=20)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=130 if c == "Alimento" else 100, anchor="center")
        tree.column("Alimento", width=220, anchor="w")

        for a in BC["composicion_alimentos_mexicanos_referencia"]["alimentos"]:
            tree.insert("", "end", values=(
                a["nombre"],
                a.get("energia_kcal", "—"),
                a.get("proteina_g", "—"),
                a.get("lipidos_g", "—"),
                a.get("carbohidratos_g", "—"),
                a.get("fibra_g", "—"),
            ))
        vsb = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y", padx=(0, 15), pady=5)
        tree.pack(fill="both", expand=True, padx=20, pady=5)

        # IG table
        tk.Label(container, text="Indice Glucemico de Alimentos Comunes",
                 font=FONT_SUBTIT, bg=COLOR_FONDO, fg=COLOR_SECUNDARIO
                 ).pack(anchor="w", padx=20, pady=(10, 5))
        cols_ig = ("Alimento", "IG", "Categoria")
        tree_ig = ttk.Treeview(container, columns=cols_ig, show="headings", height=8)
        for c in cols_ig:
            tree_ig.heading(c, text=c)
            tree_ig.column(c, width=180, anchor="center")
        tree_ig.column("Alimento", width=220, anchor="w")

        for a in BC["indice_glucemico_referencia"]["alimentos_comunes"]:
            tree_ig.insert("", "end", values=(a["alimento"], a["IG"], a["categoria"]))
        tree_ig.pack(fill="x", padx=20, pady=(0, 15))

    # ══════════════════════════════════════════════════════════════════════════
    #  PAGINA: EPIDEMIOLOGIA
    # ══════════════════════════════════════════════════════════════════════════
    def _build_epidemio(self):
        container = tk.Frame(self.main_area, bg=COLOR_FONDO)
        self.pages["epidemio"] = container

        canvas = tk.Canvas(container, bg=COLOR_FONDO, highlightthickness=0)
        sb = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        sf = tk.Frame(canvas, bg=COLOR_FONDO)
        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sf, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(sf, bg=COLOR_FONDO)
        inner.pack(fill="x", padx=30, pady=20)

        tk.Label(inner, text="Contexto Epidemiologico — Mexico",
                 font=FONT_TITULO, bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(anchor="w", pady=5)
        tk.Label(inner, text="Fuente: ENSANUT Continua 2020-2024, ENSANUT 2022-2023, CONEVAL",
                 font=FONT_SMALL, bg=COLOR_FONDO, fg=COLOR_TEXTO_SEC).pack(anchor="w")

        epi = BC["contexto_epidemiologico_mexico"]
        pa = epi["prevalencias_adultos"]

        # Cards con cifras grandes
        grid_f = tk.Frame(inner, bg=COLOR_FONDO)
        grid_f.pack(fill="x", pady=15)

        datos_cards = [
            ("75.2%", "Sobrepeso + Obesidad", "adultos >= 20 anios", COLOR_ALERTA),
            ("17.0%", "Diabetes tipo 2", f"diagnosticada: {pa['diabetes_tipo_2']['diagnosticada_pct']}%", COLOR_SECUNDARIO),
            ("47.0%", "Hipertension", f"desconocen Dx: {pa['hipertension_arterial']['desconocen_diagnostico_pct']}%", COLOR_ACENTO),
            ("50.0%", "Inseg. Alimentaria", f"severa: {epi['inseguridad_alimentaria']['severa_pct']}%", "#6A1B9A"),
        ]
        for i, (cifra, titulo, sub, color) in enumerate(datos_cards):
            card = tk.Frame(grid_f, bg=COLOR_PANEL, highlightbackground=COLOR_BORDE,
                            highlightthickness=1)
            card.grid(row=0, column=i, padx=8, pady=5, sticky="nsew")
            grid_f.columnconfigure(i, weight=1)
            tk.Frame(card, bg=color, height=4).pack(fill="x")
            tk.Label(card, text=cifra, font=FONT_GRANDE, bg=COLOR_PANEL,
                     fg=color).pack(pady=(12, 0))
            tk.Label(card, text=titulo, font=FONT_LABEL, bg=COLOR_PANEL,
                     fg=COLOR_TEXTO).pack()
            tk.Label(card, text=sub, font=FONT_SMALL, bg=COLOR_PANEL,
                     fg=COLOR_TEXTO_SEC).pack(pady=(0, 12))

        # Detalle
        detalle = CardFrame(inner, "Detalle de Prevalencias")
        detalle.pack(fill="x", pady=10)
        txt = tk.Text(detalle, font=FONT_MONO, bg=COLOR_PANEL, fg=COLOR_TEXTO,
                      height=18, wrap="word", bd=0, state="normal")
        txt.pack(fill="x", padx=14, pady=10)

        lines = [
            f"SOBREPESO: {pa['sobrepeso']['total_pct']}%  (H: {pa['sobrepeso']['hombres_pct']}%  M: {pa['sobrepeso']['mujeres_pct']}%)",
            f"OBESIDAD:  {pa['obesidad']['total_pct']}%  (H: {pa['obesidad']['hombres_pct']}%  M: {pa['obesidad']['mujeres_pct']}%)",
            f"OBESIDAD ABDOMINAL: {pa['obesidad_abdominal']['total_pct']}%",
            f"  Criterio H: cintura > 90 cm  |  M: cintura > 80 cm",
            "",
            f"DIABETES TIPO 2: {pa['diabetes_tipo_2']['total_pct']}%",
            f"  No diagnosticada: {pa['diabetes_tipo_2']['no_diagnosticada_pct']}%",
            f"  Control glucemico: {pa['diabetes_tipo_2']['control_glucemico_pct']}%",
            f"PREDIABETES: {pa['prediabetes_pct']}%",
            "",
            f"HIPERTENSION: {pa['hipertension_arterial']['total_pct']}%",
            f"  Criterio: PA >= 130/80 mmHg",
            "",
            f"NINOS 5-11 (sobrepeso+obes.): {epi['prevalencias_ninos_adolescentes']['sobrepeso_obesidad_5_a_11_pct']}%",
            f"ADOLESCENTES (sobrepeso+obes.): {epi['prevalencias_ninos_adolescentes']['sobrepeso_obesidad_adolescentes_pct']}%",
            "",
            f"RIESGOS OBESIDAD (RM vs IMC normal):",
            f"  Diabetes RM {epi['riesgos_asociados_obesidad']['diabetes_RM']}  |  HTA RM {epi['riesgos_asociados_obesidad']['hipertension_RM']}  |  Dislipidemia RM {epi['riesgos_asociados_obesidad']['dislipidemia_RM']}",
        ]
        txt.insert("1.0", "\n".join(lines))
        txt.configure(state="disabled")

    # ══════════════════════════════════════════════════════════════════════════
    #  PAGINA: NOM-043
    # ══════════════════════════════════════════════════════════════════════════
    def _build_nom043(self):
        container = tk.Frame(self.main_area, bg=COLOR_FONDO)
        self.pages["nom043"] = container

        canvas = tk.Canvas(container, bg=COLOR_FONDO, highlightthickness=0)
        sb = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        sf = tk.Frame(canvas, bg=COLOR_FONDO)
        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sf, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(sf, bg=COLOR_FONDO)
        inner.pack(fill="x", padx=30, pady=20)

        nom = BC["normativa_mexicana"]["NOM_043_SSA2_2012"]

        tk.Label(inner, text="NOM-043-SSA2-2012", font=FONT_TITULO,
                 bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(anchor="w", pady=5)
        tk.Label(inner, text=nom["titulo"], font=FONT_SMALL,
                 bg=COLOR_FONDO, fg=COLOR_TEXTO_SEC, wraplength=700,
                 justify="left").pack(anchor="w")

        # Principios
        card_p = CardFrame(inner, "Principios de la Dieta Correcta")
        card_p.pack(fill="x", pady=10)
        for nombre, desc in nom["principios_dieta_correcta"].items():
            f = tk.Frame(card_p, bg=COLOR_PANEL)
            f.pack(fill="x", padx=14, pady=3)
            tk.Label(f, text=f"{nombre.upper()}:", font=FONT_LABEL,
                     bg=COLOR_PANEL, fg=COLOR_PRIMARIO).pack(side="left")
            tk.Label(f, text=f"  {desc}", font=FONT_NORMAL,
                     bg=COLOR_PANEL, fg=COLOR_TEXTO, wraplength=650,
                     justify="left").pack(side="left", fill="x")
        tk.Frame(card_p, bg=COLOR_PANEL, height=8).pack()

        # Plato del Bien Comer
        card_pbc = CardFrame(inner, "Plato del Bien Comer", color_acento=COLOR_SECUNDARIO)
        card_pbc.pack(fill="x", pady=10)
        colores_map = {"verde": "#43A047", "amarillo": "#F9A825", "rojo": "#E53935"}
        for g in nom["plato_del_bien_comer"]["grupos"]:
            gf = tk.Frame(card_pbc, bg=COLOR_PANEL)
            gf.pack(fill="x", padx=14, pady=6)
            color_g = colores_map.get(g["color"], COLOR_TEXTO)
            # Color indicator
            ind = tk.Frame(gf, bg=color_g, width=14, height=14)
            ind.pack(side="left", padx=(0, 8))
            ind.pack_propagate(False)
            info_f = tk.Frame(gf, bg=COLOR_PANEL)
            info_f.pack(side="left", fill="x")
            tk.Label(info_f, text=f"{g['grupo']}  —  comer {g['proporcion']}",
                     font=FONT_LABEL, bg=COLOR_PANEL, fg=color_g).pack(anchor="w")
            tk.Label(info_f, text=g["funcion_principal"], font=FONT_SMALL,
                     bg=COLOR_PANEL, fg=COLOR_TEXTO_SEC, wraplength=600,
                     justify="left").pack(anchor="w")
        tk.Frame(card_pbc, bg=COLOR_PANEL, height=8).pack()

        # Recomendaciones generales
        card_rec = CardFrame(inner, "Recomendaciones Generales")
        card_rec.pack(fill="x", pady=10)
        for rec in nom["recomendaciones_generales"]:
            tk.Label(card_rec, text=f"  *  {rec}", font=FONT_NORMAL,
                     bg=COLOR_PANEL, fg=COLOR_TEXTO, anchor="w",
                     wraplength=650, justify="left").pack(fill="x", padx=14, pady=2)
        tk.Frame(card_rec, bg=COLOR_PANEL, height=8).pack()

        # Grupos vulnerables
        card_gv = CardFrame(inner, "Grupos Vulnerables", color_acento=COLOR_ALERTA)
        card_gv.pack(fill="x", pady=10)
        for gv in nom["grupos_vulnerables"]:
            tk.Label(card_gv, text=f"  *  {gv}", font=FONT_NORMAL,
                     bg=COLOR_PANEL, fg=COLOR_TEXTO, anchor="w").pack(fill="x", padx=14, pady=2)
        tk.Frame(card_gv, bg=COLOR_PANEL, height=10).pack()

    # ══════════════════════════════════════════════════════════════════════════
    #  PAGINA: ACERCA DE
    # ══════════════════════════════════════════════════════════════════════════
    def _build_acerca(self):
        container = tk.Frame(self.main_area, bg=COLOR_FONDO)
        self.pages["acerca"] = container

        canvas = tk.Canvas(container, bg=COLOR_FONDO, highlightthickness=0)
        sb = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        sf = tk.Frame(canvas, bg=COLOR_FONDO)
        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sf, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(sf, bg=COLOR_FONDO)
        inner.pack(fill="x", padx=30, pady=20)

        tk.Label(inner, text="Acerca del Sistema Experto", font=FONT_TITULO,
                 bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(anchor="w", pady=5)

        card = CardFrame(inner, "Informacion del Sistema")
        card.pack(fill="x", pady=10)
        about_text = (
            "Sistema Experto de Nutricion para la poblacion mexicana.\n"
            "Version 1.0.0\n\n"
            "Este sistema utiliza una base de conocimiento estructurada\n"
            "compilada a partir de fuentes oficiales mexicanas e\n"
            "internacionales para generar recomendaciones nutricionales\n"
            "y planes alimentarios personalizados.\n\n"
            "AVISO: Este sistema es ORIENTATIVO. No sustituye la\n"
            "consulta con un profesional de la nutricion certificado."
        )
        tk.Label(card, text=about_text, font=FONT_NORMAL, bg=COLOR_PANEL,
                 fg=COLOR_TEXTO, justify="left", wraplength=600).pack(padx=14, pady=10)

        # --- Card Autor y Licencia ---
        card_lic = CardFrame(inner, "Autor y Licencia", color_acento=COLOR_SECUNDARIO)
        card_lic.pack(fill="x", pady=10)
        lic_frame = tk.Frame(card_lic, bg=COLOR_PANEL)
        lic_frame.pack(fill="x", padx=14, pady=10)

        tk.Label(lic_frame, text="Autor:", font=FONT_LABEL,
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).grid(row=0, column=0, sticky="w", padx=5, pady=3)
        tk.Label(lic_frame, text="Daniel Diaz Rojas", font=FONT_NORMAL,
                 bg=COLOR_PANEL, fg=COLOR_ACENTO).grid(row=0, column=1, sticky="w", padx=5, pady=3)

        tk.Label(lic_frame, text="Licencia:", font=FONT_LABEL,
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).grid(row=1, column=0, sticky="w", padx=5, pady=3)
        tk.Label(lic_frame, text="MIT License", font=FONT_NORMAL,
                 bg=COLOR_PANEL, fg=COLOR_ACENTO).grid(row=1, column=1, sticky="w", padx=5, pady=3)

        tk.Label(lic_frame, text="Copyright:", font=FONT_LABEL,
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).grid(row=2, column=0, sticky="w", padx=5, pady=3)
        tk.Label(lic_frame, text="(c) 2026 Daniel Diaz Rojas", font=FONT_NORMAL,
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).grid(row=2, column=1, sticky="w", padx=5, pady=3)

        tk.Label(lic_frame, text="Version:", font=FONT_LABEL,
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).grid(row=3, column=0, sticky="w", padx=5, pady=3)
        tk.Label(lic_frame, text="1.0.0", font=FONT_NORMAL,
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).grid(row=3, column=1, sticky="w", padx=5, pady=3)

        mit_text = (
            "Permission is hereby granted, free of charge, to any person obtaining a copy "
            "of this software and associated documentation files, to deal in the Software "
            "without restriction, including without limitation the rights to use, copy, "
            "modify, merge, publish, distribute, sublicense, and/or sell copies of the "
            "Software, subject to the following conditions:\n\n"
            "The above copyright notice and this permission notice shall be included in "
            "all copies or substantial portions of the Software.\n\n"
            "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND."
        )
        tk.Label(card_lic, text=mit_text, font=("Segoe UI", 8), bg=COLOR_PANEL,
                 fg=COLOR_TEXTO_SEC, justify="left", wraplength=600).pack(padx=14, pady=(0, 10))

        # --- Card Fuentes ---
        card2 = CardFrame(inner, "Fuentes", color_acento=COLOR_ACENTO)
        card2.pack(fill="x", pady=10)
        for f in BC["metadata"]["fuentes"]:
            ff = tk.Frame(card2, bg=COLOR_PANEL)
            ff.pack(fill="x", padx=14, pady=4)
            tk.Label(ff, text=f"[{f['id']}]", font=FONT_LABEL, bg=COLOR_PANEL,
                     fg=COLOR_ACENTO).pack(side="left")
            tk.Label(ff, text=f"  {f['nombre']}", font=FONT_NORMAL, bg=COLOR_PANEL,
                     fg=COLOR_TEXTO).pack(side="left")
        tk.Frame(card2, bg=COLOR_PANEL, height=10).pack()

    # ══════════════════════════════════════════════════════════════════════════
    #  ACCION: GENERAR PLAN
    # ══════════════════════════════════════════════════════════════════════════
    def _on_generar(self):
        # Validar
        try:
            nombre = self.entries["nombre"].get_value() or "Usuario"
            edad = int(self.entries["edad"].get_value())
            peso = float(self.entries["peso"].get_value())
            talla = float(self.entries["talla"].get_value())
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Ingrese valores numericos validos para edad, peso y estatura.")
            return

        if not (10 <= edad <= 120):
            messagebox.showerror("Error", "Edad fuera de rango (10-120).")
            return
        if not (20 <= peso <= 300):
            messagebox.showerror("Error", "Peso fuera de rango (20-300 kg).")
            return
        if not (100 <= talla <= 250):
            messagebox.showerror("Error", "Estatura fuera de rango (100-250 cm).")
            return

        sexo = self.combo_sexo.get()
        actividad = self.combo_act.get()
        objetivo = self.combo_obj.get()
        preferencia = self.combo_pref.get()
        condiciones = [c for c, v in self.cond_vars.items() if v.get()]
        trimestre = int(self.combo_trim.get()) if "Embarazo" in condiciones else None

        alergias_raw = self.entry_alergias.get_value()
        alergias = []
        if alergias_raw and alergias_raw.lower() not in ("ninguna", "no", ""):
            alergias = [a.strip().lower() for a in alergias_raw.split(",")]

        # Motor
        r = motor_inferencia(sexo, edad, peso, talla, actividad, objetivo,
                             condiciones, trimestre, preferencia, alergias)
        self.resultado_data = r

        # Renderizar
        self._render_resultados(nombre, sexo, edad, peso, talla, actividad,
                                objetivo, condiciones, preferencia, alergias, r)
        self._show_page("resultados")

    def _render_resultados(self, nombre, sexo, edad, peso, talla, actividad,
                           objetivo, condiciones, preferencia, alergias, r):
        t = self.result_text
        t.configure(state="normal")
        t.delete("1.0", "end")

        def titulo(s):   t.insert("end", f"\n{s}\n", "titulo")
        def seccion(s):  t.insert("end", f"\n{'='*60}\n  {s}\n{'='*60}\n", "seccion")
        def linea(s):    t.insert("end", f"  {s}\n", "normal")
        def valor(s):    t.insert("end", f"  {s}\n", "valor")
        def alerta(s):   t.insert("end", f"  >> {s}\n", "alerta")

        titulo(f"PLAN NUTRICIONAL — {nombre.upper()}")
        linea(f"Fuentes: NOM-043, SMAE 4a ed., FAO/OMS, DRI (IOM), ENSANUT")

        seccion("PERFIL DEL PACIENTE")
        linea(f"Sexo: {sexo}  |  Edad: {edad} anios")
        linea(f"Peso: {peso} kg  |  Estatura: {talla} cm")
        linea(f"Actividad: {actividad}  |  Objetivo: {objetivo}")
        if condiciones:
            linea(f"Condiciones: {', '.join(condiciones)}")
        linea(f"Preferencia: {preferencia}")
        if alergias:
            linea(f"Alergias: {', '.join(alergias)}")

        seccion("EVALUACION ANTROPOMETRICA")
        valor(f"IMC: {r['imc']} kg/m2  ->  {r['clasificacion_imc']}")
        linea(f"Recomendacion: {r['accion_imc']}")
        linea(f"Peso ideal estimado: {r['peso_ideal']} kg")
        if r["usa_corregido"]:
            linea(f"Peso corregido (para calculos): {r['peso_calc']} kg")

        seccion("REQUERIMIENTOS ENERGETICOS")
        linea(f"Formula: {r['formula_geb']}")
        linea(f"Gasto Energetico Basal (GEB): {r['geb']:.0f} kcal/dia")
        linea(f"Factor de actividad ({actividad}): {r['fa']}")
        linea(f"GET sin ajustar: {r['get_base']:.0f} kcal/dia")
        if r["ajuste"] != 0:
            signo = "+" if r["ajuste"] > 0 else ""
            linea(f"Ajuste por objetivo/condicion: {signo}{r['ajuste']:.0f} kcal")
        valor(f">>> GET FINAL: {r['get_final']:.0f} kcal/dia <<<")

        seccion("DISTRIBUCION DE MACRONUTRIENTES")
        valor(f"Carbohidratos: {r['cho_g']:.0f} g  ({r['cho_pct']}%)")
        valor(f"Proteinas:     {r['prot_g']:.0f} g  ({r['prot_pct']}%)")
        valor(f"Lipidos:       {r['lip_g']:.0f} g  ({r['lip_pct']}%)")
        linea(f"Fibra:         >= {r['fibra_g']:.0f} g/dia")
        linea(f"Agua:          >= {r['agua_l']} L/dia")

        seccion("EQUIVALENTES SMAE (porciones diarias)")
        nombres_eq = {
            "verduras": "Verduras", "frutas": "Frutas",
            "cereales": "Cereales y Tuberculos", "leguminosas": "Leguminosas",
            "aoa": "Alimentos de Origen Animal", "leche": "Leche",
            "aceites": "Aceites y Grasas", "azucares": "Azucares"
        }
        for g, n in nombres_eq.items():
            if r["equivalentes"].get(g, 0) > 0:
                linea(f"{n:.<38} {r['equivalentes'][g]} eq.")

        seccion("MENU EJEMPLO DEL DIA")
        for tiempo, platos in r["menu"].items():
            valor(f"\n  {tiempo.upper()}")
            if not platos:
                linea("    (Sin alimentos asignados)")
            for alim, porc, cant in platos:
                linea(f"    * {alim:.<30} {porc}")

        if r["ig_info"]:
            seccion("GUIA DE INDICE GLUCEMICO")
            linea("PREFERIR (IG bajo < 55):")
            for a in r["ig_info"]["preferir"]:
                linea(f"  [OK] {a['alimento']} (IG: {a['IG']})")
            linea("\nLIMITAR (IG alto >= 70):")
            for a in r["ig_info"]["limitar"]:
                linea(f"  [!!] {a['alimento']} (IG: {a['IG']})")

        if r["deporte_info"]:
            seccion("NUTRICION DEPORTIVA (CONADE)")
            pl = r["deporte_info"]["plato"]
            linea(f"Plato recomendado: {pl['fase']} ({pl['color']})")
            for k, v in pl["distribucion"].items():
                linea(f"  * {k.replace('_', ' ').capitalize()}: {v}%")
            h = r["deporte_info"]["hidratacion"]
            linea(f"\nHidratacion:")
            linea(f"  Pre-ejercicio:  {h['pre_ejercicio']}")
            linea(f"  Durante:        {h['durante_ejercicio']}")
            linea(f"  Post-ejercicio: {h['post_ejercicio']}")
            td = r["deporte_info"]["tiempos"]
            linea(f"\nTiempos de entrenamiento:")
            for k, v in td.items():
                linea(f"  * {k.replace('_', ' ').capitalize()}: {v}")

        if r["alertas"]:
            seccion("ALERTAS CLINICAS")
            for i, al in enumerate(r["alertas"], 1):
                alerta(f"{i}. {al}")

        seccion("REFERENCIA: PLATO DEL BIEN COMER (NOM-043)")
        for g in BC["normativa_mexicana"]["NOM_043_SSA2_2012"]["plato_del_bien_comer"]["grupos"]:
            valor(f"[{g['color'].upper()}] {g['grupo']} — {g['proporcion']}")
            linea(f"     {g['funcion_principal'][:80]}")

        seccion("AVISO IMPORTANTE")
        alerta("Este plan es ORIENTATIVO y generado por un sistema experto.")
        alerta("NO sustituye la consulta con un profesional de la nutricion.")
        alerta("Consulte a un nutriologo certificado para un plan personalizado.")
        fuentes = ", ".join(f["id"] for f in BC["metadata"]["fuentes"])
        linea(f"\nFuentes: {fuentes}")
        linea("="*60)

        t.configure(state="disabled")
        t.yview_moveto(0)


# ══════════════════════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    app.mainloop()
