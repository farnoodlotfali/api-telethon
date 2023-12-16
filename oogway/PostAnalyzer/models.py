from django.db import models


class Channel(models.Model):
    channel_id = models.CharField(max_length=50)
    name = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.name} {self.channel_id}"


class PostInitial(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateTimeField(max_length=100, editable=True, null=True)
    channel_id = models.CharField(max_length=50)
    message = models.CharField(max_length=6000, editable=True, null=True)
    message_id = models.CharField(max_length=50)
    reply_to_msg_id = models.CharField(max_length=15, null=True)
    edit_date = models.DateTimeField(max_length=100, editable=True, null=True)

    def __str__(self):
        return f"{self.message_id} {self.channel_id}"


# class Post(models.Model):
#     created_at = models.DateTimeField(auto_now_add=True)
#     date = models.DateTimeField(editable=True)
#     channel_id = models.CharField(max_length=50)
#     predict_id = models.CharField(max_length=50)
#     media_id = models.CharField(max_length=50)
#     message = models.CharField(max_length=6000, editable=True)
#     message_id = models.CharField(max_length=50)
#     reply_to_msg_id = models.CharField(max_length=15)
#     edit_date = models.CharField(max_length=100, editable=True)
#     is_predict_msg = models.BooleanField(default=False, editable=True)


#     def __str__(self):
#         return f"{self.message_id} {self.channel_id}"


# class Predict(models.Model):
#     created_at = models.DateTimeField(auto_now_add=True)
#     symbol_id = models.CharField(max_length=50, editable=True)
#     market_id = models.CharField(max_length=50)
#     position = models.CharField(max_length=50, editable=True)
#     leverage = models.CharField(max_length=50, editable=True)
#     stopLoss = models.CharField(max_length=50, editable=True)
#     entry_targets_id = models.CharField(max_length=50)
#     take_profit_targets_id = models.CharField(max_length=50)
#     status_id = models.CharField(max_length=50)

#     def __str__(self):
#         return f"{self.symbol_id} {self.market_id} {self.position} {self.leverage}"


# class EntryTargets(models.Model):
#     created_at = models.DateTimeField(auto_now_add=True)
#     index = models.CharField(max_length=50)
#     value = models.CharField(max_length=50)
#     active = models.BooleanField(default=False, editable=True)
#     period = models.CharField(max_length=50)
#     Date = models.DateTimeField()

#     def __str__(self):
#         return f"{self.value} {self.active} {self.period} "
