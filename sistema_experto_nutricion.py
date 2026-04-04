"""
Sistema Experto de Nutrición (México)
Base de conocimiento: base_conocimiento_nutricion.json
Fuentes: ENSANUT, NOM-043-SSA2-2012, SMAE 4ª ed., FAO/OMS, DRI (IOM)
"""

import json
import math
import random
import os

# ─────────────────────────── CARGA DE BASE DE CONOCIMIENTO ───────────────────
def cargar_base_conocimiento():
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "base_conocimiento_nutricion.json")
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)

BC = cargar_base_conocimiento()

# ─────────────────────────── UTILIDADES ──────────────────────────────────────
SEPARADOR = "=" * 65
LINEA = "-" * 65

def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")

def encabezado(titulo):
    print(f"\n{SEPARADOR}")
    print(f"  {titulo}")
    print(SEPARADOR)

def subtitulo(texto):
    print(f"\n{LINEA}")
    print(f"  {texto}")
    print(LINEA)

def pedir_float(mensaje, minimo=0, maximo=999):
    while True:
        try:
            valor = float(input(f"  {mensaje}: "))
            if minimo <= valor <= maximo:
                return valor
            print(f"    * Ingrese un valor entre {minimo} y {maximo}.")
        except ValueError:
            print("    * Ingrese un número válido.")

def pedir_int(mensaje, minimo=0, maximo=999):
    return int(pedir_float(mensaje, minimo, maximo))

def pedir_opcion(mensaje, opciones):
    """Muestra opciones numeradas y devuelve la clave seleccionada."""
    print(f"\n  {mensaje}")
    claves = list(opciones.keys())
    for i, clave in enumerate(claves, 1):
        print(f"    {i}. {opciones[clave]}")
    while True:
        try:
            sel = int(input("  Seleccione una opción: "))
            if 1 <= sel <= len(claves):
                return claves[sel - 1]
        except ValueError:
            pass
        print(f"    * Ingrese un número entre 1 y {len(claves)}.")

def pedir_si_no(mensaje):
    while True:
        resp = input(f"  {mensaje} (s/n): ").strip().lower()
        if resp in ("s", "si", "sí"):
            return True
        if resp in ("n", "no"):
            return False
        print("    * Responda 's' o 'n'.")


# ─────────────────────────── MÓDULO 1: RECOLECCIÓN DE DATOS ──────────────────
def recolectar_datos():
    encabezado("SISTEMA EXPERTO DE NUTRICIÓN — MÉXICO")
    print("  Basado en NOM-043, SMAE, FAO/OMS, DRI")
    print("  Fuente: Base de conocimiento estructurada v1.0")

    subtitulo("DATOS PERSONALES")
    nombre = input("  Nombre: ").strip() or "Usuario"
    sexo = pedir_opcion("Sexo biológico:", {
        "M": "Masculino",
        "F": "Femenino"
    })
    edad = pedir_int("Edad (años)", 10, 120)
    peso = pedir_float("Peso actual (kg)", 20, 300)
    talla = pedir_float("Estatura (cm)", 100, 250)

    subtitulo("NIVEL DE ACTIVIDAD FÍSICA")
    actividad = pedir_opcion("¿Cuál describe mejor su actividad diaria?", {
        "sedentario": "Sedentario — Trabajo de escritorio, sin ejercicio",
        "ligera": "Ligera — Caminar poco, tareas ligeras del hogar",
        "moderada": "Moderada — Ejercicio regular, trabajo de pie (~60 min/día)",
        "intensa": "Intensa — Ejercicio vigoroso diario, trabajo pesado"
    })

    subtitulo("OBJETIVO NUTRICIONAL")
    objetivo = pedir_opcion("¿Cuál es su objetivo principal?", {
        "perdida": "Pérdida de grasa corporal",
        "mantenimiento": "Mantenimiento de peso",
        "ganancia": "Ganancia de masa muscular",
        "rendimiento": "Rendimiento deportivo (resistencia)",
        "control_glucemico": "Control glucémico (diabetes/prediabetes)"
    })

    subtitulo("CONDICIONES MÉDICAS")
    condiciones = []
    opciones_cond = {
        "diabetes": "Diabetes tipo 2 / Prediabetes",
        "hipertension": "Hipertensión arterial",
        "embarazo": "Embarazo",
        "lactancia": "Lactancia",
        "erc": "Enfermedad renal crónica",
        "ninguna": "Ninguna"
    }
    print("  Seleccione sus condiciones médicas:")
    for clave, desc in opciones_cond.items():
        if clave == "ninguna":
            continue
        if pedir_si_no(f"  ¿{desc}?"):
            condiciones.append(clave)
    if not condiciones:
        condiciones.append("ninguna")

    trimestre = None
    if "embarazo" in condiciones:
        trimestre = pedir_int("¿En qué trimestre se encuentra? (1, 2 o 3)", 1, 3)

    subtitulo("PREFERENCIAS ALIMENTARIAS")
    preferencia = pedir_opcion("Tipo de alimentación:", {
        "omnivoro": "Omnívoro (come de todo)",
        "vegetariano": "Vegetariano (sin carne ni pescado)",
        "vegano": "Vegano (sin productos animales)"
    })

    alergias = input("  Alergias/intolerancias (separadas por coma, o 'ninguna'): ").strip()
    if alergias.lower() in ("ninguna", "no", ""):
        alergias = []
    else:
        alergias = [a.strip().lower() for a in alergias.split(",")]

    return {
        "nombre": nombre,
        "sexo": sexo,
        "edad": edad,
        "peso": peso,
        "talla": talla,
        "talla_m": talla / 100,
        "actividad": actividad,
        "objetivo": objetivo,
        "condiciones": condiciones,
        "trimestre": trimestre,
        "preferencia": preferencia,
        "alergias": alergias,
    }


