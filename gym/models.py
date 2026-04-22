from datetime import timedelta
from django.utils import timezone

from django.db import models
from django.db.models import Count
# Create your models here.
# need to add validation for balance to be non-negative and also add a method to update balance when a member makes a payment or uses the gym services.
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class MainModel(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
    
    def __str__(self):
        return self.name

class Branch(MainModel):
    name = models.CharField(max_length=225)
    location = models.CharField(max_length=225)
    member = models.ManyToManyField('Member', related_name='branches')
    trainer = models.ManyToManyField('Trainer', related_name='branches')

    def __str__(self):
        return self.name

class Member(MainModel):
    name = models.CharField(max_length=225)
    balance = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])


    @property
    def is_vip(self):
        return self.balance > 1000.0
    
    def __str__(self):
        return self.name

class Specialization(models.TextChoices):
    YOGA = 'Yoga', 'Yoga'
    CARDIO = 'Cardio', 'Cardio'
    STRENGTH_TRAINING = 'Strength Training', 'Strength Training'
    CROSSFIT = 'CrossFit', 'CrossFit'
    PILATES = 'Pilates', 'Pilates'
    ZUMBA = 'Zumba', 'Zumba'
class Trainer (MainModel):

    name = models.CharField(max_length=225)
    specialization = models.CharField(max_length=50, choices=Specialization.choices)


    def __str__(self):
        return self.name


class GymClassQuerySet(models.QuerySet):
    def trending_classes(self):
    
        self.annotate(
            members_count=Count('members')
        ).filter(
            members_count__gt=15
        ).order_by('-members_count')
    

class GymclassesManager(models.Manager):
    def get_queryset(self):
        return GymClassQuerySet(self.model, using=self._db)

    def trending_classes(self):
        return self.get_queryset().trending_classes()

class GymClass(MainModel):
    title = models.CharField(max_length=225, choices=Specialization.choices)
    best_price = models.FloatField(validators=[MinValueValidator(0.0)])
    start_date = models.DateField()
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    members = models.ManyToManyField(Member, related_name='gym_classes', blank=True)

    objects = GymclassesManager()


    def apply_discount(self):
        threshold_date = timezone.now().date() + timedelta(days=30)
        if self.start_date < threshold_date:
            raise ValidationError("Not applicable for discount")
        return self.best_price * .8
    
    def __str__(self):
        return self.title
    

class Equipment(MainModel):
    name = models.CharField(max_length=225)
    is_damaged = models.BooleanField(default=False)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)


    def __str__(self):
        return self.name

class DamagedEquipmentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_damaged=True)


class DamagedEquipment(Equipment):
    objects = DamagedEquipmentManager()

    class Meta:
        proxy = True
    def __str__(self):
        return super().__str__()