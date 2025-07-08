from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .features_data import FEATURES
from .metrics_data import METRICS

from .utils import get_design_model, get_operator_options, get_group_options
from collections import defaultdict
import json
from django.core.serializers.json import DjangoJSONEncoder

PROCEDURAL_LABELS = [
    ("contribute", "Contribute"),
    ("does_not_contribute", "Does not Contribute"),
    ("importance_by_group", "Importance by Group"),
    ("feature_importance", "Feature Importance"),
    ("pre_checks", "Pre-checks"),
]

PROBABILITY_LABELS = [
    ("predicted_true", "Predicted: True"),
    ("predicted_false", "Predicted: False"),
    ("ground_truth_true", "Ground Truth: True"),
    ("ground_truth_false", "Ground Truth: False"),
]

def get_valid_condition_labels(probability_type):
    if not probability_type:
        return []

    if probability_type.startswith("predicted"):
        return [l for l in PROBABILITY_LABELS if l[0].startswith("ground_truth")]
    elif probability_type.startswith("ground_truth"):
        return [l for l in PROBABILITY_LABELS if l[0].startswith("predicted")]

    return []

def home(request):

    if request.method == "POST":
        pid = request.POST.get("pid")

        request.session['pid'] = pid

        return redirect('fairness_category')

    return render(request, 'home.html')

def under_construction(request):
    return render(request, 'under_construction.html')

def fairness_category(request, staging_id=None):
    if staging_id:
        staging = get_object_or_404(Staging, id=staging_id)
    else:
        staging = None

    pid = request.session['pid'] if (request.session['pid'] != None and request.session['pid'].strip() != "") else "temp"
    print(pid)
    if request.method == "POST":
        selection = request.POST.get("fairness")

        if staging:
            staging.category = selection
            staging.save()
        else:
            staging = Staging.objects.create(category=selection, pid=pid)

        return redirect('fairness_perspective', staging_id=staging.id)

    if staging:
        breadcrumb = [
            {"label": staging.category, "url": None},
        ]
    else:
        breadcrumb = [
            {"label": "Fairness Category", "url": None},
        ]

    return render(request, "fairness_category.html", {
        "breadcrumb": breadcrumb,
        "staging_id": staging_id,
        "selected_category": staging.category if staging else None,
    })

def fairness_perspective(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)

    if request.method == "POST":
        perspective = request.POST.get("perspective")
        staging.perspective = perspective
        staging.save()
        return redirect('metric_type', staging_id=staging.id)

    if staging.perspective != None:
        breadcrumb = [
            {"label": staging.category, "url": "fairness_category_with_id"},
            {"label": staging.perspective, "url": None},
        ]
    else:
        breadcrumb = [
            {"label": staging.category, "url": "fairness_category_with_id"},
            {"label": "Fairness Perspective", "url": None},
        ]
    
    return render(request, "fairness_perspective.html", {
        "staging_id": staging.id,
        "breadcrumb": breadcrumb,
        "selected_perspective": staging.perspective,
    })

def metric_type(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)

    if(staging.perspective != "outcome"):
        staging.metric_type = "custom_own"
        staging.save()

        return redirect('summary', staging_id=staging.id)

    if request.method == "POST":
        metric_type = request.POST.get("metric_type")
        staging.metric_type = metric_type
        staging.save()

        return redirect('summary', staging_id=staging.id)

    if staging.metric_type != None:
        breadcrumb = [
            {"label": staging.category, "url": "fairness_category_with_id"},
            {"label": staging.perspective, "url": "fairness_perspective"},
            {"label": staging.metric_type, "url": None}
        ]
    else:
        breadcrumb = [
            {"label": staging.category, "url": "fairness_category_with_id"},
            {"label": staging.perspective, "url": "fairness_perspective"},
            {"label": "Metric Type", "url": None}
        ]
    
    return render(request, "metric_type.html", {
        "staging_id": staging.id,
        "breadcrumb": breadcrumb,
        "selected_metric_type": staging.metric_type,
    })

def summary(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)

    breadcrumb = [
        {"label": staging.category, "url": "fairness_category_with_id"},
        {"label": staging.perspective, "url": "fairness_perspective"},
        {"label": staging.metric_type, "url": "metric_type" if staging.perspective == "outcome" else None},
    ]

    return render(request, "summary.html", {
        "staging_id": staging.id,
        "breadcrumb": breadcrumb,
        "category": staging.category,
        "perspective": staging.perspective,
        "metric_type": staging.metric_type,
    })

def start_designing(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)

    metric_type = staging.metric_type

    if staging.perspective == 'outcome':
        if metric_type == "existing":
            return redirect('design_existing', staging_id=staging.id)
        elif metric_type == "combine_existing":
            return redirect('design_combine_existing', staging_id=staging.id)
        elif metric_type == "custom_own":
            return redirect('custom_own_intro', staging_id=staging.id)
        else:
            return HttpResponseBadRequest("Invalid metric type")
    elif staging.perspective == 'procedural':
        return redirect('procedural_intro', staging_id=staging.id)
    elif staging.perspective == 'affordability':
        return redirect('affordability_intro', staging_id=staging.id)
    else:
        return HttpResponseBadRequest("Invalid fairness perspective type")

