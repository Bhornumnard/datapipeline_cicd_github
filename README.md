# R2DE3.0 Workshops

ไฟล์เริ่มต้นสำหรับ Workshop ในคอร์ส Road to Data Engineer

(ไฟล์เฉลย สามารถดูได้จากในระบบเรียน)

## โครงสร้างโปรเจกต์

```
├── dags/                  # DAG files (mount เข้า Airflow โดยตรง)
├── workshop/              # ไฟล์เริ่มต้นสำหรับ Workshop 5 (คัดลอกไป dags/ เมื่อทำแบบฝึกหัด)
├── docker/airflow/        # config สำหรับ local Airflow (entrypoint, plugins, data)
├── docker-compose.yml     # รัน Airflow + PostgreSQL บนเครื่อง
└── .github/workflows/     # CI/CD deploy DAGs ไป GCS
```

## Local Development (Docker Compose)

รัน Airflow บนเครื่องให้ใกล้เคียงกับ **Google Cloud Composer 3 / Airflow 3.1.7**

### สิ่งที่ต้องมี

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (ต้องเปิดอยู่)
- [gcloud CLI](https://cloud.google.com/sdk/docs/install) (ใช้ดึง Composer image)

### ตั้งค่าครั้งแรก

1. **Login gcloud และตั้งค่า Docker registry**

   ```bash
   gcloud auth login
   gcloud auth application-default login
   gcloud auth configure-docker us-docker.pkg.dev
   ```

2. **สร้างไฟล์ `.env`**

   ```bash
   cp .env.example .env
   ```

   แก้ `GCP_PROJECT_ID` เป็น GCP project จริงของคุณ (จำเป็นสำหรับ DAG ที่เรียก GCP services เช่น GCS, BigQuery)

   สำหรับ DAG ที่ใช้ AI (`dag1_sample_ai.py`, `dag2_ai_spam_filter.py`) ให้ใส่ `GOOGLE_AI_API_KEY` จาก [Google AI Studio](https://aistudio.google.com/apikey) — คีย์นี้จะถูก map เป็น Airflow connection `google_ai` อัตโนมัติผ่าน `docker-compose.yml` (ไม่ต้องสร้าง connection ใน UI)

### รัน Airflow

```bash
docker compose up
```

ครั้งแรกอาจใช้เวลาสักครู่ ระบบจะ migrate database และ start scheduler, triggerer, dag-processor

เปิด UI ที่ **http://localhost:8080** (ไม่ต้อง login — เปิด admin mode สำหรับ local dev)

### หยุด / ลบ container

```bash
# หยุดชั่วคราว
docker compose down

# ลบ container และ volume (reset database)
docker compose down -v
```

### ตรวจสอบ DAG ก่อน push

```bash
python -m py_compile dags/*.py
```

คำสั่งเดียวกับที่ CI ใช้ใน `.github/workflows/deploy-dags.yml`

### AI / LLM DAGs (`@task.llm`)

DAG ที่ใช้ Gemini ผ่าน `@task.llm`:

| DAG | ไฟล์ | คำอธิบาย |
|-----|------|----------|
| `ai_test` | `dags/dag1_sample_ai.py` | ทดสอบเรียก Gemini แบบง่าย |
| `ai_spam_filter` | `dags/dag2_ai_spam_filter.py` | สแกนรีวิว spam ด้วย LLM |

**สิ่งที่ต้องตั้ง:**

1. ใส่ `GOOGLE_AI_API_KEY` ใน `.env` (ดู `.env.example`)
2. Provider `apache-airflow-providers-common-ai` อยู่ใน `docker/airflow/requirements.txt` — ติดตั้งอัตโนมัติตอน `docker compose up` ครั้งแรก
3. วาง `reviews.csv` ใน `docker/airflow/data/` สำหรับ DAG `ai_spam_filter` (อ่านจาก `/home/airflow/gcs/data/reviews.csv`)

**หมายเหตุ:** หลังแก้ `.env` หรือ `requirements.txt` ต้อง `docker compose down` แล้ว `up` ใหม่ — แก้ไฟล์ใน `dags/` หรือ `docker/airflow/data/` ไม่ต้อง restart

### ดู log / รันคำสั่งใน container

```bash
# ดู log
docker compose logs -f airflow

# รัน Airflow CLI
docker compose exec airflow bash -c 'airflow dags list'
```

### ตัวแปร environment (`.env`)

| ตัวแปร | ค่าเริ่มต้น | คำอธิบาย |
|--------|------------|----------|
| `GCP_PROJECT_ID` | `local-dev` | GCP project สำหรับ connection `google_cloud_default` |
| `GOOGLE_AI_API_KEY` | _(ว่าง)_ | API key จาก Google AI Studio — map เป็น connection `google_ai` สำหรับ `@task.llm` (ดู `AIRFLOW_CONN_GOOGLE_AI` ใน `docker-compose.yml`) |
| `AIRFLOW_PORT` | `8080` | port ของ Airflow UI |
| `POSTGRES_PORT` | `25432` | port ของ PostgreSQL บน host |
| `GCLOUD_CONFIG_PATH` | `~/.config/gcloud` | path ไปยัง gcloud credentials (mount เข้า container) |

### โฟลเดอร์ที่ mount เข้า container

| Host path | ใน container | ใช้ทำอะไร |
|-----------|--------------|-----------|
| `./dags` | `/home/airflow/gcs/dags` | DAG files |
| `./docker/airflow/plugins` | `/home/airflow/gcs/plugins` | Airflow plugins |
| `./docker/airflow/data` | `/home/airflow/gcs/data` | ไฟล์ data ชั่วคราว (parquet, `reviews.csv` สำหรับ AI DAG) |
| `./docker/airflow/requirements.txt` | `/home/airflow/composer_requirements.txt` | pip packages เพิ่มเติม (เช่น `common-ai` provider) |
| `~/.config/gcloud` | `/home/airflow/.config/gcloud` | GCP credentials |

### Troubleshooting

| ปัญหา | วิธีแก้ |
|-------|---------|
| `Error response from daemon: pull access denied` | รัน `gcloud auth configure-docker us-docker.pkg.dev` แล้ว login ใหม่ |
| DAG ไม่ขึ้นใน UI | รอ ~10 วินาที (dag-processor refresh) หรือดู log: `docker compose logs airflow` |
| DAG import error | ตรวจ syntax ด้วย `python -m py_compile dags/*.py` |
| Port 8080 ถูกใช้อยู่ | เปลี่ยน `AIRFLOW_PORT` ใน `.env` แล้ว `docker compose up` ใหม่ |
| `task decorator 'llm' not found` | ตรวจว่า `docker/airflow/requirements.txt` มี `apache-airflow-providers-common-ai` แล้ว restart container |
| LLM task auth error | ตรวจ `GOOGLE_AI_API_KEY` ใน `.env` แล้ว restart container |
| `reviews.csv` not found (ai_spam_filter) | วางไฟล์ที่ `docker/airflow/data/reviews.csv` |

## CI/CD

เมื่อ push ไป branch `main` และมีการแก้ไขใน `dags/` workflow จะ validate syntax แล้ว sync ไป GCS bucket ของ Composer โดยอัตโนมัติ

ดูรายละเอียด secrets ที่ต้องตั้งใน `.github/workflows/deploy-dags.yml`
