from .models import Product

def cart_count(request):
    cart = request.session.get('cart', {})
    # เอายอดจำนวนของสินค้าทุกชิ้นมารวมกัน
    count = sum(cart.values())
    return {'cart_count': count}