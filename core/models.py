from django.db import models

class Staging(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incrementing integer
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
    
class DesignCombineExistingMetricsMain(models.Model):
    id = models.AutoField(primary_key=True)
    sid = models.ForeignKey(Staging, on_delete=models.CASCADE, related_name='combine_existing_designs')
    delete_flag = models.BooleanField(default=False)

    def __str__(self):
        return f"Design #{self.id} for Staging {self.sid_id}"
    
class DesignCombineExistingMetricsSub(models.Model):
    id = models.AutoField(primary_key=True)
    group_id = models.IntegerField(blank=True, null=True)
    priority_id = models.IntegerField(blank=True, null=True)
    features = models.TextField(help_text="Comma-separated list of feature and binning values", blank=True, null=True)
    metric = models.CharField(max_length=100, blank=True, null=True)
    threshold = models.FloatField(blank=True, null=True)
    weightage = models.FloatField(blank=True, null=True)
    next_condition = models.BooleanField(default=False)
    delete_flag = models.BooleanField(default=False)

    def __str__(self):
        return f"Design #{self.id} for Staging {self.group_id}"