from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from core.models import *

from collections import defaultdict

def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)

def render_metric_preview(metric, staging):
    if isinstance(metric, DesignExistingMetrics):
        return render_existing_preview(metric)

    elif isinstance(metric, DesignCombineMetrics):
        print("again")
        return render_combine_existing_preview(staging)

    elif isinstance(metric, DesignCustomOwnMetric):
        return render_custom_preview(staging)

    elif isinstance(metric, DesignProceduralMetric):
        return render_procedural_preview(staging)

    elif isinstance(metric, AffordabilityDesign):
        return render_affordability_preview(metric)

    return "Preview not available"

def render_existing_preview(metric):
    protected = []
    non_protected = []

    for item in metric.features.split(","):
        item = item.strip()
        if not item: continue
        parts = item.split("[")
        label = parts[0].strip()
        tag = parts[-1].replace("]", "").strip()
        if tag == "protected":
            protected.append(label)
        elif tag == "non-protected":
            non_protected.append(label)

    return f"""
    <span class='badge bg-primary'>Protected:</span> {' AND '.join(protected)} |
    <span class='badge bg-secondary'>Non-Protected:</span> {' AND '.join(non_protected)} |
    <span class='badge bg-success'>Metric:</span> {metric.metric} |
    <span class='badge bg-warning text-dark'>Threshold:</span> {metric.threshold}%
    """
def render_combine_existing_preview(staging):
    designs = DesignCombineMetrics.objects.filter(sid=staging, delete_flag=False).order_by('order')
    blocks = []

    for d in designs:
        protected = []
        non_protected = []

        for item in d.features.split(","):
            item = item.strip()
            if not item: continue
            parts = item.split("[")
            label = parts[0].strip()
            tag = parts[-1].replace("]", "").strip()
            if tag == "protected":
                protected.append(label)
            elif tag == "non-protected":
                non_protected.append(label)

        block = f"""<div class='card p-2 m-1'>
            <strong>Protected:</strong> {' AND '.join(protected)}<br>
            <strong>Non-Protected:</strong> {' AND '.join(non_protected)}<br>
            <strong>Metric:</strong> {d.metric}<br>
            <strong>Threshold:</strong> {d.threshold}%
        </div>"""
        blocks.append((block, d.boolean_operator or "AND"))

    final_html = ""
    for i in range(len(blocks)):
        block, op = blocks[i]
        print(i, (block, op))
        final_html += block
        if i < len(blocks) - 1:
            final_html += f"<div class='text-center'><strong>{op}</strong></div>"
    
    return final_html

def render_custom_preview(staging):
    lhs_cards = DesignCustomOwnMetric.objects.filter(sid=staging, side="LHS", delete_flag=False).order_by('order')
    rhs_cards = DesignCustomOwnMetric.objects.filter(sid=staging, side="RHS", delete_flag=False).order_by('order')
    combine_cards = DesignCustomOwnMetric.objects.filter(sid=staging, side__isnull=True, delete_flag=False).order_by('order')

    def build_block(cards):
        blocks = []
        for i, card in enumerate(cards):
            conds = card.conditions.all().order_by('id')
            conditions_str = "<br>".join([c.binning or c.feature for c in conds])

            block = f"""
            <div class="card mb-2 p-2">
                <strong>Probability Type:</strong> {card.probability_type}<br>
                <strong>Conditions:</strong><br>
                {conditions_str}
            </div>
            """

            blocks.append(block)

            # Add boolean operator *between* cards
            if card.boolean_operator and i < len(cards) - 1:
                blocks.append(f"<div class='text-center'><strong>{card.boolean_operator}</strong></div>")

        return "\n".join(blocks)

    # Compare Mode: LHS vs RHS
    if lhs_cards.exists() or rhs_cards.exists():
        return f"""
        <div class='row'>
            <div class='col'>
                <h6 class='text-primary'>LHS</h6>
                {build_block(lhs_cards)}
            </div>
            <div class='col text-center align-self-center'>
                <strong class='text-danger'>VS</strong>
            </div>
            <div class='col'>
                <h6 class='text-primary'>RHS</h6>
                {build_block(rhs_cards)}
            </div>
        </div>
        """
    
    # Combine Mode: just render all blocks
    elif combine_cards.exists():
        return f"""
        <div class='custom-combine-preview'>
            {build_block(combine_cards)}
        </div>
        """
    
    return "No custom logic defined"


def render_procedural_preview(staging):
    designs = DesignProceduralMetric.objects.filter(sid=staging, delete_flag=False).order_by('order')
    badges = []

    for d in designs:
        conds = d.conditions.all().order_by('id')
        if not conds.exists():
            continue

        c = conds[0]

        if d.label_type == "contribute":
            label = f"{c.feature} contributes"
        elif d.label_type == "does_not_contribute":
            label = f"{c.feature} does NOT contribute"
        elif d.label_type == "feature_importance":
            label = f"{c.feature} importance {c.logic_with_next} {c.value}"
        elif d.label_type == "importance_by_group":
            label = f"{c.feature} group diff {c.logic_with_next} {c.value}"
        elif d.label_type == "pre_checks":
            label = f"{c.feature} decision = {c.value}"
        else:
            label = f"{c.feature} ({d.label_type})"

        badges.append(f"<span class='badge bg-secondary m-1'>{label}</span>")

    return "<div>" + " ".join(badges) + "</div>" if badges else "<em>No procedural logic defined.</em>"


