# Sistema Experto de Nutricion — Mexico

Sistema experto basado en reglas para la generacion de recomendaciones nutricionales y planes alimentarios personalizados, contextualizado para la poblacion mexicana.

## Ejecucion

**Interfaz grafica (recomendado):**

```bash
python sistema_experto_gui.py
```

**Version de consola:**

```bash
python sistema_experto_nutricion.py
```

> Requisitos: Python 3.8+ con `tkinter` (incluido por defecto en la mayoria de instalaciones de Python en Windows, macOS y muchas distribuciones de Linux).

---

## Fuentes investigadas y compiladas

Las fuentes oficiales que se cruzaron fueron:

| Fuente | Institucion | Descripcion |
|--------|-------------|-------------|
| **ENSANUT Continua 2020-2024** | Instituto Nacional de Salud Publica (INSP) | Encuestas anuales probabilisticas con >50,000 hogares y 53,600 adultos. 145 indicadores de salud y nutricion con representatividad estatal. |
| **ENIGH** | Instituto Nacional de Estadistica y Geografia (INEGI) | Datos sobre gasto alimentario, disponibilidad y capacidad de compra de alimentos por sector poblacional. |
| **NOM-043-SSA2-2012** | Secretaria de Salud, Mexico | Norma Oficial Mexicana para orientacion alimentaria: criterios, grupos de alimentos (Plato del Bien Comer) y recomendaciones por grupo etario. |
| **Lineamientos de Nutricion Deportiva CONADE/CNAR** | Comision Nacional de Cultura Fisica y Deporte | Protocolos de nutricion para deportistas de alto rendimiento, platos nutricionales (entrenamiento ligero, moderado, competencia). |
| **SMAE 4a edicion** | Perez Lizaur AB, Palacios Gonzalez B, Castro Becerra AL, Flores Galicia I — Fomento de Nutricion y Salud, A.C. | Sistema de equivalentes alimentarios para diseno de planes de alimentacion. 8 grupos de alimentos con aporte nutrimental promedio por equivalente. |
| **Human Energy Requirements (FAO/OMS/UNU 2004)** | FAO, OMS, Universidad de las Naciones Unidas | Ecuaciones para estimacion de gasto energetico basal y total. Factores de actividad fisica. Requerimientos por grupo etario. |
| **Dietary Reference Intakes (DRIs)** | Food and Nutrition Board, Institute of Medicine, National Academies (EE.UU./Canada) | Valores de referencia: RDA, AI, UL, EAR y AMDR para macro y micronutrientes por grupo etario y sexo. |
| **USDA FoodData Central** | U.S. Department of Agriculture | Base de composicion de alimentos con valores de nutrientes por 100g de porcion comestible. API REST disponible. Licencia CC0 1.0 (dominio publico). |
| **Diagnostico de Alimentacion 2024** | CONEVAL | Datos sobre inseguridad alimentaria y pobreza laboral en Mexico. |
| **Dietary Guidelines for Americans 2020-2025** | USDA / HHS | Estimaciones rapidas de requerimientos caloricos por edad, sexo y nivel de actividad. |

---

## Estructura de la base de conocimiento

La base de conocimiento (`base_conocimiento_nutricion.json`) esta organizada en los siguientes modulos principales:

### 1. Contexto epidemiologico de Mexico
Prevalencias de obesidad (75.2% de adultos con sobrepeso u obesidad), diabetes tipo 2 (17.0%), hipertension arterial (47.0%) e inseguridad alimentaria (50.0% en algun grado), segun ENSANUT 2022-2024 y CONEVAL.

### 2. Normativa mexicana
Incluye la NOM-043-SSA2-2012 con los principios de la dieta correcta (completa, equilibrada, inocua, suficiente, variada y adecuada) y el Plato del Bien Comer con sus tres grupos de alimentos: Verduras y Frutas (verde — muchas), Cereales y Tuberculos (amarillo — suficientes), Leguminosas y Alimentos de Origen Animal (rojo — pocos).

### 3. Sistema Mexicano de Alimentos Equivalentes (SMAE)
El SMAE completo con los 8 grupos alimentarios, subgrupos y valores de energia/macronutrientes por equivalente:
- Verduras (25 kcal/eq.)
- Frutas (60 kcal/eq.)
- Cereales y Tuberculos (sin grasa: 70 kcal, con grasa: 115 kcal)
- Leguminosas (120 kcal/eq.)
- Alimentos de Origen Animal (4 subgrupos: 40-100 kcal)
- Leche (4 subgrupos: 95-200 kcal)
- Aceites y Grasas (sin proteina: 45 kcal, con proteina: 70 kcal)
- Azucares (sin grasa: 40 kcal, con grasa: 85 kcal)
- Alimentos libres en energia

### 4. Formulas de calculo energetico
Ecuaciones para estimar el Gasto Energetico Basal (GEB) y el Gasto Energetico Total (GET):
- **Harris-Benedict** (poblacion general)
- **Mifflin-St Jeor** (mas precisa para sobrepeso/obesidad)
- **FAO/OMS/UNU 1985** (por rangos de edad)
- Factores de actividad fisica FAO (sedentario, ligera, moderada, intensa)
- Formula de peso corregido para obesidad
- Estimaciones rapidas por edad, sexo y actividad (Dietary Guidelines 2020-2025)

