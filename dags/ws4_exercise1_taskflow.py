import datetime

from airflow.decorators import dag, task
import pendulum

default_args = {
    'owner': 'datath',
}

# Exercise1: Simple Pipeline - Hello World Airflow!
# รู้จักกับ Task Flow API ที่มาใหม่ใน Airflow 2.0
# เป็นวิธีการเขียน DAG แบบใหม่ ที่อ่านง่าย และทันสมัยขึ้น เหมาะสำหรับโค้ดที่เป็น PythonOperator ทั้งหมด
# ศึกษา tutorial ฉบับเต็มได้ที่นี่ https://airflow.apache.org/docs/apache-airflow/stable/tutorial_taskflow_api.html

@task()
def print_hello():
    """
    Print Hello World!
    """
    print("== Start of Exercise 1 ʕ•́ᴥ•̀ʔっ♡ ==")
    print("Hello World!")
    print("== End of Exercise 1 ʕ•́ᴥ•̀ʔっ♡ ==")
    

@task()
def print_date():
    """
    Print current date
    ref: https://www.w3schools.com/python/python_datetime.asp
    """
    # TODO: print เวลาปัจจุบัน
    print("== Start of Exercise 2 ʕ•́ᴥ•̀ʔっ♡ ==")
    print(datetime.datetime.now())
    print("== End of Exercise 2 ʕ•́ᴥ•̀ʔっ♡ ==")


@dag(default_args=default_args, schedule_interval="@once", start_date=pendulum.today("UTC").subtract(days=1), tags=['exercise'])
def exercise1_taskflow_dag():

    t1 = print_hello()
    t2 = print_date()

    # TODO: เขียน dependency ให้ทำ t1 ก่อน t2
    t1 >> t2

exercise1_dag = exercise1_taskflow_dag()
