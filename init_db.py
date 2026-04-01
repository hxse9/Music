import sqlite3
import os

DB_FILENAME = 'music.db'
SCHEMA_FILENAME = 'schema.sql'

def init_db():
    print("Database 초기화 스크립트를 시작합니다...")
    
    # DB 연결 (파일이 존재하지 않으면 자동으로 새 파일로 생성됨)
    connection = sqlite3.connect(DB_FILENAME)
    
    # schema.sql 파일 읽어오기
    try:
        with open(SCHEMA_FILENAME, 'r', encoding='utf-8') as f:
            schema_script = f.read()
    except FileNotFoundError:
        print(f"오류: {SCHEMA_FILENAME} 파일을 찾을 수 없습니다.")
        return

    # 읽어온 스크립트를 Database 서버(SQLite)에 실행
    try:
        cursor = connection.cursor()
        cursor.executescript(schema_script)
        connection.commit()
        print(f"성공적으로 {DB_FILENAME} 데이터베이스 및 테이블 구조가 생성되었습니다!")
    except Exception as e:
        print(f"데이터베이스 스키마 구성 중 오류 발생: {e}")
    finally:
        connection.close()
        
if __name__ == '__main__':
    init_db()
