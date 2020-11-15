# verneServer
Servidor Django para el proyecto Verne. Basado en el stack Django + Apache de Bitnami, que será desplegado sobre una máquina en la nube posteriormente.

# Instrucciones (despliegue local para desarrollo)
Se detalla el proceso para descargar una VM con el mismo stack, para trabajo local y desarrollo del servidor.

## Obtención y configuración de VM
1. Descargar VirtualBox (si no se tiene): https://www.virtualbox.org/wiki/Downloads
1. Descargar VM de la página oficial de Bitnami: https://bitnami.com/stack/django/virtual-machine . OJO: Descargar versión 2.2.16 (la última cuando se escribió esto)
1. Cargar la VM descargada en VirtualBox
   1. Yo personalmente le asigné 2GB RAM y 2CPU, aunque con los 512MB y 1CPU seguramente tire de sobra
   1. Recomendado: modificar la configuración de red de la máquina. Por defecto viene con adaptador puente (al menos para mí), lo que le da una IP más como a cualquier dispositivo de la red local. Eso obliga a conocer esa IP (que puede cambiar) para conectarse a él. Cambiándolo a NAT, y redireccionando los puertos 80 (HTTP) y 22 (SSH), se puede acceder como localhost tanto desde putty como desde el navegador...
1. Iniciar máquina
   1. Usuario = Contraseña = bitnami
   1. Pedirá cambiar contraseña
   1. OJO(1): Apuntar la nueva contraseña...
   1. OJO(2): Por defecto, la VM tiene distribución de teclado de EEUU, importante de cara a caracteres raros en la contraseña
1. Comprobar correcta instalación: desde la máquina anfitrión, entrar en un navegador cualquiera a la dirección localhost (asumiendo que se usa NAT, o la IP de la máquina si se tiene como adaptador puente). Debería accederse a la web de bienvenida de Bitnami
1. Habilitar SSH para conectarse desde PuTTy (en mi opinión mucho más cómodo que directamente desde VirtualBox). Instrucciones: https://docs.bitnami.com/virtual-machine/faq/get-started/enable-ssh/
1. (Recomendado, salvo que te manejes con vim) Instalar nano: sudo apt-get install nano
1. Configuración de WSGI y hosts virtuales en apache
   1. `cd /opt/bitnami/apache2/conf/vhosts`
   1. Crear archivo para HTTP (`sudo nano verneServer-http-vhost.conf`) e introducir:
   ```
   <IfDefine !IS_verneServer_LOADED>
     Define IS_verneServer_LOADED
     WSGIDaemonProcess verneServer python-home=/opt/bitnami/python python-path=/opt/bitnami/projects/verneServer
   </IfDefine>
   <VirtualHost 127.0.0.1:80 _default_:80>
     ServerAlias *
     WSGIProcessGroup verneServer
     Alias /robots.txt /opt/bitnami/projects/verneServer/static/robots.txt
     Alias /favicon.ico /opt/bitnami/projects/verneServer/static/favicon.ico
     Alias /static/ /opt/bitnami/projects/verneServer/static/
     <Directory /opt/bitnami/projects/verneServer/static>
       Require all granted
     </Directory>
     WSGIScriptAlias / /opt/bitnami/projects/verneServer/verneServer/wsgi.py
     <Directory /opt/bitnami/projects/verneServer/verneServer>
       <Files wsgi.py>
         Require all granted
       </Files>
     </Directory>
   </VirtualHost>
   ```
   1. Crear archivo para HTTPS (`sudo nano verneServer-https-vhost.conf`) e introducir:
   ```
      <IfDefine !IS_verneServer_LOADED>
     Define IS_verneServer_LOADED
     WSGIDaemonProcess verneServer python-home=/opt/bitnami/python python-path=/opt/bitnami/projects/verneServer
   </IfDefine>
   <VirtualHost 127.0.0.1:443 _default_:443>
     ServerAlias *
     SSLEngine on
     SSLCertificateFile "/opt/bitnami/apache2/conf/bitnami/certs/server.crt"
     SSLCertificateKeyFile "/opt/bitnami/apache2/conf/bitnami/certs/server.key"
     WSGIProcessGroup verneServer
     Alias /robots.txt /opt/bitnami/projects/verneServer/static/robots.txt
     Alias /favicon.ico /opt/bitnami/projects/verneServer/static/favicon.ico
     Alias /static/ /opt/bitnami/projects/verneServer/static/
     <Directory /opt/bitnami/projects/verneServer/static>
       Require all granted
     </Directory>
     WSGIScriptAlias / /opt/bitnami/projects/verneServer/verneServer/wsgi.py
     <Directory /opt/bitnami/projects/verneServer/verneServer>
       <Files wsgi.py>
         Require all granted
       </Files>
     </Directory>
   </VirtualHost>
   ```
   1. Ahora debería ser accesible el proyecto en el puerto 80
   ¡OJO! Para ver cambios es necesario reiniciar apache: ```sudo nano verneServer-https-vhost.conf```
   Por ello, para desarrollar rápido puede ser más cómodo usar el servidor de desarrollo integrado en Django, aunque por ahora me ha dado problemas para accederlo externamente


## Configuración de repositorio
Instalación de repositorio en VM

1. Crear carpeta de proyectos:
   1. sudo mkdir /opt/bitnami/projects
   1. sudo chown $USER /opt/bitnami/projects
1. Crear carpeta para este proyecto:
   1. mkdir /opt/bitnami/projects/verneServer
1. Se podría clonar directamente el repositorio en este directorio (git clone url_de_repositorio), pero recomiendo establecerlo como punto de despliegue desde PyCharm (como con la Raspberry Pi) para subidas automáticas de cada cambio


## Configuración de PyCharm
Configuración para clonar el repositorio y establecer el directorio creado arriba como punto de despliegue automático (mismo que con Raspberry Pi):

1. Si se tiene proyecto abierto, se cierra
1. Check out from Version Control -> Git -> URL de este repositorio
1. Configuración de entorno de despliegue
   1. Tools -> Deployment -> Configuration -> Add
   1. Mappings: carpeta de proyecto (local) -> /opt/bitnami/projects/verneServer (Deployment Path)
   1. Tools -> Deployment -> Automatic upload
1. Configuración de intérprete remoto (para que haya cierto IntelliSense y no dé constantemente problemas de dependencias):
   1. File -> Settings -> Project -> Project Interpreter -> Engranaje -> Add
   1. SSH Interpreter, host=localhost (asumiendo NAT en la VM), username=bitnami, password=...
   1. Interpreter: /opt/bitnami/python/bin/python
   1. Mappings: añadir uno al directorio creado antes ( /opt/bitnami/projects/verneServer )  OJO: podría estar ya añadido por defecto al haber configurado ya el despliegue

   
