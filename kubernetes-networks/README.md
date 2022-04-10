# Выполнено ДЗ № 4

- [x] Основное ДЗ
- [x] Задание со *

## В процессе сделано:

Все задания были выполнены.

livenessProbe: `ps aux | grep my_web_server_process` не имеет смысла так как команда всегда завершится кодом 0

* Поэкспериментаровл с сервисами.
  Сервис обычно имеет свой IP адрсес на который приходит трафик балансирующий между Endpoints правилами iptables или ipvs. Таким образом сервис служит в качестве балансера перед подами.
* Настроил кластер с использованием ipvc вместо iptables
* Установил Metallb, попрактиковался с сервисом типа LoadBalancer
* Настроил для CoreDNC сервис LoadBalancer
```shell
> nslookup 172-17-0-9.default.pod.cluster.local 172.17.255.2
Server:         172.17.255.2
Address:        172.17.255.2#53

Name:   172-17-0-9.default.pod.cluster.local
Address: 172.17.0.9
```
* Установил nginx-ingress

Ingress контроллер умеет балансировать трафик между Endpoints, поэтому нет необходимости в сервисе с IP адресом. 
Для ingress создал  headless сервис без ip адреса

* Установил kubernetes dashboard и настроил для него ingress 

Сайт открывается из браузера, но статика не прогружается 

* Настроил canary деплой с помощью  ingress nginx

## PR checklist:
- [x] Выставлен label с темой домашнего задания