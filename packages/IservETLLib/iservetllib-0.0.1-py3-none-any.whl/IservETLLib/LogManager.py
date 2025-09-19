import os
import uuid
from datetime import datetime
from enum import Enum
from fluent import sender, event

class FluentConf:
    def __init__(self, host, port):
        self.host = host
        self.port = port
    
    
class LogLevel(Enum):
    INFO = 'INFO'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'

class Logger:
    def __init__(self, application_name, file):
        self.file = file
        self.application_name = application_name
        self.fluent = None

    def init_fluent(self, level: LogLevel, fluent: FluentConf):
        if not fluent:
            raise Exception('Конфиг пустой')
            return
        
        sender.fluent = fluent
        sender.setup(level, host=fluent.host, port=fluent.port)


    def log(self, message):
        self.__log(LogLevel.INFO, message)

    def error(self, message, b_raise=True):
        self.__log((LogLevel.CRITICAL if b_raise else LogLevel.ERROR), message)

    def __log(self, level: LogLevel, message):
        """
        Parameters
        ----------
        level: LogLevel 
            уровень INFO ERROR CRITICAL
        message : str
            входная строка

        Raises
        -------
        Exception
            Исключение при записи в лог-файл
        """
        datetime_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f'{level.name} {datetime_string}: {message}'
        print(message)

        file = self.file
        try:
            # Создаем директорию, если она не существует
            dir = os.path.dirname(file)
            if dir:  # Если путь содержит директорию
                os.makedirs(dir, exist_ok=True)

            with open(file, 'a', encoding='utf-8') as f:
                f.write(message + '\n')
        except Exception as e:
            print(f'Ошибка записи в лог-файл {file}: {e}')

        if self.fluent:
            event.Event(level.name, {
                "id": f"etl.{self.application_name}.{uuid.uuid4()}",
                "@timestamp": datetime_string,
                "message": message
            })

        if level == LogLevel.CRITICAL:
            raise Exception(message)
        

    