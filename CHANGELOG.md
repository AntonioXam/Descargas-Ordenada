# 📝 Registro de Cambios

Todos los cambios notables de este proyecto se documentarán en este archivo.

---

## [7.0.1] - 2026-09-25

**Corrección de un fallo que solo se veía en macOS.** No hay cambios de
interfaz: esta versión existe para que el permiso se maneje bien y para que el
fallo no pueda volver sin que nadie se entere.

### 🐛 Correcciones
- **Una capacidad de permiso desconocida ya no abre los Ajustes del sistema.**
  `abrir_ajustes_del_sistema` abría el panel genérico de Privacidad aunque el
  identificador no existiera en el catálogo. Además de ser engañoso, hacía que
  la prueba del motor de permisos abriera Ajustes de verdad en macOS: la suite
  fallaba en un Mac y pasaba en Linux, por eso no se había visto. Ahora esa
  capacidad no abre nada y explica que hay que concederlo a mano

### 🧪 Pruebas
- **Las pruebas funcionales se ejecutan en cada push a `main` y en cada pull
  request** (Linux y macOS), no solo al publicar una etiqueta. El fallo anterior
  únicamente aparecía en macOS
- Se refuerza la prueba de los paneles de macOS: además de que devuelva
  instrucciones, ahora exige que **no** se abra nada cuando no hay ancla

### 📝 Documentación
- README al día: versión 7.0.1, badges, los temas reales (claro, oscuro y
  automático), la transparencia (apagada por defecto desde la 6.0.2), el nombre
  real de la acción principal y las rutas que existen
- El conteo de pruebas del CHANGELOG de la 7.0.0 vuelve a coincidir con las
  pruebas reales (36)

---

## [7.0.0] - 2026-09-24

**Identidad visual nueva.** Se abandona el aspecto de tarjetas redondeadas
heredado y se construye uno propio, a partir de la propia marca de la
aplicación: su icono es una seta roja.

### 🎨 La identidad: «mesa de clasificación»
La aplicación ordena archivos, así que ahora se parece a una mesa donde las
cosas se colocan. Cada decisión sale de ahí:

- **Se acabaron las tarjetas.** El material nativo de un organizador de archivos
  es una lista alineada, no una pila de cajas. La jerarquía la llevan ahora el
  espacio y una línea fina: ningún bloque va dentro de un contenedor redondeado
- **El carmesí es un sello, no un fondo.** Sale del sombrero de la seta
  (`#C4123C`) y aparece en dos sitios: el marcador de la sección activa y **una**
  acción por pantalla. Antes el azul del sistema estaba en todas partes y por eso
  no destacaba nada
- **Los números se alinean.** Todo valor que cambia —recuentos, tamaños,
  intervalos, rutas— va en monoespaciada con cifras tabulares, porque ahí la
  alineación significa algo
- **Cálido, no clínico.** El papel y la tinta llevan una traza del rojo de la
  seta, en vez del gris de sistema
- **Más estrecho.** El ancho de lectura baja de 980 a 760 px: con 980, una
  etiqueta y su valor quedaban a 750 px de distancia y la vista se cansaba

### 🧭 El raíl lateral
- La barra lateral pasa a ser un raíl: un escalón por detrás del papel, con el
  nombre de cada sección y **una barra carmesí** marcando dónde estás
- Ya no es una píldora de color con el icono en blanco: el icono activo va en
  carmesí sobre el papel
- Las etiquetas aparecen a partir de 880 px en vez de 1100, porque el raíl con
  nombres es la seña de identidad y conviene verlo en una ventana normal

### ✍️ Jerarquía y lenguaje
- El estado de la aplicación tenía el mismo tamaño que el título de la sección,
  así que no había jerarquía: ahora va un escalón por debajo
- Los títulos de sección estaban en gris y se leían como etiquetas secundarias;
  ahora van en tinta
- El botón de la cabecera ya no comparte el carmesí con la acción principal
- «Deshacer» deja de ser una acción de peligro: deshace, no destruye
- Se quitan las cadenas con puntos medios («Activa · modo Básico»), que son un
  recurso de plantilla; ahora se leen como frases
- Las lengüetas pasan de píldoras a subrayado

### 🐛 Correcciones
- **El permiso de notificaciones ya no se pide cuando no consta que falte.**
  Se declaraba «sin comprobar» (honesto: no se puede saber desde dentro si el
  sistema mostrará los avisos) pero la interfaz lo interpretaba como «no lo
  tienes», así que con el permiso ya concedido seguía pidiéndolo
- **La transparencia pasa a estar apagada por defecto.** En un Mac real, la
  ventana translúcida dejaba restos del fotograma anterior y al cambiar de
  sección el título se dibujaba encima del viejo. Se activa a propósito con
  `DESCARGASORDENADAS_TRANSPARENCIA=1`
- El asistente de permisos separa sus filas con líneas: con el estilo plano se
  leían como un bloque continuo

### 🧪 Pruebas
36 pruebas funcionales. Las de responsive y de tokens se derivan ahora de los
umbrales y de la lista real de tokens, así que no hay que reescribirlas cada vez
que se ajusta el diseño.