def design_combine_existing_intro(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)

    if not request.session.get(f'design_id_{staging_id}'):
        design = DesignCombineMetrics.objects.create(sid=staging, order=0)
        print('here',design)
        request.session[f'design_id_{staging_id}'] = design.id
    
    print(request.session[f'design_id_{staging_id}'])

    return render(request, "design_combine_existing_intro.html", {
        "staging_id": staging.id
    })

def design_existing_intro(request, staging_id):

    staging = get_object_or_404(Staging, id=staging_id)

    if not request.session.get(f'design_id_{staging_id}'):
        design = DesignExistingMetrics.objects.create(sid=staging)
        request.session[f'design_id_{staging_id}'] = design.id
    else:
        design = get_object_or_404(DesignExistingMetrics, id=request.session[f'design_id_{staging_id}'])

    breadcrumb = [
        {"label": staging.category, "url": "fairness_category_with_id"},
        {"label": staging.perspective, "url": "fairness_perspective"},
        {"label": staging.metric_type, "url": "metric_type"},
    ]

    return render(request, "design_existing_intro.html", {
        "staging_id": staging_id,
        "breadcrumb": breadcrumb,
    })

def design_metric_features(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)
    Model = get_design_model(staging)

    edit_id = request.GET.get("edit")
    if edit_id:
        design = get_object_or_404(Model, id=edit_id)
        request.session[f'design_id_{staging_id}'] = design.id
    else:
        design_id = request.session[f'design_id_{staging_id}']
        print(design_id)
        design = get_object_or_404(Model, id=design_id)
        

    if request.method == "POST":
        features_str = request.POST.get("features")
        if features_str:
            design.features = features_str
            design.save()
            return redirect('design_metric_select_metric', staging_id=staging_id)

    breadcrumb = [
        {"label": staging.category, "url": "fairness_category_with_id"},
        {"label": staging.perspective, "url": "fairness_perspective"},
        {"label": staging.metric_type, "url": "metric_type"},
    ]

    if design.features:
        breadcrumb_cm = [{"label": design.features, "url": "design_metric_features"}]
    else:
        breadcrumb_cm = [{"label": "Select Features", "url": None}]

    selected = []
    if design.features:
        selected = [s.strip() for s in design.features.split(",") if s.strip()]

    return render(request, "design_existing_features.html", {
        "features": FEATURES,
        "staging_id": staging_id,
        "breadcrumb": breadcrumb,
        "breadcrumb_cm": breadcrumb_cm,
        "selected_features": selected,
    })

def design_metric_select_metric(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)
    Model = get_design_model(staging)
    design_id = request.session.get(f'design_id_{staging_id}')
    design = get_object_or_404(Model, id=design_id)

    if request.method == "POST":
        selected_metric = request.POST.get("selected_metric")
        if selected_metric:
            design.metric = selected_metric
            design.save()
            return redirect('design_metric_threshold', staging_id=staging_id)

    breadcrumb = [
        {"label": staging.category, "url": "fairness_category_with_id"},
        {"label": staging.perspective, "url": "fairness_perspective"},
        {"label": staging.metric_type, "url": "metric_type"},
    ]

    if design.metric:
        breadcrumb_cm = [
            {"label": design.features, "url": "design_metric_features"},
            {"label": design.metric, "url": "design_metric_select_metric"},
        ]
    else:
        breadcrumb_cm = [
            {"label": design.features, "url": "design_metric_features"},
            {"label": "Select Metric", "url": None},
        ]

    if staging.category == "individual":
        metrics = [m for m in METRICS if m['category'] == "Individual"]
    elif staging.category == "group":
        metrics = [m for m in METRICS if m['category'] == "Group"]
    else:
        metrics = METRICS

    return render(request, "design_existing_select_metric.html", {
        "staging_id": staging_id,
        "breadcrumb": breadcrumb,
        "breadcrumb_cm": breadcrumb_cm,
        "metrics": metrics,
        "selected_metric_id": design.metric,
    })

