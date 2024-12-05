import psycopg2

def setup_database():
    try:
        # Conexión a PostgreSQL, directamente a la base de datos 'chatbot'
        connection = psycopg2.connect(
            host="chatbott-1.cd8842m827w5.eu-north-1.rds.amazonaws.com",
            port="5432",
            database="chatbot",  # Base de datos ya existente
            user="postgresadmin",
            password="somosinteligentes"
        )
        cursor = connection.cursor()

        # Crear la tabla 'usuarios' (comentada si ya se ejecutó)
        # cursor.execute("""
        #     CREATE TABLE IF NOT EXISTS usuarios (
        #         usuario_id SERIAL PRIMARY KEY,
        #         pais VARCHAR(64) NOT NULL,
        #         genero VARCHAR(30) NOT NULL,
        #         orientacion VARCHAR(30) NOT NULL,
        #         zip INT NOT NULL
        #     );
        # """)
        # print("✅ Tabla 'usuarios' creada o ya existente.")

        # Crear la tabla 'profesionales' (comentada si ya se ejecutó)
        # cursor.execute("""
        #     CREATE TABLE IF NOT EXISTS profesionales (
        #         profesional_id SERIAL PRIMARY KEY,
        #         ciudad VARCHAR(50) NOT NULL,
        #         zip INT NOT NULL,
        #         ambito_laboral VARCHAR(50),
        #         especialidad VARCHAR(50) NOT NULL
        #     );
        # """)
        # print("✅ Tabla 'profesionales' creada o ya existente.")

        # Crear la tabla 'respuestas'
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS respuestas (
                respuesta_id SERIAL PRIMARY KEY,
                usuario_id INT NOT NULL,
                respuesta_1 VARCHAR(30),
                respuesta_2 VARCHAR(30),
                respuesta_3 VARCHAR(30),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(usuario_id)
            );
        """)
        print("✅ Tabla 'respuestas' creada o ya existente.")

        connection.commit()

    except Exception as e:
        print("❌ Error al configurar la base de datos:", e)
    finally:
        if 'connection' in locals() and connection:
            connection.close()
            print("🔒 Conexión cerrada")

if __name__ == "__main__":
    setup_database()

       


