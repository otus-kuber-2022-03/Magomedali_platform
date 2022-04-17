# Выполнено ДЗ № 7 - kubernetes-operators

- [x] Основное ДЗ

## В процессе сделано:

Выполнил все пункты ДЗ. 
Создал crd, cr и operator для mysql на языке python c помощью фреймворка kopf

Вывод команды `kubectl get pods`
```shell
macali:deploy ali$ k get pods
NAME                                  READY   STATUS      RESTARTS   AGE
backup-mysql-instance-job--1-s6ptw    0/1     Completed   0          3m37s
mysql-instance-6785949c48-4fhqj       1/1     Running     0          2m50s
mysql-operator-7d4468bbd9-bggwc       1/1     Running     0          9m48s
restore-mysql-instance-job--1-lt6fp   0/1     Completed   3          2m50s
```

Задание со * (1):
При создании нашего cr, в поле status пишется объект который возвращает декоратор
```python
@kopf.on.create('otus.homework', 'v1', 'mysqls')
def Kopf(name, **_):
	return "Task with star"
```

```shell
> macali:deploy ali$ k get ms mysql-instance -o yaml
...
spec:
  database: otus-database
  image: mysql:5.7
  password: otuspassword
  storage_size: 1Gi
status:
  Kopf: Task with star
  kopf:
    progress: {}
  mysql_on_create:
    Message: Mysql created from backup

```

Задание со * (2):

Декоратор для обработки изменения пароля:
```python
@kopf.on.field('otus.homework', 'v1', 'mysqls', field='spec.user_password')
def update_password(old, new, body, namespace, logger, **kwargs):
    # Обработчик срабатывает при create, update, delete, скипаем все ивенты когда пароль не менялся
    if old is None:
        return {'info': "skip"}

    name = body['metadata']['name']
    image = body['spec']['image']
    database = body['spec']['database']
    logger.info("new pass: " + new)
    logger.info("old pass: " + old)

    try:
        password_change_job = render_template('password-change-job.yml.j2',
                                              {'name': name, 'database': database, 'image': image, 'old': old, 'new': new})
        kopf.append_owner_reference(password_change_job, owner=body)

        api = kubernetes.client.BatchV1Api()

        ##
        # Проверяем есть ранее созданная джоба, чтоб потом ее удалить
        ##
        jobname = f"password-change-{name}-job"
        jobNameExists = False
        logger.info('jobname=' + jobname)
        jobs = api.list_namespaced_job('default')
        for job in jobs.items:
            if job.metadata.name == jobname:
                api.delete_namespaced_job(jobname, 'default')
                jobNameExists = True

        api = kubernetes.client.BatchV1Api()
        if jobNameExists:
            time.sleep(3) # ждем 3 секунды пока старая джоба удалится

        api.create_namespaced_job('default', password_change_job) # создаем джобу

    except Exception as e:
        logger.error('failed to create job for change password: ' + str(e))
        pass

    return {'info': "created job for change password"}
```

При изменении параметра `user_password` у cr, оператор создает job который выполняет команду `mysql -h {{ name }} -u ali -p{{ old }} {{ database }} -e "alter user 'ali'@'%' IDENTIFIED BY '{{ new }}';`

Пример:
```shell
macali:deploy ali$ k get pods
NAME                                  READY   STATUS      RESTARTS   AGE
backup-mysql-instance-job--1-46vsp    0/1     Completed   0          10m
mysql-instance-7b447789cf-t75r9       1/1     Running     0          9m28s
restore-mysql-instance-job--1-d6bbj   0/1     Completed   3          9m28s
macali:deploy ali$ k apply -f cr.yml 
mysql.otus.homework/mysql-instance configured
macali:deploy ali$ k get pods
NAME                                          READY   STATUS              RESTARTS   AGE
backup-mysql-instance-job--1-46vsp            0/1     Completed           0          10m
mysql-instance-7b447789cf-t75r9               1/1     Running             0          10m
password-change-mysql-instance-job--1-zfzzn   0/1     ContainerCreating   0          2s
restore-mysql-instance-job--1-d6bbj           0/1     Completed           3          10m
macali:deploy ali$ k get pods
NAME                                          READY   STATUS      RESTARTS   AGE
backup-mysql-instance-job--1-46vsp            0/1     Completed   0          10m
mysql-instance-7b447789cf-t75r9               1/1     Running     0          10m
password-change-mysql-instance-job--1-zfzzn   0/1     Completed   0          11s
restore-mysql-instance-job--1-d6bbj           0/1     Completed   3          10m
macali:deploy ali$ 
macali:deploy ali$ k describe pod password-change-mysql-instance-job--1-zfzzn 
Name:         password-change-mysql-instance-job--1-zfzzn
Namespace:    default
Priority:     0
Node:         minikube/192.168.49.2
Start Time:   Sun, 17 Apr 2022 06:46:14 +0300
Labels:       controller-uid=39eccf34-c487-48b8-8ee6-2c657a478353
              job-name=password-change-mysql-instance-job
Annotations:  <none>
Status:       Succeeded
IP:           172.17.0.4
IPs:
  IP:           172.17.0.4
Controlled By:  Job/password-change-mysql-instance-job
Containers:
  mysql:
    Container ID:  docker://ab25f6813bfa54d529edce91390a71a8c2758ea7631de6db8bdd89c638475732
    Image:         mysql:5.7
    Image ID:      docker-pullable://mysql@sha256:1a73b6a8f507639a8f91ed01ace28965f4f74bb62a9d9b9e7378d5f07fab79dc
    Port:          <none>
    Host Port:     <none>
    Command:
      /bin/sh
      -c
      mysql -h mysql-instance -u ali -ps256789 otus-database -e "alter user 'ali'@'%' IDENTIFIED BY 's2567899';"
    State:          Terminated
      Reason:       Completed
      Exit Code:    0
      Started:      Sun, 17 Apr 2022 06:46:15 +0300
      Finished:     Sun, 17 Apr 2022 06:46:15 +0300
    Ready:          False
    Restart Count:  0
    Environment:    <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-msh9t (ro)
Conditions:
  Type              Status
  Initialized       True 
  Ready             False 
  ContainersReady   False 
  PodScheduled      True 
Volumes:
  kube-api-access-msh9t:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    ConfigMapOptional:       <nil>
    DownwardAPI:             true
QoS Class:                   BestEffort
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type    Reason     Age    From               Message
  ----    ------     ----   ----               -------
  Normal  Scheduled  2m32s  default-scheduler  Successfully assigned default/password-change-mysql-instance-job--1-zfzzn to minikube
  Normal  Pulled     2m31s  kubelet, minikube  Container image "mysql:5.7" already present on machine
  Normal  Created    2m31s  kubelet, minikube  Created container mysql
  Normal  Started    2m31s  kubelet, minikube  Started container mysql
macali:deploy ali$
```

## Как запустить проект:

- применить манифесты из папки kubernetes-operators/deploy

## PR checklist:
- [x] Выставлен label с темой домашнего задания