---

## [6.0.1] - 2026-09-24

Correcciones a partir de la primera instalación real en macOS. Los tres fallos
venían de dar por buenas cosas que no se habían probado en un Mac.

### 🔔 Dejaba de avisar de una versión nueva… que ya estaba instalada
El aviso «hay una versión nueva» se guarda en disco para no consultar GitHub en
cada arranque. El problema es que sobrevivía a la propia actualización: si te
avisó de la 6.0.0 estando en la 5.1.0, al instalar la 6.0.0 el aviso seguía
saliendo durante 24 horas más. Al pulsar «Buscar actualizaciones» desaparecía,
porque esa comprobación sí consulta de verdad. Ahora el aviso guardado se
compara con la versión instalada y se descarta si ya no aplica.

### 🔐 El botón de conceder un permiso no abría Ajustes
- Se usaba un identificador de panel **inventado** para Notificaciones
  (`Privacy_Notifications`), que no existe: las notificaciones tienen su propio
  panel, no están dentro de Privacidad y seguridad
- Ahora se prueba primero el identificador moderno (macOS 13 y posteriores) y
  después el clásico, y si ninguno funciona se abre al menos Ajustes del sistema
  indicando la ruta exacta a mano
- Se usa la ruta absoluta `/usr/bin/open`: al abrir la app desde el Finder, el
  `PATH` del proceso es mínimo
- **El diálogo que aparecía encima de Ajustes ha desaparecido.** Se mostraba una
  ventana modal justo después de abrir Ajustes, tapándolo, y daba la impresión
  de que no se había abierto nada. Ahora el aviso va a la barra de estado
- Para el Acceso total al disco se avisa de que puede hacer falta cerrar y
  volver a abrir la aplicación

### 💾 «Descargar e instalar» daba error en Mac
La causa no era un permiso que faltara, sino **dónde se escribía**: el
instalador, los scripts y el respaldo se guardaban dentro de la carpeta de la
aplicación. En macOS la app vive en un paquete firmado dentro de `/Applications`
y en Windows en `Program Files`, así que escribir ahí falla con un error de
permisos. Ahora todo va a la carpeta temporal del usuario.

Además, en macOS se usaba `installer -pkg -target /`, que **exige ser root** y
por tanto fallaba siempre, en silencio, escribiendo el error en un registro que
no se mostraba. Ahora se abre el `.pkg` con `open`, que lanza el Instalador del
sistema y pide la contraseña con su propio diálogo. Como consecuencia, en macOS
la aplicación ya no se reabre sola: el Instalador tiene el control, y el aviso
lo dice claramente en lugar de prometer algo que no ocurre.

### 🧪 Pruebas
- **33 pruebas funcionales** (eran 30): aviso de actualización no obsoleto,
  que la actualización no escriba dentro de la aplicación, y los paneles de
  macOS con su respaldo
- **Un fallo en una prueba ya no cuelga la suite.** Al instalarse el manejador
  de errores de la aplicación, cualquier fallo abría una ventana modal y la
  ejecución se quedaba esperando indefinidamente. Ahora las pruebas usan un
  manejador que informa por consola

### 📝 Documentación
Corregida una docstring que seguía diciendo que en macOS se usa `installer`,
cuando precisamente ese era el fallo.

---

## [6.0.0] - 2026-09-24

Versión centrada en dos cosas: que la aplicación **pida los permisos en lugar de
fallar**, y que la interfaz deje de parecer anticuada, con transparencia real y
un comportamiento correcto en cualquier tamaño de ventana.

### 🔐 Los permisos se piden antes de fallar
- **Nuevo sistema de permisos**: un único punto por el que pasa todo lo que
  depende del sistema operativo. Comprueba de verdad si el permiso está
  concedido (escribiendo un archivo de prueba, no preguntando), y si falta lo
  solicita abriendo el panel exacto donde se concede
- **Asistente de primer arranque**: la primera vez que se abre la aplicación,
  una ventana explica qué necesita y para qué, en lenguaje llano. Todo es
  omitible y se puede volver a revisar desde Ajustes
- **Centro de permisos en Ajustes**: el estado de cada permiso en vivo, con un
  botón para resolverlo. Responde de un vistazo a «¿por qué no me funciona
  esto?»
- **Se detecta al volver**: si vas a Ajustes del sistema, concedes el permiso y
  vuelves, la aplicación se da cuenta sola. Sin reiniciar
- **Nada falla en silencio**: los errores que antes se descartaban sin más
  (refrescar el Finder, notificaciones) ahora se avisan y quedan consultables
- **Windows ya no necesita administrador**: el menú contextual se registra por
  usuario, que no requiere permisos. Registrar para todo el equipo pasa a ser
  una opción explícita
- **Ningún fallo acaba en una traza**: un manejador global registra el error y
  lo muestra en una ventana legible, con el detalle plegado

### ✨ La transparencia ahora se ve de verdad
- **El efecto estaba activado y tapado a la vez**: se creaba el material nativo
  de macOS y se activaba Mica en Windows, pero la ventana nunca se declaraba
  translúcida, así que Qt pintaba su fondo opaco encima. Ahora se ve
