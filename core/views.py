from django.shortcuts import render, redirect, get_object_or_404
from .models import Staging, DesignExistingMetrics, DesignCombineMetrics
from django.http import HttpResponseBadRequest

from .features_data import FEATURES
from .metrics_data import METRICS

from .utils import get_design_model

from collections import defaultdict

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

    if(staging.perspective == 'outcome'):
        if metric_type == "existing":
            return redirect('design_existing', staging_id=staging.id)
        elif metric_type == "combine_existing":
            return redirect('design_combine_existing', staging_id=staging.id)
        elif metric_type == "custom_own":
            return redirect('design_custom_own', staging_id=staging.id)
        else:
            return HttpResponseBadRequest("Invalid metric type")
    elif(staging.perspective == 'procedural'):
        return redirect('under_construction')
    elif(staging.perspective == 'affordability'):
        return redirect('under_construction')
    else:
        return HttpResponseBadRequest("Invalid fairness perspective type")
    
def design_custom_own(request, staging_id):

    return render(request, "under_construction.html")

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
                feature_items.append({'name': name, 'binning': binning})
            elif item:
                feature_items.append({'name': item, 'binning': ''})

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
            feature_list = [f.strip() for f in design.features.split(",") if f.strip()]
        else:
            feature_list = []
        designs.append({
            "metric": design.metric,
            "threshold": design.threshold,
            "features": feature_list,
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
        if design.group_level is not None:
            has_grouping = True

        designs.append({
            "id": design.id,
            "features": feature_list,
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

        features_str = ", ".join([f.strip() for f in design.features.split(",") if f.strip()])
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