from django.db import migrations
from django.db import transaction
from django.utils.text import slugify

def slugify_names(apps, schema_editor):
    Category = apps.get_model('store', 'Category')
    Product = apps.get_model('store', 'Product')
    
    with transaction.atomic():
        # Slugify category names
        for category in Category.objects.all():
            original_slug = category.slug
            new_slug = slugify(category.name)
            if original_slug != new_slug:
                # If the new slug already exists, make it unique
                counter = 1
                test_slug = new_slug
                while Category.objects.filter(slug=test_slug).exists():
                    test_slug = f"{new_slug}-{counter}"
                    counter += 1
                category.slug = test_slug
                category.save()
        
        # Slugify product names
        for product in Product.objects.all():
            original_slug = product.slug
            new_slug = slugify(product.name)
            if original_slug != new_slug:
                # If the new slug already exists, make it unique
                counter = 1
                test_slug = new_slug
                while Product.objects.filter(slug=test_slug).exists():
                    test_slug = f"{new_slug}-{counter}"
                    counter += 1
                product.slug = test_slug
                product.save()

def reverse_slugify_names(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_clean_product_slugs'),
    ]

    operations = [
        migrations.RunPython(slugify_names, reverse_slugify_names),
    ] 