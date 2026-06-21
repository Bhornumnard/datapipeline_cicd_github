from airflow.sdk import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
import pendulum


with DAG(
    "exercise3_fan_in_dag",
    start_date=pendulum.today("UTC").subtract(days=1),
    schedule="@once",
    catchup=False,
    tags=["exercise"]
) as dag:

    # Exercise3: Fan-in Pipeline
    # ใน exercise นี้จะได้รู้จักการเขียน task ใน pipeline ขั้นตอนเยอะขึ้น
    # ใช้ EmptyOperator เป็น task จำลอง
    # create  6 dummy operators for task 0 to task 5
    t0 = EmptyOperator(task_id="task_0")
    t1 = EmptyOperator(task_id="task_1")
    t2 = EmptyOperator(task_id="task_2")
    t3 = EmptyOperator(task_id="task_3")
    t4 = EmptyOperator(task_id="task_4")
    t5 = EmptyOperator(task_id="task_5")
    t6 = EmptyOperator(task_id="task_6")

    [t0, t1, t2] >> t4
    [t3, t4, t5] >> t6
