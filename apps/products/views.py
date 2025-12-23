from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Product, Category


def home(request):
    """Home page with featured products"""
    # Exclude accessories from home page
    featured_products = Product.objects.filter(
        availability=True, 
        is_featured=True
    ).exclude(category__name='Accessory')[:6]
    
    new_products = Product.objects.filter(
        availability=True, 
        is_new=True
    ).exclude(category__name='Accessory')[:6]
    
    popular_products = Product.objects.filter(
        availability=True, 
        is_popular=True
    ).exclude(category__name='Accessory')[:6]
    
    categories = Category.objects.all()
    
    context = {
        'featured_products': featured_products,
        'new_products': new_products,
        'popular_products': popular_products,
        'categories': categories,
    }
    return render(request, 'home.html', context)


def product_list(request):
    """Product listing with filters"""
    from django.db.models import Case, When, Value, IntegerField
    
    products = Product.objects.filter(availability=True)
    categories = Category.objects.all()
    
    # Get filter parameters
    category_slug = request.GET.get('category')
    size = request.GET.get('size')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    search = request.GET.get('search')
    
    # Apply filters
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    if size:
        products = products.filter(size=size)
    
    if min_price:
        products = products.filter(price__gte=min_price)
    
    if max_price:
        products = products.filter(price__lte=max_price)
    
    if search:
        products = products.filter(name__icontains=search)
    
    # Order products: prioritize dresses and suits, accessories last
    products = products.annotate(
        category_priority=Case(
            When(category__name='Wedding Dress', then=Value(1)),
            When(category__name='Formal Dress', then=Value(2)),
            When(category__name='Suit', then=Value(3)),
            When(category__name__icontains='Coat', then=Value(4)),
            When(category__name='Accessory', then=Value(5)),
            default=Value(6),
            output_field=IntegerField(),
        )
    ).order_by('category_priority', '-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique sizes for filters and sort them logically
    all_sizes_raw = Product.objects.values_list('size', flat=True).distinct()
    # Remove duplicates and sort
    all_sizes_set = set(all_sizes_raw)
    
    # Define size order for sorting
    size_order = ['XS', 'S', 'M', 'L', 'XL', 'XXL', '36', '38', '40', '42', '44', '46', '48', '50', '52', '54', '56', 'универзална']
    
    # Sort sizes according to predefined order
    all_sizes = sorted(all_sizes_set, key=lambda x: size_order.index(x) if x in size_order else 999)
    
    # Build filter parameters string for pagination
    filter_params_list = []
    if category_slug:
        filter_params_list.append(f'category={category_slug}')
    if size:
        filter_params_list.append(f'size={size}')
    if min_price:
        filter_params_list.append(f'min_price={min_price}')
    if max_price:
        filter_params_list.append(f'max_price={max_price}')
    if search:
        filter_params_list.append(f'search={search}')
    filter_params = '&'.join(filter_params_list)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'all_sizes': all_sizes,
        'current_category': category_slug,
        'current_size': size,
        'filter_params': filter_params,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, pk):
    """Product detail page"""
    product = get_object_or_404(Product, pk=pk, availability=True)
    
    # Get related products (same category)
    related_products = Product.objects.filter(
        category=product.category,
        availability=True
    ).exclude(pk=product.pk)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)


def about(request):
    """About page"""
    return render(request, 'about.html')


def contact(request):
    """Contact page"""
    return render(request, 'contact.html')
