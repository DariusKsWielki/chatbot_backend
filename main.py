from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import Error
from datetime import datetime

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    action = req['queryResult']['action']

    if action == 'checkAvailability':
        return check_availability(req)
    elif action == 'makeReservation':
        return make_reservation(req)
    else:
        return jsonify({'fulfillmentText': 'Invalid action.'})

def check_availability(req):
    # Pobierz parametry zapytania
    date = req['queryResult']['parameters']['date']
    time = req['queryResult']['parameters']['time']

    try:
        # Nawiąż połączenie z bazą danych
        connection = psycopg2.connect(
            host='localhost',
            database='reservations',
            user='postgres',
            password='Daro1000#'
        )

        # Wykonaj zapytanie w celu sprawdzenia dostępności
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM slots WHERE date = %s AND time = %s", (date, time))
        rows = cursor.fetchall()

        if len(rows) > 0:
            fulfillment_text = 'Slot available on ' + date + ' at ' + time
        else:
            fulfillment_text = 'Slot not available on ' + date + ' at ' + time

        cursor.close()

    except Error as e:
        print("Error while connecting to PostgreSQL:", e)

    finally:
        # Zamknij połączenie z bazą danych
        if connection:
            connection.close()

    return jsonify({'fulfillmentText': fulfillment_text})

def make_reservation(req):
    # Pobierz parametry zapytania
    date = req['queryResult']['parameters']['date']
    time = req['queryResult']['parameters']['time']
    customer_name = req['queryResult']['parameters']['customer_name']

    try:
        # Nawiąż połączenie z bazą danych
        connection = psycopg2.connect(
            host='localhost',
            database='reservations',
            user='postgres',
            password='Daro1000#'
        )

        # Wykonaj zapytanie w celu zapisania rezerwacji
        cursor = connection.cursor()
        cursor.execute("INSERT INTO reservations (date, time, customer_name) VALUES (%s, %s, %s)", (date, time, customer_name))
        connection.commit()

        fulfillment_text = 'Reservation made for ' + customer_name + ' on ' + date + ' at ' + time

        cursor.close()

    except Error as e:
        print("Error while connecting to PostgreSQL:", e)

    finally:
        # Zamknij połączenie z bazą danych
        if connection:
            connection.close()

    return jsonify({'fulfillmentText': fulfillment_text})

if __name__ == '__main__':
    app.run()


