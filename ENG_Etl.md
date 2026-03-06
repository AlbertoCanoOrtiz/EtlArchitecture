## Objective

The objective is to create an ETL process within the AWS platform. This ETL process will be used to read a text file from an SFTP server, process it, and load the information into a MySQL database management system, maintaining a backup in an S3 bucket. This ETL process must include control points, alerts, validations, error handling, and error notifications.

## Instructions

Create the roles and access policies in .json format.

Create the layer and the Lambda function to read, process, and load the data.

Create the YAML files for automatic deployment using CloudFormation.

## Constraints

### MySQL Constraints

The tables will be created in the **standard** layer because the information already contains some transformations. It is important to follow the naming best practices proposed by MySQL.

- Snake script style.
- Maximum length of 64 characters. -- Avoid special characters, spaces, and names reserved by MySQL.

- Define field names in lowercase.

- Define primary keys for the table.

- Define auditable fields for the row in the table.

- Define the tables in a denormalized form, as this is a table designed for data exploitation.

### IAM constraints

- Define the role name according to the style determined by the security area.

- Create a Transfer Family Service Role; it is important to limit it only to the resources necessary for the project using the ARN. 1. "s3:ListBucket", "s3:GetObject", "s3:PutObject", s3:DeleteObject

2. "logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"

- Create a Lambda ServiceRole; it's important to limit it only to the resources needed for the project using the arn.

- 1."s3:ListBucket", "s3:GetObject", "s3:PutObject", 
2."secretsmanager:GetSecretValue", "secretsmanager:DescribeSecret" "secretsmanager:ListSecrets" 
3."events:PutRule","events:PutTargets","events:DescribeRule" 
4."logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents" 
5."ec2:CreateNetworkInterface", "ec2:DescribeNetworkInterfaces", "ec2:DeleteNetworkInterface", "ec2:AssignPrivateIpAddresses", "ec2:UnassignPrivateIpAddresses" 
-- Create a ServiceRole of eventbridge service
1. "events:PutEvents","events:PutRule","events:DescribeRule","events:DeleteRule", "events:PutTargets", "events:RemoveTargets","events:RemoveTargets","lambda:InvokeFunction"

2. "glue:StartJobRun"

### System Manager Parameter Store

- Define the parameter name according to the following contextual style:

{organization/client}-{environment}-{region}-{project}-{representative name}
- The name must be unique within the account and region where it is being created.
- Maximum length of 1011 characters.
- Names can contain alphanumeric characters, hyphens (-), underscores (_), periods (.), and slashes (/).
- Preferably add versions.

### Secrets Manager constraints

- Define the secret name according to the following contextual style:

{organization/client}-{environment}-{region}-{project}-{representative name}
- Maximum length: 3 to 63 characters.
- Names can contain alphanumeric characters, hyphens (-), underscores (_), periods (.), and slashes (/).
- Avoid using characters used by AWS.
- Define names in lowercase.
- Names should not include IP addresses in their structure.

### cloudformation constraints

- Create the cloudformation as a YAML file.

- Define the minimum parameters: the environment and region where the resource is to be deployed.

- Restrict the accepted parameter values.

### transferfamily constraints

### lambda constraints

- Define the lambda function name according to the following contextual style:

{organization/client}-{environment}-{region}-{project}-{representative name}
- Maximum length: 3 to 63 characters
- Avoid prefixes used by AWS
- Define names in lowercase.
- Names can contain alphanumeric characters, hyphens (-), underscores (_), periods (.), and slashes (/)
- Names should not include IP addresses in their structure
- Follow AWS naming best practices
- Use Python as the default programming language
- Use a version earlier than the latest stable version, Python 3.x. -- Use Paramiko when defining the layer

### glue constraints

- Define crawler

- Define the data catalog name

