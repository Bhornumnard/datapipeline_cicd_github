#!/bin/bash

# Adapted from Google Cloud composer-local-dev for local docker-compose usage.
# https://github.com/GoogleCloudPlatform/composer-local-dev

set -xe

FAST_API_DIR=/opt/python3.11/lib/python3.11/site-packages/airflow/api_fastapi/

run_as_user=/home/airflow/run_as_user.sh

get_airflow_version() {
  airflow_version=$(${run_as_user} airflow version 2>/dev/null | grep -oE '[0-9]\.[0-9]+\.[0-9]+' | head -1)
  original_ifs="$IFS"
  IFS='.'
  set -- $airflow_version
  major="$1"
  minor="$2"
  patch="$3"
  IFS="$original_ifs"
  echo "$major" "$minor" "$patch"
}

install_airflow_deps() {
  if [ -s composer_requirements.txt ]; then
    version=$(${run_as_user} airflow version | grep -oE '[0-9]\.[0-9]+\.[0-9]+\+composer')
    cp composer_requirements.txt requirements_with_airflow_version.txt
    echo "" >> requirements_with_airflow_version.txt
    echo "apache-airflow==${version}" >> requirements_with_airflow_version.txt
    sudo -E pip3 install -r requirements_with_airflow_version.txt
    sudo pip3 check
  fi
}

init_airflow() {

  $run_as_user mkdir -p ${AIRFLOW__CORE__DAGS_FOLDER}
  $run_as_user mkdir -p ${AIRFLOW__CORE__PLUGINS_FOLDER}
  $run_as_user mkdir -p ${AIRFLOW__CORE__DATA_FOLDER}

  if [ -f /var/local/setup_python_command.sh ]; then
      $run_as_user /var/local/setup_python_command.sh
  fi

  install_airflow_deps

  airflow_version=($(get_airflow_version))
  major="${airflow_version[0]}"
  minor="${airflow_version[1]}"

  if [ "$major" -eq "3" ]; then
    $run_as_user cp -r /etc/airflow/config /home/airflow/airflow/config
  else
    if ! grep -Fxq "AUTH_ROLE_PUBLIC = 'Admin'" /home/airflow/airflow/webserver_config.py; then
      $run_as_user sh -c "echo \"AUTH_ROLE_PUBLIC = 'Admin'\" >> /home/airflow/airflow/webserver_config.py"
    fi
  fi

  if [ "$major" -eq "2" ] && [ "$minor" -lt "7" ]; then
    $run_as_user airflow db init
  else
    $run_as_user airflow db migrate
  fi
}

create_user() {
  local user_name="$1"
  local user_id="$2"

  local old_user_name
  old_user_name="$(whoami)"
  local old_user_id
  old_user_id="$(id -u)"

  echo "Adding user ${user_name}(${user_id})"
  sudo useradd -m -r -g airflow -G airflow --home-dir /home/airflow \
    -u "${user_id}" -o "${user_name}"

  echo "Updating the owner of the dirs owned by ${old_user_name}(${old_user_id}) to ${user_name}(${user_id})"
  sudo find /home -user "${old_user_id}" -exec chown -h "${user_name}" {} \;
  sudo find /var -user "${old_user_id}" -exec chown -h "${user_name}" {} \;
  if [ -d "$FAST_API_DIR" ]; then
  sudo find $FAST_API_DIR -user "${old_user_id}" \
    -exec chown -h -R "${user_name}" {} \;
  fi
}

main() {
  AIRFLOW_HOME_DIR="${AIRFLOW_HOME:-/home/airflow/airflow}"

  sudo mkdir -p "${AIRFLOW_HOME_DIR}"
  sudo chown airflow:airflow "${AIRFLOW_HOME_DIR}"

  if [ -w "${run_as_user}" ]; then
    sudo chmod +x "${run_as_user}"
  fi

  if [ -d "$FAST_API_DIR" ]; then
    sudo chown -R airflow:airflow "$FAST_API_DIR"
  fi

  if [ "${COMPOSER_CONTAINER_RUN_AS_HOST_USER}" = "True" ]; then
    create_user "${COMPOSER_HOST_USER_NAME}" "${COMPOSER_HOST_USER_ID}" || true
    echo "Running Airflow as user ${COMPOSER_HOST_USER_NAME}(${COMPOSER_HOST_USER_ID})"
  else
    echo "Running Airflow as user airflow(999)"
  fi

  airflow_version=($(get_airflow_version))
  major="${airflow_version[0]}"

  init_airflow

  $run_as_user airflow scheduler &
  $run_as_user airflow triggerer &

  if [[ "$major" -eq "3" || ${AIRFLOW__SCHEDULER__STANDALONE_DAG_PROCESSOR} = "True" ]]; then
    $run_as_user airflow dag-processor &
  fi

  if [ "$major" -eq "3" ]; then
    $run_as_user airflow api-server --apps execution -p 8081 --workers 1 &
    exec $run_as_user airflow api-server --apps core
  else
    exec $run_as_user airflow webserver
  fi
}

main "$@"
