# Temporades Anuals — Disseny

**Data:** 2026-05-12  
**Branca:** Immoble

## Objectiu

Modificar la selecció de dates de temporada perquè l'usuari només triï mes i dia (sense any). D'aquesta manera, una temporada configurada com "1 gener – 31 març" s'aplica automàticament cada any.

## Enfocament: Any Fix 2000 (Opció C)

Les columnes `data_inici` i `data_fi` de `Temporada` es mantenen com a `DateField`. L'any sempre es normalitza a 2000 internament. Per exemple, "Temporada Baixa: 1 gen – 31 març" es guarda com `2000-01-01` → `2000-03-31`.

**Avantatges:**
- Cap migració de columnes necessària
- La validació de dates de Django segueix funcionant (`2000-02-31` falla sol)
- L'ordenació `ordering = ['data_inici']` segueix sent correcta (tots els anys són 2000)
- El format de l'API no canvia (continua sent ISO `YYYY-MM-DD`)

## Canvis necessaris

### 1. Backend — `backend/properties/serializers.py`

Afegir validadors de camp a `TemporadaSerializer` que forcen l'any a 2000:

```python
def validate_data_inici(self, value):
    return value.replace(year=2000)

def validate_data_fi(self, value):
    return value.replace(year=2000)
```

Cap altre canvi al backend.

### 2. Frontend — `frontend/src/Cards/temporadesCard.jsx`

Substituir els dos `<input type="date">` (per `data_inici` i `data_fi`) per un component inline `SelectMesDia` que mostra:
- Un `<select>` de mes (Gener–Desembre en català, valors 1–12)
- Un `<select>` de dia (1–31)

**Lògica del component:**
- **Lectura:** parseja el valor existent `"YYYY-MM-DD"`, extreu mes i dia
- **Escriptura:** al canviar qualsevol select, construeix `"2000-{MM}-{DD}"` i crida `handleChange`
- El component es defineix com a funció local dins del fitxer, no cal fitxer separat

**Actualitzar `handleNovaTemporada`:**  
La funció actual construeix una data a partir de la darrera `data_fi`. Caldrà que el string resultant usi any 2000:
```js
const darreraDataString = `2000-${pad(darreraData.getMonth() + 1)}-${pad(darreraData.getDate())}`;
```

### 3. Seed data — `backend/seed_data.py`

Canviar totes les dates de les temporades de `"2026-XX-XX"` a `"2000-XX-XX"`. Exemple:
```python
(0, "Temporada Baixa", "2000-01-01", "2000-03-31", 90.00),
```

## Fitxers afectats

| Fitxer | Canvi |
|--------|-------|
| `backend/properties/serializers.py` | +2 validadors de camp |
| `frontend/src/Cards/temporadesCard.jsx` | Substituir inputs de data per selectores mes+dia |
| `backend/seed_data.py` | Canviar any de dates de 2026 a 2000 |

## Fora d'abast

- Cap migració de base de dades
- Cap canvi a l'esquema de l'API
- Cap canvi al model `Temporada`
- No es valida que `data_fi >= data_inici` (ja fora d'abast abans d'aquest canvi)