def render_affordability_preview(design):
    lhs = design.cards.filter(side="LHS", delete_flag=False).order_by('created_at')
    rhs = design.cards.filter(side="RHS", delete_flag=False).order_by('created_at')

    def build_card(side_label, cards):
        conditions = "<br>".join([f"{c.feature} {c.operator} {c.value}" for c in cards]) or "<em>No conditions</em>"
        return f"""
        <div class="card p-3 mb-2">
            <h6 class="text-primary">{side_label}</h6>
            {conditions}
        </div>
        """

    lhs_block = build_card("Credit Conditions (LHS)", lhs)
    rhs_block = build_card("Personal Conditions (RHS)", rhs)

    return f"""
    <div class="row">
        <div class="col-md-5">
            {lhs_block}
        </div>
        <div class="col-md-2 text-center align-self-center">
            <strong class="text-danger">VS</strong>
        </div>
        <div class="col-md-5">
            {rhs_block}
        </div>
    </div>
    """

@superuser_required
def superadmin_dashboard(request):
    staging_data = Staging.objects.values('pid').exclude(pid__isnull=True).exclude(pid__exact='').distinct()
    participants = []

    for entry in staging_data:
        pid = entry['pid']
        sid_set = list(Staging.objects.filter(pid=pid).values_list('id', flat=True))

        # Count unique designs by staging ID
        existing_count = DesignExistingMetrics.objects.filter(sid__in=sid_set, delete_flag=False).values('sid').distinct().count()
        combine_existing_count = DesignCombineMetrics.objects.filter(sid__in=sid_set, delete_flag=False).values('sid').distinct().count()

        # Custom Logic: count distinct sid once per staging type
        own_combine_count = DesignCustomOwnMetric.objects.filter(
            sid__in=sid_set, side__isnull=True, delete_flag=False
        ).values('sid').distinct().count()

        own_compare_count = DesignCustomOwnMetric.objects.filter(
            sid__in=sid_set, side__in=["LHS", "RHS"], delete_flag=False
        ).values('sid').distinct().count()

        # Procedural: count only if conditions exist
        procedural_sids = DesignProceduralMetric.objects.filter(
            sid__in=sid_set, delete_flag=False
        ).values_list('sid', flat=True).distinct()
        procedural_count = Staging.objects.filter(id__in=procedural_sids).count()

        # Affordability: based on existence of cards under each design
        affordability_sids = AffordabilityCard.objects.filter(
            design__staging_id__in=sid_set, delete_flag=False
        ).values_list('design__staging_id', flat=True).distinct()
        affordability_count = Staging.objects.filter(id__in=affordability_sids).count()

        participants.append({
            'pid': pid,
            'existing': existing_count,
            'combine_existing': combine_existing_count,
            'own_combine': own_combine_count,
            'own_compare': own_compare_count,
            'procedural': procedural_count,
            'affordability': affordability_count,
        })

    return render(request, 'superadminpanel/dashboard.html', {'participants': participants})


@superuser_required
def superadmin_view_metrics(request, pid):
    staging_ids = list(Staging.objects.filter(pid=pid).values_list('id', flat=True))

    staging_objects = []

    if pid:
        staging_objects = Staging.objects.filter(pid=pid)

    staging_data = []

    print(len(staging_objects), "staging objects found for pid:", pid)
    for staging in staging_objects:
        metrics = []

        # Existing metrics: individual entries
        if staging.metric_type == "existing":
            for m in staging.existing_designs.filter(delete_flag=False):
                metrics.append({
                    "type": "Existing",
                    "preview": render_metric_preview(m, staging),
                    "edit_url": f"{reverse('design_metric_features', args=[staging.id])}?edit={m.id}"
                })

        # Combine Existing: one combined preview
        elif staging.metric_type == "combine_existing":
            metrics.append({
                "type": "Combined",
                "preview": render_combine_existing_preview(staging),
                "edit_url": reverse('design_combine_existing_review_all', args=[staging.id])
            })

        # Custom Own: combine or compare, single logic block
        elif staging.metric_type == "custom_own" and staging.perspective == "outcome":
            metrics.append({
                "type": "Custom Logic",
                "preview": render_custom_preview(staging),
                "edit_url": reverse('custom_own_logic_review', args=[staging.id])
            })

        # Procedural: one edit button per staging, single preview of all cards
        if staging.perspective == "procedural" and staging.procedural_designs.exists():
            metrics.append({
                "type": "Procedural",
                "preview": render_procedural_preview(staging),
                "edit_url": reverse('procedural_builder', args=[staging.id])
            })

        # Affordability: one design per staging
        if hasattr(staging, 'AffordabilityDesign') and staging.AffordabilityDesign and not staging.AffordabilityDesign.delete_flag:
            metrics.append({
                "type": "Affordability",
                "preview": render_affordability_preview(staging.AffordabilityDesign),
                "edit_url": reverse('affordability_builder', args=[staging.id])
            })

        # Append all to staging_data
        staging_data.append({
            "id": staging.id,
            "category": staging.category,
            "perspective": staging.perspective,
            "metric_type": staging.metric_type,
            "metrics": metrics,
        })


    return render(request, 'superadminpanel/view_metrics.html', {
                            "pid": pid,
                            "staging_data": staging_data,
                        })
