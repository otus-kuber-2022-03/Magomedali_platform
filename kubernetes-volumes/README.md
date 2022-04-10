# Выполнено ДЗ № 5 - kubernetes-volumes

- [x] Основное ДЗ

## В процессе сделано:

Выполнил все пункты ДЗ. Поэкспериментировал c statefulset приложениями и с pv, pvc и secret

Создание секрета для конфига minio:
```shell
> k create secret generic minio-secret --from-env-file=.env
```

Указание в env значения из secret
```yaml
          env:
            - name: MINIO_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  key: MINIO_ACCESS_KEY
                  name: minio-secret
            - name: MINIO_SECRET_KEY
              valueFrom:
                secretKeyRef:
                  key: MINIO_SECRET_KEY
                  name: minio-secret
```

## Как запустить проект:

- применить манифесты из папки kubernetes-volumes

## PR checklist:
- [x] Выставлен label с темой домашнего задания