# Validacions de Temporada a la Reserva — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Afegir 3 validacions quan es crea/previsualitza una reserva: mínim de nits per temporada, avís quan les dates no cobreixen cap temporada, i revalidació en profunditat al moment de crear la reserva. Garantir que cap error arriba al frontend amb missatge no explicatiu.

**Architecture:** Les validacions s'afegeixen a `calcular_preview_reserva()` (services.py) per tenir una sola font de veritat, actives tant al preview com a la creació. Al serializer s'afegeix una crida a `calcular_preview_reserva()` com a defensa en profunditat. Al frontend es corregeix la captura d'errors i s'afegeix la caixa d'avís.

**Tech Stack:** Django REST Framework, Python, React (JSX), CSS Modules

---

## File Map

| Fitxer | Canvi |
|--------|-------|
| `backend/bookings/tests/test_services.py` | CREAR — tests per a les noves validacions |
| `backend/bookings/services.py` | MODIFICAR — afegir min_nits + avis_sense_temporada |
| `backend/bookings/serializers.py` | MODIFICAR — cridar calcular_preview_reserva al validate() |
| `frontend/src/Cards/crearReservaCard.module.css` | MODIFICAR — afegir classe `.warnBox` |
| `frontend/src/Cards/crearReservaCard.jsx` | MODIFICAR — mostrar error real + warning al modal |

---

### Task 1: Tests fallits per a la validació de min_nits

**Files:**
- Create: `backend/bookings/tests/test_services.py`

- [ ] **Step 1: Crear el fitxer de tests amb els casos de mínim de nits**

```python
# backend/bookings/tests/test_services.py
from datetime import date
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from bookings.services import calcular_preview_reserva
from properties.models import Immoble, Temporada


def _data(immoble_pk, **kwargs):
    base = {
        "immoble": immoble_pk,
        "data_entrada": "2025-07-01",
        "data_sortida": "2025-07-05",  # 4 nits
        "num_hostes": 2,
        "descompte_immoble_aplicat": False,
        "descompte_immoble_percentatge": 0,
        "descompte_individual_aplicat": False,
        "descompte_individual_percentatge": 0,
    }
    base.update(kwargs)
    return base


class MinNitsValidacioTest(TestCase):
    def setUp(self):
        self.immoble = Immoble.objects.create(
            nom_comercial="Pis Test",
            adreca="Carrer Test 1",
            preu_base_nit=50,
        )

    def test_min_nits_complert_no_llanca_error(self):
        Temporada.objects.create(
            immoble=self.immoble,
            nom="Estiu",
            data_inici=date(2000, 6, 1),
            data_fi=date(2000, 8, 31),
            preu_nit=100,
            min_nits=3,
        )
        result = calcular_preview_reserva(_data(self.immoble.pk))
        self.assertEqual(result["nits"], 4)

    def test_min_nits_no_complert_llanca_error(self):
        Temporada.objects.create(
            immoble=self.immoble,
            nom="Estiu",
            data_inici=date(2000, 6, 1),
            data_fi=date(2000, 8, 31),
            preu_nit=100,
            min_nits=7,
        )
        with self.assertRaises(ValidationError) as ctx:
            calcular_preview_reserva(_data(self.immoble.pk))
        detail = str(ctx.exception.detail)
        self.assertIn("7", detail)
        self.assertIn("Estiu", detail)

    def test_min_nits_mes_restrictiu_bloca_reserva(self):
        # Booking spanning 2 temporades: Jul 1-Aug 3 = 4 nits
        # T1 (juliol): min_nits=2 — OK
        # T2 (agost): min_nits=7 — KO
        Temporada.objects.create(
            immoble=self.immoble,
            nom="Juliol",
            data_inici=date(2000, 7, 1),
            data_fi=date(2000, 7, 31),
            preu_nit=90,
            min_nits=2,
        )
        Temporada.objects.create(
            immoble=self.immoble,
            nom="Agost",
            data_inici=date(2000, 8, 1),
            data_fi=date(2000, 8, 31),
            preu_nit=120,
            min_nits=7,
        )
        # 4 nits: 2025-07-01 a 2025-08-03 cobreix Juliol i Agost
        with self.assertRaises(ValidationError):
            calcular_preview_reserva(_data(
                self.immoble.pk,
                data_entrada="2025-07-30",
                data_sortida="2025-08-03",  # 4 nits, Agost requereix 7
            ))
```