def design_metric_threshold(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)
    Model = get_design_model(staging)
    design_id = request.session.get(f'design_id_{staging_id}')
    design = get_object_or_404(Model, id=design_id)

    if request.method == "POST":
        threshold = request.POST.get("threshold")
        design.threshold = threshold
        design.save()
        return redirect('design_metric_summary', staging_id=staging_id)

    breadcrumb = [
        {"label": staging.category, "url": "fairness_category_with_id"},
        {"label": staging.perspective, "url": "fairness_perspective"},
        {"label": staging.metric_type, "url": "metric_type"},
    ]

    if design.threshold:
        breadcrumb_cm = [
            {"label": design.features, "url": "design_metric_features"},
            {"label": design.metric, "url": "design_metric_select_metric"},
            {"label": f"{design.threshold}%", "url": "design_metric_threshold"},
        ]
    else:
        breadcrumb_cm = [
            {"label": design.features, "url": "design_metric_features"},
            {"label": design.metric, "url": "design_metric_select_metric"},
            {"label": "Set a Threshold", "url": None},
        ]

    return render(request, "design_existing_threshold.html", {
        "staging_id": staging_id,
        "breadcrumb": breadcrumb,
        "breadcrumb_cm": breadcrumb_cm,
        "threshold": design.threshold if design.threshold is not None else "",
    })

def design_metric_summary(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)
    Model = get_design_model(staging)

    design_id = request.session.get(f'design_id_{staging_id}')
    design = get_object_or_404(Model, id=design_id)

    feature_items = []
    if design.features:
        for item in design.features.split(','):
            item = item.strip()
            if '[' in item and ']' in item:
                name = item.split('[')[0].strip()
                binning = item.split('[')[1].replace(']', '').strip()
                status = item.split('[')[2].replace(']', '').strip()
                feature_items.append({'name': name, 'binning': binning, 'status': status})
            elif item:
                feature_items.append({'name': item, 'binning': '', 'status': ''})

    breadcrumb = [
        {"label": staging.category, "url": "fairness_category_with_id"},
        {"label": staging.perspective, "url": "fairness_perspective"},
        {"label": staging.metric_type, "url": "metric_type"},
    ]

    breadcrumb_cm = [
        {"label": design.features, "url": "design_metric_features"},
        {"label": design.metric, "url": "design_metric_select_metric"},
        {"label": f"{design.threshold}%", "url": "design_metric_threshold"},
    ]

    return render(request, "design_existing_summary.html", {
        "staging_id": staging.id,
        "breadcrumb": breadcrumb,
        "breadcrumb_cm": breadcrumb_cm,
        "features": feature_items,
        "metric": design.metric,
        "threshold": design.threshold,
        "is_combined": staging.metric_type == "combine_existing",
    })

def design_save_new(request, staging_id):
    if request.method == "POST":
        staging = get_object_or_404(Staging, id=staging_id)
        Model = get_design_model(staging)

        if staging.metric_type == "combine_existing":
            existing = Model.objects.filter(sid=staging, delete_flag=False)
            order = existing.count()
            new_design = Model.objects.create(sid=staging, order=order)
        else:
            new_design = Model.objects.create(sid=staging)

        request.session[f'design_id_{staging_id}'] = new_design.id

        return redirect('design_metric_features', staging_id=staging_id)

    return HttpResponseBadRequest("Invalid request method")

def design_existing_review_all(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)

    designs_raw = DesignExistingMetrics.objects.filter(sid=staging, delete_flag=False)

    designs = []
    for design in designs_raw:
        if design.features:
            feature_list1 = [[f.strip().split("[")[0]+"["+f.strip().split("[")[1]] for f in design.features.split(",") if f.strip().split("[")[-1].replace("]","") == "protected"]
            feature_list2 = [[f.strip().split("[")[0]+"["+f.strip().split("[")[1]] for f in design.features.split(",") if f.strip().split("[")[-1].replace("]","") == "non-protected"]
        else:
            feature_list = []
        designs.append({
            "metric": design.metric,
            "threshold": design.threshold,
            "features_protected": feature_list1,
            "features_non_protected": feature_list2,
            "id": design.id
        })

    breadcrumb = [
        {"label": staging.category, "url": "fairness_category_with_id"},
        {"label": staging.perspective, "url": "fairness_perspective"},
        {"label": staging.metric_type, "url": "metric_type"},
        {"label": "Review All Metrics", "url": None}
    ]

    return render(request, "design_existing_review_all.html", {
        "designs": designs,
        "staging_id": staging.id,
        "breadcrumb": breadcrumb,
    })

def design_metric_delete(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)
    Model = get_design_model(staging)

    delete_id = request.GET.get("delete")
    if delete_id:
        design = get_object_or_404(Model, id=delete_id)
        design.delete_flag = True
        design.save()

    if staging.metric_type == "combine_existing":
        return redirect('design_combine_existing_review_all', staging_id=staging_id)
    else:
        return redirect('design_existing_review_all', staging_id=staging_id)

