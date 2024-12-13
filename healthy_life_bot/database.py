import sqlite3 
import matplotlib.pyplot as plt 
from datetime import datetime 


class Database:
    """Класс для работы с SQLite базой данных.

    Управляет всеми операциями с данными пользователей:
    создание таблиц, добавление/обновление данных,
    получение статистики и создание графиков прогресса.

    Args:
        db_name: Имя файла базы данных (по умолчанию 'fitness.db')
    """

    def __init__(self, db_name='fitness.db'):  
        self._connection = None
        self._db_name = db_name
  
    def get_connection(self):
        """Создает подключение к базе данных.

        Args:
            None

        Returns:
            sqlite3.Connection: Объект подключения к БД
        """

        return sqlite3.connect(self._db_name)

    def create_tables(self):
        """Создает необходимые таблицы в базе данных.

            Создает две таблицы:
            - users: хранит основную информацию о пользователях
            - weight_history: хранит историю изменения веса

            Args:
                None

            Returns:
                None
            """

        with self.get_connection() as conn: 
            cursor = conn.cursor() 
            cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS users ( 
                user_id INTEGER PRIMARY KEY, 
                age INTEGER NOT NULL, 
                height INTEGER NOT NULL, 
                initial_weight REAL NOT NULL, 
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
            ) 
            ''') 
             
            cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS weight_history ( 
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                user_id INTEGER, 
                weight REAL NOT NULL, 
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                FOREIGN KEY (user_id) REFERENCES users(user_id) 
            ) 
            ''') 
            conn.commit() 
 
    def add_user(self, user_id: int, age: int, height: int, weight: float):
        """Добавляет нового пользователя в базу данных.

            При добавлении пользователя также создается первая запись
            в истории веса с начальным значением.

            Args:
                user_id: Telegram ID пользователя
                age: Возраст пользователя
                height: Рост пользователя в сантиметрах
                weight: Вес пользователя в килограммах

            Returns:
                None
            """

        with self.get_connection() as conn: 
            cursor = conn.cursor() 
            cursor.execute(
                'INSERT OR REPLACE INTO users (user_id, age, height, initial_weight) VALUES (?, ?, ?, ?)',
                (user_id, age, height, weight)
            ) 
            cursor.execute( 
                'INSERT INTO weight_history (user_id, weight) VALUES (?, ?)', 
                (user_id, weight) 
            ) 
            conn.commit() 
 
    def update_weight(self, user_id: int, weight: float) -> None:
        """Добавляет новую запись веса в историю.

        Args:
            user_id: Telegram ID пользователя
            weight: Новое значение веса в килограммах

        Returns:
            None
        """

        with self.get_connection() as conn:
            cursor = conn.cursor() 
            cursor.execute(
                'INSERT INTO weight_history (user_id, weight) VALUES (?, ?)', 
                (user_id, weight)
            ) 
            conn.commit()
 
    def get_user_stats(self, user_id: int) -> dict: 
        """Получает статистику пользователя.

        Args:
            user_id: Telegram ID пользователя

        Returns:
            dict: Словарь с данными пользователя:
                {
                    'age': int,
                    'height': int,
                    'initial_weight': float,
                    'current_weight': float
                }
            None: Если пользователь не найден
        """

        with self.get_connection() as conn:
            cursor = conn.cursor() 
            cursor.execute(''' 
                SELECT u.age, u.height, 
                       (SELECT weight FROM weight_history  
                        WHERE user_id = ?  
                        ORDER BY date ASC LIMIT 1) as initial_weight,
                       (SELECT weight FROM weight_history  
                        WHERE user_id = ?  
                        ORDER BY date DESC LIMIT 1) as current_weight 
                FROM users u 
                WHERE u.user_id = ? 
            ''', (user_id, user_id, user_id)) 
            
            result = cursor.fetchone() 
            
            if result: 
                return { 
                    'age': result[0],
                    'height': result[1], 
                    'initial_weight': result[2], 
                    'current_weight': result[3] 
                } 
            return None 
 
    def create_weight_graph(self, user_id: int) -> str:
        """Создает график изменения веса пользователя.

            Args:
                user_id: Telegram ID пользователя

            Returns:
                str: Имя файла с сохраненным графиком
                None: Если нет данных для построения графика
            """

        with self.get_connection() as conn:
            cursor = conn.cursor() 
            cursor.execute(
                'SELECT date, weight FROM weight_history WHERE user_id = ? ORDER BY date', 
                (user_id,)
            ) 
            results = cursor.fetchall() 

        if not results: 
            return None

        dates = [datetime.strptime(r[0], '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y') for r in results]
        weights = [r[1] for r in results] 

        plt.figure(figsize=(10, 6)) 
        plt.plot(dates, weights, 'b-o') 
        plt.title('График изменения веса') 
        plt.xlabel('Дата') 
        plt.ylabel('Вес (кг)') 
        plt.grid(True) 
        plt.xticks(rotation=45) 
        plt.tight_layout() 

        filename = f'weight_graph_{user_id}.png' 
        plt.savefig(filename) 
        plt.close() 
         
        return filename

    def get_weight_history(self, user_id: int):
        """Получает историю изменения веса пользователя.

        Args:
            user_id: Telegram ID пользователя

        Returns:
            list: Список кортежей (дата, вес)
        """

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT date, weight 
                FROM weight_history 
                WHERE user_id = ? 
                ORDER BY date
            ''', (user_id,))
            return cursor.fetchall()
        
    def delete_user_data(self, user_id: int) -> None:
        """Удаляет все данные пользователя из базы.

        Args:
            user_id: Telegram ID пользователя

        Returns:
            None

        Raises:
            sqlite3.Error: При ошибке удаления данных
        """

        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                # cначала удаляем записи из weight_history
                cursor.execute("DELETE FROM weight_history WHERE user_id = ?", (user_id,))
                # затем удаляем самого пользователя
                cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
                conn.commit()
            except sqlite3.Error as e:
                print(f"Error deleting user data: {e}")
                conn.rollback()
                raise

    def __enter__(self):
        return self

    def close(self):
        """Закрывает соединение с базой данных."""
        if hasattr(self, '_connection') and self._connection:
            self._connection.close()
            self._connection = None