- [ ] **Step 2: Executar els tests per confirmar que fallen**

```
cd backend && python manage.py test bookings.tests.test_services.MinNitsValidacioTest -v 2
```

Esperat: `ERROR` o `FAIL` amb "module has no attribute" o similar (fitxer creat però funció no modificada).

---

### Task 2: Implementar validació de min_nits a services.py

**Files:**
- Modify: `backend/bookings/services.py`

- [ ] **Step 1: Modificar el bucle de `calcular_preview_reserva()` per recollir temporades trobades**

Localitzar el bloc de variables entre `temporades = list(immoble.temporades.all())` i `while current_day < data_sortida:` (~línies 160-164) i substituir-lo:

```python
    temporades = list(immoble.temporades.all())
    linies_nits = []
    subtotal = Decimal("0")
    current_day = data_entrada
    temporades_trobades = set()
    dies_sense_temporada = []
```

- [ ] **Step 2: Dins el bucle while, registrar la temporada trobada i els dies sense temporada**

Localitzar les línies dins el `while` (de `temporada = _temporada_for_day(...)` fins al `current_day += timedelta`) i substituir:

```python
    while current_day < data_sortida:
        temporada = _temporada_for_day(temporades, current_day)
        if temporada:
            temporades_trobades.add(temporada)
        else:
            dies_sense_temporada.append(current_day.isoformat())
        preu_nit = Decimal(temporada.preu_nit if temporada else immoble.preu_base_nit)
        comissio_percent = Decimal(temporada.comissio if temporada else DEFAULT_COMISSIO_PERCENT)
        subtotal += preu_nit
        linies_nits.append(
            {
                "data": current_day.isoformat(),
                "preu_nit": str(_money(preu_nit)),
                "temporada": temporada.nom if temporada else None,
                "comissio_percentatge": str(_percent(comissio_percent)),
                "_preu_nit": preu_nit,
                "_comissio_percentatge": comissio_percent,
            }
        )
        current_day += timedelta(days=1)
```

- [ ] **Step 3: Afegir la validació de min_nits just després del bucle while (abans dels càlculs de descomptes)**

Inserir just després del `while` i abans de `descompte_immoble_import = ...`:

```python
    for temporada_trobada in temporades_trobades:
        if nits < temporada_trobada.min_nits:
            raise ValidationError(
                f"La temporada '{temporada_trobada.nom}' requereix un mínim de "
                f"{temporada_trobada.min_nits} nits. La reserva té {nits} nits."
            )
```

- [ ] **Step 4: Afegir `avis_sense_temporada` al diccionari de retorn**

Al `return {...}` final (última línia de la funció), afegir la clau:

```python
        "avis_sense_temporada": dies_sense_temporada,
```

El return complet queda:

```python
    return {
        "nits": nits,
        "num_hostes": num_hostes,
        "subtotal_allotjament": str(_money(subtotal)),
        "descompte_immoble_percentatge": str(_percent(descompte_immoble_percent)),
        "descompte_immoble_import": str(_money(descompte_immoble_import)),
        "descompte_individual_percentatge": str(_percent(descompte_individual_percent)),
        "descompte_individual_import": str(_money(descompte_individual_import)),
        "total_allotjament": str(_money(total_allotjament)),
        "comissio_percentatge_mitjana": str(_percent(comissio_percentatge_mitjana)),
        "comissio_import": str(_money(comissio_import)),
        "taxa_turistica_per_hoste_nit": str(_money(taxa_turistica["tarifa_mitjana"])),
        "taxa_turistica_nits_aplicades": taxa_turistica["nits_aplicades"],
        "taxa_turistica_zona": taxa_turistica["zona"],
        "taxa_turistica_import": str(_money(taxa_turistica_import)),
        "total_a_abonar_turista": str(_money(total_a_abonar_turista)),
        "linies_nits": linies_nits,
        "avis_sense_temporada": dies_sense_temporada,
    }
```

