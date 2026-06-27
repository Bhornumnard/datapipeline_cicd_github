from datetime import datetime

from airflow import DAG
from airflow.sdk import task

with DAG(
    dag_id="ai_test",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["ai", "gemini", "education"],
) as dag:

    # ส่งคำถามให้ LLM
    @task.llm(
        model_id="google:gemini-3.1-flash-lite",
        llm_conn_id="google_ai",
    )
    def ask_gemini(question: str):
        return question

    @task
    def print_answer(answer: str):
        print("=" * 40)
        print(f"GEMINI ANSWER:\n{answer}")
        print("=" * 40)

    # Trigger the tasks
    response = ask_gemini(question="Apache Airflow คืออะไร สรุป 1 ประโยค")
    print_answer(answer=response)
