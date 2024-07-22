#!/bin/bash
#Make migrations folder
#echo "Make migrations folder"
#flask db init || true
#echo "Done - 1"
#
#echo "Make migrations"
#flask db migrate -m "1"
#echo "Done - 2"
#
#echo "Apply migrations"
#flask db upgrade
#echo "Done - 3"

#echo "Make migrations"
#./generate_migration.sh
#echo "Done"

# Start server
echo "Starting app"
#flask run --host=0.0.0.0 --port=5000
python -m main