- **macOS**: *vibrancy* real, con la capa insertada **por debajo** del contenido
  (como subvista quedaría encima y taparía la interfaz)
- **Windows 11**: efecto Mica y esquinas redondeadas del sistema. En Windows 10
  se mantiene el fondo opaco, porque Mica no existe ahí
- **Linux**: se acabó el `setWindowOpacity`, que no era translucidez sino bajar
  la opacidad de la ventana entera, texto incluido. Ahora se comprueba que haya
  compositor y, si no lo hay, la ventana se queda opaca
- El fondo deja pasar el material (alfa 0.70) pero las tarjetas se mantienen
  casi opacas (0.96), así que el texto no pierde contraste
- Se puede desactivar con `DESCARGASORDENADAS_SIN_TRANSPARENCIA=1`

### 📐 La ventana se adapta de verdad
- **Arreglado el fallo de fondo**: el contenido fijaba un ancho *mínimo* igual
  al espacio disponible, lo que impedía encoger la ventana por debajo de 760 px
  y hacía que el layout desbordara en pantallas pequeñas. Ahora solo tiene
  máximo
- **Tres modos de barra lateral**, sin el salto brusco de antes: con texto en
  ventanas anchas, solo iconos a partir de 660 px y **flotante** en ventanas
  estrechas, donde se abre con un botón y se cierra al pulsar fuera
- El tamaño mínimo de ventana baja de 760×560 a **620×520**

### 🎨 Aspecto más cuidado
- **Iconos propios**: 23 iconos SVG dibujados para la aplicación, en lugar de
  los genéricos de Qt que no son el lenguaje visual de ningún sistema. Nítidos
  en pantallas de alta densidad y pintados en el color del tema
- **Sistema de diseño con tokens**: espaciado, radios, tipografía y duración de
  las animaciones salen de una única escala, en lugar de números sueltos
- **Se retiró el sistema de estilos antiguo** (`temas.py`), con sus degradados
  y sus botones de otro tiempo. Ahora hay una sola fuente de verdad
- El cambio de sección se siente inmediato (90 ms en lugar de 150)

### 🧹 Otros
- La versión se lee de un único sitio: antes había números fijos repartidos que
  se quedaban desactualizados en cada publicación
- Las descripciones de uso del `Info.plist` de macOS, que faltaban
- **30 pruebas funcionales** (9 nuevas): permisos, degradación sin permisos,
  asistente, iconos, tokens y los tres modos de la interfaz

### ⚠️ Nota sobre la transparencia
Las rutas de macOS y Windows 11 están implementadas pero se han desarrollado en
un entorno Linux, así que no se han podido ejecutar. Conviene verificarlas en un
Mac y en un Windows 11 reales. Si algo no se viera bien, se puede desactivar con
la variable de entorno indicada arriba sin tocar el código.

---

## [5.1.0] - 2026-09-23

### ✨ Interfaz que se siente nativa en cada sistema
- **Transparencias reales por sistema**: *vibrancy* en macOS (el material de
  barra lateral de Finder), efecto **Mica** en Windows 11 y translucidez en
  Linux. Si el sistema no lo admite, la ventana se ve igual que antes
- **Diseño adaptable de verdad**: la barra lateral se estrecha a solo iconos en
  ventanas pequeñas y se ensancha en pantallas grandes; el contenido se limita
  a un ancho cómodo y se centra, así no queda nada descolgado en las esquinas
- Nuevos detalles: punto de estado con colores, etiquetas tipo «chip» para el
  resumen por categoría, campos de hora integrados y más aire entre secciones

### 👀 Previsualización antes de organizar
- Al pulsar «Organizar ahora» se muestra **exactamente qué se moverá**: cuántos
  archivos, cuánto ocupan, el reparto por categoría y la lista con su destino
- **Nada se toca hasta confirmar**: se puede revisar y cancelar sin riesgo
- Los archivos a medio descargar siguen quedando fuera del plan

### 🕘 Historial con deshacer
- Nueva sección **Historial**: cada organización queda registrada con fecha,
  modo y número de archivos
- Se puede **deshacer una operación concreta**, devolviendo esos archivos a su
  sitio sin afectar a las demás
- Se conservan las últimas 30 operaciones

### 📅 Organización programada
- Nuevo ajuste para organizar **todos los días a una hora concreta**
  (por ejemplo, a las 22:00), además del automático por intervalos
- Muestra cuánto falta para la próxima ejecución

### 💾 Análisis de uso de disco
- Nueva pestaña **Disco** en Avanzado: qué ocupa más, reparto por categoría,
  archivos más grandes y **sugerencias de limpieza** (temporales, descargas
  incompletas, archivos sin tocar en un año)
- Solo lectura: informa, nunca borra ni mueve nada

### ⌨️ Más comodidad
- **Atajos de teclado**: Cmd/Ctrl+O organizar, Cmd/Ctrl+Z deshacer,
  Cmd/Ctrl+1…5 cambiar de sección, Escape a la bandeja, F5 refrescar
