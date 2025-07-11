from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from core.models import *
from .AI_model import *

from collections import defaultdict

FAIRNESS_METRIC_MAP = {
    "demographic_parity": demographic_parity,
    "equal_opportunity": equal_opportunity,
    "predictive_equality": predictive_equality,
    "outcome_test": outcome_test,
    "equalized_odds": equalized_odds,
    "conditional_statistical_parity": conditional_statistical_parity,
    "counterfactual_fairness": counterfactual_fairness,
}


def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)

def render_metric_preview(metric, staging):
    if isinstance(metric, DesignExistingMetrics):
        return render_existing_preview(metric)

    elif isinstance(metric, DesignCombineMetrics):
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

    try:
        protected_df, non_protected_df, prot_cols, nonprot_cols = parse_feature_tags(
            metric.features,
            return_columns=True
        )
    except Exception as e:
        return f"<div class='alert alert-danger'>Error parsing features: {str(e)}</div>"

    threshold = (metric.threshold or 0.0)
    metric_id = (metric.metric or "").lower().strip()

    try:
        if metric_id == "counterfactual_fairness":
            if not (prot_cols and nonprot_cols):
                raise ValueError("Counterfactual fairness requires 1 protected and 1 non-protected feature.")
            col_a, col_b = prot_cols[0], nonprot_cols[0]
            assessment = counterfactual_fairness(data, col_a, col_b, threshold=threshold)

        elif metric_id == "conditional_statistical_parity":
            fn = FAIRNESS_METRIC_MAP[metric_id]
            assessment = fn(protected_df, non_protected_df, threshold, group_cols=[
                "Job", "Credit History", "Savings Account/Bonds"
            ])
        else:
            fn = FAIRNESS_METRIC_MAP.get(metric_id, FAIRNESS_METRIC_MAP["demographic_parity"])
            assessment = fn(protected_df, non_protected_df, threshold)

    except Exception as e:
        return f"<div class='alert alert-danger'>Metric computation error: {str(e)}</div>"

    for item in metric.features.split(","):
        item = item.strip()
        if not item:
            continue
        parts = item.split("[")
        label = parts[0].strip() + "[" + parts[1].strip()
        tag = parts[-1].replace("]", "").strip()
        if tag == "protected":
            protected.append(label)
        elif tag == "non-protected":
            non_protected.append(label)

    result_color = "success" if assessment["fair"] else "danger"

    return f"""
    <div class="card p-3 border-{result_color} border-2 mb-2">
        <div><strong>Protected:</strong> {' AND '.join(protected)}</div>
        <div><strong>Non-Protected:</strong> {' AND '.join(non_protected)}</div>
        <div><strong>Metric:</strong> {metric.metric}</div>
        <div><strong>Threshold:</strong> {metric.threshold}%</div>
        <div><strong>Value:</strong> {assessment['value']}</div>
        <div><strong>Result:</strong> <span class="text-{result_color}">{'Fair' if assessment['fair'] else 'Unfair'}</span></div>
    </div>
    """


