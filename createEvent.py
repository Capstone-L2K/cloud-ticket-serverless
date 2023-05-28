import json
import pymysql

# 데이터베이스 연결 정보
db_endpoint = 'your endpoint'
db_name = 'your db name'
db_username = 'your user name'
db_password = 'your password'
db_port = 3306

# 상수
DEFAULT_BANNER = 'your s3 banner'
DEFAULT_HOST_ID = 'kimewha'

def lambda_handler(event, context):
    conn = None  # conn 변수를 None으로 초기화

    try:
        # JSON 값 파싱
        if 'body' in event:
            request_body = json.loads(event['body'])
        else:
            request_body = event

        # 필수 필드 확인
        required_fields = ['event_name', 'category_id', 'event_content', 'event_date']
        missing_values = [field for field in required_fields if field not in request_body]

        if missing_values:
            missing_fields = ', '.join(missing_values)
            error_message = f"The following values are missing: {missing_fields}"
            return {'statusCode': 400, 'body': error_message}

        # DB 연결
        conn = pymysql.connect(
            host=db_endpoint,
            user=db_username,
            password=db_password,
            db=db_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        # 행사명 중복 체크
        event_name = request_body['event_name']
        if is_event_name_duplicate(conn, event_name):
            error_message = "The event name already exists"
            return {'statusCode': 400, 'body': error_message}

        # DB 입력
        event_id = insert_event(conn, request_body)
        insert_host(conn, event_id)
        insert_qrcode(conn, request_body) #추가한 부분

        # 커밋 후 성공 응답
        conn.commit()
        return {'statusCode': 200, 'body': 'Event registered successfully'}

    except Exception as e:
        # 오류 발생 시 롤백 후 오류 응답
        if conn:
            conn.rollback()
        return {'statusCode': 500, 'body': f'Error registering event: {str(e)}'}

    finally:
        # 연결 종료
        if conn:
            conn.close()

def is_event_name_duplicate(conn, event_name):
    with conn.cursor() as cursor:
        select_sql = "SELECT COUNT(*) AS count FROM tb_event WHERE event_name = %s"
        cursor.execute(select_sql, (event_name,))
        result = cursor.fetchone()
        return result['count'] > 0

def insert_event(conn, request_body):
    with conn.cursor() as cursor:
        insert_sql = "INSERT INTO tb_event (event_name, category_id, banner, event_content, event_date, event_loc) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_sql, (
            request_body['event_name'],
            request_body.get('category_id'),
            request_body.get('banner', DEFAULT_BANNER),
            request_body.get('event_content'),
            request_body.get('event_date'),
            request_body.get('event_loc')
        ))

        cursor.execute("SELECT LAST_INSERT_ID()")
        return cursor.fetchone()['LAST_INSERT_ID()']

def insert_host(conn, event_id):
    with conn.cursor() as cursor:
        insert_sql = "INSERT INTO tb_host (event_id, user_id) VALUES (%s, %s)"
        cursor.execute(insert_sql, (event_id, DEFAULT_HOST_ID))
        
# 추가 함수
def insert_qrcode(conn, request_body):
    event_name = request_body['event_name']
    category_id = request_body['category_id']
    event_date = request_body['event_date']

    qr_data = {
        'Event Name': event_name,
        'Category ID': category_id,
        'Event Date': event_date
    }

    qr_data_json = json.dumps(qr_data)

    with conn.cursor() as cursor:
        update_sql = "UPDATE tb_event SET qr_data = %s WHERE event_name = %s"
        cursor.execute(update_sql, (qr_data_json, event_name))