- **Arrastrar y soltar**: suelta una carpeta sobre la ventana y elige si
  organizarla o usarla como principal

### 🧪 Pruebas
- 21 pruebas funcionales (6 nuevas): previsualización, historial con deshacer,
  programación horaria, análisis de disco y degradación de efectos

---

## [5.0.3] - 2026-09-22

### 🖱️ Menú contextual de macOS arreglado (daba error en Finder)
- **Causa**: la Acción rápida que se instalaba en `~/Library/Services` no tenía
  los metadatos que Automator necesita (identificador del bundle, clase de la
  acción, UUID…), así que Finder respondía «Automator no ha podido ejecutar el
  flujo de trabajo: la acción no se ha cargado»
- Además, la entrada se configuraba para no recibir las carpetas seleccionadas,
  por lo que, incluso cargando, el script se ejecutaba sin saber qué organizar
- Ahora se genera el flujo con el **formato exacto de los flujos del sistema**
  (verificado contra `Run Shell Script` de `/System/Library/Automator`), de modo
  que Finder lo carga y las rutas llegan al script como argumentos
- **Reparación automática**: si la Acción rápida quedó dañada de una versión
  anterior, la aplicación la detecta al abrirse y la regenera sola; no hay que
  desinstalar ni tocar nada
- También se refresca la caché de servicios (`pbs -flush` y recarga de Finder)
  para que aparezca sin cerrar sesión
- Nueva prueba funcional que valida el flujo con `automator` de verdad

---

## [5.0.2] - 2026-09-22

### 🐛 Actualizaciones que no se detectaban (decía «5.0.0» estando la 5.0.1)
- **Causa**: la comprobación dependía en exclusiva de la API de GitHub, que sin
  autenticar permite 60 peticiones por hora. Al agotarse, GitHub responde 403 y
  la aplicación lo interpretaba como «ya tienes la última versión»… y además
  guardaba la fecha como si hubiera comprobado bien, así que **no reintentaba
  hasta 24 horas después**
- Ahora se prueban **tres canales** en orden:
  1. La API de GitHub (datos completos: notas y archivos adjuntos)
  2. La redirección de `/releases/latest`, que **no tiene límite** y basta para
     saber la versión publicada
  3. La página de etiquetas del repositorio, también sin límite
- Si todos fallan, se avisa con claridad de que **no se pudo comprobar** (ya no
  se dice «estás actualizado» cuando en realidad no se ha mirado) y se reintenta
  más tarde, sin esperar 24 h
- La descarga del instalador ya no depende de la API: se construye la URL
  directa del archivo del sistema (`.exe` / `.pkg` / `.deb`) y se verifica que
  existe antes de descargarlo
- **Migración automática**: los equipos con el archivo de estado antiguo (que
  quedó bloqueado) vuelven a comprobar la actualización en el siguiente arranque
- Nueva prueba funcional que simula el límite de GitHub y la falta de red

---

## [5.0.1] - 2026-09-22

### 🐛 Controles de auto-organización siempre coherentes
- Corregido el fallo por el que el modo Básico/Detallado y la hora se quedaban
  «pinzados»: los radios de Qt no se pueden desmarcar cuando están en grupo, así
  que apagar el interruptor dejaba el estado a medias y el siguiente cambio no
  se aplicaba
- Ahora **todo** (encender, apagar, cambiar de modo y cambiar la hora) pasa por un
  único punto que actualiza a la vez el interruptor, los radios, el
  temporizador, la tarjeta de estado y lo que se guarda para el próximo arranque
- Cambiar «Revisar cada» con la auto-organización encendida aplica el intervalo
  **al momento** y reinicia la cuenta (antes el temporizador seguía con la hora
  anterior)
- Cambiar de modo con la auto-organización **apagada** ya no la enciende sola:
  solo se recuerda la elección para cuando la actives
- Al encender se usa exactamente el modo y la hora que dejaste seleccionados
- Nueva prueba funcional de regresión que cubre todos estos casos

---

## [5.0.0] - 2026-09-22

### 🎨 Diseño nuevo tipo Apple
- La interfaz pasa de pestañas superiores a **barra lateral** con secciones Inicio,
  Actividad, Ajustes y Avanzado
- Nuevo sistema de estilos centralizado (`organizer/estilos.py`): paleta clara y
  oscura de macOS, tipografía nativa de cada sistema, tarjetas, esquinas
  redondeadas, separadores finos y transiciones suaves
- **Tema automático**: sigue el tema claro/oscuro del sistema (Windows, macOS y
  Linux) y se puede forzar Claro u Oscuro en Ajustes
- Cabecera con la carpeta actual y botón principal; animación corta al cambiar de
  sección; los interruptores tienen el tamaño correcto en cualquier resolución

### 🧭 Una sola instancia, siempre
- Bloqueo por archivo + **mutex con nombre en Windows** compartido con el
  instalador: es imposible tener dos copias abiertas
- El canal entre instancias ahora habla JSON y admite órdenes: mostrar la ventana
  u organizar una carpeta
- Si arrancas la app dos veces, la segunda no abre nada: trae al frente la que ya
  está abierta (o le pide el trabajo)

