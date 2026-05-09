import pandas as pd
import numpy as np

np.random.seed(42)

# ====================
# 1. CARGAR EL DATASET
# ====================
df = pd.read_csv('superstore.csv', encoding='latin1')
print(f"Filas: {df.shape[0]} | Columnas: {df.shape[1]}")

# ====================
# 2. EXPLORACIÓN INICIAL
# ====================
print("\n-- VALORES VACÍOS --")
print(df.isnull().sum()[df.isnull().sum() > 0])

print("\n-- TIPOS DE DATO --")
print(df.dtypes)

# ====================
# 3. LIMPIEZA
# ====================
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
df['Ship Date']  = pd.to_datetime(df['Ship Date'],  dayfirst=True)
df['Postal Code'] = df['Postal Code'].astype(str)
df['Lead_Time_Dias'] = (df['Ship Date'] - df['Order Date']).dt.days

# Simulamos columnas que el dataset no trae pero necesitamos
df['Quantity']  = np.random.randint(1, 10, len(df))
df['Discount']  = np.round(np.random.choice([0, 0.1, 0.2, 0.3], len(df)), 2)
df['Profit']    = np.round(df['Sales'] * np.random.uniform(0.05, 0.35, len(df)), 2)

assert df['Lead_Time_Dias'].min() >= 0, "ERROR: hay lead times negativos"
print(f"\nLead Time promedio: {df['Lead_Time_Dias'].mean():.1f} días")
print(f"Lead Time máximo:   {df['Lead_Time_Dias'].max()} días")

# ====================
# 4. CREAR LAS 3 TABLAS
# ====================

# --- TABLA 1: VENTAS ---
ventas = df[[
    'Order ID', 'Order Date', 'Ship Date', 'Ship Mode',
    'Customer ID', 'Customer Name', 'Segment', 'Region',
    'Category', 'Sub-Category', 'Product ID', 'Product Name',
    'Sales', 'Quantity', 'Discount', 'Profit',
    'Lead_Time_Dias'
]].copy()

print(f"\nTabla VENTAS: {ventas.shape[0]} filas | {ventas.shape[1]} columnas")

# --- TABLA 2: INVENTARIO ---
inventario = df[[
    'Product ID', 'Product Name', 'Category', 'Sub-Category'
]].drop_duplicates().reset_index(drop=True)

n = len(inventario)

inventario['Stock_Actual'] = np.random.randint(5, 250, n)

stock_minimo_map = {
    'Furniture': 5,
    'Technology': 10,
    'Office Supplies': 30
}
inventario['Stock_Minimo'] = inventario['Category'].map(stock_minimo_map).fillna(15)
inventario['Stock_Maximo'] = inventario['Stock_Minimo'] * 10

costo_map = {
    'Furniture': (80, 600),
    'Technology': (30, 800),
    'Office Supplies': (2, 80)
}
inventario['Costo_Unitario'] = inventario['Category'].apply(
    lambda c: round(np.random.uniform(*costo_map.get(c, (10, 100))), 2)
)

demanda_real = (
    df.groupby('Product ID')['Quantity'].sum() /
    df['Order Date'].nunique()
).round(2)
inventario['Demanda_Diaria_Prom'] = inventario['Product ID'].map(demanda_real).fillna(0.1)

inventario['Lead_Time_Proveedor'] = np.random.randint(3, 21, n)
inventario['Valor_Inventario'] = (
    inventario['Stock_Actual'] * inventario['Costo_Unitario']
).round(2)
inventario['Unidad'] = 'pza'

print(f"Tabla INVENTARIO: {inventario.shape[0]} filas | {inventario.shape[1]} columnas")
print(inventario.head(3))

# --- TABLA 3: INCIDENCIAS ---
incidencias = pd.DataFrame(columns=[
    'ID_Incidencia', 'Fecha', 'Product ID', 'Producto',
    'Tipo_Incidencia', 'Cantidad_Afectada',
    'Descripcion', 'Responsable', 'Estado'
])
print("\nTabla INCIDENCIAS: estructura lista para AppSheet")

# ====================
# 5. EXPORTAR
# ====================
ventas.to_csv('ventas.csv', index=False)
inventario.to_csv('inventario.csv', index=False)
incidencias.to_csv('incidencias.csv', index=False)

print("\nArchivos exportados:")
print(f"  ventas.csv      → {ventas.shape[0]} registros")
print(f"  inventario.csv  → {inventario.shape[0]} registros")
print(f"  incidencias.csv → estructura lista")
print("\n✓ Fase 1 completa")