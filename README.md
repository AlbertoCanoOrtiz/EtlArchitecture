# 🚀 AWS Glue Local ETL Pipeline

This project simulates a cloud-based ETL architecture locally using Docker. It leverages AWS Glue Libs 4.0 to run Spark jobs that process data and load it into a local MySQL instance.

# 🛠️ Environment Setup

## 1. Initialize the MySQL Database

Run this command to start a MySQL container. It automatically executes init.sql to create the standard database and the visitor, statistics, and errors tables.
Bash

```Bash

docker run -d \
  --name opensource-data-engineer-mysql-container \
  -e MYSQL_ROOT_PASSWORD=xxxx \
  -e MYSQL_DATABASE=standard \
  -e MYSQL_USER=glue \
  -e MYSQL_PASSWORD=xxxx \
  -v /home/levy/Desktop/EtlArchitecture/PyScripts/init.sql:/docker-entrypoint-initdb.d/init.sql \
  -p 3306:3306 \
  mysql:latest
```

## 2. Launch the AWS Glue Container

Start the Glue interactive container and mount your local scripts directory.
Bash


```Bash
# Start the Glue container
docker run -it \
  -v /home/levy/Desktop/EtlArchitecture:/home/glue/scripts \
  public.ecr.aws/glue/aws-glue-libs:glue_libs_4.0.0_image_01

# Set your target region
export AWS_REGION=us-east-1
```

## 3. Identify the Database IP

Before running the jobs, find the internal IP address of your MySQL container so the Glue container can connect to it.

```Bash

docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' vinkos-data-engineer-mysql-container
```

# 🏃 Execution Steps

Once inside the Glue container, use spark-submit to execute the ETL logic. These commands include the MySQL JDBC driver and necessary Glue libraries.
Step A: Process Visitor Data

This script cleans visitor logs, validates emails, and updates the visitor table.

```Bash

/home/glue_user/spark/bin/spark-submit \
  --jars /home/glue_user/aws-glue-libs/jars/*,/home/glue/scripts/PyScripts/mysql-connector-j-9.1.0.jar \
  --driver-class-path /home/glue/scripts/PyScripts/mysql-connector-j-9.1.0.jar \
  --py-files /home/glue_user/aws-glue-libs/PyGlue.zip \
  /home/glue/scripts/PyScripts/opensource-data-engineer-glue-visitor.py
```

Step B: Process Statistics Data

This script handles the interaction metrics, including clicks and platform data.

```Bash

/home/glue_user/spark/bin/spark-submit \
  --jars /home/glue_user/aws-glue-libs/jars/*,/home/glue/scripts/PyScripts/mysql-connector-j-9.1.0.jar \
  --driver-class-path /home/glue/scripts/PyScripts/mysql-connector-j-9.1.0.jar \
  --py-files /home/glue_user/aws-glue-libs/PyGlue.zip \
  /home/glue/scripts/PyScripts/opensource-data-engineer-glue-statistics.py
```

# 📂 Project Components

init.sql: Database schema defining the visitor, statistics, and errors tables.

mysql-connector-j-9.1.0.jar: The required driver for Spark-to-MySQL connectivity.

opensource-data-engineer-glue-visitor.py : ETL logic for visitor data using GlueContext and DynamicFrames.

opensource-data-engineer-glue-statistics.py: ETL logic for engagement metrics.