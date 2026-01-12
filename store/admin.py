from django.contrib import admin
from .models import Product, Order, OrderItem
from django.utils.html import format_html

# 1. ปรับแต่งหน้า Admin ของ Order
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'total_price', 'paid', 'show_slip', 'created_at')
    list_editable = ('paid',) # ติ๊ก Paid ได้เลยจากหน้าแรก

    def show_slip(self, obj):
        if obj.slip_image:
            # สร้างลิงก์ให้กดดูรูปได้
            return format_html('<a href="{}" target="_blank">View Slip</a>', obj.slip_image.url)
        return "No Slip"
    show_slip.short_description = "Payment Slip"

# 2. ลงทะเบียน Model (เช็คว่ามีอย่างละ 1 บรรทัดเท่านั้น!)
admin.site.register(Product)
admin.site.register(Order, OrderAdmin) # อันนี้ใช้คู่กับ Class ข้างบน
admin.site.register(OrderItem)