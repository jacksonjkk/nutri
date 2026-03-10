from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('aiagent', '0010_healthassessment'),
    ]

def enable_rls(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    
    tables = [
        'django_migrations',
        'django_content_type',
        'auth_permission',
        'auth_group',
        'auth_group_permissions',
        'aiagent_nutriuser',
        'aiagent_nutriuser_groups',
        'aiagent_nutriuser_user_permissions',
        'aiagent_aiinsight',
        'aiagent_dailylog',
        'aiagent_userprofile',
        'django_site',
        'django_admin_log',
        'django_session',
        'aiagent_fooditem',
        'aiagent_healthassessment',
    ]
    
    with schema_editor.connection.cursor() as cursor:
        for table in tables:
            cursor.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")

def disable_rls(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    
    tables = [
        'django_migrations',
        'django_content_type',
        'auth_permission',
        'auth_group',
        'auth_group_permissions',
        'aiagent_nutriuser',
        'aiagent_nutriuser_groups',
        'aiagent_nutriuser_user_permissions',
        'aiagent_aiinsight',
        'aiagent_dailylog',
        'aiagent_userprofile',
        'django_site',
        'django_admin_log',
        'django_session',
        'aiagent_fooditem',
        'aiagent_healthassessment',
    ]
    
    with schema_editor.connection.cursor() as cursor:
        for table in tables:
            cursor.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")

class Migration(migrations.Migration):

    dependencies = [
        ('aiagent', '0010_healthassessment'),
    ]

    operations = [
        migrations.RunPython(enable_rls, disable_rls),
    ]
