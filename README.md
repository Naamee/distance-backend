# distance-backend

[deployment-server]: flask --app distance_app run

make sure to set FLASK_APP to distance_app.py

[make-migrations]: flask db migrate -m "<migration_file_name>"
[apply-migrations]: flask db upgrade
[remove-last-migration]: flask db downgrade