def design_combine_existing_review_all(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)

    if request.method == "POST":
        for key, value in request.POST.items():
            if key.startswith("weight_"):
                design_id = key.replace("weight_", "")
                try:
                    design = DesignCombineMetrics.objects.get(id=design_id, sid=staging)
                    design.weight = float(value)
                    design.save()
                except (ValueError, DesignCombineMetrics.DoesNotExist):
                    continue

            elif key.startswith("operator_"):
                design_id = key.replace("operator_", "")
                custom_key = f"custom_operator_{design_id}"
                custom_value = request.POST.get(custom_key, "").strip()

                try:
                    design = DesignCombineMetrics.objects.get(id=design_id, sid=staging)
                    design.boolean_operator = custom_value if value == "OTHER" and custom_value else value
                    design.save()
                except DesignCombineMetrics.DoesNotExist:
                    continue

            elif key.startswith("group_"):
                design_id = key.replace("group_", "")
                try:
                    design = DesignCombineMetrics.objects.get(id=design_id, sid=staging)
                    if value.strip() == "":
                        design.group_level = None
                    else:
                        design.group_level = int(value)
                    design.save()
                except (ValueError, DesignCombineMetrics.DoesNotExist):
                    continue

        return redirect('design_combine_existing_final_summary', staging_id=staging_id)

    designs_raw = DesignCombineMetrics.objects.filter(sid=staging, delete_flag=False).order_by('order')

    designs = []
    has_grouping = False

    for design in designs_raw:
        feature_list = [f.strip() for f in design.features.split(",") if f.strip()]
        feature_list1 = [[f.strip().split("[")[0]+"["+f.strip().split("[")[1]] for f in design.features.split(",") if f.strip().split("[")[-1].replace("]","") == "protected"]
        feature_list2 = [[f.strip().split("[")[0]+"["+f.strip().split("[")[1]] for f in design.features.split(",") if f.strip().split("[")[-1].replace("]","") == "non-protected"]
        if design.group_level is not None:
            has_grouping = True

        designs.append({
            "id": design.id,
            "features": feature_list,
            "features_protected": feature_list1,
            "features_non_protected": feature_list2,
            "metric": design.metric,
            "threshold": design.threshold,
            "weight": design.weight,
            "operator": design.boolean_operator,
            "group_level": design.group_level,
        })

    return render(request, "design_combine_existing_review_all.html", {
        "designs": designs,
        "staging_id": staging.id,
        "has_grouping": has_grouping,
    })

def design_combine_existing_final_summary(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)

    designs = DesignCombineMetrics.objects.filter(sid=staging, delete_flag=False).order_by('order')

    grouped_metrics = defaultdict(list)
    group_levels_present = []

    for design in designs:
        group = design.group_level if design.group_level else 1
        group_levels_present.append(group)
    
        feature_list1 = "(" + " AND ".join([f.strip() for f in design.features.split(",") if f.strip().split("[")[-1].replace("]","") == "protected"])
        feature_list2 = "(" + " AND ".join([f.strip() for f in design.features.split(",") if f.strip().split("[")[-1].replace("]","") == "non-protected"])

        features_str = feature_list1 + ") vs (" + feature_list2 + ")"
    
        expression = f"({design.weight:.1f}% × ({features_str}, {design.metric}, {design.threshold}%))"

        grouped_metrics[group].append({
            "text": expression,
            "operator": design.boolean_operator or "AND"
        })

    sorted_groups = sorted(set(group_levels_present))

    return render(request, "design_combine_existing_final_summary.html", {
        "staging_id": staging_id,
        "grouped_metrics": [grouped_metrics[g] for g in sorted_groups],
        "group_levels": sorted_groups,
        "has_if_not": len(set(group_levels_present)) > 1,
    })

def custom_own_intro(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)
    return render(request, "custom_own_intro.html", {"staging_id": staging_id})


def custom_own_select_mode(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)

    if request.method == "POST":
        mode = request.POST.get("mode")
        staging.custom_mode = mode
        staging.save()

        if mode == "combine":
            new_metric = DesignCustomOwnMetric.objects.create(sid=staging)
            return redirect('custom_own_card_edit', staging_id=staging.id, card_id=new_metric.id)

        elif mode == "compare":
            return redirect('custom_own_compare', staging_id=staging.id)

    return render(request, "custom_own_select_mode.html", {
        "staging_id": staging.id,
    })

