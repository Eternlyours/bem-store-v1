from django.contrib import admin
from .models import OrderBoard


@admin.register(OrderBoard)
class OrderBoardAdmin(admin.ModelAdmin):
    change_list_template = 'admin/dashboard-orders.html'

    def changelist_view(self, request):
        response = super().changelist_view(
            request
        )
        try:
            queryset = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response
        
        response.context_data['orders'] = queryset
        return response