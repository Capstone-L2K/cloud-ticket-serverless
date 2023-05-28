import json
import pymysql

# Database connection information
db_endpoint = 'your endpoint'
db_name = 'your db name'
db_username = 'your username'
db_password = 'your password'
db_port = 3306

def lambda_handler(event, context):
    # Extract event_id from the query string parameters
    query_string_parameters = event.get('queryStringParameters')
    if not query_string_parameters or 'eventid' not in query_string_parameters:
        return {
            "statusCode": 400,
            "body": "Invalid URL format"
        }

    event_id = query_string_parameters.get('eventid')

    # Connect to the database
    conn = connect_to_db()
    if not conn:
        return {
            'statusCode': 500,
            'body': 'Failed to connect to the database'
        }

    try:
        # Update the event_state in the tb_event table
        with conn.cursor() as cursor:
            sql = "UPDATE tb_event SET event_state = 'close' WHERE event_id = %s"
            cursor.execute(sql, event_id)
        conn.commit()

        return {
            'statusCode': 200,
            'body': 'Event state(close) updated successfully'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': 'Failed to update event state('
        }
    finally:
        # Close the database connection
        conn.close()

def connect_to_db():
    try:
        conn = pymysql.connect(
            host=db_endpoint,
            user=db_username,
            password=db_password,
            database=db_name,
            port=db_port,
            connect_timeout=5
        )
    except Exception as e:
        print("Unable to connect to the database")
        print(e)
        return None
    return conn