### 🖱️ Menú contextual que por fin funciona
- Nuevo `--organizar-carpeta RUTA`: organiza esa carpeta **sin abrir ventana**
- Si la app ya está abierta, el menú contextual **delega** en ella; si no, lo hace
  por su cuenta y termina
- Windows: se registra en `HKEY_CURRENT_USER` (sin permisos de administrador) y
  también en carpetas y en el fondo de carpeta
- macOS: Acción rápida de Finder, con aviso de los permisos que macOS pida
- Linux: entrada `.desktop` para «Abrir con…» y script de Nautilus, todo en la
  carpeta del usuario (compatible con Flatpak/Snap)
- Los problemas de permisos se avisan de forma clara, nunca revientan

### ⬇️ Actualizar sin dejar copias sueltas
- «Descargar e Instalar» ahora hace el ciclo completo: descarga el instalador
  nativo, **cierra la app**, instala encima y **vuelve a abrirla** actualizada
- Windows: asistente en modo silencioso con `/CLOSEAPPLICATIONS` y mutex
  compartido; macOS: `installer -pkg`; Linux: instalación con permisos explícitos
- Se elimina el riesgo de dos instancias durante la actualización

### 📂 Organización más segura
- Detección de la carpeta de descargas real: registro de Windows, XDG en Linux y
  ~/Downloads en macOS, con creación automática si no existe
- **No se tocan las descargas a medias**: `.part`, `.crdownload`, `.tmp`… se quedan
  donde están para no corromperlas
- Avisos de permisos legibles con pasos concretos según el sistema
- «Cambiar carpeta» ahora permite organizarla una vez o **usarla como carpeta
  principal**, y esa elección se recuerda entre reinicios

### 🚀 Arranque con el sistema
- Linux: se usa el estándar **XDG autostart** (funciona en GNOME, KDE, XFCE…),
  con systemd de usuario como complemento opcional
- macOS: LaunchAgent más robusto (recarga limpia, límite de sesión Aqua, registro
  de errores en /tmp)

### 🪟 Instalador Windows
- `AppMutex` compartido con la aplicación: el asistente nunca se ejecuta con la
  app abierta
- `CloseApplications` / `RestartApplications` para cerrar y reabrir sin duplicados
- Registro de instalación activado para diagnosticar problemas

### 🧪 Pruebas
- 13 pruebas funcionales: organización, descargas en curso, permisos, estilos,
  barra lateral, tema automático, instancia única, menú contextual y CLI

---

## [4.8.0] - 2026-09-22

### 🐛 Automático fiable al arrancar
- La organización automática se activa justo al abrir si estaba activada (sin el retardo que fallaba)
- La tarjeta de estado muestra el estado real desde el primer segundo
- Corregido el modo guardado por defecto (Básico) y el intervalo (1 hora)

### ⬇️ Actualización "Descargar e Instalar" arreglada
- Ahora descarga el instalador nativo de tu sistema (.exe / .pkg / .deb) y lo abre
- Ya no intenta instalar un ZIP del código (fuente del error)

### 🖱️ Menú contextual (Windows)
- Comando corregido para que organice la carpeta seleccionada con `--auto`
- Verificado el registro en macOS (Acción rápida) y Linux (Nautilus / Abrir con)

---

## [4.7.0] - 2026-09-22

### 🎛️ Automático tal como lo dejaste
- Nuevo interruptor encendido/apagado para la organización automática (y para arrancar con el sistema)
- Por defecto: Básico y 1 hora; la elección se restaura al abrir la app sin tocar nada
- Añadida la opción de apagar la organización automática cuando quieras

### 🖱️ Menú contextual
- Corregido el script de Nautilus (Linux) que lanzaba la ordenación sin la carpeta
- Verificado en macOS (Acción rápida de Finder) y Linux (script y "Abrir con")

### 📂 Cambiar carpeta
- Al elegir otra carpeta, se organiza en segundo plano con aviso de progreso
- La carpeta de trabajo vuelve a ser la anterior al terminar

---

## [4.6.1] - 2026-09-21

### 🐛 Corrección de crash al arrancar (macOS)
- El icono de la bandeja se dibuja cerrando siempre el QPainter (try/finally)
- Si el dibujo falla, se usa un icono estándar de carpeta en lugar de romper el arranque
- Afectaba a la 4.5.0/4.6.0 instalada: QPainter sin cerrar podía corromper memoria (SIGSEGV)

---

## [4.6.0] - 2026-09-21

### 🎨 Interfaz afinada
- Solo quedan los temas Minimal claro y Minimal oscuro; los antiguos se retiran (migran al oscuro)
- Pestaña de Ajustes separada de Actividad; las herramientas avanzadas (IA, Fechas, Duplicados, Estadísticas) se agrupan en Avanzado

### 🖱️ Menú contextual en los tres sistemas
- macOS: acción rápida de Finder (clic derecho → Acciones rápidas → Organizar con DescargasOrdenadas)
- Linux: entrada "Abrir con…" para carpetas y script para Nautilus
- Windows: el comando ahora organiza la carpeta seleccionada (antes solo la abría)

