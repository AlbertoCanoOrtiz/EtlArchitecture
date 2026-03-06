from pyspark.sql import functions as f
from pyspark.sql import SparkSession
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from awsglue.transforms import Map, SelectFields, ApplyMapping
import logging
import sys
import os
import uuid
import re
import datetime
import json

def load_source_data(glue):
    return glue.create_dynamic_frame.from_options(
        connection_type='file',
        connection_options={'paths': ['/home/glue/scripts/visitor.txt']},
        format='csv',
        format_options={'withHeader': True, 'separator': ','}
    )

def validate_and_transform(df):
    def try_vinkos_datetime_format(somestring):
        try:
            return datetime.datetime.strptime(str(somestring), '%d/%m/%Y %H:%M').strftime('%d/%m/%Y %H:%M')
        except:
            return datetime.datetime.strptime('01/01/1000 00:00', '%d/%m/%Y %H:%M').strftime('%d/%m/%Y %H:%M')
    
    df = Map.apply(df, lambda x: x.update({'is_not_valid_email': not bool(re.match(r'[^@]+@[^@]+\.[^@]+', str(x.get('email'))))}) or x)
    df = Map.apply(df, lambda x: x.update({'fecha_primera_vista': try_vinkos_datetime_format(x.get('fecha_primera_vista'))}) or x)
    df = Map.apply(df, lambda x: x.update({'fecha_ultima_vista': try_vinkos_datetime_format(x.get('fecha_ultima_vista'))}) or x)
    return df

def split_valid_invalid(df):
    qadf = df.filter(lambda x: x.get('is_not_valid_email') == True)
    df = df.filter(lambda x: x.get('is_not_valid_email') == False)
    return df, qadf

def prepare_valid_data(df):
    df = SelectFields.apply(df, ['email', 'fecha_primera_vista', 'fecha_ultima_vista', 'vistas_totales', 'vistas_anio_actual', 'vistas_mes_actual'])
    df = ApplyMapping.apply(df, [
        ('email', 'string', 'email', 'string'),
        ('fecha_primera_vista', 'string', 'fecha_primera_vista', 'string'),
        ('fecha_utlima_vista', 'string', 'fecha_ultima_vista', 'string'),
        ('vistas_totales', 'string', 'vistas_totales', 'long'),
        ('vistas_anio_actual', 'string', 'vistas_anio_actual', 'long'),
        ('vistas_mes_actual', 'string', 'vistas_mes_actual', 'long')
    ])
    df = Map.apply(df, lambda x: x.update({
        'vistas_totales': 0 if x.get('vistas_totales') is None else x.get('vistas_totales'),
        'vistas_anio_actual': 0 if x.get('vistas_anio_actual') is None else x.get('vistas_anio_actual'),
        'vistas_mes_actual': 0 if x.get('vistas_mes_actual') is None else x.get('vistas_mes_actual')
    }) or x)
    return df

def prepare_error_data(qadf):
    qadf = Map.apply(qadf, lambda x: x.update({'uuid': str(uuid.uuid4())}) or x)
    qadf = Map.apply(qadf, lambda x: x.update({'malformacion': json.dumps({
        'uuid': x.get('uuid'),
        'payload': {k: x.get(k) for k in ['email', 'fecha_primera_vista', 'fecha_ultima_vista', 'vistas_totales', 'vistas_anio_actual', 'vistas_mes_actual']}
    })}) or x)
    return SelectFields.apply(qadf, ['malformacion'])

def load_existing_data(glue, config):
    return glue.create_dynamic_frame.from_options(
        connection_type='mysql',
        connection_options={
            'url': config['url'],
            'user': config['username'],
            'password': config['password'],
            'dbtable': 'visitor'
        }
    )

def merge_with_existing(df, indb, spark, glue):
    indb = ApplyMapping.apply(indb, [
        ('fecha_primera_vista', 'string', 'fecha_primera_vista_db', 'string'),
        ('fecha_utlima_vista', 'string', 'fecha_ultima_vista_db', 'string'),
        ('vistas_totales', 'long', 'vistas_totales_db', 'long'),
        ('vistas_anio_actual', 'long', 'vistas_anio_actual_db', 'long'),
        ('vistas_mes_actual', 'long', 'vistas_mes_actual_db', 'long'),
        ('email', 'string', 'email_db', 'string')
    ])
    
    df.toDF().createOrReplaceTempView('df')
    indb.toDF().createOrReplaceTempView('indb')
    df = DynamicFrame.fromDF(spark.sql('select df.*,indb.* from df left join indb on df.email = indb.email_db'), glue, 'jdf')
    
    updates = df.filter(lambda x: x.get('email_db') is not None)
    inserts = df.filter(lambda x: x.get('email_db') is None)
    
    if updates.count() > 0:
        updates = Map.apply(updates, lambda x: x.update({
            'fecha_ultima_vista': x.get('fecha_ultima_vista_db'),
            'vistas_totales': x.get('vistas_totales') + 1,
            'vistas_anio_actual': x.get('vistas_anio_actual') + 1,
            'vistas_mes_actual': x.get('vistas_mes_actual') + 1
        }) or x)
        updates = SelectFields.apply(updates, ['email', 'fecha_primera_vista', 'fecha_ultima_vista', 'vistas_totales', 'vistas_anio_actual', 'vistas_mes_actual'])
    
    if inserts.count() > 0:
        inserts = SelectFields.apply(inserts, ['email', 'fecha_primera_vista', 'fecha_ultima_vista', 'vistas_totales', 'vistas_anio_actual', 'vistas_mes_actual'])
    
    return updates, inserts

def write_to_mysql(glue, df, config, table):
    glue.write_dynamic_frame.from_options(
        frame=df,
        connection_type='mysql',
        connection_options={
            'url': config['url'],
            'user': config['username'],
            'password': config['password'],
            'dbtable': table,
            'useSSL': False
        }
    )

def run_pipeline():
    spark = SparkSession.builder.appName('vinkos').getOrCreate()
    glue = GlueContext(spark.sparkContext)
    job = Job(glue)
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    os.environ['AWS_DEFAULT_REGION'] = 'us_east_1'
    
    with open("config.json", "r") as file:
        config = json.load(file)
    
    # Pipeline stages
    df = load_source_data(glue)
    df = validate_and_transform(df)
    df, qadf = split_valid_invalid(df)
    df = prepare_valid_data(df)
    qadf = prepare_error_data(qadf)
    
    indb = load_existing_data(glue, config)
    
    if indb.count() > 0:
        print('Updating existing records')
        updates, inserts = merge_with_existing(df, indb, spark, glue)
        if updates.count() > 0:
            write_to_mysql(glue, updates, config, 'visitor')
        if inserts.count() > 0:
            write_to_mysql(glue, inserts, config, 'visitor')
    else:
        print('Initial load')
        write_to_mysql(glue, df, config, 'visitor')
    
    if qadf.count() > 0:
        write_to_mysql(glue, qadf, config, 'errors')
    
    print('Process completed successfully!')

if __name__ == '__main__':
    try:
        run_pipeline()
    except Exception as e:
        logging.error(f'Unexpected error: {e}')
        raise
