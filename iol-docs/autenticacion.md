Documentación para realizar el login en API V1 de InvertirOnline
Autenticación
El método de autenticación que se utiliza en esta plataforma son tokens digitales. Los tokens son simples strings que se envían al servidor. Existen dos tipos de tokens: bearer token y refresh tokens. El bearer token se debe presentar en cada request para poder acceder al recurso solicitado. Este token es válido por 15 minutos desde que se lo solicita. Para renovar este token, se utiliza el refresh token. Para obtener el primer par de tokens se realiza un request POST especificando el nombre de usuario y contraseña a:

https://api.invertironline.com/token
POST /token HTTP/1.1
Host: api.invertironline.com
Content-Type: application/x-www-form-urlencoded
username=MIUSUARIO&password=MICONTRASEÑA&grant_type=password
A continuación se presenta una captura de pantalla de la petición y su respuesta en la herramienta POSTMAN (https://www.getpostman.com/)


Una vez realizada esta petición, se debe utilizar el bearer token para acceder al recurso deseado, para hacer esto, se envía el token en el header de la petición con el Key “authorization” y como valor el token precedido de la palabra Bearer y un espacio como se ve en el ejemplo:

Ejemplo

GET /api/micuenta/miportafolio HTTP/1.1
Host: api.invertironline.com
Authorization: Bearer aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
Acá vemos la petición representada en POSTMAN


Una vez expirado el bearer token, se procede a refrescar el mismo con el refresh token. Para realizar esto se debe mandar la siguiente petición al mismo endpoint donde realizamos el login (https://api.invertironline.com/token)

POST /token HTTP/1.1
Host: api.invertironline.com
Content-Type: application/x-www-form-urlencoded
refresh_token=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb&grant_type=refresh_token
Acá vemos la petición representada en POSTMAN


Como podemos observar, nos devolvió otro par de tokens para que podamos repetir el proceso.

Made with ❤ by invertironline.com