---

## [4.5.0] - 2026-09-21

### 🗂️ Carpetas y menú contextual
- La reorganización completa ahora también lleva las carpetas sueltas a Carpetas/
- El menú contextual de Windows apunta a la carpeta elegida y usa el icono de la app
- Icono de bandeja nuevo: carpeta con flecha de ordenación (sin círculo verde ni champiñón)
- Textos de la ventana y de la bandeja más sobrios

---

## [4.4.0] - 2026-09-21

### 🎨 Rediseño minimalista
- Nueva pantalla de inicio con lo esencial: automático (Básico/Detallado), cada cuánto y arrancar con el sistema
- Temas Minimal Claro y Minimal Oscuro, planos y discretos (paleta tipo Apple)
- Ventana más compacta por defecto y pestañas en formato píldora
- Ajustes y actividad reunidos en una sola pestaña; sin colores llamativos

---

## [4.3.0] - 2026-09-21

### 🧭 Una sola instancia
- Nuevo control de instancia única en Windows, macOS y Linux
- Si la app ya está abierta, el segundo arranque la muestra en lugar de duplicarla
- El bloqueo se libera solo, incluso si la app se cierra a la fuerza

### ⚙️ Autoarranque con memoria
- El modo BÁSICO/DETALLADO y el intervalo se guardan y se restauran al arrancar
- El autoarranque del sistema se reescribe con el modo elegido
- Al apagar la auto-organización, el autoarranque deja de auto-organizar

### 🛠️ Otros
- `--nueva-instancia` para forzar una segunda copia si alguien la necesita
- Empaquetado: incluidos PySide6.QtNetwork y el módulo de instancia única

---

## [4.2.0] - 2026-09-19

### 🔁 Reparación en app instalada
- `--reparar-dependencias` ahora busca Python del sistema en modo instalado
- Evita intentar usar `pip` dentro del binario empaquetado

---

## [4.1.0] - 2026-09-19

### 🧰 Dependencias online
- Nuevo `--reparar-dependencias` para descargar e instalar dependencias faltantes
- `--info` ahora muestra las dependencias que faltan
- Instaladores adjuntados automáticamente al release

---

## [4.0.0] - 2026-09-19

### 🎉 Versión estable multiplataforma
- CLI con diagnóstico, simulación y modos de organización
- Instaladores automáticos para Windows, macOS y Linux
- GUI responsive con scroll y tamaño de ventana persistente
- Autoarranque unificado en Windows, macOS y Linux

---

## [3.9.0] - 2026-09-19

### 🧭 Organización configurable desde terminal
- Nuevo `--modo basico` y `--modo detallado`
- Nuevo `--recursivo` para procesar también las subcarpetas

---

## [3.8.0] - 2026-09-19

### 🧪 Modo simulación
- Nuevo argumento `--dry-run` para ver qué se organizaría sin mover archivos
- No crea carpetas ni modifica la huella de archivos procesados

---

## [3.7.0] - 2026-09-19

### 🧭 Diagnóstico desde terminal
- Nuevo argumento `--version` para ver la versión exacta
- Nuevo argumento `--info` para ver sistema, Python, rutas y módulos avanzados

---

## [3.6.0] - 2026-09-17

### 📦 Instaladores por Sistema
- Windows: instalador `.exe` con Inno Setup
- macOS: instalador `.pkg` nativo con `productbuild`
- Linux: paquete `.deb` listo para instalar

### 🔐 Permisos y Dependencias
- Los instaladores piden permisos de administrador
- Todas las dependencias van incluidas dentro de la app
- No hace falta ejecutar `.bat` ni `.sh`

### 🛠️ Empaquetado
- Nuevo spec de PyInstaller multiplataforma
- Recursos, iconos y `VERSION.txt` se incluyen en el paquete
- Configuración compatible con app instalada en cada sistema

---

## [3.5.0] - 2026-09-17

### 🖥️ Interfaz Responsive
- Las pestañas ahora usan scroll automático en pantallas pequeñas
- Tamaño mínimo de ventana reducido para caber en más resoluciones
- La app recuerda el tamaño y el estado maximizado entre sesiones
- Todos los campos siguen accesibles aunque la ventana no esté maximizada

### 🚀 Autoarranque Multiplataforma
- macOS usa LaunchAgent y Linux usa systemd con los argumentos reales
- Se guarda la preferencia de inicio automático en la configuración
- Se muestra una notificación nativa al activarlo o desactivarlo
- La app arranca minimizada en la bandeja del sistema

### 🔄 Actualizaciones
- Si no hay Release publicado en GitHub, ahora usa los tags del repo como fallback

### 🐧 Linux
- Autoarranque corregido con el intérprete correcto y argumentos reales

---

## [3.4.0] - 2026-09-17

### 🍎 Soporte macOS Completo

#### 🐛 Corrección Crítica de Arranque
- **Corregido el bloqueo total en macOS** - `autostart.py` importaba `winreg` (exclusivo de Windows) sin condición y la GUI lo importa siempre, por lo que la aplicación **ni siquiera arrancaba** en Mac. Ahora el import es condicional

