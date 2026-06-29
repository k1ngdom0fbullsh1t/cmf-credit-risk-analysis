# Análisis de Riesgo de Crédito — Sistema Bancario Chileno

🔗 **[Ver dashboard en vivo](https://cmf-credit-risk-chile-mact.streamlit.app/)**

Análisis exploratorio de los índices de provisiones por riesgo de crédito del sistema bancario chileno entre 2016 y 2026, basado en datos públicos de la Comisión para el Mercado Financiero (CMF).

## Descripción

Este proyecto consolida, limpia y analiza más de 120 reportes mensuales publicados por la CMF, construyendo un dataset histórico que permite visualizar la evolución del riesgo crediticio por banco y tipo de cartera (comercial, consumo, vivienda).

## Estructura del proyecto

```
├── data/
│   ├── raw/              # Archivos Excel originales descargados desde CMF
│   └── processed/        # Datasets consolidados en CSV
├── notebooks/
│   └── 01_eda.ipynb      # Análisis exploratorio de datos
├── src/
│   ├── descargar_archivos.py   # Script de descarga automática desde CMF
│   └── consolidar_datos.py     # Pipeline de consolidación y limpieza
└── dashboard/
    └── app.py            # Dashboard interactivo (Streamlit)
```

## Tecnologías utilizadas

- Python · Pandas · NumPy
- Matplotlib · Seaborn · Plotly
- Streamlit
- openpyxl · xlrd
- Git / GitHub

## Fuente de datos

**Comisión para el Mercado Financiero (CMF Chile)**  
Indicadores de Provisiones por Riesgo de Crédito de Bancos — publicación mensual  
https://www.cmfchile.cl/portal/estadisticas/626/w4-propertyvalue-29875.html

## Principales hallazgos

- El índice de consumo del sistema saltó de 2.97% (pre-COVID) a 4.09% durante la pandemia, sin volver completamente a niveles previos.
- Banco Ripley (10.4%) y Banco Falabella (4.0%) lideran consistentemente el riesgo de consumo, reflejo de su modelo de crédito masivo.
- Banco de Chile y BCI presentan las carteras más estables del período (variación histórica < 1 punto).
- El crédito de vivienda se mantiene como el de menor riesgo en todos los años analizados.
- Desde 2025 se observa una tendencia a la baja, con el índice de consumo en 2.75%, el nivel más bajo desde 2016.

## Cómo ejecutar

**1. Instalar dependencias**
```bash
pip install pandas openpyxl xlrd matplotlib seaborn plotly streamlit requests beautifulsoup4
```

**2. Descargar los datos**
```bash
python src/descargar_archivos.py
```

**3. Consolidar los datos**
```bash
python src/consolidar_datos.py
```

**4. Ejecutar el dashboard**
```bash
streamlit run dashboard/app.py
```

**5. Explorar el análisis**  
Abrir `notebooks/01_eda.ipynb` en Jupyter Notebook.

## Autor

**Marcelo Adolfo Corro Troncoso**

---

*Este análisis es de carácter académico y fue desarrollado con fines de portafolio profesional. No constituye asesoría financiera ni representa la opinión de ninguna institución. Los datos utilizados son de acceso público y provienen de la CMF Chile.*
