def cart_status(request):
    cart = request.session.get('cart', {})
    return {'cart_count': sum(cart.values())}