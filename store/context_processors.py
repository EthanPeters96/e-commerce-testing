def cart_count(request):
    """
    Context processor to make the cart count available globally.
    """
    cart = request.session.get('cart', {})
    count = sum(item['quantity'] for item in cart.values())
    return {'cart_count': count} 