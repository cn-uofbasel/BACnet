# Creates Profile Entries in the Database for each Node.
# TODO: Move somewhere else
from socialgraph.models import Profile


def create_profiles(data):
    Profile.objects.all().delete() # Delete all profile entries in the database.
    for node in data['nodes']:
        p = Profile(bacnet_id= node.get('id'), name= node.get('name'), gender=node.get('gender'), birthday=node.get('birthday'))
        p.save()