- [ ] **Step 5: Executar els tests de min_nits i confirmar que passen**

```
cd backend && python manage.py test bookings.tests.test_services.MinNitsValidacioTest -v 2
```

Esperat: `OK` (3 tests passing).

- [ ] **Step 6: Commit**

```bash
git add backend/bookings/tests/test_services.py backend/bookings/services.py
git commit -m "feat(bookings): validate min_nits per temporada and warn on missing temporada"
```

---

### Task 3: Tests fallits per a l'avís sense temporada

**Files:**
- Modify: `backend/bookings/tests/test_services.py`

- [ ] **Step 1: Afegir classe de tests per a `avis_sense_temporada`**

Afegir al final de `test_services.py`:

```python
class AvisSenseTemporadaTest(TestCase):
    def setUp(self):
        self.immoble = Immoble.objects.create(
            nom_comercial="Pis Sense Temporada",
            adreca="Carrer Test 2",
            preu_base_nit=60,
        )

    def test_sense_temporada_retorna_llista_dates(self):
        result = calcular_preview_reserva(_data(self.immoble.pk))
        self.assertIn("avis_sense_temporada", result)
        self.assertEqual(len(result["avis_sense_temporada"]), 4)
        self.assertIn("2025-07-01", result["avis_sense_temporada"])
        self.assertIn("2025-07-04", result["avis_sense_temporada"])

    def test_amb_temporada_completa_llista_buida(self):
        Temporada.objects.create(
            immoble=self.immoble,
            nom="Estiu",
            data_inici=date(2000, 6, 1),
            data_fi=date(2000, 8, 31),
            preu_nit=80,
            min_nits=1,
        )
        result = calcular_preview_reserva(_data(self.immoble.pk))
        self.assertEqual(result["avis_sense_temporada"], [])

    def test_temporada_parcial_retorna_dates_sense_cobrir(self):
        # Temporada cobreix juliol però no agost
        Temporada.objects.create(
            immoble=self.immoble,
            nom="Juliol",
            data_inici=date(2000, 7, 1),
            data_fi=date(2000, 7, 31),
            preu_nit=80,
            min_nits=1,
        )
        # Booking: 30 juliol - 3 agost (4 nits: 30 jul, 31 jul, 1 ago, 2 ago)
        # 30-31 jul cobertes, 1-2 ago no cobertes
        result = calcular_preview_reserva(_data(
            self.immoble.pk,
            data_entrada="2025-07-30",
            data_sortida="2025-08-03",
        ))
        self.assertIn("2025-08-01", result["avis_sense_temporada"])
        self.assertIn("2025-08-02", result["avis_sense_temporada"])
        self.assertNotIn("2025-07-30", result["avis_sense_temporada"])
        self.assertNotIn("2025-07-31", result["avis_sense_temporada"])
```

- [ ] **Step 2: Executar per confirmar que passen (la implementació ja és al Task 2)**

```
cd backend && python manage.py test bookings.tests.test_services.AvisSenseTemporadaTest -v 2
```

Esperat: `OK` (3 tests passing).

- [ ] **Step 3: Commit**

```bash
git add backend/bookings/tests/test_services.py
git commit -m "test(bookings): add tests for avis_sense_temporada in calcular_preview_reserva"
```

---

### Task 4: Revalidació al serializer (defensa en profunditat)

**Files:**
- Modify: `backend/bookings/serializers.py`

- [ ] **Step 1: Afegir test per a la revalidació al serializer**

