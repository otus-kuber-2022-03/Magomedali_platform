run:
	docker-compose up --scale redis-sentinel=3 -d

stop:
	docker-compose stop

restart:
	docker-compose stop && docker-compose up --scale redis-sentinel=3 -d