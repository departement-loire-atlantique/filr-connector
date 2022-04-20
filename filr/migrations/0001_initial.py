# Generated by Django 2.2.24 on 2022-04-20 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0029_auto_20210202_1627'),
    ]

    operations = [
        migrations.CreateModel(
            name='Filr',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='Title')),
                ('slug', models.SlugField(unique=True, verbose_name='Identifier')),
                ('description', models.TextField(verbose_name='Description')),
                ('basic_auth_username', models.CharField(blank=True, max_length=128, verbose_name='Basic authentication username')),
                ('basic_auth_password', models.CharField(blank=True, max_length=128, verbose_name='Basic authentication password')),
                ('client_certificate', models.FileField(blank=True, null=True, upload_to='', verbose_name='TLS client certificate')),
                ('trusted_certificate_authorities', models.FileField(blank=True, null=True, upload_to='', verbose_name='TLS trusted CAs')),
                ('verify_cert', models.BooleanField(blank=True, default=True, verbose_name='TLS verify certificates')),
                ('http_proxy', models.CharField(blank=True, max_length=128, verbose_name='HTTP and HTTPS proxy')),
                ('users', models.ManyToManyField(blank=True, related_name='_filr_users_+', related_query_name='+', to='base.ApiUser')),
            ],
            options={
                'verbose_name': 'Connecteur pour Filr',
            },
        ),
    ]
