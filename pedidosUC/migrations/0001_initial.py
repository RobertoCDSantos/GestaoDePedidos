# Generated by Django 4.1.7 on 2023-05-30 17:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pedidos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PedidoUC',
            fields=[
                ('pedido_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='pedidos.pedido')),
            ],
            options={
                'db_table': 'PedidoUC',
            },
            bases=('pedidos.pedido',),
        ),
    ]
