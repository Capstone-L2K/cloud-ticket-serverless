import json
import pymysql

# 데이터베이스 연결 정보
db_endpoint = 'your endpoint'
db_name = 'your database'
db_username = 'your username'
db_password = 'your password'
db_port = 3306


def lambda_handler(event, context):
    conn = None

    try:
        if 'body' in event:
            request_body = json.loads(event['body'])
        else:
            request_body = event

        if 'event_id' not in request_body:
            error_message = "event_id is missing"
            return {'statusCode': 400, 'body': error_message}
        
        event_id = request_body['event_id']

        # DB 연결
        conn = pymysql.connect(
            host=db_endpoint,
            user=db_username,
            password=db_password,
            db=db_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        # qr_data 조회
        qr_data = get_qr_data(conn, event_id)

        if qr_data is None:
            error_message = "No qr_data found for the given event_id"
            return {'statusCode': 404, 'body': error_message}

        return {'statusCode': 200, 'body': qr_data}

    except Exception as e:
        return {'statusCode': 500, 'body': f'Error retrieving qr_data: {str(e)}'}

    finally:
        if conn:
            conn.close()

def get_qr_data(conn, event_id):
    with conn.cursor() as cursor:
        select_sql = "SELECT qr_data FROM tb_event WHERE event_id = %s"
        cursor.execute(select_sql, (event_id,))
        result = cursor.fetchone()
        if result:
            return result['qr_data']
        else:
            return None
