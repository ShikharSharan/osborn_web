from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_update_saathi_chat_log_sources'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteErrorLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=500)),
                ('method', models.CharField(blank=True, max_length=12)),
                ('status_code', models.PositiveIntegerField(default=500)),
                ('exception_type', models.CharField(max_length=160)),
                ('message', models.TextField(blank=True)),
                ('traceback', models.TextField(blank=True)),
                ('user_label', models.CharField(blank=True, max_length=160)),
                ('ip_address', models.CharField(blank=True, max_length=64)),
                ('user_agent', models.TextField(blank=True)),
                ('is_resolved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