def render_combine_existing_preview(staging):
    designs = DesignCombineMetrics.objects.filter(sid=staging, delete_flag=False).order_by('group_level', 'order')
    if not designs.exists():
        return "<div class='alert alert-warning'>No combined designs found.</div>"

    group_map = defaultdict(list)
    for d in designs:
        group_map[d.group_level or 0].append(d)

    multiple_groups = len(group_map.keys()) > 1
    all_blocks = []
    final_result = False
    resolved_group = None
    group_logic_results = {}
    has_custom_operator = False

    for group_level in sorted(group_map.keys()):
        group_blocks = []
        logic_chain = []

        for d in group_map[group_level]:
            protected = []
            non_protected = []

            try:
                protected_df, non_protected_df, prot_cols, nonprot_cols = parse_feature_tags(
                    d.features,
                    return_columns=True
                )
            except Exception as e:
                block = f"<div class='card p-2 m-1 text-bg-danger'>Error parsing: {str(e)}</div>"
                group_blocks.append(block)
                logic_chain.append((False, d.boolean_operator or "AND"))
                continue

            threshold = (d.threshold or 0.0)
            metric_id = (d.metric or "").lower().strip()

            try:
                if metric_id == "counterfactual_fairness":
                    if not (prot_cols and nonprot_cols):
                        raise ValueError("Counterfactual fairness requires 1 protected and 1 non-protected feature.")
                    col_a, col_b = prot_cols[0], nonprot_cols[0]
                    result = counterfactual_fairness(data, col_a, col_b, threshold=threshold)
                elif metric_id == "conditional_statistical_parity":
                    fn = FAIRNESS_METRIC_MAP[metric_id]
                    result = fn(protected_df, non_protected_df, threshold, group_cols=[
                        "Job", "Credit History", "Savings Account/Bonds"
                    ])
                else:
                    fn = FAIRNESS_METRIC_MAP.get(metric_id, FAIRNESS_METRIC_MAP["demographic_parity"])
                    result = fn(protected_df, non_protected_df, threshold)
            except Exception as e:
                result = {"value": "-", "threshold": threshold, "fair": False}
                block = f"<div class='card p-2 m-1 text-bg-danger'>Metric error: {str(e)}</div>"
                group_blocks.append(block)
                logic_chain.append((False, d.boolean_operator or "AND"))
                continue

            # Extract label text
            for item in d.features.split(","):
                item = item.strip()
                if not item:
                    continue
                parts = item.split("[")
                label = parts[0].strip() + "[" + parts[1].strip()
                tag = parts[-1].replace("]", "").strip()
                if tag == "protected":
                    protected.append(label)
                elif tag == "non-protected":
                    non_protected.append(label)

            block = f"""<div class='card p-2 m-1'>
                <strong>Group Level:</strong> {group_level}<br>
                <strong>Protected:</strong> {' AND '.join(protected)}<br>
                <strong>Non-Protected:</strong> {' AND '.join(non_protected)}<br>
                <strong>Metric:</strong> {d.metric}<br>
                <strong>Threshold:</strong> {d.threshold}%<br>
                <strong>Value:</strong> {result['value']}<br>
                <strong>Result:</strong> {"Fair" if result['fair'] else "Unfair"}
            </div>"""
            group_blocks.append(block)

            op = d.boolean_operator or "AND"
            if op not in ["AND", "OR"]:
                has_custom_operator = True

            logic_chain.append((result["fair"], op))

        custom_op_found = any(op not in ["AND", "OR"] for _, op in logic_chain)

        if custom_op_found:
            group_result = None
        else:
            group_result = logic_chain[0][0] if logic_chain else False
            prev_op = None
            for val, op in logic_chain:
                if prev_op is None:
                    prev_op = op
                    continue
                if prev_op == "AND":
                    group_result = group_result and val
                elif prev_op == "OR":
                    group_result = group_result or val
                prev_op = op

        group_logic_results[group_level] = group_result

        visual = ""
        for i, block in enumerate(group_blocks):
            visual += block
            if i < len(group_blocks) - 1:
                visual += f"<div class='text-center'><strong>{logic_chain[i][1]}</strong></div>"

        if multiple_groups:
            if group_result is None:
                visual += f"<div class='alert alert-warning'>Group Level {group_level} Result: <strong>Researcher input required due to custom operator</strong></div>"
            else:
                visual += f"<div class='alert alert-secondary'>Group Level {group_level} Result: <strong>{'Fair' if group_result else 'Unfair'}</strong></div>"

        all_blocks.append((group_level, visual))

    # Evaluate final result
    if has_custom_operator:
        final_result = None
    else:
        if multiple_groups:
            for group_level in sorted(group_logic_results.keys()):
                if group_logic_results[group_level]:
                    final_result = True
                    resolved_group = group_level
                    break
            else:
                final_result = False
        else:
            final_result = next(iter(group_logic_results.values()), False)

    final_html = ""
    for _, block_html in all_blocks:
        final_html += block_html + "<hr>"

    # Final result rendering
    if final_result is None:
        result_text = "<strong>Final Combined Result:</strong> <span class='text-warning'>Researcher input required due to custom operator.</span>"
    else:
        result_text = f"<strong>Final Combined Result:</strong> {'Fair' if final_result else 'Unfair'}"
        if multiple_groups:
            result_text += f"<br><strong>Resolved At Group Level:</strong> {resolved_group}"

    final_html += f"""
        <div class='alert alert-info'>
            {result_text}
        </div>
    """

    return final_html


def render_custom_preview(staging):
    lhs_cards = DesignCustomOwnMetric.objects.filter(sid=staging, side="LHS", delete_flag=False).order_by('order')
    rhs_cards = DesignCustomOwnMetric.objects.filter(sid=staging, side="RHS", delete_flag=False).order_by('order')
    combine_cards = DesignCustomOwnMetric.objects.filter(sid=staging, side__isnull=True, delete_flag=False).order_by('order')

    def build_block(cards, threshold=None):
        blocks = []
        for i, card in enumerate(cards):
            conds = card.conditions.all().order_by('id')
            conditions_str = "<br>".join([
                f"{c.feature} ∈ [{(c.binning or "").strip().split("[")[-1].strip("]")}]" if c.binning else c.feature
                for c in conds
            ])

            block = f"""
            <div class="card mb-2 p-2">
                <strong>Probability Type:</strong> {card.probability_type}<br>
                <strong>Conditions:</strong><br>
                {conditions_str}<br>
                <strong>Threshold:</strong> {threshold or 'N/A'}<br>
            </div>
            """

            blocks.append(block)

            if card.boolean_operator and i < len(cards) - 1:
                blocks.append(f"<div class='text-center'><strong>{card.boolean_operator}</strong></div>")

        return "\n".join(blocks)

    # Compare Mode: LHS vs RHS
    if lhs_cards.exists() or rhs_cards.exists():
        try:
            global_cfg = DesignCustomOwnGlobal.objects.get(sid=staging)
            threshold = global_cfg.threshold or 0.1
        except DesignCustomOwnGlobal.DoesNotExist:
            threshold = 0.1  # fallback
        return f"""
        <div class='row'>
            <div class='col'>
                <h6 class='text-primary'>LHS</h6>
                {build_block(lhs_cards, threshold)}
            </div>
            <div class='col text-center align-self-center'>
                <strong class='text-danger'>VS</strong>
            </div>
            <div class='col'>
                <h6 class='text-primary'>RHS</h6>
                {build_block(rhs_cards, threshold)}
            </div>
        </div>
        """
    
    # Combine Mode: just render all blocks
    elif combine_cards.exists():
        try:
            global_cfg = DesignCustomOwnGlobal.objects.get(sid=staging)
            threshold = global_cfg.threshold or 0.1
        except DesignCustomOwnGlobal.DoesNotExist:
            threshold = 0.1  # fallback

        result = evaluate_combine_custom_own(combine_cards, data, threshold)
        result_color = "success" if result["fair"] else "danger"
        result_text = "Fair" if result["fair"] else "Unfair"

        result_html = f"""
        <div class='alert alert-{result_color}'>
            <strong>Final Result:</strong> <span class='text-{result_color}'>{result_text}</span><br>
            <strong>Threshold:</strong> {threshold}
        </div>
        """

        return f"""
        <div class='custom-combine-preview'>
            {build_block(combine_cards, threshold)}
            {result_html}
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
