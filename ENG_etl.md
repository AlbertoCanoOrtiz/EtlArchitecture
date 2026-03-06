## Objective

The objective is to create an ETL process within the AWS platform. This ETL process will be used to read a text file from an SFTP server, process it, and load the information into a MySQL database management system, maintaining a backup in an S3 bucket. This ETL process must include control points, alerts, validations, error handling, and error notifications.

## Instructions

Create the roles and access policies in .json format.

Create the layer and the Lambda function to read, process, and load the data.

Create the YAML files for automatic deployment using CloudFormation.

## Constraints

### IAM Constraints

- Define the role name according to the style determined by the security area.

- Create a Lambda ServiceRole. It is important to limit it to only the resources necessary for the project using the ARN. 1."s3:ListBucket", "s3:GetObject", "s3:PutObject", 
2."secretsmanager:GetSecretValue", "secretsmanager:DescribeSecret" "secretsmanager:ListSecrets" 
3."events:PutRule","events:PutTargets","events:DescribeRule" 
4."logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents" 
5."ec2:CreateNetworkInterface", "ec2:DescribeNetworkInterfaces", "ec2:DeleteNetworkInterface", "ec2:AssignPrivateIpAddresses", "ec2:UnassignPrivateIpAddresses" 
-- Create a ServiceRole of always important notification service to limit it only to the resources that are necessary for the project using the arn
1. "sns:Publish", sns:GetTopicAttributes, sns:GetTopicAttributes

- Create a ServiceRole of eventbridge service

1. "events:PutEvents","events:PutRule","events:DescribeRule","events:DeleteRule", "events:PutTargets", "events:RemoveTargets","events:RemoveTargets","lambda:InvokeFunction"

### MySQL Constraints

Tables will be created in the **standard** layer because the data already contains some transformations. It is important to follow the naming best practices proposed by MySQL.

- Use the Snake script.

- Maximum length of 64 characters.

- Avoid special characters, spaces, and names reserved by MySQL.

- Define field names in lowercase. -- Define primary keys for the table.

- Define auditable fields for the row in the table.

- Define the tables in a denormalized form since it is a table designed for data mining.

### Lambda constraints

- Define the name of the lambda function according to the following contextual style:

{organization/client}-{environment}-{region}-{project}-{representative name}.

- Maximum length of 3 to 63 characters.

- Avoid prefixes used by AWS.

- Define the names in lowercase. -- Names can contain alphanumeric characters, hyphens (-), underscores (_), periods (.), and slashes (/).

- Names should not include IP addresses in their structure.

- Follow AWS naming best practices.

- Use Python as the default programming language.

- Use a version earlier than the latest stable version, Python 3.x.

- Use Paramiko when defining the layer.

### Secrets Manager Constraints

- Define the secret name according to the following contextual style:

{organization/client}-{environment}-{region}-{project}-{representative name}

- Maximum length: 3 to 63 characters.

- Names can contain alphanumeric characters, hyphens (-), underscores (_), periods (.), and slashes (/).

- Avoid names used by AWS.

- Define names in lowercase. -- Names should not include IP addresses in their structure

## system instructions

### mysql system instructions

1. Create a table called **visitor** according to the following schema:

email: primary key

first_visit_date
last_visit_date
total_visits
current_year_visits
current_month_visits

2. Create a table called **statistics** according to the following schema:

email: primary key
jyv
badmail
unsubscribe
submit_date
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

3. Create a table called **errors** according to the following schema:

id
malformation

### lambda system instructions

1. Create a lambda function and assign it a name.

2. Select the VPC, subnet, and execution role.

3. Create a specific path: `mkdir -p build/python`, `cd build/python`. Create a Python 3.x virtual environment using the command `python3.x -m venv .`, and install Paramiko in the environment using `pip install paramiko -t .`, `zip -r paramiko_layer.zip python/`.

4. Configure a timeout of 900.

5. Configure the secret name as an environment variable in the Lambda function.

6. Configure ephemeral storage to 10,240 MB.

7. Use `paramiko_layer` as the layer in the Lambda function.

8. Configure RAM to 1024 MB.

9. The Lambda function should use the environment variable to read the source username and password from the secrets manager.

10. Invoke SFTP with `parmico` and retrieve the file to the `/tmp/` folder of the container where the Lambda function is running, then delete the file from the source.

11. Load the file using the `read_csv` function and configure the schema as JSON according to the MySQL structure. 12. Based on the following fields: column: email value: missing, column: first_visit_date value: 1000-01-01, column: last_visit_date value: 1000-01-01, column: shipment_date value: 1000-01-01, column: open_date value: 1000-01-01, column: click_date value: 1000-01-01, use the fillna() function of the pandas object.

13. Use the to_datetime function with the parameter errors='coerce' to validate the columns first_visit_date, last_visit_date, shipment_date, open_date, and click_date.

14. From the dataframes, filter the following scenarios and create the following mutually exclusive dataframes:

errors: column_name = email value = missing or column_name = first_visit_date, value = 1000-01-01, column_name = last_visit_date, value = 1000-01-01, or column_name = first_visit_date, value = null, column_name = last_visit_date, value = null visitors: not errors.

errors column_name = email value = missing or shipment_date, value = 1000-01-01, open_date, value = 1000-01-01, click_date, value = 1000-01-01 or shipment_date, value = null, open_date, value = null, click_date, value = null

statistics: not errors.

15. Generate the following JSON structure from the errors columns: { id: int, payload: {text: "email | first_visit_date | last_visit_date | total_visits | current_year_visits | current_month_visits" } } or {id: int, payload: {text: "email | jyv | badmail | baja | shipping_date | open_date | opens | viral_opens | click_date | clicks | viral_clicks | links | ips | browsers | platforms" } }.

16. Sort the dataframe built by email in descending order by the email column.

17. Query the records currently in the visitors table; perform a left join with the visitors dataframe built in the previous step using the email column, filtering out those records that do not have a corresponding email in the visitors table and inserting them into the visitors table.

18. For those that already have an email To perform the following update in the table:

standard.visitors.last_visit_date = dataframe.visitors.last_visit_date

standard.visitors.total_visits = standard.visitors.total_visits + 1

standard.visitors.current_year_visits = standard.visitors.current_year_visits + 1

standard.visitors.current_month_visits = standard.visitors.current_month_visits + 1

19. Close the database connection.

### eventbridge system instructions

1. Create a new rule and assign a name.

2. Select Schedule.

3. Configure the daily pattern cron(0 12 * * ? *)

4. Select the lambda function created in the previous step.

### system notification

1. Create a topic and assign a name.

2. Create a subscription with the emails that They need to receive alerts.

3. Create alerts in CloudWatch for "Process finished" and "Errors" by selecting the theme created from the system notification.

### CloudFormation System Instructions

1. Create a CloudFormation to deploy all the necessary roles and security groups in the project.

2. Create a CloudFormation to deploy the project's database connections.

3. Create a CloudFormation to deploy the remaining project services.
