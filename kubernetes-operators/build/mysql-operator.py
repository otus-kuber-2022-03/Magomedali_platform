import kopf
import yaml
import kubernetes
import time
import json
from jinja2 import Environment, FileSystemLoader


def render_template(filename, vars_dict):
    env = Environment(loader=FileSystemLoader('./templates'))
    template = env.get_template(filename)
    yaml_manifest = template.render(vars_dict)
    json_manifest = yaml.safe_load(yaml_manifest)
    return json_manifest


def delete_success_jobs(mysql_instance_name):
    api = kubernetes.client.BatchV1Api()
    jobs = api.list_namespaced_job('default')
    for job in jobs.items:
        jobname = job.metadata.name
        if (jobname == f"backup-{mysql_instance_name}-job"):
            if job.status.succeeded == 1:
                api.delete_namespaced_job(jobname, 'default', propagation_policy='Background')


def wait_until_job_end(jobname):
    api = kubernetes.client.BatchV1Api()
    job_finished = False
    jobs = api.list_namespaced_job('default')
    while (not job_finished) and any(job.metadata.name == jobname for job in jobs.items):
        time.sleep(1)
        jobs = api.list_namespaced_job('default')
        for job in jobs.items:
            if job.metadata.name == jobname and job.status.succeeded == 1:
                job_finished = True


@kopf.on.create('otus.homework', 'v1', 'mysqls')
def mysql_on_create(body, spec, **kwargs):
    name = body['metadata']['name']
    image = body['spec']['image']
    database = body['spec']['database']
    root_password = body['spec']['root_password']
    user_name = body['spec']['user_name']
    user_password = body['spec']['user_password']
    storage_size = body['spec']['storage_size']

    persistent_volume = render_template('mysql-pv.yml.j2', {'name': name, 'storage_size': storage_size})
    persistent_volume_claim = render_template('mysql-pvc.yml.j2', {'name': name, 'storage_size': storage_size})

    service = render_template('mysql-service.yml.j2', {'name': name})
    deployment = render_template('mysql-deployment.yml.j2',
                                 {'name': name, 'image': image, 'root_password': root_password, 'user_name': user_name, 'user_password': user_password, 'database': database})
    restore_job = render_template('restore-job.yml.j2',
                                  {'name': name, 'image': image, 'password': root_password, 'database': database})

    kopf.append_owner_reference(persistent_volume, owner=body)
    kopf.append_owner_reference(persistent_volume_claim, owner=body)
    kopf.append_owner_reference(service, owner=body)
    kopf.append_owner_reference(deployment, owner=body)
    kopf.append_owner_reference(restore_job, owner=body)

    api = kubernetes.client.CoreV1Api()

    api.create_persistent_volume(persistent_volume)
    api.create_namespaced_persistent_volume_claim('default', persistent_volume_claim)
    api.create_namespaced_service('default', service)

    api = kubernetes.client.AppsV1Api()
    api.create_namespaced_deployment('default', deployment)

    try:
        backup_pv = render_template('backup-pv.yml.j2', {'name': name})
        api = kubernetes.client.CoreV1Api()
        api.create_persistent_volume(backup_pv)
    except kubernetes.client.rest.ApiException:
        pass

    try:
        backup_pvc = render_template('backup-pvc.yml.j2', {'name': name, 'storage_size': storage_size})
        api = kubernetes.client.CoreV1Api()
        api.create_namespaced_persistent_volume_claim('default', backup_pvc)
    except kubernetes.client.rest.ApiException:
        pass

    try:
        api = kubernetes.client.BatchV1Api()
        api.create_namespaced_job('default', restore_job)
    except kubernetes.client.rest.ApiException:
        pass

    return {'Message': "Mysql created from backup"}


@kopf.on.create('otus.homework', 'v1', 'mysqls')
def Kopf(name, **kwargs):
    return "Task with star"


@kopf.on.field('otus.homework', 'v1', 'mysqls', field='spec.user_password')
def update_password(old, new, body, namespace, logger, **kwargs):
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
            time.sleep(3)

        api.create_namespaced_job('default', password_change_job)

    except Exception as e:
        logger.error('failed to create job for change password: ' + str(e))
        pass

    return {'info': "created job for change password"}


@kopf.on.delete('otus.homework', 'v1', 'mysqls')
def delete_object_make_backup(body, **kwargs):
    name = body['metadata']['name']
    image = body['spec']['image']
    root_password = body['spec']['root_password']
    database = body['spec']['database']

    delete_success_jobs(name)

    api = kubernetes.client.BatchV1Api()
    backup_job = render_template('backup-job.yml.j2',
                                 {'name': name, 'image': image, 'password': root_password, 'database': database})
    api.create_namespaced_job('default', backup_job)

    wait_until_job_end(f"backup-{name}-job")

    api = kubernetes.client.AppsV1Api()
    api.delete_namespaced_deployment(name, 'default')

    api = kubernetes.client.CoreV1Api()
    api.delete_namespaced_service(name, 'default')
    api.delete_namespaced_persistent_volume_claim(name + "-pvc", 'default')
    api.delete_persistent_volume(name + "-pv")

    return {'message': "mysql and its children resources deleted"}
