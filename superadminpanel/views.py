from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404
from core.models import *

from collections import defaultdict

def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)

def get_combine_existing_grouped(staging_id):
    # Fetch and group by level
    entries = DesignCombineMetrics.objects.filter(sid=staging_id, delete_flag="N").order_by("group_level", "order")

    grouped_metrics = defaultdict(list)
    for entry in entries:
        text = f"({entry.weight:.1f}% × ({entry.features}[{entry.metric}], {entry.threshold}%))"
        grouped_metrics[entry.group_level].append({
            "text": text,
            "operator": entry.boolean_operator if entry.boolean_operator else None
        })

    return dict(grouped_metrics)

@superuser_required
def superadmin_dashboard(request):
    staging_data = Staging.objects.values('pid').exclude(pid__isnull=True).exclude(pid__exact='').distinct()
    participants = []

    for entry in staging_data:
        pid = entry['pid']
        sid_set = Staging.objects.filter(pid=pid).values_list('id', flat=True)

        participants.append({
            'pid': pid,
            'existing': DesignExistingMetrics.objects.filter(sid__in=sid_set, delete_flag=False).count(),
            'combine_existing': DesignCombineMetrics.objects.filter(sid__in=sid_set, delete_flag=False).count(),
            'own_combine': DesignCustomOwnMetric.objects.filter(sid__in=sid_set, side__isnull=True, delete_flag=False).count(),
            'own_compare': DesignCustomOwnMetric.objects.filter(sid__in=sid_set, side__in=['LHS', 'RHS'], delete_flag=False).count(),
            'procedural': DesignProceduralMetric.objects.filter(sid__in=sid_set, delete_flag=False).count(),
            'affordability': AffordabilityCard.objects.filter(design__staging_id__in=sid_set, delete_flag=False).count(),
        })

    return render(request, 'superadminpanel/dashboard.html', {'participants': participants})


@superuser_required
def superadmin_view_metrics(request, pid):
    staging_ids = list(Staging.objects.filter(pid=pid).values_list('id', flat=True))

    combine_entries = DesignCombineMetrics.objects.filter(sid__in=staging_ids, delete_flag=False).order_by("sid", "group_level", "order")

    combine_grouped = defaultdict(lambda: defaultdict(list))

    for entry in combine_entries:
        text = f"({entry.weight:.1f}% × ({entry.features}[{entry.metric}], {entry.threshold}%))"
        combine_grouped[entry.sid][entry.group_level].append({
            "text": text,
            "operator": entry.boolean_operator if entry.boolean_operator else None
        })

    data = {
        'pid': pid,
        'existing': DesignExistingMetrics.objects.filter(sid__in=staging_ids, delete_flag=False),
        'combine_existing': combine_grouped,
        'own_combine': DesignCustomOwnMetric.objects.filter(sid__in=staging_ids, side__isnull=True, delete_flag=False),
        'own_compare_lhs': DesignCustomOwnMetric.objects.filter(sid__in=staging_ids, side='LHS', delete_flag=False),
        'own_compare_rhs': DesignCustomOwnMetric.objects.filter(sid__in=staging_ids, side='RHS', delete_flag=False),
        'procedural': DesignProceduralMetric.objects.filter(sid__in=staging_ids, delete_flag=False),
        'affordability': AffordabilityCard.objects.filter(design__staging_id__in=staging_ids, delete_flag=False),
    }

    return render(request, 'superadminpanel/view_metrics.html', data)
