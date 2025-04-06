from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import Category, Product, Order, OrderItem
import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json


class ProductListView(ListView):
    model = Product
    template_name = 'store/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(available=True)
        category_slug = self.kwargs.get('category_slug')
        search_query = self.request.GET.get('search')
        
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'store/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'product_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    
    for product_id, item in cart.items():
        product = get_object_or_404(Product, id=product_id)
        cart_item = {
            'product': product,
            'quantity': item['quantity'],
            'total_price': float(item['price']) * item['quantity']
        }
        cart_items.append(cart_item)
        total_price += cart_item['total_price']
    
    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'categories': Category.objects.all()
    })


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    
    quantity = int(request.POST.get('quantity', 1))
    if quantity > product.stock:
        quantity = product.stock
    
    cart_item = cart.get(str(product_id))
    if cart_item:
        cart[str(product_id)]['quantity'] += quantity
    else:
        cart[str(product_id)] = {
            'quantity': quantity,
            'price': str(product.price)
        }
    
    request.session['cart'] = cart
    messages.success(request, f'{product.name} added to your cart.')
    return redirect('store:cart')


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        product = get_object_or_404(Product, id=product_id)
        del cart[str(product_id)]
        request.session['cart'] = cart
        messages.success(request, f'{product.name} removed from your cart.')
    return redirect('store:cart')


def update_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        quantity = int(request.POST.get('quantity', 1))
        product = get_object_or_404(Product, id=product_id)
        
        if quantity > product.stock:
            quantity = product.stock
        
        cart[str(product_id)]['quantity'] = quantity
        request.session['cart'] = cart
        messages.success(
            request, 
            f'Cart updated: {product.name} quantity set to {quantity}.'
        )
    return redirect('store:cart')


def checkout_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('store:cart')
    
    cart_items = []
    total_price = 0
    
    for product_id, item in cart.items():
        product = get_object_or_404(Product, id=product_id)
        cart_item = {
            'product': product,
            'quantity': item['quantity'],
            'total_price': float(item['price']) * item['quantity']
        }
        cart_items.append(cart_item)
        total_price += cart_item['total_price']
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            payment_method_id = data.get('payment_method_id')
            shipping_info = data.get('shipping_info')

            # Create the order
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                first_name=shipping_info['firstName'],
                last_name=shipping_info['lastName'],
                email=shipping_info['email'],
                address=shipping_info['address'],
                postal_code=shipping_info['zipCode'],
                city=shipping_info['city'],
                total_price=total_price
            )

            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item['product'],
                    price=cart_item['total_price'],
                    quantity=cart_item['quantity']
                )

            # Create Stripe payment intent
            stripe.api_key = settings.STRIPE_SECRET_KEY
            print(f"Using Stripe API key: {stripe.api_key[:10]}...")  # Only print first 10 chars for security
            intent = stripe.PaymentIntent.create(
                amount=int(total_price * 100),  # Convert to cents
                currency='gbp',
                payment_method=payment_method_id,
                confirmation_method='manual',
                confirm=True,
                return_url=request.build_absolute_uri('/order-confirmation/'),
            )

            if intent.status == 'requires_action':
                # 3D Secure is required
                return JsonResponse({
                    'requires_action': True,
                    'payment_intent_client_secret': intent.client_secret
                })
            elif intent.status == 'succeeded':
                # Payment successful
                order.status = 'processing'
                order.save()
                
                # Clear the cart
                request.session['cart'] = {}
                
                return JsonResponse({
                    'success_url': request.build_absolute_uri('/order-confirmation/')
                })
            else:
                return JsonResponse({
                    'error': 'Invalid PaymentIntent status'
                }, status=400)

        except stripe.error.CardError as e:
            return JsonResponse({
                'error': e.error.message
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=400)
    
    return render(request, 'store/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'categories': Category.objects.all()
    })


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    # Set the Stripe API key
    stripe.api_key = settings.STRIPE_SECRET_KEY
    print(f"Webhook using Stripe API key: {stripe.api_key[:10]}...")  # Only print first 10 chars for security

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        # Clear the cart
        request.session['cart'] = {}
        
        # Add success message
        messages.success(request, 'Your order has been placed successfully!')
        
        return HttpResponse(status=200)
    
    return HttpResponse(status=200)


