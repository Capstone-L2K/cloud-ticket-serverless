import boto3
import json
import pymysql

# 데이터베이스 연결 정보
db_host = 'your host'
db_name = 'your db name'
db_user = 'your user name'
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
    
def get_user_events(user_id):
    conn = connect_to_db()
    if conn is None:
        return None
    cursor = conn.cursor()
    
    query = "SELECT event_id FROM tb_ticket_detail, tb_ticket_type WHERE user_id = %s and tb_ticket_detail.ticket_id = tb_ticket_type.ticket_id"
    cursor.execute(query, (user_id,))
    
    events = []
    for (event_id,) in cursor.fetchall():
        query = "SELECT event_name, event_date, event_loc FROM tb_event WHERE event_id = %s"
        cursor.execute(query, (event_id,))
        result = cursor.fetchone()
        if result:
            name, date, loc = result
            event = {"event_id": event_id, "event_name": name, "event_date": date.strftime('%Y-%m-%d'), "event_loc": loc}
            events.append(event)
            
    cursor.close()
    conn.close()
    return events
    

# Lambda 함수
def lambda_handler(event, context):
    
    user_id = event["queryStringParameters"].get("joinid")
    if user_id:
        events = get_user_events(user_id)
    else:
        events = []
    
    return events
