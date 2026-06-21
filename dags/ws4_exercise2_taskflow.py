import datetime

from airflow.sdk import dag, task
from airflow.providers.standard.operators.bash import BashOperator
import pendulum

default_args = {
    'owner': 'datath',
}


@task()
def print_hello():
    """
    Print Hello World!
    """
    print("Hello World!")
    

@task()
def print_date():
    """
    Print current date
    ref: https://www.w3schools.com/python/python_datetime.asp
    """
    print(datetime.datetime.now())


@dag(default_args=default_args, schedule="@once", start_date=pendulum.today("UTC").subtract(days=1), tags=['exercise'])
def exercise2_taskflow_dag():

    t1 = print_hello()
    t2 = print_date()

    # Exercise2: Fan-out Pipeline
    # ใน exercise นี้จะได้รู้จักกับการแยก pipeline ออกเพื่อให้ทำงานแบบ parallel พร้อมกันได้
    # ซึ่ง TaskFlow แบบใหม่ ก็สามารถใช้งานร่วมกับการเขียน Operator แบบเดิมได้เหมือนกัน

    # TODO: สร้าง task จาก BashOperator ด้านล่าง
    # ใช้งาน gsutil ls เพื่อดูไฟล์ใน bucket
    t3 = BashOperator(
        task_id='gsutil_ls',
        bash_command='gsutil ls',
    )
    
    # TODO: สร้าง dependency ให้ fan-out โดยที่ t1 ก่อน แล้วค่อยทำ t2, t3 พร้อม ๆ กัน
    t1 >> t2 >> t3

exercise2_dag = exercise2_taskflow_dag()
