# PetCare Journal Inteligente — Especificación de Producto y Arquitectura

API backend para gestionar la vida de mascotas (vacunas, peso, paseos, recordatorios de comida) con una capa de IA **segura** para orientación de cuidado ante síntomas leves y recetas de snacks caseros.

**Stack:** Python \+ FastAPI · PostgreSQL · Solo backend (REST) · Multi-usuario · Notificaciones por email **Naturaleza:** Proyecto de portafolio (calidad de producción, sin sobre-ingeniería).

---

## 0\. Decisiones cerradas (descubrimiento)

| Tema | Decisión |
| :---- | :---- |
| Plataforma | Solo backend. REST API documentada con OpenAPI. Sin frontend en v1. |
| Stack | Python 3.12 \+ FastAPI. |
| Persistencia | MySql \+ SQLAlchemy (async) \+ Alembic (migraciones). |
| Multi-tenant | Multi-usuario con aislamiento por `user_id` en cada recurso. |
| Notificaciones | Email (abstracción `EmailSender`, proveedor intercambiable). |
| IA síntomas | Enfoque **intermedio**: orientación detallada \+ disclaimers fuertes. **Nunca diagnostica.** Triage de 3 baldes \+ banderas rojas determinísticas. |
| IA snacks | Recetas caseras \+ **validador determinístico de ingredientes tóxicos** por especie. |

**Supuestos vigentes** (corregibles):

- `[SUPUESTO]` Proveedor LLM vía HTTP (Anthropic/OpenAI), detrás de una interfaz `LLMProvider`.
- `[SUPUESTO]` Escala de portafolio (~cientos de usuarios) → **monolito modular**, no microservicios.
- `[SUPUESTO]` PII básica (email); sin compliance estricto, pero diseñado prolijo.

---

## 1\. Análisis del dominio

### 1.1 Context map (C4 — nivel 1)

```
graph TD
    Owner([Dueño de mascota])
    subgraph Sistema[PetCare Journal API]
        API[FastAPI Backend]
        DB[(PostgreSQL)]
        Sched[Dispatcher de recordatorios]
    end
    LLM[Proveedor LLM externo]
    Mail[Proveedor de Email]
    Owner -->|REST + JWT| API
    API --> DB
    Sched --> DB
    API -->|consulta orientación / receta| LLM
    Sched -->|envía recordatorio| Mail
```

### 1.2 Entidades principales

`User`, `Pet`, `WeightRecord`, `Vaccine`, `Reminder`, `AIConsultation`, `JournalEvent` *(Should)*.

### 1.3 Casos de uso principales

1. Registrar dueño e iniciar sesión.
2. Crear y administrar el perfil de una mascota (especie, raza, edad, peso).
3. Registrar peso a lo largo del tiempo y ver su evolución.
4. Registrar vacunas y su próxima dosis.
5. Crear recordatorios (comida / paseo / vacuna) que llegan por email.
6. Consultar orientación de cuidado a partir de síntomas leves (con triage seguro).
7. Pedir una receta de snack casero validada para su especie.

### 1.4 User Stories (MVP)

- Como **dueño** quiero **registrar mi mascota con especie, raza y edad** para tener su ficha base.
- Como **dueño** quiero **cargar el peso periódicamente** para seguir su evolución.
- Como **dueño** quiero **registrar vacunas con la próxima dosis** para no olvidarme.
- Como **dueño** quiero **programar recordatorios de comida/paseo** para mantener la rutina.
- Como **dueño** quiero **describir síntomas leves y recibir orientación segura** para saber si es cuidado en casa o ir al veterinario.
- Como **dueño** quiero **pedir un snack casero apto** para premiar a mi mascota sin riesgo.

### 1.5 Reglas de negocio (numeradas)

