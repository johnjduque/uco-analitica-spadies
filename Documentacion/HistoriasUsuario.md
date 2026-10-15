# Mapa de Historias de Usuario y Backlog del Proyecto

---

## 1. Ejemplo de Desarrollo por Sprints

| Sprint | Sprint -2 | Sprint -1 | Sprint 1 | Sprint 2 | Sprint 3 | Sprint 4 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Sprint 1** | Redacción HU | Refinamiento HU | Ejecutar Sprint | - | - | - |
| **Sprint 2** | - | Redacción HU | Refinamiento HU | Ejecutar Sprint | - | - |
| **Sprint 3** | - | - | Redacción HU | Refinamiento HU | Ejecutar Sprint | - |
| **Sprint 4** | - | - | - | Redacción HU | Refinamiento HU | Ejecutar Sprint |

---

## 2. Product Backlog de Historias de Usuario

| ID | Nombre Comando / Acción | Nombre Historia | Rol (¿Quién?) | Necesidad (¿Qué?) | Propósito (¿Para qué?) | Talla | Puntos (SP) | DoR | DoD | Prioridad |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **HU1** | Registrar usuario | Registrar información de un nuevo usuario | Administrador del Sistema | Poder registrar la información de un nuevo usuario | Poder habilitar el acceso de los usuarios a la aplicación por medio de un login | S | 2 | SI | SI | 1 |
| **HU2** | Modificar usuario | Editar información de un usuario | Administrador del Sistema | Editar la información de un usuario existente | Modificar dicha información y mantener actualizados los datos de login de cada usuario en UcoMap | M | 3 | SI | SI | 2 |
| **HU3** | Eliminar usuario | Eliminar información de un usuario | Administrador del Sistema | Poder eliminar la información de un usuario existente | Eliminar del sistema usuarios que ya no forman parte de la universidad y mantener actualizados los datos | M | 3 | SI | SI | 3 |
| **HU4** | Reestablecer credenciales | Reestablecer usuario y/o contraseña de usuario existente | Administrador o Analista | Poder reestablecer la contraseña del login de un usuario | Brindar facilidad en el cambio de credenciales por seguridad o por olvido | XL | 7 | SI | SI | 4 |
| **HU5** | Consultar usuario | Consultar la información y existencia de un usuario | Administrador del Sistema | Consultar información y existencia de uno o más usuarios según criterio | Verificar existencia y tener acceso a la información de login de los usuarios en UcoMap | XL | 7 | SI | SI | 5 |
| **HU6** | Consulta ausencia intersemestral | Consultar la ausencia intersemestral | Administrador o Analista | Consultar el indicador de la ausencia intersemestral | Conocer los resultados del indicador | XL | 12 | SI | SI | 6 |
| **HU7** | Consulta tasa deserción anual | Consultar la tasa de deserción anual | Administrador o Analista | Consultar el indicador de la tasa de deserción anual | Conocer los resultados del indicador | XL | 12 | SI | SI | 7 |
| **HU8** | Consulta tasa deserción promedio acumulada | Consultar la tasa de deserción promedio acumulada | Administrador o Analista | Consultar el indicador de la tasa de deserción promedio acumulada | Conocer los resultados del indicador | XL | 12 | SI | SI | 8 |
| **HU9** | Consulta tasa graduación acumulada | Consultar la tasa de graduación acumulada | Administrador o Analista | Consultar el indicador de la tasa de graduación acumulada | Conocer los resultados del indicador | XL | 12 | SI | SI | 9 |
| **HU10** | Consulta tasa deserción por cohorte | Consultar la tasa de deserción por cohorte | Administrador o Analista | Consultar el indicador de la tasa de deserción por cohorte | Conocer los resultados del indicador | XL | 12 | SI | SI | 10 |

---

## 3. Mapa de Historias de Usuario (User Story Map)

| Release | Épica / Historia Asociada |
| :--- | :--- |
| **Release 0** | • **HU1:** Registrar información de un nuevo usuario<br>• **HU2:** Editar información de un usuario |
| **Release 1** | • **HU3:** Eliminar información de un usuario<br>• **HU5:** Consultar la información y existencia de un usuario |
| **Release 2** | • **HU4:** Reestablecer usuario y/o contraseña de un usuario existente |
| **Release 3** | • **HU6:** Consultar la ausencia intersemestral |
| **Release 4** | • **HU7:** Consultar la tasa de deserción anual |
| **Release 5** | • **HU8:** Consultar la tasa de deserción promedio acumulada |
| **Release 6** | • **HU9:** Consultar la tasa de graduación acumulada |
| **Release 7** | • **HU10:** Consultar la tasa de deserción por cohorte |

