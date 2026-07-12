from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_saathi_settings_chat_log'),
    ]

    operations = [
        migrations.AlterField(
            model_name='saathichatlog',
            name='source',
            field=models.CharField(
                choices=[
                    ('rule', 'Internal rule'),
                    ('ai', 'AI provider'),
                    ('fallback', 'Fallback'),
                    ('ai_disabled', 'AI disabled fallback'),
                    ('ai_not_configured', 'AI not configured fallback'),
                    ('ai_error', 'AI error fallback'),
                    ('rate_limit', 'Rate limited'),
                ],
                max_length=20,
            ),
        ),
    ]