- **RN-01** Un dueño solo puede ver/editar sus propias mascotas y los datos derivados (aislamiento por `user_id`).
- **RN-02** El peso siempre se guarda como **historial** (no se sobreescribe); el "peso actual" es el último registro.
- **RN-03** Toda recomendación de IA incluye **disclaimer obligatorio** y queda **registrada** (`AIConsultation`).
- **RN-04** Antes de invocar al LLM por síntomas, se ejecuta el **screening determinístico de banderas rojas**; si hay match → balde `URGENCIA`, se omite el LLM.
- **RN-05** La IA de síntomas **nunca devuelve un nombre de enfermedad ni un diagnóstico**; solo orientación \+ balde de triage.
- **RN-06** Toda receta generada pasa por el **validador de ingredientes tóxicos por especie**; si contiene alguno, se rechaza o se regenera excluyéndolo.
- **RN-07** Las recomendaciones de cuidado y porción se contextualizan con especie/edad/peso de la mascota.
- **RN-08** Borrado de mascota \= **soft-delete** (`deleted_at`); el historial no se elimina físicamente.

---

## 2\. Diseño del producto

**Visión:** los dueños llevan vacunas, comida y paseos de forma dispersa (memoria, papel, chats). PetCare Journal centraliza el historial y los recordatorios, y suma una capa de IA que orienta el cuidado y propone snacks **sin reemplazar al veterinario**. La propuesta de valor del portafolio es demostrar una integración de IA **bien resuelta y segura**, no un wrapper de LLM.

**MVP (Must):**

- Auth (registro/login JWT) \+ aislamiento multi-usuario.
- Perfil de mascota \+ historial de peso.
- Vacunas con próxima dosis.
- Recordatorios (comida/paseo/vacuna) con dispatcher \+ envío por email.
- Endpoint IA síntomas con guardarraíles.
- Endpoint IA snacks con validador de tóxicos.
- OpenAPI docs \+ tests \+ despliegue dockerizado.