# ─────────────────────────── MÓDULO 2: CÁLCULO DE IMC ───────────────────────
def calcular_imc(datos):
    imc = datos["peso"] / (datos["talla_m"] ** 2)
    datos["imc"] = round(imc, 1)

    reglas = BC["reglas_sistema_experto"]["reglas_clasificacion_IMC"]
    for regla in reglas:
        cond = regla["condicion"].replace("IMC", str(imc))
        # Parsear condición
        if evaluar_condicion_imc(imc, regla["condicion"]):
            datos["clasificacion_imc"] = regla["clasificacion"]
            datos["accion_imc"] = regla["accion"]
            break
    return datos

def evaluar_condicion_imc(imc, condicion):
    """Evalúa las condiciones de IMC de la base de conocimiento."""
    cond = condicion.replace("IMC", "").strip()
    if cond.startswith("< "):
        return imc < float(cond[2:])
    elif cond.startswith("≥"):
        return imc >= float(cond[2:].strip())
    elif "–" in cond:
        partes = cond.split("–")
        low = float(partes[0].strip())
        high = float(partes[1].strip())
        return low <= imc <= high
    return False


# ─────────────────────────── MÓDULO 3: PESO IDEAL Y CORREGIDO ───────────────
def calcular_peso_ideal(datos):
    """Fórmula de Lorentz simplificada."""
    talla_cm = datos["talla"]
    if datos["sexo"] == "M":
        pi = talla_cm - 100 - ((talla_cm - 150) / 4)
    else:
        pi = talla_cm - 100 - ((talla_cm - 150) / 2.5)
    datos["peso_ideal"] = round(max(pi, 40), 1)

    # Peso corregido para obesidad (de la BC)
    if datos["imc"] >= 30:
        pc = (datos["peso"] - datos["peso_ideal"]) * 0.25 + datos["peso_ideal"]
        datos["peso_calculo"] = round(pc, 1)
        datos["usa_peso_corregido"] = True
    else:
        datos["peso_calculo"] = datos["peso"]
        datos["usa_peso_corregido"] = False
    return datos


# ─────────────────────────── MÓDULO 4: GASTO ENERGÉTICO BASAL ───────────────
def calcular_geb(datos):
    peso = datos["peso_calculo"]
    talla = datos["talla"]
    edad = datos["edad"]
    sexo = datos["sexo"]

    # Seleccionar fórmula según condición
    if datos["imc"] >= 25:
        # Mifflin-St Jeor (más precisa para sobrepeso/obesidad, según BC)
        formulas = BC["calculo_requerimientos_energeticos"]["ecuaciones_gasto_energetico_basal"]["mifflin_st_jeor"]
        if sexo == "M":
            geb = (10 * peso) + (6.25 * talla) - (5 * edad) + 5
        else:
            geb = (10 * peso) + (6.25 * talla) - (5 * edad) - 161
        datos["formula_geb"] = "Mifflin-St Jeor"
    else:
        # Harris-Benedict
        formulas = BC["calculo_requerimientos_energeticos"]["ecuaciones_gasto_energetico_basal"]["harris_benedict"]
        if sexo == "M":
            geb = 66.47 + (13.75 * peso) + (5.0 * talla) - (6.74 * edad)
        else:
            geb = 655.1 + (9.56 * peso) + (1.85 * talla) - (4.68 * edad)
        datos["formula_geb"] = "Harris-Benedict"

    datos["geb"] = round(geb, 0)
    return datos


# ─────────────────────────── MÓDULO 5: GASTO ENERGÉTICO TOTAL ────────────────
def calcular_get(datos):
    factores = BC["calculo_requerimientos_energeticos"]["factores_actividad_fisica_FAO"]
    sexo_key = "hombres" if datos["sexo"] == "M" else "mujeres"
    fa = factores[datos["actividad"]][sexo_key]
    datos["factor_actividad"] = fa

    get_base = datos["geb"] * fa

    # Ajuste por objetivo
    objetivo = datos["objetivo"]
    reglas_obj = BC["reglas_sistema_experto"]["reglas_distribucion_por_objetivo"]
    regla_sel = next((r for r in reglas_obj if _mapear_objetivo(objetivo) == r["objetivo"]), None)

    ajuste = 0
    if regla_sel:
        if "deficit_kcal" in regla_sel:
            rango = regla_sel["deficit_kcal"].split("-")
            ajuste = -(int(rango[0]) + int(rango[1])) / 2
        elif "superavit_kcal" in regla_sel:
            rango = regla_sel["superavit_kcal"].split("-")
            ajuste = (int(rango[0]) + int(rango[1])) / 2

    # Ajuste por embarazo
    if "embarazo" in datos["condiciones"] and datos["trimestre"]:
        extras = BC["condiciones_especiales"]["embarazo"]["energia_extra_kcal"]
        trim_map = {1: "primer_trimestre", 2: "segundo_trimestre", 3: "tercer_trimestre"}
        ajuste += extras[trim_map[datos["trimestre"]]]

    # Ajuste por lactancia
    if "lactancia" in datos["condiciones"]:
        ajuste += BC["condiciones_especiales"]["lactancia"]["energia_extra_kcal"]

    get_final = get_base + ajuste

    # Verificar mínimos seguros
    minimo = 1500 if datos["sexo"] == "M" else 1200
    if get_final < minimo:
        datos["alerta_calorias_bajas"] = True
        get_final = minimo

    datos["get_base"] = round(get_base, 0)
    datos["ajuste_kcal"] = round(ajuste, 0)
    datos["get_final"] = round(get_final, 0)
    return datos

