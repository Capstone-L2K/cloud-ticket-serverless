import json
import logging
import pymysql
from urllib.parse import urlparse

# 로그 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Database connection information
db_endpoint = 'your endpoint'
db_name = 'your db name'
db_username = 'your username'
db_password = 'your password'
db_port = 3306

def connect_to_db():
    try:
        conn = pymysql.connect(host=db_endpoint, user=db_username, password=db_password, database=db_name, port=db_port, connect_timeout=5)
    except Exception as e:
        logger.error("Unable to connect to the database")
        logger.error(e)
        return None
    return conn

def get_tickets(event_id):
    conn = connect_to_db()
    if conn is None:
        return None
    
    cursor = conn.cursor()
    
    query = "SELECT ticket_name, ticket_date, ticket_price, ticket_count FROM tb_ticket_type WHERE event_id = %s"
    value = (event_id,)
    
    try:
        cursor.execute(query, value)
        tickets = []
        for row in cursor.fetchall():
            ticket_name = row[0]
            ticket_date = row[1]
            ticket_price = row[2]
            ticket_count = row[3]
            
            ticket = {
                "ticket_name": ticket_name,
                "ticket_date": ticket_date.strftime("%Y-%m-%d"),  # 날짜 객체를 문자열로 변환
                "ticket_price": ticket_price,
                "ticket_count": ticket_count
            }
            tickets.append(ticket)
    except Exception as e:
        logger.error("Failed to get tickets")
        logger.error(e)
        return None
    
    cursor.close()
    conn.close()
    return tickets

# Lambda 함수
def lambda_handler(event, context):
    # URL에서 event id 추출
    path_parameters = event.get('pathParameters')
    if not path_parameters or 'eventid' not in path_parameters:
        logger.error("Invalid URL format")
        return {
            "statusCode": 400,
            "body": "Invalid URL format"
        }
    
    event_id = path_parameters.get('eventid')
    
    if not event_id.isdigit():
        logger.error("Invalid event ID")
        return {
            "statusCode": 400,
            "body": "Invalid event ID"
        }
    
    try:
        # 로그 메시지 생성
        logger.info(f"Fetching tickets for event ID: {event_id}")
        
        # 특정 이벤트의 티켓 정보 가져오기
        tickets = get_tickets(event_id)
        
        if tickets is None:
            # 로그 메시지 생성
            logger.error("Failed to get tickets")
            
            return {
                "statusCode": 500,
                "body": "Failed to get tickets"
            }
        
        # 로그 메시지 생성
        logger.info(f"Retrieved {len(tickets)} tickets")
        
        return tickets
        
    except Exception as e:
        # 로그 메시지 생성
        logger.error("An error occurred")
        logger.error(e)
        
        return {
            "statusCode": 500,
            "body": "An error occurred"
        }
