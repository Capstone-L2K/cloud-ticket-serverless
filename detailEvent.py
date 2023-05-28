import boto3
import json
import pymysql
from datetime import datetime

# 데이터베이스 연결 정보
db_host = 'your host'
db_name = 'your db name'
db_user = 'your username'
db_password = 'your password'
db_port = 3306

# RDS 연결
def connect_to_db():
    try:
        conn = pymysql.connect(host=db_host, user=db_user, passwd=db_password, db=db_name, connect_timeout=5)
    except Exception as e:
        print("Unable to connect to the database")
        print(e)
        return None
    return conn
    
def get_event_detail(eventid):
    conn = connect_to_db()
    if conn is None:
        return None
    cursor = conn.cursor()
    
    query = "SELECT event_name, category_id, banner, event_content, event_content_image, event_date, event_loc, event_lat, event_long FROM tb_event WHERE event_id = %s"
    cursor.execute(query, (eventid,))
    
    result = cursor.fetchone()
    
    # date 타입을 문자열로 변환하고 딕셔너리 형태로 변경
    result = {
        "event_name": result[0],
        "category_id": result[1],
        "banner": result[2],
        "event_content": result[3],
        "event_content_imgage": result[4],
        "event_date": result[5].strftime('%Y-%m-%d %H:%M:%S'),
        "event_loc": result[6],
        "event_lat": result[7],
        "event_long": result[8]
    }
    
    # 현재 시각과 비교하여 이벤트 진행 상태 확인
    current_time = datetime.now()
    event_time = datetime.strptime(result['event_date'], '%Y-%m-%d %H:%M:%S')
    if current_time < event_time:
        result['event_ing'] = "진행 중"
    else:
        result['event_ing'] = "종료"
    
    # tb_ticket_type 테이블에서 event_id에 해당하는 ticket_id 검색
    query = "SELECT ticket_id FROM tb_ticket_type WHERE event_id = %s"
    cursor.execute(query, (eventid,))
    
    ticket_ids = [row[0] for row in cursor.fetchall()]
    
    # tb_ticket_detail에서 ticket_id에 해당하는 row 수 확인
    if ticket_ids:
        query = "SELECT COUNT(*) FROM tb_ticket_detail WHERE ticket_id IN ({})".format(','.join(['%s'] * len(ticket_ids)))
        cursor.execute(query, tuple(ticket_ids))
        
        event_joinnum = cursor.fetchone()[0]
        result['event_joinnum'] = event_joinnum
    else:
        result['event_joinnum'] = 0
    
    # tb_ticket_type에서 event_id에 해당하는 ticket_id의 최댓값 검색
    query = "SELECT MAX(ticket_price) FROM tb_ticket_type WHERE event_id = %s"
    cursor.execute(query, (eventid,))
    
    ticket_max_price = cursor.fetchone()[0]
    result['ticket_max_price'] = ticket_max_price
    
    cursor.close()
    conn.close()
    return result
    

# Lambda 함수
def lambda_handler(event, context):
    
    eventid = event["queryStringParameters"].get("eventid")
    events = get_event_detail(eventid)

    return events
