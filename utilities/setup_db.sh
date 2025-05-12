source .env
mysql -u ${DB_USER} -p${DB_PASSWORD} -h ${DB_HOST} -P ${DB_PORT} -D ${DB_NAME} -e "source ./schema.sql;"
