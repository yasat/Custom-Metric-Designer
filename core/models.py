from django.db import models

class Staging(models.Model):
    id = models.AutoField(primary_key=True)
    pid = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    perspective = models.CharField(max_length=50, blank=True, null=True)
    metric_type = models.CharField(max_length=50, blank=True, null=True)

    priority = models.IntegerField(default=0, blank=True, null=True)

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
    
class DesignCustomOwnMetric(models.Model):
    id = models.AutoField(primary_key=True)
    sid = models.ForeignKey(Staging, on_delete=models.CASCADE)
    probability_type = models.CharField(max_length=100, blank=True, null=True)
    boolean_operator = models.CharField(max_length=10, blank=True, null=True)
    order = models.IntegerField(default=0)
    delete_flag = models.BooleanField(default=False)

    side = models.CharField(
        max_length=3,
        choices=[("LHS", "Left"), ("RHS", "Right")],
        blank=True,
        null=True,
        help_text="Used only in compare mode to distinguish logic sides."
    )

    def __str__(self):
        return f"CustomOwnMetric #{self.id} ({self.side})"

class DesignCustomOwnCondition(models.Model):
    metric = models.ForeignKey(DesignCustomOwnMetric, on_delete=models.CASCADE, related_name='conditions')
    feature = models.CharField(max_length=100)
    binning = models.CharField(max_length=255, blank=True, null=True)
    logic_with_next = models.CharField(max_length=15, blank=True, null=True)

class DesignCustomOwnGlobal(models.Model):
    sid = models.OneToOneField(Staging, on_delete=models.CASCADE, related_name='custom_own_global')
    metric_name = models.CharField(max_length=100)
    threshold = models.FloatField(null=True, blank=True)

class DesignProceduralMetric(models.Model):
    id = models.AutoField(primary_key=True)
    sid = models.ForeignKey(Staging, on_delete=models.CASCADE, related_name='procedural_designs')
    label_type = models.CharField(max_length=50)
    boolean_operator = models.CharField(max_length=15, blank=True, null=True)
    order = models.IntegerField(default=0)
    delete_flag = models.BooleanField(default=False)

    preview = models.TextField(blank=True)

    def __str__(self):
        return f"ProceduralMetric #{self.id} for Staging {self.sid_id}"


class DesignProceduralCondition(models.Model):
    metric = models.ForeignKey(DesignProceduralMetric, on_delete=models.CASCADE, related_name='conditions')
    feature = models.CharField(max_length=100)
    value = models.CharField(max_length=100, blank=True, null=True)
    logic_with_next = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.feature}[{self.value}]"


class DesignProceduralGlobal(models.Model):
    sid = models.OneToOneField(Staging, on_delete=models.CASCADE, related_name='procedural_global')
    metric_name = models.CharField(max_length=100)
    threshold = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"ProceduralGlobal for Staging {self.sid_id}"
    
class AffordabilityDesign(models.Model):
    id = models.AutoField(primary_key=True)
    staging_id = models.OneToOneField(Staging, on_delete=models.CASCADE, related_name='AffordabilityDesign')
    metric_name = models.CharField(max_length=255, blank=True)
    threshold = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    delete_flag = models.BooleanField(default=False)

    def __str__(self):
        return self.metric_name or f"Affordability-{self.staging_id}"


class AffordabilityCard(models.Model):
    SIDE_CHOICES = [("LHS", "Left Side"), ("RHS", "Right Side")]
    OPERATOR_CHOICES = [
        ("=", "="), ("!=", "≠"), ("<", "<"), ("<=", "≤"), (">", ">"), (">=", "≥")
    ]

    design = models.ForeignKey(AffordabilityDesign, on_delete=models.CASCADE, related_name="cards")
    side = models.CharField(max_length=3, choices=SIDE_CHOICES)
    feature = models.CharField(max_length=255)
    operator = models.CharField(max_length=5, choices=OPERATOR_CHOICES)
    value = models.CharField(max_length=255)
    delete_flag = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.feature} {self.operator} {self.value} ({self.side})"