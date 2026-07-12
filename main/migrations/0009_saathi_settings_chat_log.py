from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_add_new_osborn_branches'),
    ]

    operations = [
        migrations.CreateModel(
            name='SaathiSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Default', max_length=80, unique=True)),
                ('ai_enabled', models.BooleanField(default=True, help_text='If enabled, unmatched questions can be sent to the configured AI provider.')),
                ('fallback_reply', models.TextField(default='I can help with clinic information and simple general health guidance. For personal diagnosis or treatment advice, please speak with a doctor directly.')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Saathi Setting',
                'verbose_name_plural': 'Saathi Settings',
            },
        ),
        migrations.CreateModel(
            name='SaathiChatLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('reply', models.TextField(blank=True)),
                ('source', models.CharField(choices=[('rule', 'Internal rule'), ('ai', 'AI provider'), ('fallback', 'Fallback'), ('rate_limit', 'Rate limited')], max_length=20)),
                ('ai_model', models.CharField(blank=True, max_length=80)),
                ('ip_address', models.CharField(blank=True, max_length=64)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
