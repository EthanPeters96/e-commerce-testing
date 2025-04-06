from django.db import migrations
from django.db import transaction

def clean_product_slugs(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    with transaction.atomic():
        for product in Product.objects.all():
            original_slug = product.slug
            cleaned_slug = original_slug.strip().replace(' ', '-')
            if original_slug != cleaned_slug:
                # If the cleaned slug already exists, make it unique
                counter = 1
                test_slug = cleaned_slug
                while Product.objects.filter(slug=test_slug).exists():
                    test_slug = f"{cleaned_slug}-{counter}"
                    counter += 1
                product.slug = test_slug
                product.save()

def reverse_clean_product_slugs(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_clean_category_slugs'),
    ]

    operations = [
        migrations.RunPython(clean_product_slugs, reverse_clean_product_slugs),
    ] 