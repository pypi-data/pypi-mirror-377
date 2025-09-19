import json
from sqlalchemy import create_engine, text, URL
from sqlalchemy.exc import SQLAlchemyError

class DBConfig:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
    
    def __str__(self):
        return f"DatabaseConfig(host={self.host}, port={self.port}, user={self.user}, database={self.database})"
    
    def __repr__(self):
        return self.__str__()

class DBManager:
    def __init__(self, application_name, config_string, logger):
        self.db_config = self.parse_db_config(config_string)
        self.connection_string = URL.create(
            drivername="postgresql",
            username=self.db_config.user,
            password=self.db_config.password,
            host=self.db_config.host,
            database=self.db_config.database,
        )
        self.application_name = application_name
        if logger:
            self.logger = logger

    def parse_db_config(self, config_string):
        """Парсит строку конфигурации создает DatabaseConfig"""
        config_dict = {}
        
        # Разделяем по точкам с запятой
        pairs = config_string.split(';')
        
        for pair in pairs:
            if ':' in pair:
                key, value = pair.split(':', 1)  # split только по первому двоеточию
                config_dict[key.strip()] = value.strip()
        
        # Создаем объект конфигурации
        return DBConfig(
            host=config_dict.get('host', ''),
            port=int(config_dict.get('port', 0)),
            user=config_dict.get('user', ''),
            password=config_dict.get('password', ''),
            database=config_dict.get('database', '')
        )
    
    def query_database(self, query, queryParams):
        connection_string = self.connection_string
        try:
            engine = create_engine(connection_string, 
                connect_args={
                    "application_name": self.application_name
                }
            )
            
            with engine.connect() as conn:
                # Выполнение запроса с параметрами
                result = conn.execute(query, queryParams)
                #print("[query_database]", query, queryParams)
                # Получение всех результатов
                items = result.fetchall()
                
                conn.commit()
                return items
                
        except SQLAlchemyError as e:
            error_msg = f"Database error: {e}"
            self.logger.log(f'{error_msg} {query} {queryParams}')
            return None
            
        finally:
            # Гарантированное отключение от БД
            if 'engine' in locals():
                engine.dispose()


    def of_users(self, sender_id):
        query = text("""
            SELECT * FROM core.of_users(
                (SELECT to_jsonb(t) FROM core.sf_users(:sender_id) as t), 
                '{"c_profiles":["user", "brigade"]}'::jsonb
            );
            """
        )
        queryParams = {
            "sender_id": sender_id
        }
        return query, queryParams


    def of_levels(self, sender_id):
        query = text("""
            SELECT * FROM core.of_levels(
                (SELECT to_jsonb(t) FROM core.sf_users(:sender_id) as t), 
                null
            );
            """
        )
        queryParams = {
            "sender_id": sender_id
        }
        return query, queryParams

    def cs_event_types(self):
        query = text("""
            SELECT id, c_name, c_const, b_disabled, b_default
            FROM dbo.cs_event_types;
            """
        )
        queryParams = {}
        return query, queryParams
    
    def of_arm_cd_user_events(self, sender_id, d_date_start, d_date_end):
        query = text("""
            SELECT * FROM dbo.of_arm_cd_user_events(
                (SELECT to_jsonb(t) FROM core.sf_users(:sender_id) as t), 
                :json_params
            );
            """
        )
        queryParams = {
            "sender_id": sender_id,
            "json_params": json.dumps({
                "d_date_start": d_date_start,
                "d_date_end": d_date_end
            })
        }
        return query, queryParams

    def of_arm_add_calendar_data(self, sender_id, data):
        query = text("""
            SELECT * FROM dbo.of_arm_add_calendar_data(
                (SELECT to_jsonb(t) FROM core.sf_users(:sender_id) as t), 
                :json_params
            );
            """
        )
        queryParams = {
            "sender_id": sender_id,
            "json_params": json.dumps(data)
        }
        return query, queryParams