def custom_own_card_edit(request, staging_id, card_id):
    staging = get_object_or_404(Staging, id=staging_id)
    metric = get_object_or_404(DesignCustomOwnMetric, id=card_id, sid=staging)

    if request.method == "POST":
        metric.probability_type = request.POST.get("probability_type")
        metric.save()

        DesignCustomOwnCondition.objects.filter(metric=metric).delete()

        total = int(request.POST.get("total_conditions", 0))
        used_label_condition = False

        for i in range(total):
            feature = request.POST.get(f"feature_{i}")
            logic = request.POST.get(f"logic_{i}")
            custom_logic = request.POST.get(f"custom_logic_{i}", "").strip()

            if feature in [l[0] for l in PROBABILITY_LABELS]:
                if used_label_condition:
                    continue
                used_label_condition = True
                binning = feature
            elif request.POST.get(f"binning_max_{i}"):
                min_val = request.POST.get(f"binning_{i}")
                max_val = request.POST.get(f"binning_max_{i}")
                binning = f"{feature}[{min_val}-{max_val}]"
            else:
                value = request.POST.get(f"binning_{i}")
                binning = f"{feature}[{value}]"

            DesignCustomOwnCondition.objects.create(
                metric=metric,
                feature=feature,
                binning=binning,
                logic_with_next=custom_logic if logic == "CUSTOM" and custom_logic else logic
            )

        if metric.order == 0:
            existing = DesignCustomOwnMetric.objects.filter(sid=staging, delete_flag=False).exclude(id=metric.id)
            metric.order = existing.count()
            metric.save()

        if "save_add_new" in request.POST:
            new_metric = DesignCustomOwnMetric.objects.create(sid=staging, order=metric.order + 1)
            return redirect('custom_own_card_edit', staging_id=staging.id, card_id=new_metric.id)

        elif "save_review_all" in request.POST:
            return redirect('custom_own_logic_review', staging_id=staging.id)

    existing_conditions = DesignCustomOwnCondition.objects.filter(metric=metric).order_by('id')

    return render(request, "custom_own_card_edit.html", {
        "staging_id": staging.id,
        "metric": metric,
        "features": FEATURES,
        "labels": get_valid_condition_labels(metric.probability_type),
        "conditions": existing_conditions,
        "probability_labels": PROBABILITY_LABELS,
    })

def custom_own_card_new(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)
    new_metric = DesignCustomOwnMetric.objects.create(sid=staging)
    return redirect('custom_own_card_edit', staging_id=staging.id, card_id=new_metric.id)

def custom_own_logic_review(request, staging_id, side=None):
    staging = get_object_or_404(Staging, id=staging_id)
    if side in ["LHS", "RHS"]:
        cards = DesignCustomOwnMetric.objects.filter(
            sid=staging, side=side, delete_flag=False
        ).order_by('order')
        is_compare_mode = True
    else:
        cards = DesignCustomOwnMetric.objects.filter(
            sid=staging, side__isnull=True, delete_flag=False
        ).order_by('order')
        is_compare_mode = False

    is_compare_mode = cards.filter(side__in=["LHS", "RHS"]).exists()

    if request.method == "POST":
        for key, value in request.POST.items():
            if key.startswith("operator_"):
                card_id = key.split("_")[1]
                custom_key = f"custom_operator_{card_id}"
                custom_value = request.POST.get(custom_key, "").strip()

                try:
                    card = DesignCustomOwnMetric.objects.get(id=card_id, sid=staging)
                    card.boolean_operator = custom_value if value == "CUSTOM" and custom_value else value
                    card.save()
                except DesignCustomOwnMetric.DoesNotExist:
                    continue

        if is_compare_mode:
            return redirect('custom_own_compare', staging_id=staging_id)
        else:
            return redirect('custom_own_set_threshold', staging_id=staging_id)

    return render(request, "custom_own_logic_review.html", {
        "staging_id": staging.id,
        "cards": cards,
        "label_lookup": dict(PROBABILITY_LABELS),
        "is_compare_mode": is_compare_mode,
    })


def custom_own_set_threshold(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)

    global_obj, _ = DesignCustomOwnGlobal.objects.get_or_create(sid=staging)

    if request.method == "POST":
        global_obj.metric_name = request.POST.get("metric_name")

        threshold_raw = request.POST.get("threshold")
        try:
            global_obj.threshold = float(threshold_raw)
        except (TypeError, ValueError):
            return render(request, "custom_own_set_threshold.html", {
                "staging_id": staging.id,
                "metric_name": global_obj.metric_name,
                "threshold": threshold_raw,
                "error": "Please enter a valid numeric threshold."
            })

        global_obj.save()
        return redirect('custom_own_final_review', staging_id=staging_id)

    return render(request, "custom_own_set_threshold.html", {
        "staging_id": staging.id,
        "metric_name": global_obj.metric_name,
        "threshold": global_obj.threshold,
    })

def custom_own_final_review(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)
    global_obj = get_object_or_404(DesignCustomOwnGlobal, sid=staging)
    cards = DesignCustomOwnMetric.objects.filter(sid=staging, delete_flag=False).order_by('order')

    logic_string = []
    for i, card in enumerate(cards):
        logic_string.append(f"{card.probability_type}")
        if card.boolean_operator and i < len(cards) - 1:
            logic_string.append(card.boolean_operator)

    return render(request, "custom_own_final_review.html", {
        "staging_id": staging.id,
        "metric_name": global_obj.metric_name,
        "threshold": global_obj.threshold,
        "logic_string": logic_string,
        "cards": cards,
        "label_lookup": dict(PROBABILITY_LABELS),
    })

