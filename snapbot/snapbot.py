import boto3
import botocore
import click

session = boto3.Session(profile_name='snapshotty')
ec2 = session.resource('ec2')

def filter_instances(project):
    instances = []

    if project:
        filters = [{'Name': 'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances

@click.group()
def cli():
    """Commands for commandline"""


@cli.group()
def snapshots():
    """Commands for snapshots"""

@snapshots.command('list')
@click.option('--project', default=None, help="Snapshots of a Project")
@click.option('--all', 'list_all', deafult=False, is_flag=True)
def list_snapshots(project, list_all):
    """List all snapshots"""
    
    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(", ".join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    str(s.start_time)
                )))

                if s.state == 'completed' and not list_all:
                    break
    return


@cli.group('volumes')
def volumes():
    """Commands for volumes"""

@volumes.command('list')
@click.option('--project', default=None, help="Volumes of a Project")
def list_volumes(project):    
    """Lists all volumes"""
    
    instances = filter_instances(project)
    
    for i in instances:
        for v in i.volumes.all():
            print(", ". join((
                v.id,
                i.id,
                v.state,
                str(v.size) + "GiB"
            )))
    
    return


@cli.group('instances')
def instances():
    """Commands for instances"""

@instances.command('snapshot')
@click.option('--project', default=None, help="Instances of a Project")
def create_snapshots(project):
    """Takes a snapshot of all instances or ones under a project"""
    instances = filter_instances(project)

    for i in instances:
        print(f"Stopping {i.id}...")
        i.stop()
        i.wait_until_stopped()
        for v in i.volumes.all():
            print(f"Creating snapshot of {v.id}...")
            v.create_snapshot(Description="Snapshot created by snabot.py")
        print(f"Restarting {i.id}...")  
        i.start()
        i.wait_until_running()
    return


@instances.command('list')
@click.option('--project', default=None, help="Instances of a Project")
def list_instances(project):    
    """Lists all instances id, type, state, public dns name, launch time, and the project tag if avaliable"""
    instances = filter_instances(project)

    for i in instances:
        tags = {t['Key']: t['Value'] for t in i.tags or []}
        print(", ".join((
            i.id, 
            i.instance_type,
            i.state['Name'],
            i.public_dns_name,
            str(i.launch_time),
            tags.get('Project', 'NO project')
        )))
    

@instances.command('stop')
@click.option('--project', default=None, help="Instances of a Project")
def stop_instance(project):
    """Stops all instances unless given project tag"""
    instances = filter_instances(project)

    for i in instances:
        print(f"Stopping instance: {i.id}....")
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print(f"Could not stop {i.id}: {e}")
            continue
    
    return

@instances.command('start')
@click.option('--project', default=None, help="Instances of a Project")
def start_instance(project):
    """Stops all instances unless given project tag"""
    instances = filter_instances(project)

    for i in instances:
        print(f"Starting instance: {i.id}....")
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print(f"Could not start {i.id}: {e}")
            continue
    
    return

if __name__ == '__main__':
    cli()