### 5. Distribucion de macronutrientes
Rangos AMDR (IOM/National Academies): carbohidratos 45-65%, proteinas 10-35%, lipidos 20-35%. Distribucion por objetivos especificos:
- Perdida de grasa (CHO 40-50%, PRO 25-30%, LIP 25-30%, deficit 500-750 kcal)
- Mantenimiento (CHO 45-55%, PRO 15-20%, LIP 25-35%)
- Ganancia muscular (CHO 50-60%, PRO 25-30%, LIP 15-25%, superavit 250-500 kcal)
- Rendimiento deportivo (CHO 55-65%, PRO 12-15%, LIP 20-30%)
- Control glucemico (CHO 40-50%, PRO 20-25%, LIP 30-35%)

Incluye perfil lipidico recomendado, fibra dietetica (14g/1000 kcal) y requerimientos de agua.

### 6. Tablas DRI completas de vitaminas y minerales
Valores de referencia (RDA, AI, UL) para adultos 19-50 anios de:
- **Vitaminas**: A, C, D, E, K, B1, B2, B3, B5, B6, B7, B9 (folato), B12, colina
- **Minerales**: calcio, hierro, magnesio, zinc, selenio, yodo, fosforo, potasio, sodio, cobre, manganeso, cromo, molibdeno, fluoruro

### 7. Modulo de nutricion deportiva CONADE
Basado en los protocolos del Centro Nacional de Alto Rendimiento (CNAR):
- **3 Platos Nutricionales**: entrenamiento ligero (azul), moderado (amarillo), intenso/competencia (naranja)
- **Hidratacion deportiva**: pre, durante y post-ejercicio
- **Suplementacion**: clasificacion AIS (A: con evidencia, B: en estudio, C: sin evidencia, D: prohibidos)
- Requerimientos proteicos por disciplina (resistencia, fuerza, deportes intermitentes)
- Protocolo de nutricion de la Federacion Mexicana de Taekwondo

### 8. Condiciones especiales
Recomendaciones nutricionales para:
- **Embarazo**: energia extra por trimestre (0, +340, +452 kcal), nutrientes criticos (hierro 27mg, ac. folico 600ug, calcio 1000mg, DHA 200mg)
- **Lactancia**: +500 kcal/dia, nutrientes criticos
- **Adultos mayores (60+)**: proteina 1.0-1.2 g/kg, vitamina D 20ug, calcio 1200mg, B12
- **Diabetes tipo 2**: CHO 45-60% de IG bajo, fibra 25-30g, sodio <2000mg, criterios diagnosticos
- **Hipertension arterial**: principios de la dieta DASH, sodio <2300mg (ideal <1500), potasio ~4700mg
- **Enfermedad renal cronica**: requiere supervision de nefrologo

### 9. Tabla de composicion de alimentos mexicanos
20 alimentos representativos de la dieta mexicana con valores por 100g:
Tortilla de maiz, frijol negro, arroz, pollo, huevo, nopal, aguacate, jitomate, chile poblano, avena, leche, platano, guayaba, mango, lenteja, sardina, amaranto, chia, flor de calabaza y quelite/verdolaga.

### 10. Indice glucemico
21 alimentos comunes clasificados en bajo (<55), medio (56-69) y alto (>=70), basado en las tablas internacionales de la Universidad de Sydney.

### 11. Reglas heuristicas para el motor de inferencia
- **Clasificacion IMC**: 6 rangos con acciones recomendadas
- **Distribucion por objetivo**: 5 perfiles nutricionales con rangos de macronutrientes
- **Tiempos de comida**: 3 principales + 2 colaciones con porcentajes (25/10/30/10/25)
- **Nutricion deportiva**: tiempos pre/durante/post-entrenamiento
- **Alertas clinicas**: 8 reglas para deteccion de riesgos (anemia, osteoporosis, defectos tubo neural, sodio excesivo, proteina excesiva, fibra baja, deficiencia de vitamina D, dieta hipocalorica)

### 12. APIs externas recomendadas
- **USDA FoodData Central API**: >400,000 alimentos, valores por 100g, CC0
- **SMAE Digital**: Sistema digital basado en SMAE + USDA
- **IDEAS-ENSANUT**: Tablero en linea del INSP con datos de salud y nutricion

### 13. Plantilla de proceso para generacion automatica de planes
Flujo de 12 pasos: calculo de IMC, clasificacion, GEB, GET, ajuste por objetivo, distribucion de macronutrientes, conversion a equivalentes SMAE, distribucion en tiempos de comida, asignacion de alimentos, verificacion de micronutrientes, generacion de alertas y creacion de menu semanal.

---

## Siguiente paso natural

Expandir la tabla de composicion de alimentos, ya sea integrando la API de USDA FoodData Central o construyendo un catalogo local mas amplio, y codificar las reglas en el formato que use tu sistema experto (Prolog, CLIPS, o un engine en Python/TS).

---

## Estructura de archivos

```
py/
  base_conocimiento_nutricion.json   # Base de conocimiento (JSON)
  sistema_experto_gui.py             # Interfaz grafica (tkinter)
  sistema_experto_nutricion.py       # Version de consola
  README.md                          # Este archivo
```

---

## Aviso

Este sistema es **orientativo** y fue generado con fines educativos. **No sustituye** la consulta con un profesional de la nutricion certificado. Consulte a un nutriologo para un plan personalizado.
