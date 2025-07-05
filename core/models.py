from django.db import models

class Staging(models.Model):
    id = models.AutoField(primary_key=True)
    pid = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    perspective = models.CharField(max_length=50, blank=True, null=True)
    metric_type = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Staging {self.id}"
    
class DesignExistingMetrics(models.Model):
    id = models.AutoField(primary_key=True)
    sid = models.ForeignKey(Staging, on_delete=models.CASCADE, related_name='existing_designs')
    features = models.TextField(help_text="Comma-separated list of feature and binning values", blank=True, null=True)
    metric = models.CharField(max_length=100, blank=True, null=True)
    threshold = models.FloatField(blank=True, null=True)
    delete_flag = models.BooleanField(default=False)

    def __str__(self):
        return f"Design #{self.id} for Staging {self.sid_id}"

class DesignCombineMetrics(models.Model):
    id = models.AutoField(primary_key=True)
    sid = models.ForeignKey(Staging, on_delete=models.CASCADE, related_name='combined_designs')
    features = models.TextField(blank=True, null=True)
    metric = models.CharField(max_length=100, blank=True, null=True)
    threshold = models.FloatField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    group_level = models.IntegerField(null=True, blank=True, help_text="Indicates the logical chain level.")
    boolean_operator = models.CharField(
        max_length=10,
        choices=[("AND", "AND"), ("OR", "OR")],
        blank=True,
        null=True,
        help_text="Boolean operator applied after this metric, chaining to the next"
    )
    order = models.IntegerField(default=0)
    delete_flag = models.BooleanField(default=False)

    def __str__(self):
        return f"CombinedMetric #{self.id} for Staging {self.sid_id}"