from django.db import migrations


SPORTS = [
    "Football", "Basketball", "Baseball", "Cricket", "Tennis",
    "Swimming", "Running", "Cycling", "Volleyball", "Boxing",
    "Golf", "Rugby", "Hockey", "Badminton", "Table Tennis",
]

ENTERTAINMENT = [
    "Movies", "Music", "Gaming", "Reading", "Cooking",
    "Travel", "Photography", "Dancing", "Painting", "Hiking",
    "Yoga", "Fitness", "Podcasts", "Theatre", "Comedy",
]


def seed_data(apps, schema_editor):
    Sport = apps.get_model('profiles', 'Sport')
    Entertainment = apps.get_model('profiles', 'Entertainment')

    for name in SPORTS:
        Sport.objects.get_or_create(name=name)

    for name in ENTERTAINMENT:
        Entertainment.objects.get_or_create(name=name)


def unseed_data(apps, schema_editor):
    Sport = apps.get_model('profiles', 'Sport')
    Entertainment = apps.get_model('profiles', 'Entertainment')
    Sport.objects.filter(name__in=SPORTS).delete()
    Entertainment.objects.filter(name__in=ENTERTAINMENT).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_add_referral_is_redeemed'),
    ]

    operations = [
        migrations.RunPython(seed_data, reverse_code=unseed_data),
    ]
