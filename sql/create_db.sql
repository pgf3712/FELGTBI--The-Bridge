CREATE TABLE administradores (
    administrador_id SERIAL PRIMARY KEY, 
    nombre VARCHAR(50),
    apellidos VARCHAR(50),
    fecha_nac DATE,
    email VARCHAR(60) NOT NULL,
    contrasena VARCHAR(40) NOT NULL,
    rol varchar(20) NOT NULL
);

CREATE TABLE llm_log (
    log_id SERIAL PRIMARY KEY, 
    prompt TEXT,
    respuesta_llm TEXT
);

-- Relaciones en tablas

CREATE TABLE usuarios (
    usuario_id SERIAL PRIMARY KEY,
    genero VARCHAR(30) NOT NULL,
    orien_sex VARCHAR(30) NOT NULL,
    edad INT NOT NULL,
    pais VARCHAR(30) NOT NULL,
    ciudad VARCHAR(50) NOT NULL
);

CREATE TABLE ambitos (
    ambito_id SERIAL PRIMARY KEY,
    ambito VARCHAR(40) NOT NULL
);

CREATE TABLE especialidades (
    especialidad_id SERIAL PRIMARY KEY,
    ambito_id INT NOT NULL,
    especialidad VARCHAR (40) NOT NULL,
    FOREIGN KEY (ambito_id) REFERENCES ambitos(ambito_id)
);

CREATE TABLE profesionales (
    profesional_id SERIAL PRIMARY KEY,
    ciudad VARCHAR(40) NOT NULL, 
    cod_postal INT NOT NULL, 
    especialidad_id INT NOT NULL,
    FOREIGN KEY (especialidad_id) REFERENCES especialidades(especialidad_id)
);

CREATE TABLE preguntas (
    pregunta_id SERIAL PRIMARY KEY, 
    pregunta VARCHAR(100),
    rol VARCHAR(20)
);

CREATE TABLE respuestas (
    respuesta_id SERIAL PRIMARY KEY, 
    respuesta VARCHAR(100),
    rol VARCHAR(20)
); 

CREATE TABLE preguntas_respuestas (
    pregunta_id INT NOT NULL, 
    respuesta_id INT NOT NULL, 
    PRIMARY KEY (pregunta_id, respuesta_id),
    FOREIGN KEY (pregunta_id) REFERENCES preguntas(pregunta_id),
    FOREIGN KEY (respuesta_id) REFERENCES respuestas(respuesta_id)
);

CREATE TABLE interacciones (
    interaccion_id SERIAL PRIMARY KEY,
    usuario_id INT,
    profesional_id INT, 
    pregunta_id INT NOT NULL,
    respuesta_id INT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(usuario_id),
    FOREIGN KEY (profesional_id) REFERENCES profesionales(profesional_id),
    FOREIGN KEY (pregunta_id, respuesta_id) REFERENCES preguntas_respuestas(pregunta_id, respuesta_id)
);