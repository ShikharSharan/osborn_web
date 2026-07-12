from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_site_error_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='saathichatlog',
            name='error_detail',
            field=models.TextField(blank=True),
        ),
    ]