---

## 4. Plan de Liberaciones (Release Plan)

| Historia de Usuario | Sprint | Días Hábiles | Acumulado Días Hábiles | Release |
| :--- | :---: | :---: | :---: | :---: |
| **HU1** - Registrar información de un nuevo usuario | Sprint 1 | 10 | 10 | Release 0 |
| **HU2** - Editar información de un usuario | Sprint 1 | - | - | Release 0 |
| **HU3** - Eliminar información de un usuario | Sprint 2 | 10 | 20 | Release 1 |
| **HU5** - Consultar la información y existencia de un usuario | Sprint 2 | - | - | Release 1 |
| **HU4** - Reestablecer usuario y/o contraseña de un usuario existente | Sprint 3 | 7 | 27 | Release 2 |
| **HU6** - Consultar la ausencia intersemestral | Sprint 4 | 7 | 34 | Release 3 |
| **HU7** - Consultar la tasa de deserción anual | Sprint 5 | 7 | 41 | Release 4 |
| **HU8** - Consultar la tasa de deserción promedio acumulada | Sprint 6 | 7 | 48 | Release 5 |
| **HU9** - Consultar la tasa de graduación acumulada | Sprint 7 | 7 | 55 | Release 6 |
| **HU10** - Consultar la tasa de deserción por cohorte | Sprint 8 | 7 | 62 | Release 7 |

---

## 5. Detalle de Historias de Usuario

---

### 🔹 HU1: Registrar información de un nuevo usuario

* **Tarjeta:**
  * **Como:** Administrador del Sistema
  * **Necesito:** Poder registrar la información de un nuevo usuario
  * **Para:** Poder habilitar el acceso de los usuarios a la aplicación por medio de un login
  * *Narrativa completa:* Como Administrador del Sistema, necesito poder registrar la información de un nuevo usuario, para poder habilitar el acceso de los usuarios a la aplicación por medio de un login.
* **Tallaje:** Talla **S** | Puntos: **2** | **DoR:** SI | **DoD:** SI
* **Restricciones de Diseño y Reglas:**
  * Deben tenerse en cuenta los campos descritos en el requisito de información que no deben ser visibles por el usuario.
  * Al validar un usuario previamente registrado con el mismo correo, se valida contenido (case-insensitive para mayúsculas/minúsculas).
  * Existen dos roles: *Administrador* (consultas de indicadores, crear, eliminar y modificar usuarios) y *Analista* (consulta de indicadores y modificar contraseña).
  * Sólo el usuario con rol Administrador puede registrar nuevos usuarios.
* **Criterios de Aceptación:**
  * **CA1 (Éxito):** Dado que un Administrador ingresa todos los datos correctamente y el usuario no existe previamente, cuando ejecuta registrar, entonces se persiste la información, se actualiza la lista, se limpia el formulario y se muestra el mensaje de éxito `GEN_USU_EXI_00001`.
  * **CA2 (Errores de validación):** Dado que un Administrador ingresa datos incorrectos/incompletos, cuando ejecuta registrar, entonces se muestran los mensajes de error correspondientes (`GEN_USU_ERR_00003` por obligatoriedad, `GEN_USU_ERR_00004` por formato, `GEN_USU_ERR_00005` por longitud).

---

### 🔹 HU2: Editar información de un usuario

* **Tarjeta:**
  * **Como:** Administrador del Sistema
  * **Necesito:** Editar la información de un usuario existente
  * **Para:** Modificar dicha información y mantener actualizados los datos de login de los usuarios en UcoMap
  * *Narrativa completa:* Como Administrador del Sistema, necesito editar la información de un usuario existente, con el fin de modificar dicha información y mantener actualizado los datos de login de cada uno de los usuarios que hacen parte de UcoMap.
* **Tallaje:** Talla **M** | Puntos: **3** | **DoR:** SI | **DoD:** SI
* **Restricciones de Diseño y Reglas:**
  * Deben respetarse los campos no visibles para el usuario.
  * Validación de correos sin distinción de mayúsculas/minúsculas.
  * La modificación general sólo la realiza el Administrador (excepto cambio de contraseña).
  * Sólo se actualiza contraseña o rol; al cambiar de correo se debe crear un usuario nuevo y eliminar el anterior.
