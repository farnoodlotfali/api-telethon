from django.contrib import admin
from .models import (
    Channel,
    PostInitial,
    Symbol,
    Market,
    PostStatus,
    Predict,
    TakeProfitTarget,
    EntryTarget,
    Post,
)

admin.site.register(PostInitial)
admin.site.register(Channel)
admin.site.register(Symbol)
admin.site.register(Market)
admin.site.register(PostStatus)
admin.site.register(Predict)
admin.site.register(TakeProfitTarget)
admin.site.register(EntryTarget)
admin.site.register(Post)

# Register your models here.
