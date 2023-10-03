### Estructuras de Proyectos Por Equipos


# DevSecOps
## Proceso DevSecOps
Se utilizará GitHub como herramienta para el control de versiones de código fuente.
Se utilizará GitHub Actions para la automatización de los workflows garantizando CI/CD.
Para el control de versiones de artefactos se utilizará:
* ECR, como el registro de contenedores de Docker administrado por AWS
* GitHub Package, para alojar y administrar los paquetes (artefactos) de software 
[Introduction to GitHub Packages](https://docs.github.com/en/packages/learn-github-packages/introduction-to-github-packages)


### Usuario
Cada usuario dentro de GitHub debe tener el siguiente estándar de nombramiento: el nombre del usuario seguido de -abatech. Ejemplo: juribe-abatech

### Estrategia 
Como estrategia de desarrollo utilizaremos Monorepo, es decir un único repositorio donde se almacenará el código fuente  para todos los proyectos de Abatech, esto nos permitirá tener una única fuente de la verdad, a tener una mejor visibilidad de los proyectos y activos, a gestionar las dependencias, a mejorar la colaboración y a aumentar la velocidad en el desarrollo. 

### Estructura del Repositorio
La estructura del repositorio de Abatech tendrá 4 carpetas en la raiz: 
* .github/workflows: En esta carpeta se almacenarán los flujos de trabajo (en formato .yml) para automatizar los procesos de CI/CD.          
Nota: Debe existir un único workflow por proyecto. Es responsabilidad de la célula encargada del proyecto de mantener y actualizar el workflow siguiendo los lineamientos establecidos dentro de DevOps.
* back: En esta carpeta se almacenarán los proyectos que hacen parte del backend.
* front: En esta carpeta se almacenarán los proyectos que hacen parte del frontend.
* infra: En esta carpeta se almacenarán los activos correspondientes a la infraestructura como código (IaC) definidos por el equipo de Arquitecture.

**Consideraciones Generales**

Todos los proyectos deben contener:
* readme.md con el siguiente formato: por definirse 
* .gitignore 
* sonar-project.properties

Idioma: Todos los nombres de los proyectos deben estar en inglés. 

Todos los nombres deben ir en minúscula.

El nombre de los proyectos debe ser uno que identifique claramente el propósito del proyecto

### Estrategia de Versionamiento
Como estrategia de versionamiento utilizaremos Trunk-Based Development, cuyo objetivo principal es poder integrar pequeños cambios continuamente dentro de un branch (rama) principal, esto nos permitirá aumentar la velocidad en la entrega del software y agilizar la práctca de CI/CD.

Se tiene la rama principal (main), y esta es la que se despliega en los diferentes entornos (dev, qa, pdn) . De esta rama se desprenden las ramas Features, que son las ramas en donde trabajaran los desarrolladores, una vez los cambios estén en producción, estas ramas serán eliminadas.


### Proceso

Como regla general, las Historias de Usuario deben ser pequeñas y que entreguen valor al negocio, de tal forma que se puedan realizar commits (confirmar) de manera constantes y frecuentes, para tener releases mucho mas controlados.

Los desarrolladores crearan una rama Feature por cada historia de usuario en la cual trabajaran. Esa rama debe ser creada a partir de la rama main. Cuando terminen su desarrollo en el entorno local, y creen y ejecuten sus pruebas unitarias (en el ambiente local) y hayan validado que las pruebas unitarias tengan una cobertura del 100%, deben realizar un Pull Request a la rama main. 

Una vez se implemente un Pull request, se despliega el proceso de CI que contiene los siguientes pasos.
* Ejecución de las Pruebas de Desarrollo (explicadas mas adelante)
* Despliegue en el entorno de Desarrollo (dev)
* Ejecución de las Pruebas de Conformidad (explicadas mas adelante)
* Ejecución de las Pruebas de Seguridad (explicadas mas adelante)

El responsable de aprobar los Pull Request es el Tech Lead, definirse en el CODEOWNER, al hacer el merge con la rama main, se activa el proceso de CD, que contiene las siguientes etapas:
* Compilación del código (generación de artefacto)


#### Pull Request

Para realizar el merge del Pull Request (previamente revisado y aprobado), se utilizará git commit con fast forward para visualizar el histórico del proyecto. 
Se usará la opción Squash and merge.


### Prácticas

Para tener una exitosa implementación de Trunk-Based Development se requiere de las siguientes prácticas: 

#### Feature Flags

Es una técnica de desarrollo que permite habilitar y deshabilitar funcionalidad en base a una configuración (esconder trabajo que esta en progreso) para tener mas estabilidad hasta completar la funcionalidad. 

Tipos de Features Flags:

* Para despliegue y entorno
* Para experimentación (solo ciertos usuarios puedan ver ciertos cambios) 
* Para liberaciones canario (liberar nuevas versiones) 
* Para pruebas 

[GitHub - Unleash](https://github.com/Unleash/unleash)

#### Monitoreo de Builds y Pipelines

Se trata de tener visibilidad sobre problemas en el código y resolverlos rápidamente. 

#### Rollforwards

Es la práctica de corregir errores sin revertir a versiones previas, sino corrigiendo el error lo más pronto posible. 

### Consideraciones generales

* Se debe integrar rapidamente, al menos una vez al día.

* Pequeños cambios incrementales y continuos. 

* Las ramas Feature son de corta duración (short-lived), ya que se busca desplegar nuevas funcionalidades y pequeños cambios rápidamente. 

* Ocultar las funcionalidades que no han sido terminadas.

* Los desarrolladores deben ser responsables de su código y grarantizar que el código que suben es de calidad.

* Pruebas automatizadas 

* El artefacto de salida de la compilación debe ser único para los diferentes ambientes. No hay artefactos diferentes para cada ambiente, es decir, se compilará una única vez y ese artefacto será promovido entre los diferentes entornos (dev, qa, pdn).

### Versionamiento del Software

Una de las razones por las que el software tiene número de versiones es para mostrar el progreso, poder identificar las diferentes caracteristicas que se tiene sobre las versiones mas recientes. 

Un número de versión consta de tres números separados por puntos(.). Cada uno de los número de versión tiene un signifaciado específico que esta relacionado con la compatibilidad del software.


* Fix version: El último número (de izquierda a derecha), significa una diferencia en términos de correción de errores. En el ejemplo, la versión 2.5.8 incluye una o más correcciones de errores sobre la versión 2.5.7. Incluye correcciones de errores compatibles con versiones anteriores.

* Feature version: El número de la mitad, signifca que existen una o mas características nuevas, lo que se obtiene son nuevas funcionalidades de una manera compatible con versiones anteriores. 

* Breaking version: El primer número (de izquierda a derecha), significa que hay cambios importantes en el software/proyecto.

Yendo de derecha a izquierda, si se actualiza uno de los números, si hay uno a la derecha, se restablece a cero.

Se iniciará las versiones de software en 1.0.0

## Configuración Terminal

* Instalar terminal zsh

```
# install zsh package
  sudo apt-get update 
  sudo apt install zsh
# Check if zsh was successfully installed
  zsh --version
# Install additional plugin for zsh
  sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

* Instalar fuente **Meslo LGS** para terminal

```
# Open in browser the following links
  https://github.com/romkatv/powerlevel10k-media/raw/master/MesloLGS%20NF%20Regular.ttf
  https://github.com/romkatv/powerlevel10k-media/raw/master/MesloLGS%20NF%20Bold.ttf
  https://github.com/romkatv/powerlevel10k-media/raw/master/MesloLGS%20NF%20Italic.ttf
  https://github.com/romkatv/powerlevel10k-media/raw/master/MesloLGS%20NF%20Bold%20Italic.ttf
```

* Instalar tema PowerLevel10K para zsh

```
# Manual installation of PowerLevel10K
  git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ~/powerlevel10k
  echo 'source ~/powerlevel10k/powerlevel10k.zsh-theme' >>~/.zshrc

# In .zshrc file override ZSH_THEME default value
  vim ~/.zshrc
  ZSH_THEME=powerlevel10k/powerlevel10k

# Configure p10k theme by following the steps shown in the CLI
  p10k configure
```

* Configurar la nueva fuente de la terminal. 

Para ello se accede al drop down de Windows Terminal y click en **Configuración.**

![imagen](./coe/images/coe-img/configureTerminal/terminal.png)

* En seguida se da click en el perfil de la distribución de Windows que se tenga para utilizar en conjunto con WSL, en este caso **Ubuntu.**

![imagen](./coe/images/coe-img/configureTerminal/terminal1.png)

* Ir a la sección **Apariencia** y seleccionar la fuente descargada, en este caso **MesloLGS NF** y guardar.

![imagen](./coe/images/coe-img/configureTerminal/terminal2.png)



## Herramientas DevSecOps

Dentro de DevSecOps se han definido diferentes herramientas para garantizar la calidad y seguridad de los proyectos dentro de AbaTech. 

### Secrets Scanning
Las herramientas de escaneo de secretos pueden escanear y monitorear los repositorios de git y los pull requests, se pueden usar para evitar que se realicen commits de secretos o para encontrar y eliminar secretos que ya se han comprometido con el control de código fuente.

#### GitGuardian Shield

Es una herramienta CLI, de código abierto de GitGuardian, que ayuda a detectar más de 200 tipos de secretos, así como otras posibles vulnerabilidades de seguridad o rupturas de políticas. Ayuda en la prevención y reparación.

Es esencial tener detección de secretos, porque ahí es donde viven las amenazas activas.
GitGuardian Shield aprovecha el motor de detección de GitGuardian y lo hace mediante la API de GitGuardian.

![imagen](./coe/images/coe-img/toolsDevSecOps/GitGuardian.png)  

**Instalación**

* Se necesita establecer un API Key para establecer una conexión segura.

En https://www.gitguardian.com/  registrarse gratis, una vez registrados se debe crear un API Key.

En el Menu de la izquierda en la opción API, crear el API Key.

![imagen](./coe/images/coe-img/toolsDevSecOps/GitGuardianAPI.png)                    

Se debe dar un nombre, en la opción Expires configurar el tiempo en que quiere que se expire el API Key, en Scope debe seleccionar la opción scan para que pueda escanear los proyectos. (Recuerde que esta configuración es para ejecutarla de forma local en su entorno)

![imagen](./coe/images/coe-img/toolsDevSecOps/GitGuardianAPI1.png)  

![imagen](./coe/images/coe-img/toolsDevSecOps/GitGuardianAPI2.png)  

* Una vez generada el API Key se debe guardar como una variable de ambiente
    - Linux

    ```
    export GITGUARDIAN_API_KEY=value
    printenv
    ```    

    - Windows

    ```
    setx GITGUARDIAN_API_KEY value
    set
    ```    

  Se debe cerar y abrir nuevamente la terminal para que se tomen los cambios

* Instalar GitGuardian Shield

```
pip install ggshield
```

* Instalar pre-commit hook (Esto les ayudará a validar en el commit que no estén insertanddo secretos)

```
ggshield install -m local
ggshield install -m global
```

![imagen](https://blog.gitguardian.com/content/images/size/w600/2023/06/230531---GitHub-Push-Protection.png)  

* Ejecutar el comando para que realice el escaneo antes de confirmar el commit (esta instrucción solo se debe ejecutar una única vez)

```
ggshield scan pre-commit
```

### Static Application Security Testing - SAST

Es una metodología de pruebas que analiza el código fuente para encontrar vulnerabilidades de seguridad que hacen que las aplicaciones sean susceptibles a ataques. Estas pruebas, analizan las aplicaciones antes que se compile el código. 

Las pruebas de seguridad de aplicaciones estáticas, es un método de prueba de caja blanca, se utilizan para proteger el software mediante la revisión del código fuente para identificar las fuentes de vulnerabilidades, examina el código para encontrar fallas y debilidades del software. 

#### Sonarqube

Es una herramienta que permite realizar análisis estático de código. 

Identifica puntos de mejora y se obtienen métricas que ayudan a mejorar el código. 

Valida:
* Reliability (Bugs)

* Security (Vulnerabilities, Security Hotspots)

* Maintainability (Debt, Code Smells)

* Coverage

* Duplications

**Instalación**

Se puede realizar la instalación de SonarQube de la siguiente manera:

* La imagen la pueden tomar de [Sonarqube- Offical Image](https://hub.docker.com/_/sonarqube)

* Crear el docker-compose.yml 

    [docker-compose](https://github.com/SonarSource/docker-sonarqube/blob/master/example-compose-files/sq-with-postgres/docker-compose.yml)

* Se requiere ampliar la memoria virtual, para esto se debe ejecutar 

```
wsl -d docker-desktop
sysctl -w vm.max_map_count=262144
```  

* Ejecutar el comando 

```
docker-compose up -d
```

El siguiente [link](https://medium.com/javascript-nicaragua/dockerizando-sonarqube-ae87838f6555) pueden tomarlo como referencia 

Una vez que los contenedores esten ejecutandose correctamente:

![imagen](./coe/images/coe-img/sonarqube.png)

En el navegador ingresar la URL http://localhost:9000

Se verá ejecutandose SonarQube

![imagen](./coe/images/coe-img/sonarqube1.png)

Para acceder **la primera vez** los datos de acceso son:
    - user: admin
    - password: admin

Una vez entre, le pedirá cambiar la contraseña para el usuario admin.

Para ejecutar el análisis del código localmente, se debe generar un token:

* En My Account 
![imagen](./coe/images/coe-img/sonarqube2.png)

* En Security
Generar un token
![imagen](./coe/images/coe-img/sonarqube3.png)

Copiar el token para utilizarlo mas adelante

![imagen](./coe/images/coe-img/sonarqube4.png)

Ejecutar 

```
npm install -g sonarqube-scanner
```

Dentro de cada uno de los proyectos se debe crear un archivo de configuración en el directorio raíz del proyecto llamado _sonar-project.properties_

```
# must be unique in a given SonarQube instance
sonar.projectKey=my:project

# --- optional properties ---

# defaults to project key
#sonar.projectName=My project
# defaults to 'not provided'
#sonar.projectVersion=1.0
 
# Path is relative to the sonar-project.properties file. Defaults to .
#sonar.sources=.
 
# Encoding of the source code. Default is default system encoding
#sonar.sourceEncoding=UTF-8
```

![imagen](./coe/images/coe-img/sonarqube6.png)

Configurar el archivo _sonar-scanner.properties_
Este archivo se encuentra en $install_directory/conf/sonar-scanner.properties:
C:\Users\<user>\.sonar\native-sonar-scanner\sonar-scanner-4.5.0.2216-windows\conf
```
sonar.host.url=http://localhost:9000
sonar.login=<token generado previamente>
```

![imagen](./coe/images/coe-img/sonarqube5.png)

Ejecutar
```
sonar-scanner
```

**Quality Gates**

Los Quality Gates hacen cumplir las políticas de calidad definidas dentro de AbaTech 
Las políticas definidas son:

![imagen](https://dx.appirio.com/quality-sonarqube/granting-permissions/SonarQube-QualityGate-1.png)

#### Snyk

Es una herramienta de seguridad cloud-native, que escanea y monitorea los proyectos en busca de vulnerabilidades de seguridad. Cubre diferentes áreas de seguridad

* Snyk Open Source: 

* Snyk Code:

* Snyk Container:

* Snyk Infrastructure as Code:

**Instalación**

* Ejecutar 

```
npm install snyk@latest -g
snyk --version
```

* Snyk CLI depende de la API de Snyk.io  Para conectarse se debe ejecutar:

```
snyk auth
```

* Seguir los pasos:

![imagen](https://s2-recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/166/500/original/Snyk-logo-colour-2020.png?1603191972)  


* Monitorear el proyecto

Snyk también puede monitorear el proyecto periódicamente y alertar sobre nuevas vulnerabilidades. 

_snyk monitor_ es similar _snyk test_ y se puede usar para crear un proyecto en el sitio web de Snyk que será monitoreado continuamente en busca de nuevas vulnerabilidades.

Ejecutar

```
snyk monitor
```

### Dynamic Application Security Testing (DAST)

Es una metodología de pruebas que busca vulnerabilidades de seguridad simulando ataques externos a una aplicación mientras la aplicación se está ejecutando, intentando penetrar la aplicación desde el exterior comprobando sus interfaces expuestas en busca de vulnerabilidades y fallas.  

Las pruebas de seguridad de aplicaciones dinámicas son un método de prueba de caja negra que examina la aplicación mientras se ejecuta para encontrar vulnerabilidades que un atacante podría explotar.

### Documentación 

Para la generación de la documentación del código fuente se utilizará la misma sintaxis dependiendo del lenguaje de programación que se use.

| Lenguaje de Programación       | Sintaxis
| :---         | :---         |     
| TypeScript   | [CompoDoc](https://compodoc.app/) |    
| Angular      | [CompoDoc](https://compodoc.app/) |       
| NestJS       | [CompoDoc](https://compodoc.app/) |       
| Servicios Web RESTful      | [Swagger](https://swagger.io/) |       
| Flutter      | [Dartdoc](https://dart.dev/tools/dartdoc) |      

#### Compodoc

Compodoc es una herramienta de documentación, generando la documentación estática de una aplicación. Compodoc ayuda a proporcionar una documentación clara y útil de la aplicación.

**Instalación**

* Instalación Global.
Instalar desde npm:
```
npm install -g @compodoc/compodoc
```

* Crear o actualizar el archivo llamado _tsconfig.json_, que contenga una clave de inclusión (include) que apunte a la carpeta en donde está el código fuente del proyecto a analizar, también puede usar la clave de exclusión (exclude):

```
{
  "include": ["src/**/*.ts"],
  "exclude": ["src/test.ts", "src/**/*.spec.ts", "src/app/file-to-exclude.ts"]
}
```

* En el archivo _package.json_ ingresar las siguientes lineas de código:

```
"doc": "npx @compodoc/compodoc -p tsconfig.json -d ./documentation -s"
```

* Ejecutar

```
npx @compodoc/compodoc -p tsconfig.json -d ./documentation -s     

```
En el navegador abrir http://127.0.0.1:8080 y deberá ver la documentación del proyecto.


Aquí puede consultar más detalle del [uso](https://compodoc.app/guides/usage.html).