def custom_own_compare(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)

    lhs_cards = DesignCustomOwnMetric.objects.filter(sid=staging, side="LHS", delete_flag=False).order_by('order')
    rhs_cards = DesignCustomOwnMetric.objects.filter(sid=staging, side="RHS", delete_flag=False).order_by('order')

    label_lookup = dict(PROBABILITY_LABELS)

    return render(request, "custom_own_compare.html", {
        "staging_id": staging_id,
        "lhs_cards": lhs_cards,
        "rhs_cards": rhs_cards,
        "label_lookup": label_lookup,
    })


def custom_own_card_new_compare(request, staging_id, side):
    staging = get_object_or_404(Staging, id=staging_id)
    order = DesignCustomOwnMetric.objects.filter(sid=staging, side=side, delete_flag=False).count()
    metric = DesignCustomOwnMetric.objects.create(sid=staging, side=side, order=order)
    return redirect('custom_own_card_edit_compare', staging_id=staging_id, card_id=metric.id)

def custom_own_card_edit_compare(request, staging_id, card_id):
    staging = get_object_or_404(Staging, id=staging_id)
    metric = get_object_or_404(DesignCustomOwnMetric, id=card_id, sid=staging)

    if request.method == "POST":
        metric.probability_type = request.POST.get("probability_type")
        metric.save()

        DesignCustomOwnCondition.objects.filter(metric=metric).delete()

        total = int(request.POST.get("total_conditions", 0))
        used_label_condition = False

        for i in range(total):
            feature = request.POST.get(f"feature_{i}")
            logic = request.POST.get(f"logic_{i}")
            custom_logic = request.POST.get(f"custom_logic_{i}", "").strip()

            if feature in [l[0] for l in PROBABILITY_LABELS]:
                if used_label_condition:
                    continue
                used_label_condition = True
                binning = feature
            elif request.POST.get(f"binning_max_{i}"):
                min_val = request.POST.get(f"binning_{i}")
                max_val = request.POST.get(f"binning_max_{i}")
                binning = f"{feature}[{min_val}-{max_val}]"
            else:
                value = request.POST.get(f"binning_{i}")
                binning = f"{feature}[{value}]"

            DesignCustomOwnCondition.objects.create(
                metric=metric,
                feature=feature,
                binning=binning,
                logic_with_next=custom_logic if logic == "CUSTOM" and custom_logic else logic
            )

        if metric.order == 0:
            existing = DesignCustomOwnMetric.objects.filter(sid=staging, side=metric.side, delete_flag=False).exclude(id=metric.id)
            metric.order = existing.count()
            metric.save()

        if "save_add_new" in request.POST:
            new_order = metric.order + 1
            new_card = DesignCustomOwnMetric.objects.create(sid=staging, side=metric.side, order=new_order)
            return redirect('custom_own_card_edit_compare', staging_id=staging_id, card_id=new_card.id)

        if "save_review_all" in request.POST:
            return redirect('custom_own_logic_review_side', staging_id=staging_id, side=metric.side)

    existing_conditions = DesignCustomOwnCondition.objects.filter(metric=metric).order_by('id')

    return render(request, "custom_own_card_edit.html", {
        "staging_id": staging.id,
        "metric": metric,
        "features": FEATURES,
        "labels": get_valid_condition_labels(metric.probability_type),
        "conditions": existing_conditions,
        "probability_labels": PROBABILITY_LABELS,
    })

def custom_own_card_delete(request, staging_id, card_id):
    staging = get_object_or_404(Staging, id=staging_id)
    metric = get_object_or_404(DesignCustomOwnMetric, id=card_id, sid=staging)
    metric.delete_flag = True
    metric.save()
    return redirect('custom_own_compare', staging_id=staging_id)

def custom_own_compare_set_threshold(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)
    global_obj, _ = DesignCustomOwnGlobal.objects.get_or_create(sid=staging)

    if request.method == "POST":
        global_obj.metric_name = request.POST.get("metric_name")

        threshold_raw = request.POST.get("threshold")
        try:
            global_obj.threshold = float(threshold_raw)
        except (TypeError, ValueError):
            return render(request, "custom_own_compare_set_threshold.html", {
                "staging_id": staging_id,
                "metric_name": global_obj.metric_name,
                "threshold": threshold_raw,
                "error": "Please enter a valid numeric threshold."
            })

        global_obj.save()
        return redirect('custom_own_compare_final_review', staging_id=staging_id)

    return render(request, "custom_own_compare_set_threshold.html", {
        "staging_id": staging_id,
        "metric_name": global_obj.metric_name,
        "threshold": global_obj.threshold,
    })

def custom_own_compare_final_review(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)
    global_obj = get_object_or_404(DesignCustomOwnGlobal, sid=staging)

    lhs_cards = DesignCustomOwnMetric.objects.filter(sid=staging, side="LHS", delete_flag=False).order_by('order')
    rhs_cards = DesignCustomOwnMetric.objects.filter(sid=staging, side="RHS", delete_flag=False).order_by('order')

    return render(request, "custom_own_compare_final_review.html", {
        "staging_id": staging_id,
        "metric_name": global_obj.metric_name,
        "threshold": global_obj.threshold,
        "lhs_cards": lhs_cards,
        "rhs_cards": rhs_cards,
        "label_lookup": dict(PROBABILITY_LABELS),
    })