def order_confirmation_view(request):
    # Get the latest order for the current user
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user).order_by('-created').first()
    else:
        # For non-authenticated users, try to get the order from the session
        order_id = request.session.get('last_order_id')
        order = Order.objects.filter(id=order_id).first() if order_id else None
    
    if not order:
        return redirect('store:cart')
    
    # Get order items
    order_items = order.items.all()
    
    return render(request, 'store/order_confirmation.html', {
        'order': order,
        'order_items': order_items,
        'categories': Category.objects.all()
    })


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect to the next page if it exists, otherwise to the product list
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('store:product_list')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'store/login.html')


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, 
                f'Account created successfully! Welcome, {user.username}!'
            )
            return redirect('store:product_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserCreationForm()
    
    return render(request, 'store/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('store:login')


@staff_member_required
def admin_dashboard(request):
    """
    Custom admin dashboard for superuser to manage the store.
    """
    # Get statistics
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    available_products = Product.objects.filter(available=True).count()
    low_stock_products = Product.objects.filter(stock__lt=10).count()
    
    # Get products by category
    products_by_category = Category.objects.annotate(
        product_count=Count('products')
    ).order_by('-product_count')
    
    # Get low stock products
    low_stock = Product.objects.filter(stock__lt=10).order_by('stock')
    
    # Get recently added products
    recent_products = Product.objects.order_by('-created')[:5]
    
    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'available_products': available_products,
        'low_stock_products': low_stock_products,
        'products_by_category': products_by_category,
        'low_stock': low_stock,
        'recent_products': recent_products,
        'categories': Category.objects.all(),
    }
    
    return render(request, 'store/admin/dashboard.html', context)


@staff_member_required
def create_superuser(request):
    """
    View to create a new superuser from the admin dashboard.
    Only accessible to existing superusers.
    """
    if not request.user.is_superuser:
        messages.error(request, 'Only superusers can create other superusers.')
        return redirect('store:admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validate input
        if not all([username, email, password1, password2]):
            messages.error(request, 'All fields are required.')
            return render(request, 'store/admin/create_superuser.html')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'store/admin/create_superuser.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'store/admin/create_superuser.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'store/admin/create_superuser.html')
        
        # Create the superuser
        try:
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password1),
                is_staff=True,
                is_superuser=True
            )
            messages.success(
                request, 
                f'Superuser {username} created successfully.'
            )
            return redirect('store:admin_dashboard')
        except Exception as e:
            messages.error(request, f'Error creating superuser: {str(e)}')
    
    return render(request, 'store/admin/create_superuser.html')


@staff_member_required
def category_form(request, category_id=None):
    """
    View for adding and editing categories.
    """
    category = None
    if category_id:
        category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        description = request.POST.get('description')
        
        if not all([name, slug]):
            messages.error(request, 'Name and slug are required.')
            return render(request, 'store/admin/category_form.html', {'category': category})
        
        if Category.objects.filter(slug=slug).exclude(id=category_id).exists():
            messages.error(request, 'A category with this slug already exists.')
            return render(request, 'store/admin/category_form.html', {'category': category})
        
        if category:
            category.name = name
            category.slug = slug
            category.description = description
            category.save()
            messages.success(request, f'Category "{name}" updated successfully.')
        else:
            Category.objects.create(
                name=name,
                slug=slug,
                description=description
            )
            messages.success(request, f'Category "{name}" created successfully.')
        
        return redirect('store:admin_dashboard')
    
    return render(request, 'store/admin/category_form.html', {'category': category})


@staff_member_required
def delete_category(request, category_id):
    """
    View for deleting categories.
    """
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Category "{name}" deleted successfully.')
        return redirect('store:admin_dashboard')
    
    return render(request, 'store/admin/delete_confirmation.html', {
        'object': category,
        'object_type': 'category',
        'back_url': 'store:admin_dashboard'
    })


@staff_member_required
def product_form(request, product_id=None):
    """
    View for adding and editing products.
    """
    product = None
    if product_id:
        product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        available = request.POST.get('available') == 'on'
        image = request.FILES.get('image')
        
        if not all([name, slug, category_id, price, stock]):
            messages.error(request, 'All fields except image are required.')
            return render(request, 'store/admin/product_form.html', {
                'product': product,
                'categories': Category.objects.all()
            })
        
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            messages.error(request, 'Selected category does not exist.')
            return render(request, 'store/admin/product_form.html', {
                'product': product,
                'categories': Category.objects.all()
            })
        
        if Product.objects.filter(slug=slug).exclude(id=product_id).exists():
            messages.error(request, 'A product with this slug already exists.')
            return render(request, 'store/admin/product_form.html', {
                'product': product,
                'categories': Category.objects.all()
            })
        
        if product:
            product.name = name
            product.slug = slug
            product.category = category
            product.description = description
            product.price = price
            product.stock = stock
            product.available = available
            if image:
                product.image = image
            product.save()
            messages.success(request, f'Product "{name}" updated successfully.')
        else:
            if not image:
                messages.error(request, 'Image is required for new products.')
                return render(request, 'store/admin/product_form.html', {
                    'product': product,
                    'categories': Category.objects.all()
                })
            
            Product.objects.create(
                name=name,
                slug=slug,
                category=category,
                description=description,
                price=price,
                stock=stock,
                available=available,
                image=image
            )
            messages.success(request, f'Product "{name}" created successfully.')
        
        return redirect('store:admin_dashboard')
    
    return render(request, 'store/admin/product_form.html', {
        'product': product,
        'categories': Category.objects.all()
    })


@staff_member_required
def delete_product(request, product_id):
    """
    View for deleting products.
    """
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted successfully.')
        return redirect('store:admin_dashboard')
    
    return render(request, 'store/admin/delete_confirmation.html', {
        'object': product,
        'object_type': 'product',
        'back_url': 'store:admin_dashboard'
    }) 