* **Criterios de Aceptación:**
  * **CA1 (Éxito):** Al ingresar datos válidos y ejecutar actualizar, se persiste la información, se actualiza la lista, se limpia el formulario y se muestra mensaje `GEN_USU_EXI_00006`.
  * **CA2 (Errores):** Al ingresar datos con errores de reglas/longitud/obligatoriedad, se muestran mensajes `GEN_USU_ERR_00003` o `GEN_USU_ERR_00005`.

---

### 🔹 HU3: Eliminar información de un usuario

* **Tarjeta:**
  * **Como:** Administrador del Sistema
  * **Necesito:** Poder eliminar la información de un usuario existente
  * **Para:** Eliminar del sistema usuarios que ya no forman parte de la universidad y mantener actualizados los datos
* **Tallaje:** Talla **M** | Puntos: **3** | **DoR:** SI | **DoD:** SI
* **Restricciones de Diseño y Reglas:**
  * Operación permitida exclusivamente para el rol Administrador.
* **Criterios de Aceptación:**
  * **CA1 (Éxito):** Al confirmar eliminación de un usuario existente, se elimina de la base de datos, se actualiza la lista y se muestra mensaje `GEN_USU_EXI_00007`.
  * **CA2 (Validación):** Errores de formato/obligatoriedad muestran `GEN_USU_ERR_00003`, `GEN_USU_ERR_00004` o `GEN_USU_ERR_00005`.
  * **CA3 (No encontrado):** Si el usuario no existe, se muestra mensaje de error `GEN_USU_ERR_00008`.

---

### 🔹 HU4: Reestablecer usuario y/o contraseña de un usuario existente

* **Tarjeta:**
  * **Como:** Administrador del Sistema o Analista
  * **Necesito:** Poder reestablecer la contraseña del login de un usuario
  * **Para:** Brindar facilidad en el cambio de credenciales por seguridad o por olvido
* **Tallaje:** Talla **XL** | Puntos: **7** | **DoR:** SI | **DoD:** SI
* **Restricciones de Diseño y Reglas:**
  * El cambio de contraseña se realiza por medio del correo electrónico registrado.
  * Puede ser ejecutado por Administrador o Analista.
* **Criterios de Aceptación:**
  * **CA1 (Éxito):** Al ingresar datos correctos, se actualizan las credenciales, se limpia formulario y se muestra mensaje `GEN_USU_EXI_00009`.
  * **CA2 (Validación):** Error en reglas de longitud muestra mensaje `GEN_USU_ERR_00005`.
  * **CA3 (No encontrado):** Si el usuario no existe, muestra mensaje de error `GEN_USU_ERR_00008`.

---

### 🔹 HU5: Consultar la información y existencia de un usuario

* **Tarjeta:**
  * **Como:** Administrador del Sistema
  * **Necesito:** Consultar la información y existencia de uno o más usuarios según el criterio especificado
  * **Para:** Verificar existencia y tener acceso a la información de login en UcoMap
* **Tallaje:** Talla **XL** | Puntos: **7** | **DoR:** SI | **DoD:** SI
* **Restricciones de Diseño y Reglas:**
  * Consulta exclusiva para el rol Administrador.
* **Criterios de Aceptación:**
  * **CA1 (Éxito):** Si el usuario existe, se retorna la información y se muestra mensaje `GEN_USU_EXI_00011`.
  * **CA2 (Validación):** Errores de datos devuelven `GEN_USU_ERR_00003`, `GEN_USU_ERR_00004` o `GEN_USU_ERR_00005`.
  * **CA3 (No encontrado):** Si el correo no existe, se muestra mensaje `GEN_USU_ERR_00012`.

---

### 🔹 HU6: Consultar la ausencia intersemestral

* **Tarjeta:**
  * **Como:** Administrador del Sistema o Analista
  * **Necesito:** Consultar el indicador de ausencia intersemestral
  * **Para:** Conocer los resultados del indicador
* **Tallaje:** Talla **XL** | Puntos: **12** | **DoR:** SI | **DoD:** SI
* **Restricciones de Diseño y Reglas:**
  * Los parámetros de consulta deben seleccionarse mediante listas desplegables.