def procedural_intro(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)
    breadcrumb = [
        {"label": staging.category or "Fairness Category", "url": "fairness_category_with_id"},
        {"label": staging.perspective or "Perspective", "url": "fairness_perspective"},
        {"label": "Procedural Fairness", "url": None},
        {"label": "Intro", "url": None}
    ]
    return render(request, 'procedural_intro.html', {
        "staging_id": staging.id,
        "breadcrumb": breadcrumb
    })

def procedural_builder(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)
    existing_metrics = DesignProceduralMetric.objects.filter(sid=staging, delete_flag=False).order_by('order')

    if request.method == "POST" and "delete_card_id" in request.POST:
        card_id = request.POST.get("delete_card_id")
        DesignProceduralMetric.objects.filter(id=card_id, sid=staging).update(delete_flag=True)
        return redirect('procedural_builder', staging_id=staging_id)

    if request.method == "POST":
        raw = request.POST.get("cards_data", "[]")
        try:
            card_list = json.loads(raw)
        except json.JSONDecodeError:
            card_list = []

        keep_ids = []

        for i, card in enumerate(card_list):
            card_id = card.get("id")
            label_type = card.get("label")
            preview = card.get("preview", "")
            feature = card.get("feature", "")
            operator = card.get("operator", "")
            value = card.get("value", "")
            group_a = card.get("groupA", "")
            group_b = card.get("groupB", "")
            decision = card.get("decision", "")

            if card_id:
                try:
                    metric = DesignProceduralMetric.objects.get(id=card_id, sid=staging)
                    metric.label_type = label_type
                    metric.order = i
                    metric.preview = preview
                    metric.delete_flag = False
                    metric.save()
                    metric.conditions.all().delete()
                except DesignProceduralMetric.DoesNotExist:
                    metric = DesignProceduralMetric.objects.create(
                        sid=staging, label_type=label_type, order=i, preview=preview
                    )
            else:
                metric = DesignProceduralMetric.objects.create(
                    sid=staging, label_type=label_type, order=i, preview=preview
                )

            keep_ids.append(metric.id)

            if label_type in ["contribute", "does_not_contribute"]:
                DesignProceduralCondition.objects.create(
                    metric=metric, feature=feature,
                    value="Contributes" if label_type == "contribute" else "Does Not Contribute"
                )
            elif label_type == "feature_importance":
                DesignProceduralCondition.objects.create(
                    metric=metric, feature=feature, value=value, logic_with_next=operator
                )
            elif label_type == "importance_by_group":
                DesignProceduralCondition.objects.create(
                    metric=metric, feature=group_a, value=group_b, logic_with_next=operator
                )
            elif label_type == "pre_checks":
                DesignProceduralCondition.objects.create(
                    metric=metric, feature=feature, value=decision
                )

        DesignProceduralMetric.objects.filter(sid=staging).exclude(id__in=keep_ids).update(delete_flag=True)

        return redirect('procedural_set_threshold', staging_id=staging_id)

    cards_json = []
    for m in existing_metrics:
        conds = m.conditions.all()
        d = {
            "id": m.id,
            "label": m.label_type,
            "preview": m.preview
        }
        if m.label_type in ["contribute", "does_not_contribute"] and conds:
            d["feature"] = conds[0].feature
        elif m.label_type == "feature_importance" and conds:
            d["feature"] = conds[0].feature
            d["value"] = conds[0].value
            d["operator"] = conds[0].logic_with_next
        elif m.label_type == "importance_by_group" and conds:
            d["groupA"] = conds[0].feature
            d["groupB"] = conds[0].value
            d["operator"] = conds[0].logic_with_next
        elif m.label_type == "pre_checks" and conds:
            d["feature"] = conds[0].feature
            d["decision"] = conds[0].value

        cards_json.append(d)

    return render(request, 'procedural_card_builder.html', {
        "staging_id": staging_id,
        "cards": existing_metrics,
        "features": FEATURES,
        "labels": dict(PROCEDURAL_LABELS),
        "cards_json": json.dumps(cards_json, cls=DjangoJSONEncoder)
    })



def procedural_set_threshold(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)
    global_obj, _ = DesignProceduralGlobal.objects.get_or_create(sid=staging)

    if request.method == "POST":
        global_obj.metric_name = request.POST.get("metric_name")
        threshold_raw = request.POST.get("threshold")
        try:
            global_obj.threshold = float(threshold_raw)
        except (TypeError, ValueError):
            return render(request, 'procedural_set_threshold.html', {
                "staging_id": staging_id,
                "metric_name": global_obj.metric_name,
                "threshold": threshold_raw,
                "error": "Please enter a valid numeric threshold."
            })

        global_obj.save()
        return redirect('procedural_final_review', staging_id=staging_id)

    return render(request, 'procedural_set_threshold.html', {
        "staging_id": staging_id,
        "metric_name": global_obj.metric_name,
        "threshold": global_obj.threshold,
    })


