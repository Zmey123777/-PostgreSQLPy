import psycopg2

def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            client_id SERIAL PRIMARY KEY,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            email VARCHAR(100)
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS phones (
            phone_id SERIAL PRIMARY KEY,
            client_id INTEGER REFERENCES clients(client_id) ON DELETE CASCADE,
            phone VARCHAR(20)
        );
        """)
        conn.commit()

def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO clients (first_name, last_name, email) VALUES (%s, %s, %s) RETURNING client_id;
        """, (first_name, last_name, email))
        client_id = cur.fetchone()[0]
        if phones:
            for phone in phones:
                cur.execute("""
                INSERT INTO phones (client_id, phone) VALUES (%s, %s);
                """, (client_id, phone))
        conn.commit()
        return client_id

def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO phones (client_id, phone) VALUES (%s, %s);
        """, (client_id, phone))
        conn.commit()

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as cur:
        if first_name:
            cur.execute("""
            UPDATE clients SET first_name = %s WHERE client_id = %s;
            """, (first_name, client_id))
        if last_name:
            cur.execute("""
            UPDATE clients SET last_name = %s WHERE client_id = %s;
            """, (last_name, client_id))
        if email:
            cur.execute("""
            UPDATE clients SET email = %s WHERE client_id = %s;
            """, (email, client_id))
        if phones is not None:
            cur.execute("""
            DELETE FROM phones WHERE client_id = %s;
            """, (client_id,))
            for phone in phones:
                cur.execute("""
                INSERT INTO phones (client_id, phone) VALUES (%s, %s);
                """, (client_id, phone))
        conn.commit()

def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
        DELETE FROM phones WHERE client_id = %s AND phone = %s;
        """, (client_id, phone))
        conn.commit()

def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
        DELETE FROM clients WHERE client_id = %s;
        """, (client_id,))
        conn.commit()

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    query = """
    SELECT c.client_id, c.first_name, c.last_name, c.email, p.phone 
    FROM clients c 
    LEFT JOIN phones p ON c.client_id = p.client_id
    WHERE 1=1
    """
    params = []
    if first_name:
        query += " AND c.first_name = %s"
        params.append(first_name)
    if last_name:
        query += " AND c.last_name = %s"
        params.append(last_name)
    if email:
        query += " AND c.email = %s"
        params.append(email)
    if phone:
        query += " AND p.phone = %s"
        params.append(phone)
    
    with conn.cursor() as cur:
        cur.execute(query, tuple(params))
        results = cur.fetchall()
        return results

# Установите свою конфигурацию для доступа к ДБ
connection_parameters = {
    'dbname': '',
    'user': '',
    'password': '',  
    'host': ''
}


# Запуск функций
with psycopg2.connect(**connection_parameters) as conn:
    create_db(conn)
    
    client_id = add_client(conn, 'Юрий', 'Кэшинвалидатович', 'Юрий@example.com', ['123456789', '987654321'])
    print(f"Добавлен клиент с ID: {client_id}")
    
    add_phone(conn, client_id, '555555555')
    print(f"Добавлен телефон для клиента ID: {client_id}")
    
    change_client(conn, client_id, first_name='Юрий', last_name='Кэшинвалидатович', email='Юрий@example.com', phones=['111111111', '222222222'])
    print(f"Изменена информация о клиенте for ID: {client_id}")
    
    delete_phone(conn, client_id, '111111111')
    print(f"Удален телефон для клиента ID: {client_id}")
    
    clients = find_client(conn, first_name='Юрий')
    print(f"Найдены клиенты: {clients}")
    
    delete_client(conn, client_id)
    print(f"Удален клиент ID: {client_id}")

conn.close()