Afegir al final de `backend/bookings/tests/test_services.py`:

```python
from bookings.models import Persona
from bookings.serializers import ReservaSerializer


class ReservaSerializerTemporadaTest(TestCase):
    def setUp(self):
        self.immoble = Immoble.objects.create(
            nom_comercial="Pis Serializer Test",
            adreca="Carrer Test 3",
            preu_base_nit=50,
        )
        Temporada.objects.create(
            immoble=self.immoble,
            nom="Estiu",
            data_inici=date(2000, 6, 1),
            data_fi=date(2000, 8, 31),
            preu_nit=100,
            min_nits=7,
        )
        self.persona = Persona.objects.create(nom_complet="Test Inquili")

    def _payload(self, **kwargs):
        base = {
            "immoble": self.immoble.pk,
            "inquili": self.persona.pk,
            "data_entrada": "2025-07-01",
            "data_sortida": "2025-07-05",  # 4 nits, min és 7
            "num_hostes": 2,
            "descompte_immoble_aplicat": False,
            "descompte_immoble_percentatge": "0.00",
            "descompte_individual_aplicat": False,
            "descompte_individual_percentatge": "0.00",
        }
        base.update(kwargs)
        return base

    def test_serializer_rebutja_reserva_per_min_nits(self):
        serializer = ReservaSerializer(data=self._payload())
        valid = serializer.is_valid()
        self.assertFalse(valid)
        errors_str = str(serializer.errors)
        self.assertIn("7", errors_str)

    def test_serializer_accepta_reserva_amb_min_nits_complert(self):
        serializer = ReservaSerializer(data=self._payload(
            data_sortida="2025-07-09",  # 8 nits, min és 7 → OK
        ))
        # Pot fallar per altres raons (camps opcionals), però no per min_nits
        serializer.is_valid()
        errors_str = str(serializer.errors)
        self.assertNotIn("mínim", errors_str.lower())
        self.assertNotIn("min_nits", errors_str.lower())
```

- [ ] **Step 2: Executar per confirmar que fallen**

```
cd backend && python manage.py test bookings.tests.test_services.ReservaSerializerTemporadaTest -v 2
```

Esperat: `FAIL` — el serializer no valida min_nits encara.

- [ ] **Step 3: Modificar `ReservaSerializer.validate()` a serializers.py**

Afegir l'import de `calcular_preview_reserva` al capdamunt del fitxer (just sota els imports existents):

```python
from .services import calcular_preview_reserva
```

Localitzar el mètode `validate(self, data)` i afegir el bloc de revalidació just **abans** del `return data` final:

```python
    def validate(self, data):
        immoble = data.get('immoble', getattr(self.instance, 'immoble', None))
        data_entrada = data.get('data_entrada', getattr(self.instance, 'data_entrada', None))
        data_sortida = data.get('data_sortida', getattr(self.instance, 'data_sortida', None))

        if immoble and data_entrada and data_sortida:
            conflicte_qs = ReservaBasica.objects.filter(
                immoble=immoble,
                data_entrada__lt=data_sortida,
                data_sortida__gt=data_entrada,
            ).exclude(estat_reserva='cancelada')

            if self.instance:
                conflicte_qs = conflicte_qs.exclude(pk=self.instance.pk)

            if conflicte_qs.exists():
                conflicte = conflicte_qs.first()
                raise serializers.ValidationError(
                    f"Les dates se solapen amb la reserva {conflicte.codi_reserva} "
                    f"({conflicte.data_entrada} – {conflicte.data_sortida})."
                )

            calcular_preview_reserva({
                "immoble": immoble.pk,
                "data_entrada": str(data_entrada),
                "data_sortida": str(data_sortida),
                "num_hostes": data.get("num_hostes", 1),
                "descompte_immoble_aplicat": False,
                "descompte_immoble_percentatge": 0,
                "descompte_individual_aplicat": False,
                "descompte_individual_percentatge": 0,
            })

        return data
```

