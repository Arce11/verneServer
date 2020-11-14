# verneServer
Servidor Django para el proyecto Verne. Basado en el stack Django + Apache de Bitnami, que será desplegado sobre una máquina en la nube posteriormente.

# Instrucciones (despliegue local para desarrollo)
Se detalla el proceso para descargar una VM con el mismo stack, para trabajo local y desarrollo del servidor.

1. Descargar VirtualBox (si no se tiene): https://www.virtualbox.org/wiki/Downloads
1. Descargar VM de la página oficial de Bitnami: https://bitnami.com/stack/django/virtual-machine . OJO: Descargar versión 2.2.16 (la última cuando se escribió esto)
1. Cargar la VM descargada en VirtualBox
   1. Yo personalmente le asigné 2GB RAM y 2CPU, aunque con los 512MB y 1CPU seguramente tire de sobra
   1. Recomendado: modificar la configuración de red de la máquina. Por defecto viene con adaptador puente (al menos para mí), lo que le da una IP más como a cualquier dispositivo de la red local. Eso obliga a conocer esa IP (que puede cambiar) para conectarse a él. Cambiándolo a NAT, y redireccionando los puertos 80 (HTTP) y 22 (SSH), se puede acceder como localhost tanto desde putty como desde el navegador...
1. Iniciar máquina
   1. Usuario = Contraseña = bitnami
   1. Pedirá cambiar contraseña
1. Comprobar correcta instalación: desde la máquina anfitrión, entrar en un navegador cualquiera a la dirección localhost (asumiendo que se usa NAT, o la IP de la máquina si se tiene como adaptador puente). Debería accederse a la web de bienvenida de Bitnami
1. Habilitar SSH para conectarse desde PuTTy (en mi opinión mucho más cómodo que directamente desde VirtualBox). Instrucciones: https://docs.bitnami.com/virtual-machine/faq/get-started/enable-ssh/
