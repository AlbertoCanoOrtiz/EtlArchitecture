## objective

    El objetivo es crear un ETL dentro de la plataforma de aws; este ETL sera usando para leer de una servidor sftp un archivo de texto, procesarlo y cargar la informacion a un sistema manejador de base de datos Mysql, manteniendo un respaldo en un bucket de S3. Es necesario que este ETL cuente con puntos de control, alertas, validaciones, manejor de errores y notificaciones de errores. 

## instructions

   Crear los roles y las polticas de acceso en formato .json 
   Crear el layeer y la funcion lambda oara leer procesar y cargar los datos.
   Crear los archivos yaml para el despliegue automatico mediante cloudformation


## constrains 

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
 
### iam contrains

    -- Definir el nombre del rol de acuerdo al estilo determinado por el area de seguridad. 
    -- Crear un ServiceRole de trasfer family service importante limitarlo solo a los recursos que sean necesarios para el proyecto mediante el arn.
       1."s3:ListBucket", "s3:GetObject", "s3:PutObject", s3:DeleteObject
       2."logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"     
    -- Crear un ServiceRole de lambda service importante limitarlo solo a los recursos que sean necesarios para el proyecto mediante el arn.
       1."s3:ListBucket", "s3:GetObject", "s3:PutObject",
       2."secretsmanager:GetSecretValue", "secretsmanager:DescribeSecret" "secretsmanager:ListSecrets"
       3."events:PutRule","events:PutTargets","events:DescribeRule"
       4."logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"
       5."ec2:CreateNetworkInterface", "ec2:DescribeNetworkInterfaces", "ec2:DeleteNetworkInterface", "ec2:AssignPrivateIpAddresses", "ec2:UnassignPrivateIpAddresses"
    -- Crera un ServiceRole de eventbridge service 
       1."events:PutEvents","events:PutRule","events:DescribeRule","events:DeleteRule", "events:PutTargets", "events:RemoveTargets","events:RemoveTargets","lambda:InvokeFunction"
       2."glue:StartJobRun"

### system manager parameter store
    
    -- Definir el nombre del parametro de acuerdo al siguente estilo contextual
    {organizacion/cliente}-{ambiente}-{region}-{proyecto}-{nombre representativo}
    -- El nombre debe de ser unico en la cuenta y en la region donde se esta creando
    -- longitud maxima de 1011 caracteres 
    -- los nombres pueden contener caracteres alpha numericos, giones medios (-), gion bajo (_), puntos (.) y slashes (/)
    -- Preferentemente agregar versiones

###  secrets manager contrains

    -- Definir el nombre del secreto de acuerdo a con el siguente estilo contextual 
    {organizacion/cliente}-{ambiente}-{region}-{proyecto}-{nombre representativo}
    -- longitd maxima de 3 a 63 caracteres.
    -- los nombres pueden contener caracteres alpha numericos, giones medios (-), gion bajo (_), puntos (.) y slashes (/)
    -- Evitar usados por AWS.
    -- Definir los nombres en minuscula.
    -- Los nombres no deberan integrar en su estructura direccion IP

###  cloudformation contrains

    -- Crear el cloudformation como un archivo yaml.
    -- Definir como parametros minimos: el ambiente y la region donde se plantea desplegar el recurso.
    -- Restringir los valores aceptados por los parametros.

### transferfamily constrains 
    

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

###  glue contrains
    
    -- Definir crawler
    -- Definir el nombre del data catalog  
    {organizacion/cliente}-{ambiente}-{region}-{database}-{nombre representativo de la entidad}
    -- Deginir el nombre del conexion a base de datos:
    {protocolo}-{ambiente}-{region}-{database}
    -- Longitus maxima de 3 a 63 caracteres
    -- los nombres pueden contener caracteres alpha numericos, giones medios (-), gion bajo (_), puntos (.) y slashes (/)
    -- Hacer uso de las fuentes de datos, las transformacion y los destinos de datos nativos del servicio.
    -- Evitar la construccion de bucles for, while en su caso hacer uso de las funciones ApplyMaping, DropFields, Filter, Map, Aggregate, FillMisingValues,PivotRowsToColumns: en caso de que se necesite una funcionalidad muy especifica hacer uso de custom transformations y tratar hacer uso de las funciones de pyspark/spark. 



## Instructions

### secrets manager system instructions

    1. crear un secret para el usuario y asignar el nombre; se sugiere que en la particula {nombre representativo} usar user_sftp_on_prem
    2. crear un secret para el password y asignar el nombre; se sugiere que en la particula {nombre representativo} usar password_sftp_on_prem
    

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


### tranferfamily system instructions
    
    1.Crear el server y asignar el nombre
    2.Usar el protocolo SFTP
    3.Seleccionar el vcp endpoint



    4.Configurar Usuario 
    5.Configurar Service Role
    6.Configurar el s3 home directory 

### Lambda system instructions
    1. Crear una funcion lambda y asignar el nombre.
    2. Seleccionar la vpc las subnest y el role de ejecucion.
    3. Crear las sig enviroment vars ConnectorId, RetrieveFilePaths, LocalDirectoryPath
    4. Crear una lamnda y usar StartFileTransfe,r configurar: ConnectorId, RetrieveFilePaths, LocalDirectoryPath apartir de las variables de entorno.
    5. Configurar el timeout 900.

