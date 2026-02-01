Introducción
En esta página presentamos la documentación para nuestro Servicio de APIs.
Todas las acciones realizadas por este medio impactan en el entorno REAL.

Requisitos para el uso de APIs
Para poder hacer uso de las APIs se requiere una Cuenta de Inversión Abierta, y realizar los siguientes pasos:
Loguearse en el sitio
Ingresar a la sección de mensajes y enviar uno solicitando la activación de APIs
Una vez que se le confirmemos la activación del produco, debe ingresar a la Sección APIs para aceptar los términos y condiciones del servicio:
Mi Cuenta > Personalización > APIs
Autenticación
El método de autenticación que se utiliza en esta plataforma son tokens digitales. Los tokens son simples strings que se envían al servidor. Existen dos tipos de tokens: bearer token y refresh tokens. El bearer token se debe presentar en cada request para poder acceder al recurso solicitado. Este token es válido por 15 minutos desde que se lo solicita.
Para renovar este token, se utiliza el refresh token. Para conocer más acerca del mecanismo de autenticación ingrese al siguiente link Ver método de autenticación.

Donde además podrá encontrar algunos ejemplos del uso de las APIs
Entorno de Pruebas (Sandbox API)
Contamos con un entorno de pruebas que te permite probar tus desarrollos en un ambiente seguro y aislado del mercado. Se pueden realizar operaciones simuladas de compra/venta y pedidos de cancelación. También uno puede actuar como broker asignándose fondos a su cuenta, además de cancelar o concertar ordenes. Tu cuenta en este ambiente no guarda ninguna relación con tu usuario ni con los servicios de API de InvertirOnline.com.

Funciones de APIs
A continuación se describe las operaciones que están realizadas en APIs.

Comenzar: 
Ingresar Token invertironline.com APIs
 ¿Dónde encuentro el token?help
Versión API 2.0
AsesoresShow/HideList OperationsExpand Operations
post /api/v2/Asesor/Movimientos
AsesoresOperarShow/HideList OperationsExpand Operations
post /api/v2/asesores/operar/VenderEspecieD
AsesoresTestInversorShow/HideList OperationsExpand Operations
get /api/v2/asesores/test-inversor
post /api/v2/asesores/test-inversor
post /api/v2/asesores/test-inversor/{idClienteAsesorado}
MiCuentaShow/HideList OperationsExpand Operations
get /api/v2/estadocuenta
get /api/v2/portafolio/{pais}
delete /api/v2/operaciones/{numero}
get /api/v2/operaciones/{numero}
get /api/v2/operaciones
NotificacionShow/HideList OperationsExpand Operations
get /api/v2/Notificacion
OperarShow/HideList OperationsExpand Operations
get /api/v2/operar/CPD/PuedeOperar
get /api/v2/operar/CPD/{estado}/{segmento}
get /api/v2/operar/CPD/Comisiones/{importe}/{plazo}/{tasa}
post /api/v2/operar/CPD
post /api/v2/operar/Token
post /api/v2/operar/Vender
post /api/v2/operar/Comprar
post /api/v2/operar/rescate/fci
post /api/v2/operar/VenderEspecieD
post /api/v2/operar/ComprarEspecieD
post /api/v2/operar/suscripcion/fci
OperatoriaSimplificadaShow/HideList OperationsExpand Operations
get /api/v2/OperatoriaSimplificada/MontosEstimados/{monto}
get /api/v2/OperatoriaSimplificada/{idTipoOperatoria}/Parametros
get /api/v2/OperatoriaSimplificada/Validar/{monto}/{idTipoOperatoria}
get /api/v2/OperatoriaSimplificada/VentaMepSimple/MontosEstimados/{monto}
post /api/v2/Cotizaciones/MEP
post /api/v2/OperatoriaSimplificada/Comprar
PerfilShow/HideList OperationsExpand Operations
get /api/v2/datos-perfil
TitulosShow/HideList OperationsExpand Operations
get /api/v2/Titulos/FCI
get /api/v2/Titulos/FCI/{simbolo}
get /api/v2/Titulos/FCI/TipoFondos
get /api/v2/Cotizaciones/MEP/{simbolo}
get /api/v2/Titulos/FCI/Administradoras
get /api/v2/{mercado}/Titulos/{simbolo}
get /api/v2/{mercado}/Titulos/{simbolo}/Opciones
get /api/v2/{pais}/Titulos/Cotizacion/Instrumentos
get /api/v2/Cotizaciones/{Instrumento}/{Pais}/Todos
get /api/v2/Cotizaciones/{Instrumento}/{Panel}/{Pais}
get /api/v2/{mercado}/Titulos/{simbolo}/CotizacionDetalle
get /api/v2/cotizaciones-orleans/{Instrumento}/{Pais}/Todos
get /api/v2/{pais}/Titulos/Cotizacion/Paneles/{instrumento}
get /api/v2/cotizaciones-orleans/{Instrumento}/{Pais}/Operables
get /api/v2/{Mercado}/Titulos/{Simbolo}/Cotizacion
get /api/v2/cotizaciones-orleans-panel/{Instrumento}/{Pais}/Todos
get /api/v2/Titulos/FCI/Administradoras/{administradora}/TipoFondos
get /api/v2/cotizaciones-orleans-panel/{Instrumento}/{Pais}/Operables
get /api/v2/{mercado}/Titulos/{simbolo}/CotizacionDetalleMobile/{plazo}
get /api/v2/Titulos/FCI/Administradoras/{administradora}/TipoFondos/{tipoFondo}
get /api/v2/{mercado}/Titulos/{simbolo}/Cotizacion/seriehistorica/{fechaDesde}/{fechaHasta}/{ajustada}
[ API VERSION: V2 ]