import os
import sys
from django.core.management.base import BaseCommand
from apps.products.models import Category, Product


class Command(BaseCommand):
    help = 'Fix encoding issues in category names and update product descriptions'

    def handle(self, *args, **kwargs):
        # Fix console output encoding
        if sys.platform == 'win32':
            sys.stdout.reconfigure(encoding='utf-8')
        
        self.stdout.write('Fixing encoding issues...')
        
        # Fix category names
        self.fix_categories()
        
        # Update product descriptions
        self.update_descriptions()
        
        self.stdout.write(self.style.SUCCESS('[OK] Encoding issues fixed successfully!'))

    def fix_categories(self):
        self.stdout.write('Fixing category names...')
        
        # Define correct category names
        category_fixes = {
            'Wedding Dress': 'Венчаница',
            'Formal Dress': 'Свечен Фустан',
            'Suit': 'Костум',
            'Accessory': 'Додаток',
            'Women Winter Coat': 'Женски Капут',
            'Men Winter Coat': 'Машки Капут',
        }
        
        for name_en, name_mk_correct in category_fixes.items():
            try:
                category = Category.objects.get(name=name_en)
                if category.name_mk != name_mk_correct:
                    category.name_mk = name_mk_correct
                    category.save()
                    self.stdout.write(f'  [✓] Fixed: {name_en} -> {name_mk_correct}')
                else:
                    self.stdout.write(f'  [✓] Already correct: {name_mk_correct}')
            except Category.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  [!] Category not found: {name_en}'))

    def update_descriptions(self):
        self.stdout.write('Updating product descriptions...')
        
        # Get winter coat categories
        women_coat_cat = Category.objects.filter(name='Women Winter Coat').first()
        men_coat_cat = Category.objects.filter(name='Men Winter Coat').first()
        
        count = 0
        
        # Update women's coat descriptions
        if women_coat_cat:
            products = Product.objects.filter(category=women_coat_cat)
            for product in products:
                if 'палто' in product.description.lower():
                    product.description = product.description.replace('палто', 'капут')
                    product.description = product.description.replace('Палто', 'Капут')
                    product.description = product.description.replace('зимско', 'женски')
                    product.save()
                    count += 1
            self.stdout.write(f'  [✓] Updated {products.count()} women\'s coat descriptions')
        
        # Update men's coat descriptions
        if men_coat_cat:
            products = Product.objects.filter(category=men_coat_cat)
            for product in products:
                if 'палто' in product.description.lower():
                    product.description = product.description.replace('палто', 'капут')
                    product.description = product.description.replace('Палто', 'Капут')
                    product.description = product.description.replace('зимско', 'машки')
                    product.save()
                    count += 1
            self.stdout.write(f'  [✓] Updated {products.count()} men\'s coat descriptions')
        
        self.stdout.write(f'  [✓] Total products updated: {count}')

