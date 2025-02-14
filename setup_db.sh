DB_FILE="test_db/db.sqlite3"

[ -e "$DB_FILE" ] && rm "$DB_FILE"
python src/manage.py migrate
python src/manage.py loaddata user
python src/manage.py loaddata organization
python src/manage.py loaddata shift
