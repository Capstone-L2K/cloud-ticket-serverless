import json
import pymysql

# 데이터베이스 연결 정보
db_endpoint = 'your endpoint'
db_name = 'your db name'
db_username = 'your username'
db_password = 'your password'
db_port = 3306

def connect_to_db():
    try:
        conn = pymysql.connect(host=db_endpoint, user=db_username, password=db_password, database=db_name, port=db_port, connect_timeout=5)
    except Exception as e:
        print("Unable to connect to the database")
        print(e)
        return None
    return conn

def check_event_exist(event_id):
    conn = connect_to_db()
    if conn is None:
        return False

    cursor = conn.cursor()

    query = "SELECT COUNT(*) FROM tb_event WHERE event_id = %s"
    value = (event_id,)

    try:
        cursor.execute(query, value)
        count = cursor.fetchone()[0]
        if count == 0:
            return False
    except Exception as e:
        print("Failed to check event existence")
        print(e)
        return False

    cursor.close()
    conn.close()
    return True
    
def create_ticket(event_id, ticket_name, ticket_date, ticket_price, ticket_count):
    conn = connect_to_db()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    
    query = "INSERT INTO tb_ticket_type (event_id, ticket_name, ticket_date, ticket_price, ticket_count) VALUES (%s, %s, %s, %s, %s)"
    values = (event_id, ticket_name, ticket_date, ticket_price, ticket_count)
    
    try:
        cursor.execute(query, values)
        conn.commit()
    except Exception as e:
        print("Failed to create ticket")
        print(e)
        conn.rollback()
        return False
    
    cursor.close()
    conn.close()
    return True

# Lambda 함수
def lambda_handler(event, context):
    # 요청 본문에서 티켓 정보 추출
    try:
        event_id = event["eventid"]
        ticket_name = event["ticketname"]
        ticket_date = event["ticketdate"]
        ticket_price = event["ticketprice"]
        ticket_count = event["ticketcount"]
    except KeyError:
        return {
            "statusCode": 400,
            "body": "Invalid ticket information format"
        }
    
    if event_id is None:
        return {
            "statusCode": 400,
            "body": "Missing eventid parameter"
        }
    
    # 이벤트 존재 여부 확인
    if not check_event_exist(event_id):
        return {
            "statusCode": 400,
            "body": "Event does not exist"
        }
    
    if ticket_name is None or ticket_date is None or ticket_price is None or ticket_count is None:
        return {
            "statusCode": 400,
            "body": "Missing ticket information"
        }
    
    # 티켓 생성
    success = create_ticket(event_id, ticket_name, ticket_date, ticket_price, ticket_count)
    
    if not success:
        return {
            "statusCode": 500,
            "body": "Failed to create ticket"
        }
    
    return {
        "statusCode": 200,
        "body": "Ticket created successfully"
    }
