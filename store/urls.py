from django.urls import path
from . import views

# ✅ ต้องมีบรรทัดนี้ เพื่อบอกว่าลิ้งก์ทั้งหมดในนี้เป็นของแอป 'store'
app_name = 'store'

urlpatterns = [
    # หน้าร้านค้า (Home ของ Store)
    path('', views.product_list, name='store'), 

    # ออกจากระบบ (ตั้งชื่อว่า manual_logout ให้ชัดเจน ไม่ตีกับระบบ)
    path('logout/', views.manual_logout, name='manual_logout'),

    # สินค้า
    path('shop/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    
    # ตะกร้าสินค้า
    path('cart/', views.cart_detail, name='cart_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
    
    # คำสั่งซื้อ
    path('my-orders/', views.my_orders, name='my_orders'),
    
    # จัดการสินค้า (Admin)
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:pk>/', views.delete_product, name='delete_product'),

    path('download/<int:product_id>/', views.download_script, name='download_script'),
    path('upload-slip/<int:order_id>/', views.upload_slip, name='upload_slip'),
]