{organization/client}-{environment}-{region}-{database}-{entity's representative name}

- Define the database connection name:

{protocol}-{environment}-{region}-{database}

- Maximum length: 3 to 63 characters

-- Names can contain alphanumeric characters, hyphens (-), underscores (_), periods (.), and slashes (/).

- Use the service's native data sources, transformations, and data destinations.

- Avoid using for and while loops. Instead, use the functions ApplyMaping, DropFields, Filter, Map, Aggregate, FillMissingValues, and PivotRowsToColumns. If very specific functionality is needed, use custom transformations and try to utilize PySpark/Spark functions.

## Instructions

### Secrets Manager System Instructions

1. Create a secret for the user and assign a name. It is suggested that the {representative name} field be replaced with user_sftp_on_prem.

2. Create a secret for the password and assign a name. It is suggested that the `password_sftp_on_prem` parameter be used in the `{representative name}` field.

### MySQL System Instructions

1. Create a table called `**visitor**` according to the following schema:

email: primary key

first_visit_date
last_visit_date
total_visits
current_year_visits
current_month_visits

2. Create a table called `**statistics**` according to the following schema:

email: primary key

jyv

badmail
unsubscribe

send_date

open_date

opens
viral_opens

click_date

clicks
viral_clicks

links

ips

browsers

platforms

3. Create a table called `**errors**` according to the following schema:

id
malformation

### TransferFamily System Instructions

1. Create the server and assign the name.

2. Use the SFTP protocol.

### TransferFamily System Instructions 3. Select the VPC endpoint

4. Configure User

5. Configure Service Role

6. Configure the S3 home directory

### Lambda system instructions

1. Create a Lambda function and assign a name.

2. Select the VPC, subnet, and execution role.

3. Create the following environment variables: ConnectorId, RetrieveFilePaths, LocalDirectoryPath

4. Create a Lambda function and use StartFileTransfer to configure ConnectorId, RetrieveFilePaths, and LocalDirectoryPath from the environment variables.

5. Configure the timeout to 900.

### glue system instructions

#### glue database connections system instructions

1. Define the database connection name.

2. Create the connection string "jdbc:mysql://[Your-Database-Endpoint]:3306/[Database-Name] ,S3://".

3. Assign a username and password.

4. Assign the VPC, select the subnets, and the security group.

#### glue database system instructions

1. Create a database and assign a name.

#### glue table system instructions

1. Create a table and assign a name. Create as many tables as there are in the MySQL schema.

2. Assign the name of the database created in the previous step.

3. Add the columns and their data types; match the MySQL structure.

#### glue crawler system instructions

1. Create the crawler and assign a name.

2. Select "Use an existing table" and reference a table in the glue table for each crawler.

#### glue crawler system instructions 3. In the configuration options: When the crawler finds changes in the schema: Ignore the changes and do not update the table in the data catalog -- "Update the table definition in the data catalog."

4. In the configuration options: When the crawler finds a deleted object: Mark the table as deprecated or Ignore it. -- "Mark the partition as deprecated in the data catalog"

#### glue job system instructions

1. Add an S3 data source node and configure the connection and object name in the bucket.

2. Add a Fill Missing Values ​​node and configure the following fields: column_name = email, value = missing, column_name = first_visit_date, value = 1000-01-01, column_name = last_visit_date, value = 1000-01-01, shipping_date, value = 1000-01-01, opening_date, value = 1000-01-01, click_date, value = 1000-01-01

3. Add a schema node and configure the field formats: column_name = email, format = string, column_name = first_visit_date, format = dd/mm/yyyy HH:mm, column_name = last_visit_date, format = dd/mm/yyyy HH:mm, column_name = shipping_date, format = dd/mm/yyyy HH:mm, column_name = fecha_open , format = dd/mm/yyyy HH:mm, column_name = fecha_click , format = dd/mm/yyyy HH:mm

4. If necessary, create a custom node using the to_date and isNull functions.

5. Add a filter node and create the following mutually exclusive dataframes:

errors: column_name = email value = missing or column_name = fecha_primera_visita , value = 1000-01-01, column_name = fecha_ultima_visita , value = 1000-01-01, or column_name = fecha_primera_visita , value = null, column_name = fecha_ultima_visita , value = null visitors : not errors

errors column_name = email value = missing or fecha_envio , value = 1000-01-01, fecha_open , value = 1000-01-01, fecha_click , value = 1000-01-01 or fecha_envio , value = null, fecha_open , value = null, fecha_click , value = null
statistics: not errors

7. Generate the following JSON structure from the errors columns: { id: int, payload : {text:"email | fecha_primera_visita | fecha_ultima_visita | visitas_totales | visitas_anio_actual | visitas_mes_actual" } } or {id: int, payload: {text: "email | jyv | badmail | baja | fecha_envio | fecha_open | opens | opens_virales | fecha_click | clicks | clicks_virales | links | ips | navegadores | plataformas } }

8. Query the records currently in the visitors table; perform a left join with the visitors dataframe created in the previous step using the email column, filtering for records that do not have a corresponding email address in the visitors table and inserting them into the visitors table.

18. For those records that already have a corresponding email address, perform the following updates in the table:

standard.visitors.last_visit_date = dataframe.visitors.last_visit_date

standard.visitors.total_visits = standard.visitors.total_visits + 1

standard.visitors.current_year_visits = standard.visitors.current_year_visits + 1

standard.visitors.current_month_visits = standard.visitors.current_month_visits + 1

9. Add a MySQL data target node and configure the connection and the table name.

#### system notification system instructions

1. Create a topic and assign a name. In the `{representative-name}` field, it is suggested to add `glue_job_notifications`.

2. Create a subscription with the email addresses that need to receive alerts.

#### Eventbridge System Instructions

1. Create a new rule and assign a name.

2. Select Schedule.

3. Configure the daily pattern `cron(0 12 * * ? *)`.

4. Select the glue job created in the previous step.

5. Create a new rule and assign a name. In the `{representative-name}` field, it is suggested to add `glue_job_notifications`.

6. Select Rule with an event pattern.

7. Configure an Eventbridge rule: `{"source": ["glue_job_name"], "detail-type": ["Glue Job State Change"], "detail": {"state": ["SUCCEEDED", "FAILED", "TIMEOUT", "STOPPED"] }}`

8. Select the glue job created in the previous step.

1. Create a new rule and name it.

2. Select Schedule.

3. Configure the daily pattern cron(0 12 * * ? *)

4. Select the lambda function created in previous steps.