* **Criterios de Aceptación:**
  * **CA1 (Éxito):** Al seleccionar filtros válidos y presionar generar consulta, retorna los porcentajes de retención y ausentismo junto con mensaje de éxito `GEN_USU_EXI_00010`.
  * **CA2 (Advertencia campos):** Si faltan parámetros requeridos, muestra mensaje `GEN_USU_ADV_00013`.
  * **CA3 (Filtro por defecto):** Si no se filtra, toma valor 'Todos' por defecto y muestra advertencia informativa `GEN_USU_INF_00014`.

---

### 🔹 HU7: Consultar la tasa de deserción anual

* **Tarjeta:**
  * **Como:** Administrador del Sistema o Analista
  * **Necesito:** Consultar el indicador de la tasa de deserción anual
  * **Para:** Conocer los resultados del indicador
* **Tallaje:** Talla **XL** | Puntos: **12** | **DoR:** SI | **DoD:** SI
* **Restricciones de Diseño y Reglas:**
  * Selección de parámetros mediante listas desplegables.
* **Criterios de Aceptación:**
  * **CA1 (Éxito):** Muestra porcentaje de retención y porcentaje de deserción con mensaje de éxito `GEN_USU_EXI_00010`.
  * **CA2 (Advertencia):** Mensaje `GEN_USU_ADV_00013` al faltar datos requeridos.
  * **CA3 (Filtro por defecto):** Listas por defecto en 'Todos' muestran mensaje informativo `GEN_USU_INF_00014`.

---

### 🔹 HU8: Consultar la tasa de deserción promedio acumulada

* **Tarjeta:**
  * **Como:** Administrador del Sistema o Analista
  * **Necesito:** Consultar el indicador de tasa de deserción promedio acumulada
  * **Para:** Conocer los resultados del indicador
* **Tallaje:** Talla **XL** | Puntos: **12** | **DoR:** SI | **DoD:** SI
* **Restricciones de Diseño y Reglas:**
  * Selección de parámetros mediante listas desplegables.
* **Criterios de Aceptación:**
  * **CA1 (Éxito):** Muestra el indicador con porcentaje por semestre y mensaje de éxito `GEN_USU_EXI_00010`.
  * **CA2 (Advertencia):** Mensaje `GEN_USU_ADV_00013` por campos incompletos.
  * **CA3 (Filtro por defecto):** Mensaje `GEN_USU_INF_00014` cuando se consulta con filtros globales ('Todos').

---

### 🔹 HU9: Consultar la tasa de graduación acumulada

* **Tarjeta:**
  * **Como:** Administrador del Sistema o Analista
  * **Necesito:** Consultar el indicador de la tasa de graduación acumulada
  * **Para:** Conocer los resultados del indicador
* **Tallaje:** Talla **XL** | Puntos: **12** | **DoR:** SI | **DoD:** SI
* **Restricciones de Diseño y Reglas:**
  * Selección de parámetros mediante listas desplegables.
* **Criterios de Aceptación:**
  * **CA1 (Éxito):** Retorna datos consolidados por semestre y mensaje de éxito `GEN_USU_EXI_00010`.
  * **CA2 (Advertencia):** Mensaje `GEN_USU_ADV_00013` si falta selección obligatoria.
  * **CA3 (Filtro por defecto):** Mensaje `GEN_USU_INF_00014` al consultar sobre todos los programas/facultades.

---

### 🔹 HU10: Consultar la tasa de deserción por cohorte

* **Tarjeta:**
  * **Como:** Administrador del Sistema o Analista
  * **Necesito:** Consultar el indicador de tasa de deserción por cohorte
  * **Para:** Conocer los resultados del indicador
* **Tallaje:** Talla **XL** | Puntos: **12** | **DoR:** SI | **DoD:** SI
* **Restricciones de Diseño y Reglas:**
  * Parámetros en listas desplegables.
  * Mostrar como máximo 14 semestres por cohorte consultada.
* **Criterios de Aceptación:**
  * **CA1 (Éxito):** Retorna porcentajes por año y semestre (hasta 14 semestres por cohorte) y mensaje `GEN_USU_EXI_00010`.
  * **CA2 (Advertencia):** Mensaje `GEN_USU_ADV_00013` si falta selección de parámetros.
  * **CA3 (Filtro por defecto):** Mensaje `GEN_USU_INF_00014` al usar valor general 'Todos'.