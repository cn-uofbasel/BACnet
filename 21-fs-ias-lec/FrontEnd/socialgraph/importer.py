# Creates Profile Entries in the Database for each Node.
# TODO: Move somewhere else
from socialgraph.models import Profile


def create_profiles(data):
    Profile.objects.all().delete()  # Delete all profile entries in the database.
    for node in data['nodes']:
        p = Profile(bacnet_id=node.get('id'), name=node.get('name'), gender=node.get('gender'),
                    birthday=node.get('birthday'), country=node.get('country'), town=node.get('town'),
                    language=node.get('language'),
                    profile_pic=node.get('profile_pic') if node.get('profile_pic') is not None else 'default.jpg')
        p.save()
    print("Updated Database!")
