import pandas as pd
import numpy as np

np.random.seed(42)

# Cargo las tablas
ventas     = pd.read_csv('ventas.csv')
inventario = pd.read_csv('inventario.csv')

ventas['Order Date'] = pd.to_datetime(ventas['Order Date'])
print(f"Ventas: {ventas.shape[0]} filas | Inventario: {inventario.shape[0]} filas")

# ---- 1. CLASIFICACIÓN ABC ----
inv = inventario.sort_values('Valor_Inventario', ascending=False).copy()
inv['Valor_Acumulado'] = inv['Valor_Inventario'].cumsum()
total = inv['Valor_Inventario'].sum()
inv['Pct_Acumulado'] = inv['Valor_Acumulado'] / total

def clase_abc(pct):
    if pct <= 0.80: return 'A'
    elif pct <= 0.95: return 'B'
    else: return 'C'

inv['Clase_ABC'] = inv['Pct_Acumulado'].apply(clase_abc)

resumen = inv.groupby('Clase_ABC').agg(
    Productos=('Product ID', 'count'),
    Valor=('Valor_Inventario', 'sum')
).round(2)
resumen['Pct_Productos'] = (resumen['Productos'] / len(inventario) * 100).round(1)
resumen['Pct_Valor']     = (resumen['Valor'] / total * 100).round(1)

print("\n-- ABC --")
print(resumen)

# ---- 2. PUNTO DE REORDEN Y ALERTAS ----
inv['Stock_Seguridad'] = (
    inv['Demanda_Diaria_Prom'] * inv['Lead_Time_Proveedor'] * 0.5
).round(0)

inv['Punto_Reorden'] = (
    inv['Demanda_Diaria_Prom'] * inv['Lead_Time_Proveedor'] +
    inv['Stock_Seguridad']
).round(0)

def alerta(row):
    if row['Stock_Actual'] <= row['Stock_Minimo']:
        return 'CRITICO'
    elif row['Stock_Actual'] <= row['Punto_Reorden']:
        return 'REORDENAR'
    return 'OK'

inv['Alerta'] = inv.apply(alerta, axis=1)

print("\n-- ALERTAS --")
print(inv['Alerta'].value_counts())

print("\n-- TOP 10 CRÍTICOS --")
criticos = inv[inv['Alerta'] == 'CRITICO'][[
    'Product Name', 'Category', 'Stock_Actual',
    'Stock_Minimo', 'Punto_Reorden', 'Valor_Inventario'
]].head(10)
print(criticos.to_string())

# ---- 3. ROTACIÓN ----
ventas_x_producto = ventas.groupby('Product ID').agg(
    Unidades_Vendidas=('Quantity', 'sum'),
    Ingresos_Total=('Sales', 'sum'),
    Num_Ordenes=('Order ID', 'nunique')
).reset_index()

df = inv.merge(ventas_x_producto, on='Product ID', how='left')
df[['Unidades_Vendidas', 'Ingresos_Total', 'Num_Ordenes']] = \
    df[['Unidades_Vendidas', 'Ingresos_Total', 'Num_Ordenes']].fillna(0)

df['Rotacion'] = (
    df['Unidades_Vendidas'] / df['Stock_Actual'].replace(0, np.nan)
).round(2)

print("\n-- TOP 10 ESTRELLA --")
print(df.nlargest(10, 'Rotacion')[[
    'Product Name', 'Category', 'Rotacion', 'Unidades_Vendidas', 'Stock_Actual'
]].to_string())

# Productos sin movimiento — common en cualquier almacén real
# (descontinuados, temporadas pasadas, errores de compra)
obsoletos = pd.DataFrame({
    'Product ID':        [f'OBSOLETO-{i:03d}' for i in range(1, 151)],
    'Product Name':      [f'Producto Sin Rotación {i:03d}' for i in range(1, 151)],
    'Category':          np.random.choice(['Furniture', 'Technology', 'Office Supplies'], 150),
    'Sub-Category':      np.random.choice(['Chairs', 'Phones', 'Paper', 'Binders'], 150),
    'Stock_Actual':      np.random.randint(10, 100, 150),
    'Stock_Minimo':      5,
    'Stock_Maximo':      200,
    'Costo_Unitario':    np.round(np.random.uniform(10, 500, 150), 2),
    'Demanda_Diaria_Prom': 0,
    'Lead_Time_Proveedor': np.random.randint(3, 21, 150),
    'Unidad':            'pza',
    'Clase_ABC':         'C',
    'Alerta':            'CRITICO',
    'Valor_Acumulado':   0,
    'Pct_Acumulado':     0,
    'Stock_Seguridad':   0,
    'Punto_Reorden':     0,
    'Unidades_Vendidas': 0,
    'Ingresos_Total':    0,
    'Num_Ordenes':       0,
    'Rotacion':          0
})

obsoletos['Valor_Inventario'] = (
    obsoletos['Stock_Actual'] * obsoletos['Costo_Unitario']
).round(2)

df['Origen']       = 'Real'
obsoletos['Origen'] = 'Simulado'

df = pd.concat([df, obsoletos], ignore_index=True)

# ---- 4. COSTO OBSOLETO ----
estancados = df[df['Unidades_Vendidas'] == 0]
costo_obs  = estancados['Valor_Inventario'].sum()

print(f"\n-- INVENTARIO OBSOLETO --")
print(f"Productos sin movimiento: {len(estancados)}")
print(f"Valor inmovilizado:       ${costo_obs:,.2f}")
print(f"% del inventario total:   {costo_obs/total*100:.1f}%")

# ---- EXPORTAR ----
df.to_csv('inventario_analizado.csv', index=False)
print("\n✓ inventario_analizado.csv exportado")