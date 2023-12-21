#!/bin/bash

until PGPASSWORD=${POSTGRES_PASSWORD} psql -h ${POSTGRES_HOST} -p 5432 -U postgres -c "\q"; do
  >&2 echo "Postgres is not available, sleep..."
  sleep 1
done

>&2 echo "Postgres is up"

pwd
ls


eval "$(conda shell.bash hook)"
conda activate venv
conda list

cd /home/app/backend/
python3 manage.py makemigrations myapp
python3 manage.py migrate

COUNT=$(PGPASSWORD=${POSTGRES_PASSWORD} psql -h ${POSTGRES_HOST} -p 5432 -U postgres -d ${POSTGRES_DB_NAME} -tAc 'select count(*) from auth_user;')
if [ "$COUNT" -gt "0" ] ; then
  >&2 echo "Superuser Exist!!! This is hotfix mode"
  >&2 echo "No need to create superuser"
else
  >&2 echo "Superuser NOT Exist!!! This is fresh install mode"
  cd /home/app/scripts/
  ./create_superuser.sh
fi


cd /home/app/
concurrently "cd /home/app/frontend && npm run start" "cd /home/app/backend && python3 manage.py runserver 0.0.0.0:8000"

