import boto3
import json
import pymysql

# 데이터베이스 연결 정보
db_host = 'your host'
db_name = 'your db name'
db_user = 'your user name'
db_password = 'your pwd'
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
    
def get_host_event(hostid):
    conn = connect_to_db()
    if conn is None:
        return None
    cursor = conn.cursor()
    
    query = "SELECT tb_event.event_id, event_name, banner, event_date, event_loc FROM tb_event, tb_host WHERE tb_host.user_id = %s and tb_host.event_id = tb_event.event_id"
    cursor.execute(query, (hostid))
    
    result = cursor.fetchall()
    
    # date 타입을 문자열로 변환하고 딕셔너리 형태로 변경
    result = [{"event_id": id, "event_name": name, "banner": banner, "event_date": date.strftime('%Y-%m-%d'), "event_loc": loc} for (id, name, banner, date, loc) in result]
    cursor.close()
    conn.close()
    return result
    
    
def get_all_events():
    conn = connect_to_db()
    if conn is None:
        return None
    cursor = conn.cursor()
    
    query = "SELECT event_id, event_name, banner, event_date, event_loc FROM tb_event"
    cursor.execute(query)
    
    result = cursor.fetchall()
    
    # date 타입을 문자열로 변환하고 딕셔너리 형태로 변경
    result = [{"event_id": id, "event_name": name, "banner": banner, "event_date": date.strftime('%Y-%m-%d'), "event_loc": loc} for (id, name, banner, date, loc) in result]
    cursor.close()
    conn.close()
    return result
    

# Lambda 함수
def lambda_handler(event, context):
    
    hostid = event["queryStringParameters"].get("hostid")
    if hostid:
        events = get_host_event(hostid)
    else:
        events = get_all_events()
    
    return events