###  glue system instrucciones
   
   #### glue database connections system instructions
    1.Definir el nombre de la conexion a base de datos.
    2.Crear la cadena de conexion "jdbc:mysql://[Your-Database-Endpoint]:3306/[Database-Name] ,S3://".
    3.Asignar usuario y contraseña. 
    4.Asignar la VPC, seleccionar la subnets y el grupo de seguridad

   #### glue database system instructions 
    1. Crear una base de datos y asignar el nombre

   #### glue table system instructions
    1. Crear una tabla y asignar el nombre crear tantas tablas como existan el esquema de mysql
    2. Asignar el nombre de la base de datos que se ha creado en el punto anterior
    3. Agregar las columnas y su tipo de dato; hacer coincidir con la estructura de mysql 
   
   #### glue crawler system instructions 
    1. Crear el crawler y asignar el nombre 
    2. Seleccionar usar una tabla existente y referenciar por cada crawler una tabla en el glue table.
    3.En las opciones de configuracion: cuando el crawler encuentre cabios en el esquema: ignorar los cambios y no actualizar la tabla en el data catalog --"Update the table definition in the data catalog." 
    4. En las opciones de configuracion: Cuando el crawler encuentre un objeto eliminado: Marcar la tabla como obsoleta o Ignorar. --"Mark the partition as deprecated in the data catalog"

   #### glue job system instructions
    1. Agregar un nodo de origen de datos s3 y configurar la conexion y el nombre del objeto en el bucket.

    2. Agregar un nodo Fill Missing Values y configurar column_name = email, value = missing, column_name = fecha_primera_visita , value = 1000-01-01, column_name = fecha_ultima_visita , value = 1000-01-01, fecha_envio , value = 1000-01-01, fecha_open , value = 1000-01-01, fecha_click , value = 1000-01-01

    3. Agregar un nodo de schema, configurar el formato de los campos column_name = email, format = string, column_name = fecha_primera_visita , format = dd/mm/yyyy HH:mm, column_name = fecha_ultima_visita , format = dd/mm/yyyy HH:mm, column_name = fecha_envio , format = dd/mm/yyyy HH:mm, column_name = fecha_open , format = dd/mm/yyyy HH:mm, column_name = fecha_click , format = dd/mm/yyyy HH:mm

    4. En caso de ser necesario crear un custom node using to_date function and isNull function
    5. Agregar un nodo de filtro y crear los sig mutuamente excluyentes dataframes: 
    
    errors: column_name = email value = missing or column_name = fecha_primera_visita , value = 1000-01-01, column_name = fecha_ultima_visita , value = 1000-01-01, or column_name = fecha_primera_visita , value = null, column_name = fecha_ultima_visita , value = null  visitors : not errors 
    
    errors column_name = email value = missing or fecha_envio , value = 1000-01-01, fecha_open , value = 1000-01-01, fecha_click , value = 1000-01-01 or fecha_envio , value = null, fecha_open , value = null, fecha_click , value = null
    statistics: not errors

    7. Generar de las columnas de errors  la sig json structure: { id: int, payload : {text:"email | fecha_primera_visita | fecha_ultima_visita | visitas_totales | visitas_anio_actual | visitas_mes_actual" } } or {id: int, payload: {text: "email | jyv | badmail | baja | fecha_envio | fecha_open | opens | opens_virales | fecha_click | clicks | clicks_virales | links | ips | navegadores | plataformas } }

    8. Hacer una consulta de los registros que tiene actualmente la tabla visitors; hacer un left join con el dataframe visitors que se construyo en el paso anterior usando la columna email, filtar aquellos registros que no tengan un correspondiente email en la tabla visitors e insertarlos en la tabla visitors.
    18. Para aquellos que ya tengan un correspondiente hacer la sig actualizacion en la tabla :
    standard.visitors.fecha_ultima_visita = dataframe.vistors.fecha_ultima_visita
    standard.visitors.visitas_totales = standard.visitors.visitas_totales + 1
    standard.visitors.visitas_anio_actual = standard.visitors.visitas_anio_actual + 1
    standard.visitors.visitas_mes_actual = standard.visitors.visitas_mes_actual + 1

    9. Agregar un nodo de target de datos mysql y configurar la conexion y el nombre de la tabla.

   #### system notification system instructions 

    1. Crea un tema y asignar el nombre, en la particula {nombre-representativo} se sugiere agregar glue_job_notificaciones
    2. Crear una suscripcion con los emails que necesiten recibir las alertas
   
   #### eventbridge system system instructions

    1. Crear una nueva regla y asignar el nombre.
    2. Seleccionar Schedule.
    3. Configurar el patron diario cron(0 12 * * ? *)
    4. Seleccionar el glue job que se creo en el paso anterior.

    5. Crear una nueva regla y asignar el nombre, en la particula {nombre-representativo} se sugiere agregar glue_job_notificaciones
    6. Seleccionar Rule with an event pattern.
    7. Configurar una Eventbridge rule {"source": ["glue_job_name"], "detail-type": ["Glue Job State Change"], "detail": { "state": ["SUCCEEDED", "FAILED", "TIMEOUT", "STOPPED"] }}
    8. Seleccionar el glue job que se creo en el paso anterior.

    1. Crear una nueva regla y asignar el nombre.
    2. Seleccionar Schedule.
    3. Configurar el patron diario cron(0 12 * * ? *)
    4. Seleccionar la lambda se creo en pasos anteriores.

 


