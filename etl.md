## objective

    El objetivo es crear un ETL dentro de la plataforma de aws; este ETL sera usando para leer de una servidor sftp un archivo de texto, procesarlo y cargar la informacion a un sistema manejador de base de datos Mysql, manteniendo un respaldo en un bucket de S3. Es necesario que este ETL cuente con puntos de control, alertas, validaciones, manejor de errores y notificaciones de errores. 

## instructions

   Crear los roles y las polticas de acceso en formato .json 
   Crear el layeer y la funcion lambda oara leer procesar y cargar los datos.
   Crear los archivos yaml para el despliegue automatico mediante cloudformation

## constrains

### iam contrains

    -- Definir el nombre del rol de acuerdo al estilo determinado por el area de seguridad. 
    -- Crear un ServiceRole de lambda service importante limitarlo solo a los recursos que sean necesarios para el proyecto mediante el arn.
       1."s3:ListBucket", "s3:GetObject", "s3:PutObject",
       2."secretsmanager:GetSecretValue", "secretsmanager:DescribeSecret" "secretsmanager:ListSecrets"
       3."events:PutRule","events:PutTargets","events:DescribeRule"
       4."logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"
       5."ec2:CreateNetworkInterface", "ec2:DescribeNetworkInterfaces", "ec2:DeleteNetworkInterface", "ec2:AssignPrivateIpAddresses", "ec2:UnassignPrivateIpAddresses"
    -- Crear un ServiceRole de simpre notification service importante limitarlo solo a los recursos que sean necesarios para el proyecto mediante el arn
       1."sns:Publish",sns:GetTopicAttributes,sns:GetTopicAttributes 
    -- Crera un ServiceRole de eventbridge service 
       1."events:PutEvents","events:PutRule","events:DescribeRule","events:DeleteRule", "events:PutTargets", "events:RemoveTargets","events:RemoveTargets","lambda:InvokeFunction"

    
### mysqs constrains
    
    Las tablas seran creadas en la capa **standard** debido a que la informacion ya contiene alguna transformacion,  es importante seguir las buenas practicas de nombrado propuestas por mysql.
    -- Estilo de escritura snake.
    -- Longitud maxima de 64 caracteres.
    -- Evitar caracteres especiales, espacios y nombres reservados por mysql
    -- Definir los nombres de los campos en miniscula.
    -- Definir llaves primarias para la tabla.
    -- Definir campos auditables para el renglon en la tabla.
    -- Definar las tablas en una forma desnormalizada ya que es una tabla diseñada para
    la explotacion de datos

### lambda contrains
    
    -- Definir el nombre de la funcion lambda de acuerdo al siguente estilo contextual 
    {organizacion/cliente}-{ambiente}-{region}-{proyecto}-{nombre representativo}. 
    -- longitd maxima de 3 a 63 caracteres.
    -- Evitar prefijos usados por AWS.
    -- Definir los nombres en minuscula.
    -- los nombres pueden contener caracteres alpha numericos, giones medios (-), gion bajo (_), puntos (.) y slashes (/)
    -- Los nombres no deberan integrar en su estructura direccion IP
    -- Seguir las buenas practicas de nombrado definidas por AWS
    -- usar python como leguaje de programacion default
    -- usar una version antes de la ultima version marcada como estable python3.x.
    -- Usar paramiko al definir el layer 


###  secrets manager contrains

    -- Definir el nombre del secreto de acuerdo a con el siguente estilo contextual 
    {organizacion/cliente}-{ambiente}-{region}-{proyecto}-{nombre representativo}
    -- longitd maxima de 3 a 63 caracteres.
    -- los nombres pueden contener caracteres alpha numericos, giones medios (-), gion bajo (_), puntos (.) y slashes (/)
    -- Evitar usados por AWS.
    -- Definir los nombres en minuscula.
    -- Los nombres no deberan integrar en su estructura direccion IP