#### 🚀 Autoarranque en macOS
- **LaunchAgent corregido** - Usaba el argumento `--auto-organizar` (inexistente); ahora usa `--autostart --minimizado`, los argumentos reales de `INICIAR.py`
- **Rutas con espacios** - El XML del plist ahora escapa correctamente espacios y caracteres especiales
- **launchctl moderno** - Usa `bootstrap`/`bootout` (sintaxis actual de macOS) con fallback a `load`/`unload` para versiones antiguas

#### 🔄 Actualizaciones en macOS
- **Reinicio corregido** - Tras actualizar, usaba constantes exclusivas de Windows (`DETACHED_PROCESS`, `CREATE_NO_WINDOW`) que no existen en Mac/Linux y provocaban error. Ahora cada plataforma usa su mecanismo correcto (`start_new_session` en Unix)

### 🐧 Soporte Linux
- Autoarranque con systemd ya existía; los nuevos lanzadores de terminal lo hacen usable de principio a fin

### ⚙️ Lanzadores Multiplataforma
- `INSTALAR_DEPENDENCIAS.sh` - Instalador para Mac/Linux que crea un entorno virtual `.venv` (evita el Python "externally-managed" de macOS/Homebrew)
- `INICIAR.sh` - Lanzador de terminal que usa el `.venv` si existe
- `INICIAR.command` y `INSTALAR_DEPENDENCIAS.command` - Doble clic desde Finder en macOS

### ✅ Pruebas
- Nuevas pruebas de regresión multiplataforma: import de `autostart` en cualquier SO y existencia de lanzadores

---

## [3.3.0] - 2026-09-17
## [3.3.0] - 2026-09-17

### 🔧 Correcciones Críticas

#### 🔄 Sistema de Actualizaciones
- **Corregido el repositorio de GitHub** - Apuntaba a `AntonioIbanez1` (inexistente) y ahora apunta a `AntonioXam/Descargas-Ordenada`, por lo que la búsqueda de versiones vuelve a funcionar
- **Corregido el módulo antiguo** `actualizaciones.py` - Usaba una URL de ejemplo (`usuario/descargasordenadas`) y versión 3.1.0

### 📌 Versión Centralizada
- Nuevo módulo `organizer/version.py` - `VERSION.txt` es ahora la única fuente de verdad de la versión
- Todos los módulos (GUI, actualizaciones, arranque) leen la versión del mismo sitio
- Eliminadas las versiones duplicadas y desincronizadas (3.1.0, 3.2.0 y 1.0.0 en distintos archivos)

### 🧮 Mejoras Técnicas
- Comparación de versiones semánticas rellenando con ceros - `3.3` y `3.3.0` ahora se comparan correctamente
- El footer de la GUI muestra la versión dinámicamente en lugar de un texto fijo
- `__version__` del paquete `organizer` ahora se sincroniza con `VERSION.txt`

### 📚 Documentación
- Corregidas todas las URLs de GitHub en docs y scripts (antes apuntaban al usuario equivocado)

---

## [3.2.0] - 2026-01-14

### ✨ Nuevas Funcionalidades

#### ⏱️ Intervalos Personalizables
- Selector de tiempo para auto-organización con opciones:
  - ⚡ 30 segundos
  - 🕐 1 minuto
  - 🕐 5 minutos
  - 🕐 10 minutos
  - 🕐 30 minutos
  - 🕐 1 hora
  - 📅 1 día
- El intervalo seleccionado se muestra en tiempo real en el estado y logs

#### 🚀 Gestión de Inicio Mejorada
- Botón dedicado **"Agregar al Inicio"** para activar arranque automático
- Botón dedicado **"Quitar del Inicio"** para desactivar arranque automático
- Se eliminó el checkbox confuso de "Iniciar con el sistema"
- Mensajes claros de confirmación

#### 🔄 Actualizaciones Completamente Automáticas
- **Descarga automática** desde GitHub (repositorio público)
- **Instalación automática** en la misma carpeta
- **Reinicio automático** de la aplicación tras actualizar
- **Backup automático** antes de actualizar
- **Preservación de configuración** (.config/)
- **Verificación de versión** - Solo descarga si hay versión nueva
- **Sin necesidad de cuenta GitHub** - Acceso público
- **Barra de progreso** durante la descarga

### 🎨 Mejoras de Interfaz

#### Ventana Principal
- Tamaño inicial: 1200x850 (antes 1000x700)
- Tamaño mínimo: 1100x800
- Todos los campos visibles sin scroll
- Footer con versión "v3.2.0" en pequeño (abajo derecha)

#### Títulos
- **Antes:** "DescargasOrdenadas v3.0 - Funcionalidades Completas"
- **Ahora:** "🍄 DescargasOrdenadas - Organizador Automático"
- Versión solo en el footer (discreta)
- Headers genéricos sin número de versión

#### Textos Dinámicos
- Estado de auto-organización muestra el intervalo real
- Tooltip de bandeja del sistema actualizado con intervalo
- Logs con información precisa del tiempo configurado

