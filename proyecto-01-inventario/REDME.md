# SISTEMA DE ANALISIS DE INVENTARIO

## La problematica
Una empresa con más de 2,000 SKUs no tenía visibilidad sobre qué productos estaban por agotarse, cuáles no tenían rotación y cuánto capital tenía inmobilizado en inventario sin movimiento.

## ¿Qué hice?
- Limpié y estructure datos de ventas e inventario desde un dataset real
- Clasifiqué los productos con el método ABC (Principio de Pareto)
- Calculé el punto de reorden para cada producto
- Identifiqué que productos críticos y sin rotación 
- Construí un dashboard en Power BI

## Hallazgos clave
- El 28% de los productos concentran el 80% del vaor del inventario (Clase A)
- 119 productos estan por debajo del stock minimo y requieren reabastecimiento inmediato
- 150 SKUs sin rotación representan $1.9M en capital inmovilizado (4.3% del inventario)
- Technology lidera el valor del inventario, seguido del Furniture

## Herramientas
-Python     -pandas     -NumPy     -Power Bi

## Archivos
| limpieza.py | Carga, limpieza y estructura de datos
| analisis.py | Clasificación ABC, punto de reorden y rotación 
| inventario_analizado.csv | Dataset final con todas las indicaciones

## Dashboaard
[Dashboard](dashboard.png)