from django.contrib import admin

from .models import (
    Channel,
    EntryTarget,
    Market,
    Post,
    PostStatus,
    Predict,
    Symbol,
    TakeProfitTarget,
    SettingConfig
)

admin.site.register(Channel)
admin.site.register(Symbol)
admin.site.register(Market)
admin.site.register(PostStatus)
admin.site.register(Predict)
admin.site.register(TakeProfitTarget)
admin.site.register(EntryTarget)
admin.site.register(Post)
admin.site.register(SettingConfig)
# Register your models here.