### 🧹 Limpieza del Proyecto

#### Documentación Eliminada (25 archivos)
Se eliminó documentación redundante y temporal:
- Todos los `RESUMEN_*.txt`
- Todos los `GUIA_*.txt` duplicados
- Archivos de estado temporal
- Instrucciones de desarrollo

#### Scripts Eliminados (9 archivos)
Se eliminaron scripts de desarrollo temporal:
- Scripts de configuración manual de GitHub
- Scripts de pruebas de desarrollo
- Scripts de integración de versiones

#### Documentación Conservada
Solo se mantiene documentación útil para usuarios:
- ✅ `README.md` (principal)
- ✅ `docs/COMO_USAR.md`
- ✅ `docs/BANDEJA_SISTEMA.md`
- ✅ `docs/CREAR_PORTABLES.md`
- ✅ `docs/INSTRUCCIONES_PORTABLE.md`
- ✅ `docs/MEJORAS_IMPLEMENTADAS.md`
- ✅ `docs/ACTUALIZACIONES.md` (nuevo)
- ✅ `docs/PUBLICAR_EN_GITHUB.md` (nuevo)

### 🔧 Cambios Técnicos

#### Sistema de Actualizaciones
- Versión actual: `3.2.0`
- GitHub User: `AntonioIbanez1`
- GitHub Repo: `Descargas-Ordenada`
- API URL pública sin autenticación
- Función `reiniciar_aplicacion()` mejorada
- Script batch temporal para reinicio en Windows

#### Configuración
- Nuevo archivo `VERSION.txt` con la versión actual
- Script `scripts/PREPARAR_RELEASE.bat` para crear releases
- Módulo `actualizaciones_mejorado.py` actualizado a v3.2.0

### 📄 Archivos Nuevos
- `VERSION.txt`
- `CHANGELOG.md`
- `docs/ACTUALIZACIONES.md`
- `docs/PUBLICAR_EN_GITHUB.md`
- `scripts/PREPARAR_RELEASE.bat`

### 🐛 Correcciones
- Arreglado: Intervalo de auto-organización siempre mostraba "30 seg"
- Arreglado: Versión hardcodeada en múltiples lugares
- Arreglado: Ventana pequeña que cortaba campos
- Arreglado: Confusión entre checkbox y botones de inicio

### 🗑️ Archivos Eliminados
- 25 archivos de documentación temporal
- 9 scripts de desarrollo
- `INICIAR_SIN_CONSOLA.pyw` (consolidado en INICIAR.bat)

---

## [3.1.0] - 2026-01-13

### ✨ Nuevas Funcionalidades

#### 🔔 Notificaciones Nativas
- Integración con el sistema de notificaciones de Windows
- Librería `plyer` para notificaciones multiplataforma
- Checkbox para activar/desactivar
- Fallback a notificaciones Qt si plyer no está disponible

#### 🎨 Sistema de Temas
- 5 temas personalizables:
  - 🔵 Azul Oscuro (predeterminado)
  - 🟢 Verde Oscuro
  - 🟣 Púrpura
  - 🟠 Naranja
  - ⚫ Gris
- Selector de tema en tiempo real
- Configuración guardada entre sesiones

#### 💾 Configuración Portable
- Sistema de configuración JSON portable
- Archivo `.config/descargasordenadas_config.json`
- Guarda:
  - Tema seleccionado
  - Notificaciones activas
  - Última carpeta seleccionada
  - Tamaño y posición de ventana
  - Última verificación de actualizaciones

#### 🖱️ Menú Contextual de Windows
- Opción "Organizar con DescargasOrdenadas" al hacer click derecho en carpetas
- Registro en el registro de Windows
- Checkbox para activar/desactivar
- Funciona con `pywin32`

#### 🔄 Sistema de Actualizaciones
- Verificación automática desde GitHub
- Descarga manual desde la interfaz
- Comprobación de versión semántica
- Notificación de nuevas versiones disponibles

### 🔧 Mejoras Técnicas
- Módulos separados para cada funcionalidad
- Imports con try-except para dependencias opcionales
- Logging mejorado
- Manejo de errores robusto

---

## [3.0.0] - 2026-01-12

### ✨ Versión Base

- 📁 Organización automática de archivos
- 🤖 Categorización con IA
- 📅 Organización por fechas
- 🔍 Detector de duplicados
- 🪟 Ejecución sin consola
- 🍄 Icono en bandeja del sistema
- 📋 Sistema de logs
- 🎨 Interfaz gráfica con PySide6
- 📊 Vista de estadísticas
- ⚙️ Configuración avanzada

---

## Formato

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

### Tipos de Cambios
- **✨ Nuevas Funcionalidades** - Para funciones nuevas
- **🎨 Mejoras de Interfaz** - Cambios visuales
- **🐛 Correcciones** - Arreglos de bugs
- **🔧 Cambios Técnicos** - Refactorización, optimización
- **🗑️ Eliminado** - Funciones/archivos eliminados
- **📄 Documentación** - Solo cambios en documentación
- **🔒 Seguridad** - Vulnerabilidades corregidas
