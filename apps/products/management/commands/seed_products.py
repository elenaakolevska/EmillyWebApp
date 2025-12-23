import os
import random
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.products.models import Category, Product
from apps.delivery.models import DeliveryOption
from apps.recommendations.models import RecommendationRule


class Command(BaseCommand):
    help = 'Seed database with products from pictures folder'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting data seeding...')
        
        # Create categories
        categories = self.create_categories()
        
        # Create delivery options
        self.create_delivery_options()
        
        # Create products from pictures folder
        self.create_products(categories)
        
        # Create recommendation rules
        self.create_recommendation_rules(categories)
        
        self.stdout.write(self.style.SUCCESS('[OK] Data seeding completed successfully!'))

    def create_categories(self):
        self.stdout.write('Creating categories...')
        
        category_data = [
            ('Wedding Dress', 'Венчаница', 'wedding-dress'),
            ('Formal Dress', 'Свечен Фустан', 'formal-dress'),
            ('Suit', 'Костум', 'suit'),
            ('Accessory', 'Додаток', 'accessory'),
            ('Women Winter Coat', 'Женски Капут', 'women-winter-coat'),
            ('Men Winter Coat', 'Машки Капут', 'men-winter-coat'),
        ]
        
        categories = {}
        for name, name_mk, slug in category_data:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'name_mk': name_mk, 'slug': slug}
            )
            categories[name] = category
            if created:
                self.stdout.write(f'  [+] Created category: {name}')
        
        return categories

    def create_delivery_options(self):
        self.stdout.write('Creating delivery options...')
        
        delivery_options = [
            {
                'name': 'Pickup at Salon',
                'name_mk': 'Подигнување во Салон',
                'description': 'Pick up directly at our boutique',
                'description_mk': 'Подигнете ја нарачката директно од нашиот бутик',
                'price': 0,
                'estimated_days': 0,
            },
            {
                'name': 'Standard Delivery',
                'name_mk': 'Стандардна Достава',
                'description': 'Delivery in 3-5 working days',
                'description_mk': '3-5 работни дена',
                'price': 200,
                'estimated_days': 4,
            },
            {
                'name': 'Express Delivery',
                'name_mk': 'Експресна Достава',
                'description': 'Next day delivery',
                'description_mk': 'Следен ден',
                'price': 500,
                'estimated_days': 1,
            },
        ]
        
        for option_data in delivery_options:
            option, created = DeliveryOption.objects.get_or_create(
                name=option_data['name'],
                defaults=option_data
            )
            if created:
                self.stdout.write(f'  [+] Created delivery option: {option_data["name"]}')

    def create_products(self, categories):
        self.stdout.write('Creating products from pictures folder...')
        
        pictures_dir = settings.MEDIA_ROOT
        
        # Define folder to category mapping
        folder_mapping = {
            'wedding dresses': 'Wedding Dress',
            'formal dresses': 'Formal Dress',
            'suits': 'Suit',
            'accessories': 'Accessory',
            'winter coats - women': 'Women Winter Coat',
            'winter coats -men': 'Men Winter Coat',
        }
        
        # Define sizes for different categories
        sizes_wedding = ['36', '38', '40', '42', '44', '46', '48']
        sizes_formal = ['XS', 'S', 'M', 'L', 'XL']
        sizes_suit = ['46', '48', '50', '52', '54', '56']
        sizes_accessory = ['универзална']
        
        # Define colors (Macedonian)
        colors_white = ['бела', 'слонова-коска']
        colors_black = ['црна']
        colors_formal = ['црвена', 'сина', 'зелена', 'розова', 'бордо', 'виолетова', 'златна', 'сребрена', 'смарагдна', 'темно-сина']
        colors_suit = ['црна', 'сина', 'сива', 'темно-сина']
        colors_accessory = ['златна', 'сребрена', 'црна', 'бела']
        
        product_count = 0
        
        for folder_name, category_name in folder_mapping.items():
            folder_path = os.path.join(pictures_dir, folder_name)
            
            if not os.path.exists(folder_path):
                self.stdout.write(self.style.WARNING(f'  ! Folder not found: {folder_path}'))
                continue
            
            category = categories[category_name]
            
            # Get all image files
            image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            for image_file in image_files:
                # Extract product name from filename (without extension)
                product_name = os.path.splitext(image_file)[0]
                
                # Determine size based on category
                if category_name == 'Wedding Dress':
                    size = random.choice(sizes_wedding)
                    colors = colors_white
                    price = random.randint(25000, 45000)
                elif category_name == 'Formal Dress':
                    size = random.choice(sizes_formal)
                    colors = colors_formal
                    price = random.randint(8000, 18000)
                elif category_name == 'Suit':
                    size = random.choice(sizes_suit)
                    colors = colors_suit
                    price = random.randint(15000, 30000)
                elif category_name == 'Accessory':
                    size = random.choice(sizes_accessory)
                    colors = colors_accessory
                    price = random.randint(2000, 8000)
                elif 'Winter Coat' in category_name:
                    size = random.choice(sizes_formal)
                    colors = colors_formal
                    price = random.randint(12000, 25000)
                else:
                    size = 'M'
                    colors = colors_formal
                    price = 10000
                
                color = random.choice(colors)
                
                # Create relative image path
                image_path = f"{folder_name}/{image_file}"
                
                # Check if product already exists
                if not Product.objects.filter(name=product_name, category=category).exists():
                    # Determine if featured/new/popular
                    is_featured = random.random() < 0.2  # 20% chance
                    is_new = random.random() < 0.3  # 30% chance
                    is_popular = random.random() < 0.25  # 25% chance
                    
                    # Create appropriate description based on category
                    if category_name == 'Women Winter Coat':
                        description = f"Елегантен женски капут од нашата ексклузивна колекција."
                    elif category_name == 'Men Winter Coat':
                        description = f"Елегантен машки капут од нашата ексклузивна колекција."
                    elif category_name == 'Accessory':
                        description = f"Елегантен додаток со уникатен дизајн."
                    else:
                        description = f"Елегантен {category.name_mk.lower()} од нашата ексклузивна колекција."
                    
                    Product.objects.create(
                        name=product_name,
                        category=category,
                        description=description,
                        price=price,
                        size=size,
                        color=color,
                        availability=True,
                        image_path=image_path,
                        is_featured=is_featured,
                        is_new=is_new,
                        is_popular=is_popular,
                    )
                    product_count += 1
            
            self.stdout.write(f'  [+] Processed {category_name}: {len(image_files)} products')
        
        self.stdout.write(self.style.SUCCESS(f'[OK] Created {product_count} products'))

    def create_recommendation_rules(self, categories):
        self.stdout.write('Creating recommendation rules...')
        
        # Rule: Wedding Dress → Accessories
        if 'Wedding Dress' in categories and 'Accessory' in categories:
            rule, created = RecommendationRule.objects.get_or_create(
                name='Wedding Dress Accessories',
                defaults={
                    'rule_type': 'category_based',
                    'trigger_category': categories['Wedding Dress'],
                    'discount_percentage': 15,
                    'priority': 10,
                    'is_active': True,
                }
            )
            if created:
                rule.recommended_categories.add(categories['Accessory'])
                self.stdout.write('  [+] Created rule: Wedding Dress -> Accessories')
        
        # Rule: Formal Dress → Accessories
        if 'Formal Dress' in categories and 'Accessory' in categories:
            rule, created = RecommendationRule.objects.get_or_create(
                name='Formal Dress Accessories',
                defaults={
                    'rule_type': 'category_based',
                    'trigger_category': categories['Formal Dress'],
                    'discount_percentage': 10,
                    'priority': 5,
                    'is_active': True,
                }
            )
            if created:
                rule.recommended_categories.add(categories['Accessory'])
                self.stdout.write('  [+] Created rule: Formal Dress -> Accessories')
        
        # Rule: Suit → Accessories
        if 'Suit' in categories and 'Accessory' in categories:
            rule, created = RecommendationRule.objects.get_or_create(
                name='Suit Accessories',
                defaults={
                    'rule_type': 'category_based',
                    'trigger_category': categories['Suit'],
                    'discount_percentage': 10,
                    'priority': 5,
                    'is_active': True,
                }
            )
            if created:
                rule.recommended_categories.add(categories['Accessory'])
                self.stdout.write('  [+] Created rule: Suit -> Accessories')
        
        # Rule: Women Winter Coat → Accessories
        if 'Women Winter Coat' in categories and 'Accessory' in categories:
            rule, created = RecommendationRule.objects.get_or_create(
                name='Women Winter Coat Accessories',
                defaults={
                    'rule_type': 'category_based',
                    'trigger_category': categories['Women Winter Coat'],
                    'discount_percentage': 15,
                    'priority': 10,
                    'is_active': True,
                }
            )
            if created:
                rule.recommended_categories.add(categories['Accessory'])
                self.stdout.write('  [+] Created rule: Women Winter Coat -> Accessories')
        
        # Rule: Men Winter Coat → Accessories
        if 'Men Winter Coat' in categories and 'Accessory' in categories:
            rule, created = RecommendationRule.objects.get_or_create(
                name='Men Winter Coat Accessories',
                defaults={
                    'rule_type': 'category_based',
                    'trigger_category': categories['Men Winter Coat'],
                    'discount_percentage': 15,
                    'priority': 10,
                    'is_active': True,
                }
            )
            if created:
                rule.recommended_categories.add(categories['Accessory'])
                self.stdout.write('  [+] Created rule: Men Winter Coat -> Accessories')

