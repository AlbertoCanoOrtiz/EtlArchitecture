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
from datetime import datetime
import json

def load_source_data(glue):
    return glue.create_dynamic_frame.from_options(
        connection_type='file',
        connection_options={'paths': ['/home/glue/scripts/statistics.txt']},
        format='csv',
        format_options={'withHeader': True, 'separator': ','}
    )

def validate_and_transform(df):
    def try_vinkos_datetime_format(somestring):
        try:
            return datetime.strptime(str(somestring), '%d/%m/%Y %H:%M').strftime('%d/%m/%Y %H:%M')
        except:
            return datetime.strptime('01/01/1000 00:00', '%d/%m/%Y %H:%M').strftime('%d/%m/%Y %H:%M')
    
    df = Map.apply(df, lambda x: x.update({'badmail': not bool(re.match(r'[^@]+@[^@]+\.[^@]+', str(x.get('email'))))}) or x)
    df = Map.apply(df, lambda x: x.update({'fecha_open': try_vinkos_datetime_format(x.get('fecha_open'))}) or x)
    df = Map.apply(df, lambda x: x.update({'fecha_envio': try_vinkos_datetime_format(x.get('fecha_envio'))}) or x)
    df = Map.apply(df, lambda x: x.update({'fecha_click': try_vinkos_datetime_format(x.get('fecha_click'))}) or x)
    return df

def split_valid_invalid(df):
    qadf = df.filter(lambda x: x.get('badmail') == True or x.get('fecha_open') == '01/01/1000 00:00')
    df = df.filter(lambda x: x.get('badmail') == False and x.get('fecha_open') != '01/01/1000 00:00')
    return df, qadf

def prepare_error_data(qadf):
    qadf = Map.apply(qadf, lambda x: x.update({'uuid': str(uuid.uuid4())}) or x)
    qadf = Map.apply(qadf, lambda x: x.update({'malformacion': json.dumps({
        'uuid': x.get('uuid'),
        'payload': {k: x.get(k) for k in ['email', 'jyv', 'badmail', 'baja', 'fecha_envio', 'fecha_open', 
                                           'opens', 'opens_virales', 'fecha_click', 'clicks', 'clicks_virales', 
                                           'links', 'ips', 'navegadores', 'plataformas']}
    })}) or x)
    return SelectFields.apply(qadf, ['malformacion'])

def load_existing_data(glue, config):
    return glue.create_dynamic_frame.from_options(
        connection_type='mysql',
        connection_options={
            'url': config['url'],
            'user': config['username'],
            'password': config['password'],
            'dbtable': 'statistics'
        }
    )

def find_new_records(df, indb, spark, glue):
    indb = ApplyMapping.apply(indb, [
        ('baja', 'string', 'baja_db', 'string'),
        ('fecha_open', 'string', 'fecha_open_db', 'string'),
        ('clicks', 'long', 'clicks_db', 'long'),
        ('opens_virales', 'long', 'opens_virales_db', 'long'),
        ('badmail', 'boolean', 'badmail_db', 'boolean'),
        ('fecha_envio', 'string', 'fecha_envio_db', 'string'),
        ('links', 'string', 'links_db', 'string'),
        ('jyv', 'string', 'jyv_db', 'string'),
        ('clicks_virales', 'long', 'clicks_virales_db', 'long'),
        ('navegadores', 'string', 'navegadores_db', 'string'),
        ('plataformas', 'string', 'plataformas_db', 'string'),
        ('opens', 'long', 'opens_db', 'long'),
        ('fecha_click', 'string', 'fecha_click_db', 'string'),
        ('email', 'string', 'email_db', 'string'),
        ('ips', 'string', 'ips_db', 'string')
    ])
    
    df.toDF().createOrReplaceTempView('df')
    indb.toDF().createOrReplaceTempView('indb')
    df = DynamicFrame.fromDF(spark.sql('select df.*,indb.* from df left join indb on df.email = indb.email_db'), glue, 'jdf')
    
    new_records = df.filter(lambda x: x.get('email_db') is None)
    
    if new_records.count() > 0:
        new_records = SelectFields.apply(new_records, ['email', 'baja', 'fecha_open', 'clicks', 'opens_virales', 
                                                        'badmail', 'fecha_envio', 'links', 'jyv', 'clicks_virales', 
                                                        'navegadores', 'plataformas', 'opens', 'fecha_click', 'ips'])
    
    return new_records

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
    os.environ['AWS_DEFAULT_REGION'] = 'us_east-1'
    
    with open("config.json", "r") as file:
        config = json.load(file)
    
    # Pipeline stages
    df = load_source_data(glue)
    df = validate_and_transform(df)
    df, qadf = split_valid_invalid(df)
    qadf = prepare_error_data(qadf)
    
    indb = load_existing_data(glue, config)
    
    if indb.count() > 0:
        print('Appending new records')
        new_records = find_new_records(df, indb, spark, glue)
        if new_records.count() > 0:
            write_to_mysql(glue, new_records, config, 'statistics')
    else:
        print('Initial load')
        write_to_mysql(glue, df, config, 'statistics')
    
    if qadf.count() > 0:
        write_to_mysql(glue, qadf, config, 'errors')
    
    print('Process completed successfully!')

if __name__ == '__main__':
    try:
        run_pipeline()
    except Exception as e:
        logging.error(f'Unexpected error: {e}')
        raise
