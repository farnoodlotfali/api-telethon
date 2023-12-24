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


class Symbol(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=20, editable=True)

    def __str__(self):
        return f"{self.name}"


class Market(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=20, editable=True)

    def __str__(self):
        return f"{self.name}"


class PostStatus(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=35, editable=True)

    def __str__(self):
        return f"{self.name}"


class Post(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateTimeField(editable=True)
    channel_id = models.CharField(max_length=50)
    message_id = models.CharField(max_length=50)
    message = models.CharField(max_length=6000, editable=True)
    reply_to_msg_id = models.CharField(max_length=15, null=True)
    edit_date = models.CharField(max_length=100, editable=True, null=True)
    is_predict_msg = models.BooleanField(default=False, editable=True, null=True)

    def __str__(self):
        return f"{self.message_id} {self.channel_id}"


class Predict(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    status = models.ForeignKey(PostStatus, on_delete=models.CASCADE)
    position = models.CharField(max_length=50, editable=True)
    leverage = models.CharField(max_length=50, editable=True)
    stopLoss = models.CharField(max_length=50, editable=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.symbol.name} {self.market.name} {self.position} {self.leverage}"


class EntryTarget(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    index = models.CharField(max_length=50)
    value = models.CharField(max_length=50)
    active = models.BooleanField(default=False, editable=True, null=True)
    period = models.CharField(max_length=60, null=True)
    date = models.DateTimeField(editable=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.post.message_id} {self.value} {self.active}"


class TakeProfitTarget(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    index = models.CharField(max_length=50)
    value = models.CharField(max_length=50)
    active = models.BooleanField(default=False, editable=True, null=True)
    period = models.CharField(max_length=60, null=True)
    date = models.DateTimeField(editable=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.post.message_id} {self.value} {self.active}"
