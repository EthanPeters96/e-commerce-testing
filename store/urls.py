from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('category/<slug:category_slug>/',
         views.ProductListView.as_view(),
         name='product_list_by_category'),
    path('product/<slug:product_slug>/',
         views.ProductDetailView.as_view(),
         name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/',
         views.add_to_cart,
         name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/',
         views.remove_from_cart,
         name='remove_from_cart'),
    path('update-cart/<int:product_id>/',
         views.update_cart,
         name='update_cart'),
    path('checkout/',
         views.checkout_view,
         name='checkout'),
    path('order-confirmation/',
         views.order_confirmation_view,
         name='order_confirmation'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/create-superuser/', views.create_superuser, name='create_superuser'),
    path('admin-dashboard/category/add/', views.category_form, name='add_category'),
    path('admin-dashboard/category/<int:category_id>/edit/', views.category_form, name='edit_category'),
    path('admin-dashboard/category/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    path('admin-dashboard/product/add/', views.product_form, name='add_product'),
    path('admin-dashboard/product/<int:product_id>/edit/', views.product_form, name='edit_product'),
    path('admin-dashboard/product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
]

 