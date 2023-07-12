install:
	pip install --upgrade pip
	pip install -r requirements.txt

migrationsWindows:
	python manage.py makemigrations
	python manage.py migrate

migrationsMac:
	python3 manage.py makemigrations
	python3 manage.py migrate

runWindows: 
	python manage.py runserver

runMac: 
	python3 manage.py runserver

allWindows:
	$(MAKE) install
	$(MAKE) migrationsWindows
	$(MAKE) runWindows

allMac:
	$(MAKE) install
	$(MAKE) migrationsMac
	$(MAKE) runMac