**Exclusiones explícitas (Won't v1):** frontend, telemedicina/chat con vet real, push/WhatsApp, marketplace, roles avanzados.

**Evolución:**

- **V2 (Expansión):** journal/timeline, curva de peso \+ condición corporal (BCS), rol admin, rotación de refresh tokens.
- **V3 (Automatización):** scheduling avanzado (RRULE/iCal), multi-canal (push, WhatsApp), preferencias de notificación.
- **Largo plazo (Escala):** migración a Celery+Redis, caché de IA, rate limiting, observabilidad.

---

## 3\. Arquitectura

### 3.1 Estilo: monolito modular

Para escala de portafolio, microservicios serían sobre-ingeniería. Un **monolito modular** con módulos por dominio y capas claras es lo correcto, y deja la puerta abierta a extraer servicios si algún día hace falta.

```
graph TD
    Client[Cliente REST]
    subgraph FastAPI[FastAPI - Monolito modular]
        R[Routers / API v1]
        S[Services - lógica de negocio]
        Repo[Repositories]
        Guard[Capa de guardarraíles IA]
    end
    subgraph Infra[Infraestructura]
        PG[(PostgreSQL)]
        Disp[Dispatcher recordatorios - APScheduler]
    end
    LLMI[LLMProvider - interfaz]
    EML[EmailSender - interfaz]
    Client --> R --> S
    S --> Repo --> PG
    S --> Guard --> LLMI
    Disp --> Repo
    Disp --> EML
```

**Módulos:** `auth`, `pets`, `health` (peso \+ vacunas), `reminders`, `ai` (síntomas \+ snacks). **Capas:** `router` (I/O \+ validación Pydantic) → `service` (reglas) → `repository` (acceso a datos) → `model` (SQLAlchemy). Esquemas Pydantic separados de los modelos ORM.

### 3.2 Decisión arquitectónica: motor de recordatorios

El único fork real de arquitectura. Para recordatorios **no se programa un job por recordatorio**: se corre un **dispatcher periódico** que cada minuto consulta los que vencen.

| Criterio | A. APScheduler + dispatcher | B. Celery + Redis | C. RQ + Redis |
| :---- | :---- | :---- | :---- |
| Ventajas | Cero infra extra, simple, robusto con el patrón dispatcher | Estándar de industria, escala horizontal | Más liviano que Celery |
| Desventajas | Atado al proceso (mitigable con jobstore persistente) | Más piezas (broker + worker + beat) | Menos features/madurez |
| Costo infra | Ninguno | Redis + worker | Redis + worker |
| Complejidad | Baja | Alta | Media |
| Escalabilidad | Media | Alta | Media-Alta |
| Velocidad de desarrollo | Alta | Baja | Media |

**Recomendación:** **Opción A** para el MVP — APScheduler con un único job dispatcher que consulta `reminders WHERE next_run_at <= now() AND status = 'pending'`. Es simple, robusto e **idempotente**. El patrón dispatcher hace que migrar a Celery (V3/Escala) sea un *swap*, no un *rewrite* — y te deja contar las dos opciones en una entrevista.

### 3.3 Flujo de la IA de síntomas (el diferenciador)

```
flowchart TD
    A[POST symptom-check] --> B[Validar input - Pydantic]
    B --> C[Cargar contexto de la mascota]
    C --> D{Screening determinístico<br/>de banderas rojas}
    D -- match --> E[Balde URGENCIA<br/>sin LLM]
    D -- sin match --> F[Invocar LLM<br/>salida JSON estructurada]
    F --> G[Validar salida + forzar disclaimer<br/>+ degradar balde si hay riesgo]
    E --> H[Registrar en AIConsultation]
    G --> H
    H --> I[Respuesta + disclaimer]
```

Puntos clave:

- **El LLM nunca es la última línea de seguridad.** El screening de banderas rojas (dificultad para respirar, convulsiones, sangre, no come/bebe hace X, ingestión de tóxico, etc.) es código determinístico, ejecutado **antes** del modelo.
- Salida del LLM **estructurada (JSON)**: `bucket` (`home_care` | `see_vet_soon` | `urgent`), `observations`, `home_care_tips`, `when_to_worry`. **Sin** campo de diagnóstico.
- El texto de síntomas se trata como **dato, no como instrucción** (mitigación de prompt injection); system prompt robusto \+ validación de la salida.

### 3.4 Flujo de la IA de snacks

1. Cargar especie (y condiciones/alergias si existen).
2. LLM genera receta como JSON (`ingredients[]`, `steps[]`, `portion_by_weight`).
3. **Validador determinístico de tóxicos por especie** (chocolate, xilitol, uvas/pasas, cebolla/ajo, cafeína, alcohol, macadamia, etc.). Si hay match → rechazar o **regenerar excluyendo** el ingrediente.
4. Adjuntar disclaimer (los snacks no deben superar ~10% de las calorías diarias; consultar al veterinario para dietas).

### 3.5 Stack de soporte

- **ORM/migraciones:** SQLAlchemy 2.0 (async) \+ Alembic.
- **Auth:** OAuth2 password flow (nativo FastAPI) → JWT (access \+ refresh), hashing con `passlib[bcrypt]`/argon2.
- **Email:** abstracción `EmailSender`; impl con `aiosmtplib`/`fastapi-mail` sobre SMTP (Resend/Mailgun/SendGrid free tier).
- **LLM:** interfaz `LLMProvider` \+ impl HTTP; timeouts y reintentos.
- **Config:** `pydantic-settings`, secretos por variables de entorno.
- **Docs:** OpenAPI/Swagger automático.

---

## 4\. Modelo de datos

```
erDiagram
    USER ||--o{ PET : posee
    PET ||--o{ WEIGHT_RECORD : tiene
    PET ||--o{ VACCINE : tiene
    PET ||--o{ REMINDER : tiene
    PET ||--o{ AI_CONSULTATION : genera
    PET ||--o{ JOURNAL_EVENT : registra

    USER {
        uuid id PK
        string email UK
        string hashed_password
        bool is_active
        timestamptz created_at
    }
    PET {
        uuid id PK
        uuid user_id FK
        string name
        string species
        string breed
        date birth_date
        string sex
        timestamptz created_at
        timestamptz deleted_at
    }
    WEIGHT_RECORD {
        uuid id PK
        uuid pet_id FK
        numeric weight_kg
        timestamptz recorded_at
    }
    VACCINE {
        uuid id PK
        uuid pet_id FK
        string name
        date dose_date
        date next_due_date
        string notes
    }
    REMINDER {
        uuid id PK
        uuid pet_id FK
        string type
        string title
        string frequency
        time time_of_day
        int[] days_of_week
        timestamptz next_run_at
        timestamptz last_run_at
        string status
        timestamptz deleted_at
    }
    AI_CONSULTATION {
        uuid id PK
        uuid pet_id FK
        string type
        jsonb input
        jsonb output
        string bucket
        timestamptz created_at
    }
    JOURNAL_EVENT {
        uuid id PK
        uuid pet_id FK
        string type
        jsonb payload
        timestamptz occurred_at
    }
```

**Decisiones:**

- **Multi-tenant** por `user_id` en `PET`; todo lo demás cuelga de `pet_id` y se scopea vía el dueño.
- **Soft-delete** en `PET` y `REMINDER` (`deleted_at`); el historial nunca se borra físicamente.
- **Índices clave:** `reminders(next_run_at, status)` (lo usa el dispatcher), `pets(user_id)`, `weight_records(pet_id, recorded_at)`, FKs.
- **Integridad:** `email` único; FKs con `ON DELETE` controlado por la app (soft-delete).
- **Scheduling v1 simple** (`frequency` \+ `time_of_day` \+ `days_of_week`); RRULE/iCal queda para V3.
- **`AI_CONSULTATION`** cumple la RN-03 (trazabilidad de lo recomendado).

---

## 5\. APIs e integraciones

Base: `/api/v1`. Auth: `Bearer <JWT>`. Errores con envelope consistente y códigos HTTP correctos (`401` no auth, `403` no es tuyo, `404` no existe, `422` validación, `429` rate limit).

### 5.1 Endpoints

| Método | Ruta | Descripción |
| :---- | :---- | :---- |
| POST | `/auth/register` | Crear dueño |
| POST | `/auth/login` | Obtener access \+ refresh token |
| POST | `/auth/refresh` | Renovar access token |
| GET / POST | `/pets` | Listar / crear mascotas |
| GET / PATCH / DELETE | `/pets/{id}` | Ver / editar / soft-delete |
| GET / POST | `/pets/{id}/weights` | Historial / nuevo peso |
| GET / POST | `/pets/{id}/vaccines` | Listar / registrar vacuna |
| PATCH / DELETE | `/vaccines/{id}` | Editar / borrar vacuna |
| GET / POST | `/pets/{id}/reminders` | Listar / crear recordatorio |
| PATCH / DELETE | `/reminders/{id}` | Editar / borrar recordatorio |
| POST | `/pets/{id}/ai/symptom-check` | Triage de síntomas (con guardarraíles) |
| POST | `/pets/{id}/ai/snack-recipe` | Receta de snack (validada) |
| GET | `/pets/{id}/journal` | Timeline *(V2)* |

### 5.2 Contrato — `POST /pets/{id}/ai/symptom-check`

**Request**
```json
{ "symptoms": "Está decaído y comió menos hoy, sin vómitos." }
```

**Response 200**
```json
{
  "bucket": "see_vet_soon",
  "observations": "Decaimiento y baja de apetito en 24h ameritan seguimiento.",
  "home_care_tips": ["Ofrecer agua fresca", "Observar apetito en las próximas horas"],
  "when_to_worry": ["Si deja de beber", "Si aparece vómito o diarrea"],
  "disclaimer": "Orientación general. No reemplaza la consulta veterinaria.",
  "consultation_id": "…"
}
```

Si el screening determinístico detecta una bandera roja, `bucket` = `"urgent"` **sin** invocar al LLM.

### 5.3 Contrato — `POST /pets/{id}/ai/snack-recipe`

**Request**
```json
{ "preferences": "bajo en grasa", "available_ingredients": ["zanahoria", "avena"] }
```

**Response 200**
```json
{
  "title": "Galletas de zanahoria y avena",
  "ingredients": [{ "name": "zanahoria", "qty": "1 mediana" }, { "name": "avena", "qty": "1/2 taza" }],
  "steps": ["Rallar la zanahoria", "Mezclar con la avena", "Hornear 15 min"],
  "portion_by_weight": "1 unidad por cada 5 kg, máx. 10% de las calorías diarias",
  "safety_check": "passed",
  "disclaimer": "Snack ocasional. Consultá al veterinario ante dietas o condiciones."
}
```

Si el validador detecta un ingrediente tóxico para la especie, devuelve `422` o regenera excluyéndolo.

### 5.4 Integraciones externas

- **LLM** (`LLMProvider`): timeouts, reintentos, salida JSON validada.
- **Email** (`EmailSender`): SMTP/API; cola lógica vía estado del recordatorio (idempotencia).

---

## 6\. Roadmap

| Fase | Objetivos | Entregables | Dependencias | Riesgos |
| :---- | :---- | :---- | :---- | :---- |
| **0 Descubrimiento** ✓ | Cerrar alcance | Esta spec | — | — |
| **1 MVP** | API funcional end-to-end | Auth, pets, peso, vacunas, recordatorios+email, ambos endpoints IA, OpenAPI, tests, Docker | PostgreSQL, LLM key, SMTP | Seguridad de la IA |
| **2 Expansión** | Más valor para el dueño | Journal, curva de peso/BCS, admin, refresh rotation | MVP | Crecimiento del modelo de datos |
| **3 Automatización** | Recordatorios y canales | RRULE, push/WhatsApp, preferencias | V2 | Complejidad scheduling |
| **4 Escala** | Producción seria | Celery+Redis, caché IA, rate limit, observabilidad | V3 | Costos infra |

---

## 7\. Riesgos

| Riesgo | Tipo | Impacto | Prob. | Mitigación |
| :---- | :---- | :---- | :---- | :---- |
| La IA minimiza algo grave | Producto/Legal | Alto | Media | Banderas rojas determinísticas \+ triage \+ disclaimer \+ log; nunca diagnostica |
| Receta con ingrediente tóxico | Producto/Seguridad | Alto | Media | Validador determinístico post-LLM \+ regeneración |
| Fuga de datos entre usuarios (IDOR) | Seguridad | Alto | Media | Scoping por `user_id` en cada query \+ tests de autorización |
| Prompt injection vía síntomas | Seguridad | Medio | Media | Input como dato, no instrucción; salida estructurada validada |
| Dispatcher duplica/pierde envíos | Operacional | Medio | Media | Idempotencia (`status`, `last_run_at`), jobstore persistente |
| Costo/latencia del LLM | Operacional | Medio | Media | Timeouts, rate limit en endpoints IA, caché (V4) |
| Secretos en el repo | Seguridad | Alto | Baja | Variables de entorno / secrets manager |
| Abuso de envío de emails | Operacional | Medio | Media | Rate limiting \+ verificación de email |

---

## 8\. Plan de implementación

**Orden de construcción**

1. Scaffold: FastAPI \+ `pydantic-settings` \+ conexión DB \+ Alembic.
2. **Auth** (registro/login JWT) \+ dependencia de *scoping* por usuario.
3. **Pets** CRUD (con soft-delete).
4. **Health**: peso (historial) \+ vacunas.
5. **Reminders** \+ dispatcher (APScheduler) \+ `EmailSender`.
6. **LLM abstraction** \+ `symptom-check` \+ screening de banderas rojas.
7. **`snack-recipe`** \+ validador de tóxicos.
8. Tests → Docker/CI → deploy.

**Componentes críticos:** auth/scoping, dispatcher idempotente, capa de guardarraíles IA.

**Quick wins:** Pets \+ Vaccines CRUD (valor visible rápido) y los **docs OpenAPI automáticos** (muestran bien en portafolio).

**Errores comunes a evitar**

- Dejar al LLM como única línea de seguridad.
- Programar un job por recordatorio en vez del patrón dispatcher.
- No scopear queries por `user_id` (IDOR).
- Meter la API key en el repo.
- I/O síncrono bloqueando el event loop async.

**Estrategia de pruebas:** `pytest` \+ `httpx.AsyncClient`; **tests unitarios sin LLM** del screener de banderas rojas y del validador de tóxicos (son la red de seguridad); tests de autorización (IDOR); mock del `LLMProvider`.

**Despliegue:** Docker \+ `docker-compose` (api \+ postgres); Alembic en el arranque; CI con GitHub Actions (lint \+ test); deploy a Fly.io / Render / Railway (tier económico, ideal para portafolio).

---

*Generado como especificación inicial. Ajustable a medida que evolucione el proyecto.*
