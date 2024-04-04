# LLM-Chat: Interfaz de Texto para Grandes Modelos de Lenguaje (LLMs)

[Advertencia: ¡Riesgo de Force Push!](#advertencia-¡riesgo-de-force-push) • [Descargo de Responsabilidad](#descargo-de-responsabilidad) • [Instalación](#instalación) • [Uso](#uso) • [Actualización de Gestión de Proyecto](#🚀-actualización-de-gestión-de-proyecto)

Este proyecto proporciona una interfaz de texto para interactuar con los modelos de [Mistral AI](https://mistral.ai/) y [OpenAI](https://www.openai.com/). La aplicación permite a los usuarios seleccionar un modelo, ingresar una pregunta y recibir la respuesta del modelo.

## Nota
Hasta ahora este proyecto solo permitía acceder a los modelos de Mistral. Ahora es posible acceder también a varios modelos de OpenAI. Estamos actualizando la documentación en consecuencia, pero el proceso de actualización aún no está completado.

## Descargo de Responsabilidad
Este proyecto no está afiliado, asociado, autorizado, o de cualquier manera oficialmente conectado con las empresas Mistral AI u OpenAI, o cualquiera de sus filiales o afiliados. Los nombres "Mistral AI" y "OpenAI" así como nombres relacionados, marcas, emblemas e imágenes son marcas registradas de sus respectivos propietarios. El sitio web oficial de Mistral AI se puede encontrar en [https://mistral.ai/] y el de OpenAI en [https://www.openai.com/].

## Prerrequisitos
Para usar este proyecto con éxito, se requiere una clave API de Mistral AI o de OpenAI (o de ambas). Obtener estas clave API puede incurrir en costos financiero y deben adquirirse directamente de Mistral AI u OpenAI respectivamente. Por favor, visite los sitios web oficiales de Mistral AI y OpenAI para más información sobre cómo obtener sus claves API.

## Instalación

### Usando `poetry` (recomendado)

Asegúrese de haber instalado [Poetry](https://python-poetry.org/docs/#installation).

Para instalar los paquetes de Python requeridos para este proyecto, ejecute:

```
poetry install
```

### Usando `pip`

En el archivo `pyproject.toml`, dentro de la sección `[tool.poetry.dependencies]` se enumeran las dependencias. Puede instalarlos usando pip, ya sea globalmente o dentro de un entorno virtual:

```
pip install mistralai openai rich [...resto de las dependencias]
```

## Ejecución

**Antes de ejecutar la aplicación**, asegúrese de haber establecido al menos una de las API keys, sea como variables de entorno o en el archivo `.env`.

Ejemplo estableciendo la API key de Mistral en Linux:

```
export MISTRAL_API_KEY=<su_clave_api>
```
En Windows:

```
set MISTRAL_API_KEY=<su_clave_api>
```

Para usar el archivo `.env` puede tomarse como ilustración el contenido del archivo `.env.example`.


**Para ejecutar la aplicación**, ejecute el archivo `src/main.py`.

Usando poetry:

```
poetry run python src/main.py
```

O, si se instaló usando pip, use el siguiente comando (en su caso, tras activar el entorno virtual):

```
python src/main.py
```

## Uso

Esta aplicación le permite interactuar con los modelos LLM de Mistral y OpenAI de manera conversacional. Después de lanzar la aplicación, le pedirá que elija entre los modelos disponibles o que proceda con el modelo predeterminado. Una vez seleccionado un modelo, puede comenzar a escribir su consulta. Si esta abarca múltiples líneas, simplemente continúe escribiendo hasta que haya terminado de formular su pregunta. Para indicar que ha terminado de ingresar su pregunta, escriba `end` en una nueva línea. El modelo procesará entonces su entrada y proporcionará una respuesta. Después de recibir una respuesta, es libre de iniciar una nueva consulta siguiendo el mismo proceso.

Las conversaciones se grabarán de manera automática en el directorio `data/chats`. Puede cargar una conversación grabada para continuarla usando el comando `/load` seguido con el id numérico de la conversación. Si desea editar el texto de una conversación antes de cargarla, simplemente edite el archivo, cuidando de respetar el formato general del mismo. También puede copiar el contenido en un nuevo archivo, en cuyo caso necesitará asignarle como nombre el siguiente número de id disponible. No es necesario cambiar el id contenido dentro del archivo, ni ningún otro metadato.

Para iniciar una nueva conversación en lugar de continuar con la actual, use el comando `/new` al principio de su consulta.

Para obtener ayuda sobre los comandos disponibles, use el comando `/help`.

### Marcadores de posición

Si su consulta incluye marcadores de posición (por ejemplo, `$0concepto`), simplemente escriba su consulta con estos marcadores. Después de enviar su consulta, se le pedirá que reemplace cada marcador de posición uno por uno. Este método de sustitución simple es la manera más directa de usar marcadores de posición para consultas personalizadas.

#### Sintaxis de los marcadores de posición
La sintaxis de los marcadores de posición está diseñada para ser intuitiva y flexible, permitiendo la personalización dinámica de la consulta. Los marcadores de posición deben comenzar con el prefijo `$0` seguido de uno o más caracteres alfabéticos (incluyendo el guión bajo `_`). Opcionalmente, estos pueden ser seguidos por uno o más dígitos. Esta estructura asegura que los marcadores de posición sean fácilmente identificables dentro de la consulta y puedan ser reemplazados de acuerdo con la entrada del usuario. Por ejemplo, un marcador de posición podría verse como `$0concepto`, `$0nombre_variable`, o `$0pregunta1`, donde cada marcador de posición está preparado para ser sustituido con un valor específico que el usuario proporcionará más tarde. Esta sintaxis es esencial para distinguir los marcadores de posición del texto normal y asegurar que la app identifique y procese con precisión durante la fase de sustitución de la consulta.

#### Ejemplo de una sustitución simple de marcador de posición:

```
Por favor, ingrese su consulta (o presione Enter para ver más opciones). Escriba
'end' como el único contenido de una línea cuando haya terminado.
> ¿Qué es $0concepto? Defínelo brevemente.
end

Por favor, indique el valor de $0concepto
> la ilustración
Marcador de posición sustituido con éxito

...procesando consulta
```

#### Generación automática de varias consultas
Para un uso más avanzado, si su consulta incluye marcadores de posición y desea realizar múltiples consultas relacionadas en una sola ejecución, puede usar el comando `/for` con el formato `/for valor1,valor2,valor3`. Esto permite que la aplicación reemplace los marcadores de posición con los valores indicados antes de procesar las consultas. Esta característica es especialmente útil para realizar de manera eficiente una serie de consultas relacionadas sin necesidad de reiniciar el proceso para cada nueva entrada, mejorando así la experiencia del usuario y la eficiencia al interactuar con el sistema.


#### Ejemplo de una consulta avanzada con el comando `/for`:

```
Por favor, ingrese su consulta (o presione Enter para ver más opciones). Escriba
'end' como el único contenido de una línea cuando haya terminado.
> ¿Qué es $0concepto? Defínelo brevemente.
end

Por favor, indique el valor de $0concepto
> /for la ilustración,el barroco,el renacimiento
Marcadores de posición sustituidos con éxito

...procesando consulta
```

### Salir del programa

Para salir del programa, simplemente deje la pregunta en blanco y escriba `exit` en el siguiente menú.


### Características

Esta aplicación ofrece las siguientes funcionalidades:

- Selección de modelo interactivo.
- Validación de entrada y manejo de errores.
- Mostrar interacciones del modelo con marcas de tiempo e indicadores de roles.
- Carga de conversaciones previas, en su estado original o editadas por el usuario.


### Desarrollo

#### Advertencia: ¡Riesgo de Force Push!

Si tiene cambios locales que no desea perder, por favor no use `git pull` o `git fetch`. Estos comandos pueden sobrescribir cambios locales.


#### 🚀 Actualización de Gestión de Proyecto

Para mejorar cómo gestionamos las versiones y documentamos los cambios, estamos haciendo algunos cambios importantes:

- **Estableciendo Puntos de Cambio de Versión**: De ahora en adelante, las versiones significativas del proyecto estarán claramente marcadas en la historia de git. Esto facilita navegar por las diferentes etapas del proyecto y acceder a versiones específicas.

- **Introduciendo un Registro de Cambios Detallado**: Un `CHANGELOG.md` ahora es parte del proyecto. Listará modificaciones, nuevas características y correcciones para cada lanzamiento, brindando a todos una vista clara de cómo evoluciona el proyecto.

Gracias por su comprensión y paciencia mientras hacemos estas mejoras. Si tiene alguna pregunta o necesita ayuda para navegar los cambios, no dude en comunicarse.

#### Dependencias de desarrollo

Este proyecto utiliza [Poetry](https://python-poetry.org/) para la gestión de paquetes y el manejo de dependencias. Para configurar el entorno de desarrollo e instalar las herramientas requeridas, ejecute:

```
poetry install --with dev
```

Las dependencias de desarrollo incluyen `mypy` para la comprobación estática de tipos.

### Licencia

Este proyecto está licenciado bajo la [Licencia GPLv3](https://www.gnu.org/licenses/quick-guide-gplv3.html).

### Agradecimientos

Este proyecto se construye utilizando las siguientes bibliotecas de código abierto:

- [Mistral AI](https://github.com/mistralai/client-python)
- [Rich](https://github.com/Textualize/rich)


Estamos agradecidos con sus respectivos mantenedores y contribuyentes.