- [ ] **Step 4: Executar els tests del serializer per confirmar que passen**

```
cd backend && python manage.py test bookings.tests.test_services.ReservaSerializerTemporadaTest -v 2
```

Esperat: `OK` (2 tests passing).

- [ ] **Step 5: Executar tots els tests de bookings per detectar regressions**

```
cd backend && python manage.py test bookings -v 2
```

Esperat: tots passen.

- [ ] **Step 6: Commit**

```bash
git add backend/bookings/tests/test_services.py backend/bookings/serializers.py
git commit -m "feat(bookings): revalidate temporada conditions on reservation create/update"
```

---

### Task 5: Frontend — errors explicatius i avís sense temporada

**Files:**
- Modify: `frontend/src/Cards/crearReservaCard.module.css`
- Modify: `frontend/src/Cards/crearReservaCard.jsx`

- [ ] **Step 1: Afegir classe `.warnBox` al CSS**

Afegir just després del bloc `.errorBox p + p { ... }` (línia ~146):

```css
.warnBox {
  margin-bottom: 20px;
  padding: 12px 14px;
  border: 1px solid #fde68a;
  border-radius: 10px;
  background: #fffbeb;
  color: #92400e;
}

.warnBox p {
  margin: 0;
}

.warnBox p + p {
  margin-top: 6px;
}
```

- [ ] **Step 2: Corregir el catch del preview perquè mostri l'error real**

Localitzar el `catch` dins `handleSubmit` (línia ~283):

```js
    } catch {
      setPreviewError("No s'ha pogut calcular el resum econòmic de la reserva.");
    }
```

Substituir per:

```js
    } catch (err) {
      setPreviewError(err.message || "No s'ha pogut calcular el resum econòmic de la reserva.");
    }
```

- [ ] **Step 3: Afegir el bloc d'avís sense temporada al modal de preview**

Localitzar el bloc `{previewReserva.linies_nits?.length > 0 && (...)}` (~línia 596). Afegir **just abans** d'aquest bloc:

```jsx
            {previewReserva.avis_sense_temporada?.length > 0 && (
              <div className={styles.warnBox}>
                <p>
                  <strong>Avís:</strong> Les dates següents no tenen temporada configurada per a aquest immoble.
                  S&apos;aplicarà el preu base de l&apos;immoble ({previewReserva.avis_sense_temporada.length} nit
                  {previewReserva.avis_sense_temporada.length !== 1 ? "s" : ""}):
                </p>
                <p>{previewReserva.avis_sense_temporada.join(", ")}</p>
              </div>
            )}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/Cards/crearReservaCard.module.css frontend/src/Cards/crearReservaCard.jsx
git commit -m "feat(frontend): show temporada warning in preview and display real error messages"
```

---

### Task 6: Verificació final

- [ ] **Step 1: Executar tots els tests del backend**

```
cd backend && python manage.py test bookings properties -v 2
```

Esperat: tots passen, sense errors ni warnings.

- [ ] **Step 2: Provar manualment el flux happy path**

Iniciar dev server i crear una reserva amb dates que cobreixin una temporada i respectin min_nits. Verificar que el preview es mostra correctament sense avisos.

- [ ] **Step 3: Provar el cas d'error min_nits**

Crear una reserva amb menys nits de les requerides per la temporada. Verificar que:
- Al preview: es mostra l'error real (`err.message`) en el `previewError`
- No apareix el missatge genèric "No s'ha pogut calcular el resum econòmic"

- [ ] **Step 4: Provar el cas d'avís sense temporada**

Crear una reserva amb dates que no cobreixi cap temporada. Verificar que:
- Al modal de preview: apareix la caixa groga d'avís amb les dates
- La reserva es pot confirmar igualment

- [ ] **Step 5: Provar que un error de backend al crear retorna text explicatiu**

Verificar que si el backend rebutja la creació (p.ex. per min_nits), `confirmError` mostra el text real del backend, no "Error desconegut".