## system intructions

  
### mysql system instructions

    1. Crear una tabla llamada **visitor** de acuerdo al siguiente eschema : 
        email : llave primaria 
        fecha_primera_visita 
        fecha_ultima_visita 
        visitas_totales 
        visitas_anio_actual 
        visitas_mes_actual
    2. Crear una tabla llamada **statistics** de acuerdo al siguiente eschema :
        email : llave primaria
        jyv
        badmail
        baja
        fecha_envio
        fecha_open
        opens
        opens_virales
        fecha_click
        clicks
        clicks_virales
        links
        ips
        navegadores
        plataformas
    
    3. Crear una tabla llamada **errors** de acuerdo al sig schema :
        id
        malformacion

  ### lambda system instructions 

    1. Crear una funcion lambda y asignar el nombre.
    2. Seleccionar la vpc las subnest y el role de ejecucion.
    3. Crear una ruta especifica mkdir -p build/python , cd build/python Crear en algun ambiente un virtual enviroment de pyhton 3.x usando el commando python3.x -m venv . , instalar en el enviroment paramiko usando pip install paramiko -t . ,zip -r paramiko_layer.zip python/.
    4. Configurar timeout 900.
    5. Consigurar el nombre del secreto como una enviroment variable en la funcion lambda.
    6. Configure ephemeral storage 10,240 MB.
    7. Usar el paramiko_layer como layer en la funciona lambda.
    8. Configurar RAM 1024 MB.
    9. la funcion lambda debera usar la enviroment var para leer del secrets manager el usuario y la contraseña de la fuente.
    10. Invocar sftp con parmico y traer el file a la carpera /tmp/ del contenedor donde la lambda esta corriendo y eliminar el archivo de la fuente.
    11. Cargar el archivo usando la funcion read_csv y configurando el esquema como un json de acuero a la estructura de mysql.
    12. Deacuerdo con los sig campos columna: email valor: missing, columna : fecha_primera_visita valor: 1000-01-01, columna : fecha_ultima_visita valor: 1000-01-01, columna : fecha_envio valor: 1000-01-01, columna : fecha_open valor: 1000-01-01, columna : fecha_click valor: 1000-01-01, usar la fucion fillna() del objeto pandas.
    13. Usar la funcion to_datetime con el parametro errors='coerce' para validar las columnas fecha_primera_visita, fecha_ultima_visita, fecha_envio, fecha_open, fecha_click.
    14. De los dataframes filtrar los sig escenarios y crear los sig dataframes mutuamente excluyentes: 
    errors: column_name = email value = missing or column_name = fecha_primera_visita , value = 1000-01-01, column_name = fecha_ultima_visita , value = 1000-01-01, or column_name = fecha_primera_visita , value = null, column_name = fecha_ultima_visita , value = null  visitors : not errors.
    errors column_name = email value = missing or fecha_envio , value = 1000-01-01, fecha_open , value = 1000-01-01, fecha_click , value = 1000-01-01 or fecha_envio , value = null, fecha_open , value = null, fecha_click , value = null
    statistics: not errors.
    15. Generar de las columnas de eroors  la sig json structure: { id: int, payload : {text:"email | fecha_primera_visita | fecha_ultima_visita | visitas_totales | visitas_anio_actual | visitas_mes_actual" } } or {id: int, payload: {text: "email | jyv | badmail | baja | fecha_envio | fecha_open | opens | opens_virales | fecha_click | clicks | clicks_virales | links | ips | navegadores | plataformas } }.
    16. Ordenar el dataframe construido por email de manera descendente la columna email.
    17. Hacer una consulta de los registros que tiene actualmente la tabla visitors; hacer un left join con el dataframe visitors que se construyo en el paso anterior usando la columna email, filtar aquellos registros que no tengan un correspondiente email en la tabla visitors e insertarlos en la tabla visitors.
    18. Para aquellos que ya tengan un correspondiente hacer la sig actualizacion en la tabla :
    standard.visitors.fecha_ultima_visita = dataframe.vistors.fecha_ultima_visita
    standard.visitors.visitas_totales = standard.visitors.visitas_totales + 1
    standard.visitors.visitas_anio_actual = standard.visitors.visitas_anio_actual + 1
    standard.visitors.visitas_mes_actual = standard.visitors.visitas_mes_actual + 1
    19. cerrar la conexion a la base de datos.
  
  ### eventbridge system instructions

    1. Crear una nueva regla y asignar el nombre.
    2. Seleccionar Schedule.
    3. Configurar el patron diario cron(0 12 * * ? *)
    4. Seleccionar la funcion lambda que se creo en el paso anterior.

  ### system notification 

    1. Crea un tema y asigna el nombre
    2. Crear una suscripcion con los emails que necesiten recibir las alertas
    3. Crear en cloud whatch alarmas para Process finished y Errors el selecciona el tema creado del system notification creado. 


  ### cloudformation system instructions

    1. Crear un cloudformation para desplegar todos los roles y grupos de seguridad en el proyecto necesarios en el proyecto.
    2. Crear un cloudformation para desplegar las conexiones a base de datos del proyecto.
    3. Craer un cloudformation para desplegar los servicios restantes del proyecto. 

