from django.db import migrations
from django.db import transaction

def clean_category_slugs(apps, schema_editor):
    Category = apps.get_model('store', 'Category')
    with transaction.atomic():
        for category in Category.objects.all():
            original_slug = category.slug
            cleaned_slug = original_slug.strip()
            if original_slug != cleaned_slug:
                # If the cleaned slug already exists, make it unique
                counter = 1
                test_slug = cleaned_slug
                while Category.objects.filter(slug=test_slug).exists():
                    test_slug = f"{cleaned_slug}-{counter}"
                    counter += 1
                category.slug = test_slug
                category.save()

def reverse_clean_category_slugs(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(clean_category_slugs, reverse_clean_category_slugs),
    ] 