def _mapear_objetivo(objetivo):
    mapa = {
        "perdida": "Pérdida de grasa",
        "mantenimiento": "Mantenimiento",
        "ganancia": "Ganancia muscular",
        "rendimiento": "Rendimiento deportivo (resistencia)",
        "control_glucemico": "Control glucémico (diabetes/prediabetes)"
    }
    return mapa.get(objetivo, "Mantenimiento")


# ─────────────────────────── MÓDULO 6: MACRONUTRIENTES ───────────────────────
def calcular_macronutrientes(datos):
    reglas = BC["reglas_sistema_experto"]["reglas_distribucion_por_objetivo"]
    obj_nombre = _mapear_objetivo(datos["objetivo"])
    regla = next((r for r in reglas if r["objetivo"] == obj_nombre), reglas[1])

    def promedio_rango(s):
        partes = s.split("-")
        return (float(partes[0]) + float(partes[1])) / 2

    cho_pct = promedio_rango(regla["carbohidratos_pct"])
    prot_pct = promedio_rango(regla["proteinas_pct"])
    lip_pct = promedio_rango(regla["lipidos_pct"])

    kcal = datos["get_final"]

    cho_g = round((kcal * cho_pct / 100) / 4, 1)
    prot_g = round((kcal * prot_pct / 100) / 4, 1)
    lip_g = round((kcal * lip_pct / 100) / 9, 1)

    # Verificar proteína mínima por kg
    req_prot = BC["requerimientos_proteicos_especificos"]
    prot_min_g_kg = req_prot["poblacion_general_g_por_kg"]
    if datos["edad"] >= 60:
        prot_min_g_kg = 1.1  # promedio de 1.0-1.2
    if datos["objetivo"] == "ganancia":
        prot_min_g_kg = 1.8  # promedio de 1.6-2.0
    if datos["objetivo"] == "rendimiento":
        prot_min_g_kg = 1.3

    prot_min = datos["peso_calculo"] * prot_min_g_kg
    if prot_g < prot_min:
        prot_g = round(prot_min, 1)
        # Recalcular lípidos y carbohidratos
        kcal_prot = prot_g * 4
        kcal_restante = kcal - kcal_prot
        lip_g = round((kcal_restante * lip_pct / (cho_pct + lip_pct)) / 9, 1)
        cho_g = round((kcal_restante - lip_g * 9) / 4, 1)

    datos["macros"] = {
        "carbohidratos_g": cho_g,
        "proteinas_g": prot_g,
        "lipidos_g": lip_g,
        "carbohidratos_pct": round(cho_pct, 0),
        "proteinas_pct": round(prot_pct, 0),
        "lipidos_pct": round(lip_pct, 0),
    }

    # Fibra
    fibra = BC["distribucion_macronutrientes"]["fibra_dietetica"]
    datos["macros"]["fibra_g"] = max(25, round(14 * kcal / 1000, 0))

    # Agua
    agua = BC["distribucion_macronutrientes"]["agua"]
    clave = "hombres_AI_litros_dia" if datos["sexo"] == "M" else "mujeres_AI_litros_dia"
    datos["macros"]["agua_litros"] = agua[clave]

    return datos


# ─────────────────────────── MÓDULO 7: EQUIVALENTES SMAE ────────────────────
def calcular_equivalentes(datos):
    """Convierte gramos de macronutrientes a equivalentes SMAE."""
    kcal = datos["get_final"]
    cho_g = datos["macros"]["carbohidratos_g"]
    prot_g = datos["macros"]["proteinas_g"]
    lip_g = datos["macros"]["lipidos_g"]

    # Distribución aproximada por grupos SMAE
    # Verduras: 25 kcal, 2g prot, 0g lip, 4g CHO
    # Frutas: 60 kcal, 0g prot, 0g lip, 15g CHO
    # Cereales s/g: 70 kcal, 2g prot, 0g lip, 15g CHO
    # Leguminosas: 120 kcal, 8g prot, 1g lip, 20g CHO
    # AOA mod grasa: 75 kcal, 7g prot, 5g lip, 0g CHO
    # Leche semidesc: 110 kcal, 9g prot, 4g lip, 12g CHO
    # Aceites: 45 kcal, 0g prot, 5g lip, 0g CHO

    # Heurística basada en rangos calóricos
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

    # Ajustar si es vegetariano/vegano
    if datos["preferencia"] == "vegetariano":
        eq["leguminosas"] += 2
        eq["aoa"] = max(0, eq["aoa"] - 2)  # solo lácteos/huevo
        eq["leche"] += 1
    elif datos["preferencia"] == "vegano":
        eq["leguminosas"] += 3
        eq["aoa"] = 0
        eq["leche"] = 0
        eq["cereales"] += 2
        eq["aceites"] += 1

    # Si diabetes, reducir azúcares y ajustar
    if "diabetes" in datos["condiciones"] or datos["objetivo"] == "control_glucemico":
        eq["azucares"] = 0
        eq["frutas"] = min(eq["frutas"], 2)

    datos["equivalentes"] = eq
    return datos


