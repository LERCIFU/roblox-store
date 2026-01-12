from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order, OrderItem
from django.contrib.auth.decorators import login_required
import requests
from .forms import ProductForm
from django.contrib.auth import logout
from django.http import FileResponse, Http404, HttpResponseForbidden
import os
from django.conf import settings

@login_required
def download_script(request, product_id):
    # 1. หาสินค้า
    product = get_object_or_404(Product, id=product_id)
    
    # 2. 🛡️ เช็คว่า User เคยซื้อและจ่ายเงินหรือยัง? (Security Check)
    # ค้นหา Order ของ User นี้ ที่มีสินค้านี้ และจ่ายเงินแล้ว (paid=True)
    has_purchased = Order.objects.filter(
        customer_name=request.user.username,
        items__product=product, # เช็คว่าใน order มีสินค้านี้ไหม (ผ่านตาราง OrderItem)
        paid=True
    ).exists()

    # ถ้าไม่ใช่ Superuser และ ไม่เคยซื้อ -> ห้ามโหลด!
    if not request.user.is_superuser and not has_purchased:
        return HttpResponseForbidden("⛔ คุณยังไม่ได้ซื้อสินค้านี้ หรือยังไม่ได้ชำระเงิน")

    # 3. เช็คว่ามีไฟล์จริงๆ ไหม
    if not product.script_file:
        raise Http404("ไม่พบไฟล์สคริปต์")

    # 4. 📤 ส่งไฟล์ให้โหลด (โดยไม่เปิดเผย Path จริง)
    file_path = product.script_file.path
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
    return response

# 1. ฟังก์ชันเพิ่มของลงตะกร้า
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    
    # เก็บข้อมูลพื้นฐานลง Session
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    
    request.session['cart'] = cart
    # ✅ แก้เป็น store:cart_detail
    return redirect('store:cart_detail')

# 2. ฟังก์ชันดูของในตะกร้า
def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = product.price * quantity
            total_price += subtotal
            cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
        except Product.DoesNotExist:
            continue
        
    return render(request, 'store/cart_detail.html', {
        'cart_items': cart_items, 
        'total_price': total_price
    })

# 3. ฟังก์ชันเคลียร์ตะกร้า
def clear_cart(request):
    if 'cart' in request.session:
        del request.session['cart']
    # ✅ แก้เป็น store:product_list
    return redirect('store:product_list')

# 4. รายละเอียดสินค้า
def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk)
    return render(request, 'store/product_detail.html', {'product': product})

# 5. หน้าร้านค้า
def product_list(request):
    query = request.GET.get('search')
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})

# 6. สั่งซื้อและแจ้งเตือน Discord
def checkout(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        
        if request.user.is_authenticated:
            customer_name = request.user.username
        else:
            customer_name = request.POST.get('customer_name')

        if not cart:
            # ✅ แก้เป็น store:product_list
            return redirect('store:product_list')

        total_price = 0
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            total_price += product.price * quantity

        order = Order.objects.create(
            customer_name=customer_name,
            total_price=total_price,
            paid=False
        )

        discord_message = f"🔔 **ออเดอร์ใหม่มาแล้ว! (#{order.id})**\n"
        discord_message += f"👤 ลูกค้า: **{customer_name}**\n"
        discord_message += "---------------------------------\n"

        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )
            discord_message += f"📦 {product.name} x {quantity} = {product.price * quantity} บ.\n"

        discord_message += "---------------------------------\n"
        discord_message += f"💰 **ยอดรวม: {total_price} บาท**"

        webhook_url = 'https://discord.com/api/webhooks/1458009167381139509/1gSu6Hhe-EQcwKE90Jd8Pko4yTm9S1kFjU2IDxB67arMUeBR2fTHUgyBjuMuwpQJcYsy'
        try:
            requests.post(webhook_url, json={'content': discord_message})
        except:
            print("ส่ง Discord ไม่ผ่าน แต่บันทึก DB แล้ว")

        del request.session['cart']
        return render(request, 'store/success.html')
        
    # ✅ แก้เป็น store:cart_detail
    return redirect('store:cart_detail')

@login_required
def my_orders(request):
    orders = Order.objects.filter(customer_name=request.user.username).order_by('-created_at')
    return render(request, 'store/my_orders.html', {'orders': orders})

def add_product(request):
    if not request.user.is_superuser:
        # ✅ แก้เป็น store:product_list
        return redirect('store:product_list')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # ✅✅ จุดที่ Error เมื่อกี้ แก้เป็น store:product_list เรียบร้อย
            return redirect('store:product_list')
    else:
        form = ProductForm()

    return render(request, 'store/add_product.html', {'form': form})

# 1. ฟังก์ชันแก้ไขสินค้า (Edit)
def edit_product(request, pk):
    if not request.user.is_superuser:
        # ✅ แก้เป็น store:product_list
        return redirect('store:product_list')

    product = get_object_or_404(Product, id=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            # ✅ แก้เป็น store:product_list
            return redirect('store:product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'store/edit_product.html', {'form': form, 'product': product})

# 2. ฟังก์ชันลบสินค้า (Delete)
def delete_product(request, pk):
    if not request.user.is_superuser:
        # ✅ แก้เป็น store:product_list
        return redirect('store:product_list')

    product = get_object_or_404(Product, id=pk)

    if request.method == 'POST':
        product.delete()
        # ✅ แก้เป็น store:product_list
        return redirect('store:product_list')

    return render(request, 'store/delete_confirm.html', {'product': product})

def upload_slip(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer_name=request.user.username)

    if request.method == 'POST':
        slip = request.FILES.get('slip_image')
        if slip:
            # 1. บันทึกรูปภาพลง Database ก่อน
            order.slip_image = slip
            order.save()

            # 2. เตรียมข้อมูลส่ง Discord 🚀
            webhook_url = 'https://discord.com/api/webhooks/1460176250902544394/kanTURG_tRgy_vg2panKhr2RevWdJhYZ6RmtAQLPEqY2uzpkiuWr5BEXb9MGkNeemVwc'
            
            # ข้อความแจ้งเตือน
            message_content = f"💸 **มีการแจ้งชำระเงินเข้ามา!**\n"
            message_content += f"🧾 **Order:** #{order.id}\n"
            message_content += f"👤 **User:** {order.customer_name}\n"
            message_content += f"💰 **ยอดเงิน:** {order.total_price} บาท\n"
            message_content += f"---------------------------------"

            try:
                # สำคัญ! เทคนิคการส่งไฟล์รูปไป Discord
                # เราต้อง rewind ไฟล์ให้กลับไปจุดเริ่มต้นก่อนส่ง (เพราะ Django เพิ่งอ่านไปบันทึก DB)
                slip.seek(0) 

                files = {
                    'file': (slip.name, slip, slip.content_type)
                }
                data = {
                    'content': message_content
                }

                # ส่ง POST Request แบบมีไฟล์แนบ (multipart/form-data)
                requests.post(webhook_url, data=data, files=files)
                
            except Exception as e:
                print(f"Discord Error: {e}")

            return redirect('store:my_orders')

    return render(request, 'store/upload_slip.html', {'order': order})
def manual_logout(request):
    logout(request)
    return redirect('login') # อันนี้ถูกแล้ว (เพราะไปหน้า login กลาง)

def home(request):
    # อันนี้หน้า home ว่างๆ ถ้าไม่ได้ใช้ก็ทิ้งไว้ได้ครับ
    return render(request, 'store/home.html')