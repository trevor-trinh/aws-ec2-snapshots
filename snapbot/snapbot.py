import boto3
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
def instances():
    """Commands for instances"""

@instances.command('list')
@click.option('--project', default=None, help="Instances of a Project")
def list_instances(project):    
    """Lists all instances id, type, state, public dns name, launch time, and the project tag if aviable"""
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
        i.stop()

@instances.command('start')
@click.option('--project', default=None, help="Instances of a Project")
def start_instance(project):
    """Stops all instances unless given project tag"""
    instances = filter_instances(project)

    for i in instances:
        print(f"Starting instance: {i.id}....")
        i.start()

if __name__ == '__main__':
    instances()