def procedural_final_review(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)
    global_obj = get_object_or_404(DesignProceduralGlobal, sid=staging)
    designs = DesignProceduralMetric.objects.filter(sid=staging, delete_flag=False).order_by('order')

    cards = []
    for d in designs:
        cards.append({
            "label_type": d.label_type,
            "preview": d.preview,
            "id": d.id,
            "conditions": list(d.conditions.all())
        })

    breadcrumb = [
        {"label": "Procedural Fairness", "url": "procedural_intro"},
        {"label": "Final Review", "url": None}
    ]
    return render(request, 'procedural_final_review.html', {
        "staging_id": staging_id,
        "metric_name": global_obj.metric_name,
        "threshold": global_obj.threshold,
        "cards": cards,
        "breadcrumb": breadcrumb
    })

@csrf_exempt
def save_procedural_card(request, staging_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    staging = get_object_or_404(Staging, id=staging_id)
    label = data.get("label")
    preview = data.get("preview", "")
    feature = data.get("feature", "")
    value = data.get("value", "")
    operator = data.get("operator", "")
    groupA = data.get("groupA", "")
    groupB = data.get("groupB", "")
    decision = data.get("decision", "")

    metric = DesignProceduralMetric.objects.create(
        sid=staging,
        label_type=label,
        order=0,
        preview=preview
    )

    if label in ["contribute", "does_not_contribute"]:
        DesignProceduralCondition.objects.create(
            metric=metric,
            feature=feature,
            value="Contributes" if label == "contribute" else "Does Not Contribute"
        )
    elif label == "feature_importance":
        DesignProceduralCondition.objects.create(
            metric=metric,
            feature=feature,
            value=value,
            logic_with_next=operator
        )
    elif label == "importance_by_group":
        DesignProceduralCondition.objects.create(
            metric=metric,
            feature=groupA,
            value=groupB,
            logic_with_next=operator
        )
    elif label == "pre_checks":
        DesignProceduralCondition.objects.create(
            metric=metric,
            feature=feature,
            value=decision
        )

    return JsonResponse({"id": metric.id})




def affordability_intro(request, staging_id):
    return render(request, "affordability_intro.html", {
        "staging_id": staging_id
    })


def affordability_builder(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)

    design, _ = AffordabilityDesign.objects.get_or_create(
        staging_id=staging,
        defaults={"metric_name": "", "threshold": 0}
    )

    lhs_cards = AffordabilityCard.objects.filter(design=design, side="LHS", delete_flag=False)
    rhs_cards = AffordabilityCard.objects.filter(design=design, side="RHS", delete_flag=False)

    return render(request, "affordability_builder.html", {
        "staging_id": staging_id,
        "lhs_cards": lhs_cards,
        "rhs_cards": rhs_cards,
        "features": FEATURES,
    })


def save_affordability_card(request, staging_id):
    if request.method == "POST":
        staging = get_object_or_404(Staging, id=staging_id)
        design = get_object_or_404(AffordabilityDesign, staging_id=staging)

        data = json.loads(request.body)

        card = AffordabilityCard.objects.create(
            design=design,
            side=data["side"],
            feature=data["feature"],
            operator=data["operator"],
            value=data["value"]
        )

        return JsonResponse({"id": card.id})
    return JsonResponse({"error": "Invalid request"}, status=400)


def delete_affordability_card(request, staging_id):
    if request.method == "POST":
        card_id = request.POST.get("card_id")
        card = get_object_or_404(AffordabilityCard, id=card_id)
        card.delete_flag = True
        card.save()
        return redirect("affordability_builder", staging_id=staging_id)
    return JsonResponse({"error": "Invalid request"}, status=400)


def affordability_set_threshold(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)
    design = get_object_or_404(AffordabilityDesign, staging_id=staging)

    if request.method == "POST":
        design.metric_name = request.POST.get("metric_name", "")
        design.threshold = request.POST.get("threshold", 0)
        design.save()
        return redirect("affordability_final_review", staging_id=staging_id)

    return render(request, "affordability_set_threshold.html", {
        "staging_id": staging_id,
        "metric_name": design.metric_name,
        "threshold": design.threshold,
    })


def affordability_final_review(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)
    design = get_object_or_404(AffordabilityDesign, staging_id=staging)
    cards = design.cards.filter(delete_flag=False)

    return render(request, "affordability_final_review.html", {
        "staging_id": staging_id,
        "metric_name": design.metric_name,
        "threshold": design.threshold,
        "cards": cards,
    })