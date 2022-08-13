# Выполнено ДЗ № 10 logging

- [x] Основное ДЗ
- [x] Задание со *

Выполнил все задания кроме логов аудита и хостов

**TODO:**
После сдачи дипломной работы вернутся к логам [аудита](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/) и к логам хостов
+ к [логированию ивентов](https://github.com/max-rocket-internet/k8s-event-logger/tree/master/chart)

## В процессе сделано:

### Настроил логирование nginx ingress на стэке EFK

- Добавил дашбоард в Kibana
![img.png](efk/img_3.png)
![img.png](efk/img_1.png)
- Настроил мониторинг elasticsearch на prometheus - grafana
![img.png](efk/img.png)


### Настроил логирование nginx ingress на стэке Grafana Loki

- Создание datasource loki при установке prometheus-operator
![img.png](img.png)

- Парсинг обработка логов с помощью promtail и Loki. Cоздание дашбардов в grafana
![img_2.png](img_2.png)
  
## PR checklist:
- [x] Выставлен label с темой домашнего задания