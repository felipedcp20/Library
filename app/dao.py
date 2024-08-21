import os
import mysql.connector
from mysql.connector import Error
from datetime import datetime

from app.models.database import User

DBACCESS_DB_USER = os.getenv("DBACCESS_DB_USER")
DBACCESS_DB_PASSWORD = os.getenv("DBACCESS_DB_PASSWORD")
DBACCESS_DB_HOST = os.getenv("DBACCESS_DB_HOST")
DBACCESS_DB_PORT = os.getenv("DBACCESS_DB_PORT")
DBACCESS_DB_SCHEMA = os.getenv("DBACCESS_DB_SCHEMA")



class Dao(object):
    def __init__(self):
        try:
            self.dbaas_conn = mysql.connector.connect(
                user=DBACCESS_DB_USER,
                password=DBACCESS_DB_PASSWORD,
                host=DBACCESS_DB_HOST,
                port=DBACCESS_DB_PORT,
                database=DBACCESS_DB_SCHEMA,
            )

            self.dbaas_conn._execute_query("use heroku_c5a6c07a5c79520;")
            

        except Error as e:
            print("No se pudo conectar a la base de datos DBAccess. Error: %s", str(e))
            raise e

    def close(self):
        self.dbaas_conn.close()

    def get_user(self, username: str):
        cursor = self.dbaas_conn.cursor(dictionary=True)
        query = """SELECT u.id, u.username, u.password, u.active, tu.role 
            FROM users u 
            JOIN type_users tu ON u.role_id = tu.id 
            WHERE u.username = %s;"""
        cursor.execute(query, (username,))
        user_data = cursor.fetchone()
        cursor.close()

        if user_data:
            return User(**user_data)
        else:
            return None

    def get_books(self):
        cursor = self.dbaas_conn.cursor(dictionary=True)
        query = "SELECT * FROM books"
        cursor.execute(query)
        books = cursor.fetchall()
        cursor.close()

        return books

    def register_loan(self, loan):
        cursor = self.dbaas_conn.cursor(dictionary=True)
        now = datetime.now()
        query = "INSERT INTO loans (id_book, id_user, loan_date) values (%s, %s, %s)"

        cursor.execute(query, (loan.book_id, loan.user_id, now))
        loan_id = cursor.lastrowid
        self.dbaas_conn.commit()
        cursor.close()
        return loan_id
        

    def create_book(self, book):
        cursor = self.dbaas_conn.cursor(dictionary=True)
        query = "INSERT INTO books (name, author, editorial) values (%s, %s, %s)"
        cursor.execute(query, (book.name, book.author, book.editorial))
        self.dbaas_conn.commit()
        cursor.close()

    def delete_book(self, book_id):
        cursor = self.dbaas_conn.cursor(dictionary=True)
        query = "DELETE FROM books WHERE id = %s"
        cursor.execute(query, (book_id,))
        self.dbaas_conn.commit()
        cursor.close()

        
    def update_quantity_books(self, book_id, quantity):
        cursor = self.dbaas_conn.cursor(dictionary=True)
        query = "UPDATE books SET quantity = %s WHERE id = %s"
        cursor.execute(query, (quantity, book_id))
        self.dbaas_conn.commit()
        cursor.close()

    def get_quantity_books(self, book_id):
        cursor = self.dbaas_conn.cursor(dictionary=True)
        query = "SELECT quantity FROM books WHERE id = %s"
        cursor.execute(query, (book_id,))
        quantity = cursor.fetchone()
        cursor.close()

        return quantity["quantity"]    
    

    def return_book(self, id_prestamo):
        cursor = self.dbaas_conn.cursor(dictionary=True)
        now = datetime.now()
        query = "UPDATE loans SET return_date = %s WHERE id = %s"
        cursor.execute(query, (now, id_prestamo))
        self.dbaas_conn.commit()

        # Retrieve the updated row data
        query = "SELECT * FROM loans WHERE id = %s"
        cursor.execute(query, (id_prestamo,))
        updated_loan = cursor.fetchone()
        cursor.close()

        return updated_loan["id_book"]

    def get_loans(self, all, user_id):
        cursor = self.dbaas_conn.cursor(dictionary=True)
        if all:
            query = "SELECT * FROM loans"
            cursor.execute(query)
        else:
            query = "SELECT * FROM loans WHERE id_user = %s"
            cursor.execute(query, (user_id,))
        loans = cursor.fetchall()
        cursor.close()

        return loans


    def create_user(self, user):
        cursor = self.dbaas_conn.cursor(dictionary=True)
        query = "INSERT INTO users (username, password, active, role_id) values (%s, %s, %s, %s)"
        cursor.execute(query, (user.username, user.password, user.active, user.role))
        self.dbaas_conn.commit()
        cursor.close()