use standard;

create table visitor(
        email varchar(255) primary key, 
        fecha_primera_visita varchar(16), 
        fecha_ultima_visita varchar(16), 
        visitas_totales bigint, 
        visitas_anio_actual bigint,
        visitas_mes_actual bigint
);

create table statistics(
        email varchar(255) primary key,
        jyv varchar(50),
        badmail boolean,
        baja varchar(50),
        fecha_envio varchar(16),
        fecha_open varchar(16),
        opens bigint,
        opens_virales bigint,
        fecha_click varchar(16),
        clicks bigint,
        clicks_virales bigint,
        links varchar(255),
        ips varchar(255),
        navegadores varchar(1500),
        plataformas varchar(1500)
);

create table errors(
        id int AUTO_INCREMENT primary KEY,
        malformacion json
);