# ─────────────────────────── MÓDULO 8: DISTRIBUCIÓN POR TIEMPOS DE COMIDA ───
def distribuir_tiempos_comida(datos):
    dist = BC["reglas_sistema_experto"]["reglas_tiempos_comida"]["general"]["distribucion_ejemplo"]
    eq = datos["equivalentes"]

    tiempos = {
        "Desayuno (25%)": {},
        "Colación AM (10%)": {},
        "Comida (30%)": {},
        "Colación PM (10%)": {},
        "Cena (25%)": {}
    }

    # Distribución de equivalentes por tiempo de comida
    distribucion = {
        "Desayuno (25%)":    {"verduras": 1, "frutas": 1, "cereales": 0.25, "leguminosas": 0, "aoa": 0.25, "leche": 0.5, "aceites": 0.2, "azucares": 0},
        "Colación AM (10%)": {"verduras": 0, "frutas": 0.2, "cereales": 0.1, "leguminosas": 0, "aoa": 0, "leche": 0.25, "aceites": 0.1, "azucares": 0},
        "Comida (30%)":      {"verduras": 0.4, "frutas": 0, "cereales": 0.35, "leguminosas": 0.5, "aoa": 0.5, "leche": 0, "aceites": 0.3, "azucares": 0.5},
        "Colación PM (10%)": {"verduras": 0, "frutas": 0.2, "cereales": 0.1, "leguminosas": 0, "aoa": 0, "leche": 0.25, "aceites": 0.1, "azucares": 0.5},
        "Cena (25%)":        {"verduras": 0.3, "frutas": 0, "cereales": 0.2, "leguminosas": 0.5, "aoa": 0.25, "leche": 0, "aceites": 0.3, "azucares": 0}
    }

    # Calcular distribución normalizada
    for tiempo, proporciones in distribucion.items():
        total_prop = sum(proporciones.values()) or 1
        for grupo in eq:
            cant = round(eq[grupo] * proporciones.get(grupo, 0) /
                         sum(distribucion[t].get(grupo, 0) for t in distribucion) if
                         sum(distribucion[t].get(grupo, 0) for t in distribucion) > 0 else 0)
            tiempos[tiempo][grupo] = max(cant, 0)

    # Simplificar: distribución directa por proporciones fijas
    tiempos = {
        "Desayuno": {
            "verduras": max(1, eq["verduras"] // 4),
            "frutas": max(1, eq["frutas"] // 3),
            "cereales": max(1, eq["cereales"] // 4),
            "leguminosas": 0,
            "aoa": max(1, eq["aoa"] // 3),
            "leche": max(0, eq["leche"] // 2),
            "aceites": max(1, eq["aceites"] // 4),
        },
        "Colación AM": {
            "frutas": 1,
            "aceites": 1 if eq["aceites"] > 3 else 0,
        },
        "Comida": {
            "verduras": max(1, eq["verduras"] // 3),
            "cereales": max(1, eq["cereales"] // 3),
            "leguminosas": max(1, eq["leguminosas"]),
            "aoa": max(1, eq["aoa"] // 3),
            "aceites": max(1, eq["aceites"] // 3),
        },
        "Colación PM": {
            "verduras": 1,
            "leche": max(0, (eq["leche"] + 1) // 2),
        },
        "Cena": {
            "verduras": max(1, eq["verduras"] // 3),
            "cereales": max(1, eq["cereales"] // 4),
            "aoa": max(1, eq["aoa"] // 3),
            "aceites": max(1, eq["aceites"] // 4),
        },
    }

    datos["tiempos_comida"] = tiempos
    return datos


# ─────────────────────────── MÓDULO 9: MENÚ CON ALIMENTOS ───────────────────
ALIMENTOS_POR_GRUPO = {
    "verduras": [
        ("Nopales cocidos", "1 taza"),
        ("Brócoli cocido", "½ taza"),
        ("Calabaza cocida", "½ taza"),
        ("Chayote cocido", "½ taza"),
        ("Espinacas cocidas", "½ taza"),
        ("Jitomate crudo", "1 pieza"),
        ("Lechuga", "1 taza"),
        ("Zanahoria rallada", "½ taza"),
        ("Chile poblano", "1 pieza"),
        ("Flor de calabaza", "1 taza"),
        ("Quelites/Verdolagas", "½ taza"),
        ("Ejotes cocidos", "½ taza"),
    ],
    "frutas": [
        ("Guayaba", "2 piezas"),
        ("Papaya picada", "1 taza"),
        ("Manzana", "1 pieza mediana"),
        ("Plátano", "½ pieza"),
        ("Naranja", "1 pieza"),
        ("Mango", "½ pieza"),
        ("Melón picado", "1 taza"),
        ("Fresa", "1 taza"),
        ("Mandarina", "2 piezas"),
    ],
    "cereales": [
        ("Tortilla de maíz", "1 pieza"),
        ("Arroz cocido", "⅓ taza"),
        ("Avena en hojuelas", "⅓ taza"),
        ("Pan integral", "1 rebanada"),
        ("Bolillo sin migajón", "½ pieza"),
        ("Elote cocido", "½ pieza"),
        ("Camote cocido", "⅓ taza"),
        ("Pasta cocida", "½ taza"),
        ("Amaranto", "¼ taza"),
    ],
    "leguminosas": [
        ("Frijol negro cocido", "½ taza"),
        ("Lenteja cocida", "½ taza"),
        ("Garbanzo cocido", "½ taza"),
        ("Habas cocidas", "½ taza"),
        ("Alubia cocida", "½ taza"),
    ],
    "aoa": [
        ("Pechuga de pollo s/piel", "30 g"),
        ("Atún en agua (drenado)", "30 g"),
        ("Huevo entero", "1 pieza"),
        ("Queso panela", "40 g"),
        ("Sardina en aceite", "30 g"),
        ("Carne de res magra", "30 g"),
        ("Pescado blanco", "30 g"),
    ],
    "aoa_vegetariano": [
        ("Huevo entero", "1 pieza"),
        ("Queso panela", "40 g"),
        ("Queso cottage", "¼ taza"),
        ("Yogurt griego natural", "¾ taza"),
    ],
    "leche": [
        ("Leche semidescremada", "1 taza (240 mL)"),
        ("Yogurt natural", "1 taza"),
        ("Leche descremada", "1 taza (240 mL)"),
    ],
    "aceites": [
        ("Aceite de oliva", "1 cucharadita"),
        ("Aguacate", "⅓ pieza"),
        ("Almendras", "14 piezas"),
        ("Nuez", "4 mitades"),
        ("Cacahuate", "10 piezas"),
        ("Semillas de chía", "1 cucharada"),
    ],
    "azucares": [
        ("Miel de abeja", "1 cucharadita"),
        ("Azúcar mascabado", "2 cucharaditas"),
    ],
}

def generar_menu_dia(datos):
    """Genera un menú para un día con variación aleatoria."""
    tiempos = datos["tiempos_comida"]
    menu = {}
    pref = datos["preferencia"]
    alergias = datos["alergias"]

    for tiempo, grupos in tiempos.items():
        platos = []
        for grupo, cantidad in grupos.items():
            if cantidad <= 0:
                continue
            # Seleccionar grupo de alimentos correcto
            if grupo == "aoa" and pref == "vegano":
                continue
            if grupo == "leche" and pref == "vegano":
                platos.append(("Bebida de soya", "1 taza", cantidad))
                continue

            clave_grupo = grupo
            if grupo == "aoa" and pref == "vegetariano":
                clave_grupo = "aoa_vegetariano"

            opciones = ALIMENTOS_POR_GRUPO.get(clave_grupo, [])
            if not opciones:
                continue

            # Filtrar alergias
            opciones_filtradas = [
                o for o in opciones
                if not any(a in o[0].lower() for a in alergias)
            ]
            if not opciones_filtradas:
                opciones_filtradas = opciones

            seleccion = random.choice(opciones_filtradas)
            porcion_texto = seleccion[1]
            if cantidad > 1:
                porcion_texto = f"{cantidad} eq. → {seleccion[1]} c/u"
            platos.append((seleccion[0], porcion_texto, cantidad))

        menu[tiempo] = platos

    datos["menu"] = menu
    return datos


# ─────────────────────────── MÓDULO 10: ALERTAS CLÍNICAS ────────────────────
def generar_alertas(datos):
    alertas = []
    reglas_alertas = BC["reglas_sistema_experto"]["reglas_alertas_clinicas"]

    # Alerta: calorías muy bajas
    if datos.get("alerta_calorias_bajas"):
        alertas.append(
            "ALERTA: El cálculo resultó en calorías muy bajas. Se ajustó al "
            f"mínimo seguro ({'1500' if datos['sexo'] == 'M' else '1200'} kcal). "
            "Requiere supervisión médica."
        )

    # Alerta: obesidad
    if datos["imc"] >= 35:
        alertas.append(
            f"ALERTA: {datos['clasificacion_imc']} (IMC {datos['imc']}). "
            "Se recomienda derivación a equipo multidisciplinario."
        )

    # Alerta: diabetes
    if "diabetes" in datos["condiciones"]:
        alertas.append(
            "ALERTA: Paciente con diabetes/prediabetes. Se priorizaron "
            "carbohidratos de bajo índice glucémico. Distribuir carbohidratos "
            "uniformemente. Monitorear glucosa."
        )

    # Alerta: hipertensión
    if "hipertension" in datos["condiciones"]:
        principios = BC["condiciones_especiales"]["hipertension_arterial"]["dieta_DASH_principios"]
        alertas.append(
            "ALERTA: Hipertensión arterial. Se recomienda dieta DASH: "
            "sodio <2300 mg/día (ideal <1500), potasio ~4700 mg/día."
        )

    # Alerta: embarazo
    if "embarazo" in datos["condiciones"]:
        nut_crit = BC["condiciones_especiales"]["embarazo"]["nutrientes_criticos"]
        alertas.append(
            f"ALERTA: Embarazo (trimestre {datos['trimestre']}). Nutrientes críticos: "
            f"ácido fólico ≥{nut_crit['acido_folico_ug_DFE']} µg, "
            f"hierro ≥{nut_crit['hierro_mg']} mg, "
            f"calcio ≥{nut_crit['calcio_mg']} mg, "
            f"DHA ≥{nut_crit['omega_3_DHA_mg_dia']} mg/día."
        )

    # Alerta: lactancia
    if "lactancia" in datos["condiciones"]:
        alertas.append(
            "ALERTA: Periodo de lactancia. Energía extra: +500 kcal/día. "
            "Asegurar calcio, ácido fólico y vitamina B12."
        )

    # Alerta: adulto mayor
    if datos["edad"] >= 60:
        alertas.append(
            "ALERTA: Adulto mayor. Proteína ≥1.0 g/kg/día. "
            "Vitamina D: 20 µg/día. Calcio: 1200 mg/día. "
            "Considerar suplementación de B12."
        )

    # Alerta: ERC
    if "erc" in datos["condiciones"]:
        alertas.append(
            "ALERTA: Enfermedad renal crónica detectada. Este plan es "
            "orientativo. REQUIERE supervisión de nefrólogo y nutriólogo. "
            "Restricción de proteína, sodio, potasio y fósforo según estadio."
        )

    # Alerta: mujer premenopáusica (hierro)
    if datos["sexo"] == "F" and datos["edad"] < 50 and "embarazo" not in datos["condiciones"]:
        alertas.append(
            "NOTA: Mujer premenopáusica. Requerimiento de hierro: 18 mg/día. "
            "Incluir fuentes de hierro hemo + vitamina C para absorción."
        )

    datos["alertas"] = alertas
    return datos


# ─────────────────────────── MÓDULO 11: ÍNDICE GLUCÉMICO ────────────────────
def obtener_recomendaciones_ig(datos):
    """Si el usuario tiene diabetes, recomendar alimentos de IG bajo."""
    if "diabetes" not in datos["condiciones"] and datos["objetivo"] != "control_glucemico":
        return datos

    ig_data = BC["indice_glucemico_referencia"]["alimentos_comunes"]
    ig_bajo = [a for a in ig_data if a["categoria"] == "bajo"]
    ig_alto = [a for a in ig_data if a["categoria"] == "alto"]

    datos["ig_recomendaciones"] = {
        "preferir": ig_bajo,
        "limitar": ig_alto,
    }
    return datos


# ─────────────────────────── MÓDULO 12: HIDRATACIÓN DEPORTIVA ────────────────
def obtener_recomendaciones_deporte(datos):
    if datos["objetivo"] != "rendimiento" and datos["actividad"] != "intensa":
        return datos

    hidratacion = BC["nutricion_deportiva_CONADE"]["hidratacion_deportiva"]
    platos = BC["nutricion_deportiva_CONADE"]["platos_nutricionales"]
    tiempos_dep = BC["reglas_sistema_experto"]["reglas_tiempos_comida"]["deportista"]

    datos["deporte"] = {
        "hidratacion": hidratacion,
        "plato_recomendado": platos[1] if datos["actividad"] == "moderada" else platos[2],
        "tiempos_entrenamiento": tiempos_dep,
    }
    return datos


# ─────────────────────────── PRESENTACIÓN DE RESULTADOS ─────────────────────
def mostrar_resultados(datos):
    limpiar_pantalla()
    encabezado(f"PLAN NUTRICIONAL — {datos['nombre'].upper()}")
    print(f"  Fecha de generación: {BC['metadata']['fecha_compilacion']}")
    print(f"  Fuentes: NOM-043, SMAE, FAO/OMS, DRI (IOM)")

    # --- Perfil ---
    subtitulo("PERFIL DEL PACIENTE")
    sexo_txt = "Masculino" if datos["sexo"] == "M" else "Femenino"
    print(f"  Sexo: {sexo_txt}  |  Edad: {datos['edad']} años")
    print(f"  Peso: {datos['peso']} kg  |  Estatura: {datos['talla']} cm")
    print(f"  Actividad: {datos['actividad'].capitalize()}")
    print(f"  Objetivo: {_mapear_objetivo(datos['objetivo'])}")
    if datos["condiciones"] != ["ninguna"]:
        print(f"  Condiciones: {', '.join(datos['condiciones'])}")
    if datos["alergias"]:
        print(f"  Alergias: {', '.join(datos['alergias'])}")
    print(f"  Preferencia: {datos['preferencia'].capitalize()}")

    # --- IMC ---
    subtitulo("EVALUACIÓN ANTROPOMÉTRICA")
    print(f"  IMC: {datos['imc']} kg/m²")
    print(f"  Clasificación: {datos['clasificacion_imc']}")
    print(f"  Recomendación: {datos['accion_imc']}")
    print(f"  Peso ideal estimado: {datos['peso_ideal']} kg")
    if datos["usa_peso_corregido"]:
        print(f"  Peso corregido (para cálculos): {datos['peso_calculo']} kg")

    # --- Energía ---
    subtitulo("REQUERIMIENTOS ENERGÉTICOS")
    print(f"  Fórmula utilizada: {datos['formula_geb']}")
    print(f"  Gasto Energético Basal (GEB): {datos['geb']:.0f} kcal/día")
    print(f"  Factor de actividad ({datos['actividad']}): {datos['factor_actividad']}")
    print(f"  GET sin ajustar: {datos['get_base']:.0f} kcal/día")
    if datos["ajuste_kcal"] != 0:
        signo = "+" if datos["ajuste_kcal"] > 0 else ""
        print(f"  Ajuste por objetivo/condición: {signo}{datos['ajuste_kcal']:.0f} kcal")
    print(f"  >>> GET FINAL: {datos['get_final']:.0f} kcal/día <<<")

    # --- Macronutrientes ---
    subtitulo("DISTRIBUCIÓN DE MACRONUTRIENTES")
    m = datos["macros"]
    print(f"  Carbohidratos: {m['carbohidratos_g']:.0f} g  ({m['carbohidratos_pct']:.0f}%)")
    print(f"  Proteínas:     {m['proteinas_g']:.0f} g  ({m['proteinas_pct']:.0f}%)")
    print(f"  Lípidos:       {m['lipidos_g']:.0f} g  ({m['lipidos_pct']:.0f}%)")
    print(f"  Fibra:         ≥{m['fibra_g']:.0f} g/día")
    print(f"  Agua:          ≥{m['agua_litros']} L/día (incluye alimentos)")

    # --- Equivalentes SMAE ---
    subtitulo("EQUIVALENTES SMAE (porciones diarias)")
    eq = datos["equivalentes"]
    nombres = {
        "verduras": "Verduras", "frutas": "Frutas",
        "cereales": "Cereales y Tubérculos", "leguminosas": "Leguminosas",
        "aoa": "Alimentos de Origen Animal", "leche": "Leche",
        "aceites": "Aceites y Grasas", "azucares": "Azúcares"
    }
    for grupo, nombre in nombres.items():
        if eq.get(grupo, 0) > 0:
            print(f"  {nombre:.<35} {eq[grupo]} eq.")

    # --- Menú del día ---
    subtitulo("MENÚ EJEMPLO DEL DÍA")
    for tiempo, platos in datos["menu"].items():
        print(f"\n  ▸ {tiempo.upper()}")
        if not platos:
            print("    (Sin alimentos asignados)")
            continue
        for alimento, porcion, cantidad in platos:
            print(f"    • {alimento:.<30} {porcion}")

    # --- Índice glucémico ---
    if "ig_recomendaciones" in datos:
        subtitulo("GUÍA DE ÍNDICE GLUCÉMICO")
        print("  PREFERIR (IG bajo < 55):")
        for a in datos["ig_recomendaciones"]["preferir"][:8]:
            print(f"    ✓ {a['alimento']} (IG: {a['IG']})")
        print("\n  LIMITAR (IG alto ≥ 70):")
        for a in datos["ig_recomendaciones"]["limitar"][:5]:
            print(f"    ✗ {a['alimento']} (IG: {a['IG']})")

    # --- Recomendaciones deportivas ---
    if "deporte" in datos:
        subtitulo("NUTRICIÓN DEPORTIVA (CONADE)")
        dep = datos["deporte"]
        plato = dep["plato_recomendado"]
        print(f"  Plato recomendado: {plato['fase']} ({plato['color']})")
        for k, v in plato["distribucion"].items():
            print(f"    • {k.replace('_', ' ').capitalize()}: {v}%")
        print(f"\n  Hidratación:")
        h = dep["hidratacion"]
        print(f"    Pre-ejercicio:  {h['pre_ejercicio']}")
        print(f"    Durante:        {h['durante_ejercicio']}")
        print(f"    Post-ejercicio: {h['post_ejercicio']}")
        print(f"\n  Tiempos de entrenamiento:")
        for k, v in dep["tiempos_entrenamiento"].items():
            print(f"    • {k.replace('_', ' ').capitalize()}: {v}")

    # --- Alertas ---
    if datos["alertas"]:
        subtitulo("ALERTAS CLÍNICAS")
        for i, alerta in enumerate(datos["alertas"], 1):
            print(f"  {i}. {alerta}")

    # --- Plato del Bien Comer ---
    subtitulo("REFERENCIA: PLATO DEL BIEN COMER (NOM-043)")
    grupos_pbc = BC["normativa_mexicana"]["NOM_043_SSA2_2012"]["plato_del_bien_comer"]["grupos"]
    for g in grupos_pbc:
        print(f"  [{g['color'].upper()}] {g['grupo']} — {g['proporcion']}")
        print(f"         Función: {g['funcion_principal'][:70]}")

    # --- Contexto epidemiológico ---
    subtitulo("CONTEXTO: PREVALENCIAS EN MÉXICO (ENSANUT)")
    epi = BC["contexto_epidemiologico_mexico"]["prevalencias_adultos"]
    print(f"  Sobrepeso + Obesidad: {epi['sobrepeso_obesidad_combinado_pct']}% de adultos")
    print(f"  Diabetes tipo 2: {epi['diabetes_tipo_2']['total_pct']}%")
    print(f"  Hipertensión arterial: {epi['hipertension_arterial']['total_pct']}%")
    inseg = BC["contexto_epidemiologico_mexico"]["inseguridad_alimentaria"]
    print(f"  Inseguridad alimentaria (algún grado): {inseg['algun_grado_pct']}%")

    # --- Disclaimer ---
    subtitulo("AVISO IMPORTANTE")
    print("  Este plan es ORIENTATIVO y generado por un sistema experto.")
    print("  NO sustituye la consulta con un profesional de la nutrición.")
    print("  Consulte a un nutriólogo certificado para un plan personalizado.")
    print("  Fuentes: " + ", ".join(f["id"] for f in BC["metadata"]["fuentes"]))
    print(f"\n{SEPARADOR}\n")


# ─────────────────────────── MÓDULO 13: COMPOSICIÓN DE ALIMENTOS ─────────────
def consultar_alimento():
    """Permite consultar la composición de un alimento de la base."""
    alimentos = BC["composicion_alimentos_mexicanos_referencia"]["alimentos"]
    encabezado("CONSULTA DE COMPOSICIÓN DE ALIMENTOS")
    print("  Alimentos disponibles en la base:\n")
    for i, a in enumerate(alimentos, 1):
        print(f"    {i:2d}. {a['nombre']}")

    while True:
        try:
            sel = int(input("\n  Seleccione un alimento (0 para volver): "))
            if sel == 0:
                return
            if 1 <= sel <= len(alimentos):
                a = alimentos[sel - 1]
                subtitulo(f"COMPOSICIÓN: {a['nombre'].upper()} (por 100g)")
                for clave, valor in a.items():
                    if clave == "nombre":
                        continue
                    nombre_bonito = clave.replace("_", " ").capitalize()
                    print(f"  {nombre_bonito:.<35} {valor}")
                print()
            else:
                print("    * Número fuera de rango.")
        except ValueError:
            print("    * Ingrese un número válido.")

        if not pedir_si_no("¿Consultar otro alimento?"):
            return


# ─────────────────────────── MENÚ PRINCIPAL ──────────────────────────────────
def menu_principal():
    while True:
        limpiar_pantalla()
        encabezado("SISTEMA EXPERTO DE NUTRICIÓN — MÉXICO")
        print("  Base de conocimiento: NOM-043, SMAE, FAO/OMS, DRI, ENSANUT\n")
        print("    1. Generar plan nutricional personalizado")
        print("    2. Consultar composición de alimentos")
        print("    3. Ver contexto epidemiológico de México")
        print("    4. Ver principios de la dieta correcta (NOM-043)")
        print("    5. Salir\n")

        opcion = input("  Seleccione una opción: ").strip()

        if opcion == "1":
            try:
                datos = recolectar_datos()
                datos = calcular_imc(datos)
                datos = calcular_peso_ideal(datos)
                datos = calcular_geb(datos)
                datos = calcular_get(datos)
                datos = calcular_macronutrientes(datos)
                datos = calcular_equivalentes(datos)
                datos = distribuir_tiempos_comida(datos)
                datos = generar_menu_dia(datos)
                datos = obtener_recomendaciones_ig(datos)
                datos = obtener_recomendaciones_deporte(datos)
                datos = generar_alertas(datos)
                mostrar_resultados(datos)
            except KeyboardInterrupt:
                print("\n  Cancelado.")
            input("  Presione Enter para continuar...")

        elif opcion == "2":
            consultar_alimento()

        elif opcion == "3":
            limpiar_pantalla()
            encabezado("CONTEXTO EPIDEMIOLÓGICO — MÉXICO")
            epi = BC["contexto_epidemiologico_mexico"]
            pa = epi["prevalencias_adultos"]
            print(f"\n  Fuente: {epi['fuente']}\n")
            print(f"  Sobrepeso: {pa['sobrepeso']['total_pct']}%")
            print(f"    Hombres: {pa['sobrepeso']['hombres_pct']}% | Mujeres: {pa['sobrepeso']['mujeres_pct']}%")
            print(f"  Obesidad: {pa['obesidad']['total_pct']}%")
            print(f"    Hombres: {pa['obesidad']['hombres_pct']}% | Mujeres: {pa['obesidad']['mujeres_pct']}%")
            print(f"  Combinado (sobrepeso+obesidad): {pa['sobrepeso_obesidad_combinado_pct']}%")
            print(f"  Obesidad abdominal: {pa['obesidad_abdominal']['total_pct']}%")
            print(f"\n  Diabetes tipo 2: {pa['diabetes_tipo_2']['total_pct']}%")
            print(f"    Diagnosticada: {pa['diabetes_tipo_2']['diagnosticada_pct']}%")
            print(f"    Control glucémico: {pa['diabetes_tipo_2']['control_glucemico_pct']}%")
            print(f"  Prediabetes: {pa['prediabetes_pct']}%")
            print(f"\n  Hipertensión arterial: {pa['hipertension_arterial']['total_pct']}%")
            print(f"    Desconocen diagnóstico: {pa['hipertension_arterial']['desconocen_diagnostico_pct']}%")
            pna = epi["prevalencias_ninos_adolescentes"]
            print(f"\n  Niños 5-11 años (sobrepeso+obesidad): {pna['sobrepeso_obesidad_5_a_11_pct']}%")
            print(f"  Adolescentes (sobrepeso+obesidad): {pna['sobrepeso_obesidad_adolescentes_pct']}%")
            inseg = epi["inseguridad_alimentaria"]
            print(f"\n  Inseguridad alimentaria:")
            print(f"    Algún grado: {inseg['algun_grado_pct']}%")
            print(f"    Severa: {inseg['severa_pct']}%")
            riesgos = epi["riesgos_asociados_obesidad"]
            print(f"\n  Riesgos asociados a obesidad (razón de momios vs IMC normal):")
            print(f"    Diabetes: RM {riesgos['diabetes_RM']}")
            print(f"    Hipertensión: RM {riesgos['hipertension_RM']}")
            print(f"    Dislipidemia: RM {riesgos['dislipidemia_RM']}")
            input("\n  Presione Enter para continuar...")

        elif opcion == "4":
            limpiar_pantalla()
            encabezado("PRINCIPIOS DE LA DIETA CORRECTA (NOM-043)")
            nom = BC["normativa_mexicana"]["NOM_043_SSA2_2012"]
            principios = nom["principios_dieta_correcta"]
            for nombre, desc in principios.items():
                print(f"\n  {nombre.upper()}")
                print(f"    {desc}")
            print("\n  RECOMENDACIONES GENERALES:")
            for rec in nom["recomendaciones_generales"]:
                print(f"    • {rec}")
            print(f"\n  Comidas recomendadas al día:")
            cr = nom["comidas_recomendadas_dia"]
            print(f"    Principales: {cr['principales']} | Colaciones: {cr['colaciones']}")
            print(f"\n  PLATO DEL BIEN COMER:")
            for g in nom["plato_del_bien_comer"]["grupos"]:
                print(f"\n  [{g['color'].upper()}] {g['grupo']} — comer {g['proporcion']}")
                print(f"    {g['funcion_principal']}")
            print(f"\n  Grupos vulnerables:")
            for gv in nom["grupos_vulnerables"]:
                print(f"    • {gv}")
            input("\n  Presione Enter para continuar...")

        elif opcion == "5":
            print("\n  ¡Hasta luego! Recuerde consultar a un nutriólogo.\n")
            break


# ─────────────────────────── PUNTO DE ENTRADA ────────────────────────────────
if __name__ == "__main__":
    menu_principal()
