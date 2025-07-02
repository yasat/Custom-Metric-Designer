from django.shortcuts import render, redirect, get_object_or_404
from .models import Staging, DesignExistingMetrics, DesignCombineExistingMetricsMain, DesignCombineExistingMetricsSub
from django.http import HttpResponseBadRequest

from .features_data import FEATURES
from .metrics_data import METRICS

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

def design_existing_features(request, staging_id):

    staging = get_object_or_404(Staging, id=staging_id)

    edit_id = request.GET.get("edit")
    if edit_id:
        design = get_object_or_404(DesignExistingMetrics, id=edit_id)
        request.session[f'design_id_{staging_id}'] = design.id
    else:
        design_id = request.session.get(f'design_id_{staging_id}')
        design = get_object_or_404(DesignExistingMetrics, id=design_id)

    if request.method == "POST":
        features_str = request.POST.get("features")
        if features_str:
            design.features = features_str
            design.save()
            return redirect('design_existing_select_metric', staging_id=staging_id)

    breadcrumb = [
        {"label": staging.category, "url": "fairness_category_with_id"},
        {"label": staging.perspective, "url": "fairness_perspective"},
        {"label": staging.metric_type, "url": "metric_type"},
    ]

    if design.features != None:
        breadcrumb_cm = [
            {"label": design.features, "url": "design_existing_features"},
        ]
    else:
        breadcrumb_cm = [
            {"label": "Select Features", "url": None},
        ]

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

def design_existing_select_metric(request, staging_id):

    staging = get_object_or_404(Staging, id=staging_id)
    design_id = request.session.get(f'design_id_{staging_id}')
    design = get_object_or_404(DesignExistingMetrics, id=design_id)

    if request.method == "POST":
        selected_metric = request.POST.get("selected_metric")
        if selected_metric:
            design.metric = selected_metric
            design.save()
            return redirect('design_existing_threshold', staging_id=staging_id)

    breadcrumb = [
        {"label": staging.category, "url": "fairness_category_with_id"},
        {"label": staging.perspective, "url": "fairness_perspective"},
        {"label": staging.metric_type, "url": "metric_type"},
    ]

    if design.metric != None:
        breadcrumb_cm = [
            {"label": design.features, "url": "design_existing_features"},
            {"label": design.metric, "url": "design_existing_select_metric"},
        ]
    else:
        breadcrumb_cm = [
            {"label": design.features, "url": "design_existing_features"},
            {"label": "Select Metric", "url": None},
        ]

    selected_metric_id = design.metric if design.metric else None

    if(staging.category == "individual"):
        metrics = [metric for metric in METRICS if metric['category'] == "Individual"]
    elif(staging.category == "group"):
        metrics = [metric for metric in METRICS if metric['category'] == "Group"]
    else:
        metrics = METRICS

    return render(request, "design_existing_select_metric.html", {
        "staging_id": staging_id,
        "breadcrumb": breadcrumb,
        "metrics": metrics,
        "breadcrumb_cm": breadcrumb_cm,
        "selected_metric_id": selected_metric_id,
    })

def design_existing_threshold(request, staging_id):

    staging = get_object_or_404(Staging, id=staging_id)
    design_id = request.session.get(f'design_id_{staging_id}')
    design = get_object_or_404(DesignExistingMetrics, id=design_id)

    if request.method == "POST":
        threshold = request.POST.get("threshold")

        design.threshold = threshold
        design.save()
        return redirect('design_existing_summary', staging_id=staging_id)

    breadcrumb = [
        {"label": staging.category, "url": "fairness_category_with_id"},
        {"label": staging.perspective, "url": "fairness_perspective"},
        {"label": staging.metric_type, "url": "metric_type"},
    ]

    if design.threshold != None:
        breadcrumb_cm = [
            {"label": design.features, "url": "design_existing_features"},
            {"label": design.metric, "url": "design_existing_select_metric"},
            {"label": design.threshold, "url": "design_existing_threshold"},
        ]
    else:
        breadcrumb_cm = [
            {"label": design.features, "url": "design_existing_features"},
            {"label": design.metric, "url": "design_existing_select_metric"},
            {"label": "Set a Threshold", "url": None},
        ]
    
    threshold = design.threshold if design.threshold is not None else ""

    return render(request, "design_existing_threshold.html", {
        "staging_id": staging_id,
        "breadcrumb": breadcrumb,
        "breadcrumb_cm": breadcrumb_cm,
        "threshold": threshold,
    })

def design_existing_summary(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)
    design_id = request.session.get(f'design_id_{staging_id}')
    design = get_object_or_404(DesignExistingMetrics, id=design_id)

    # Split and clean feature strings like: "Age [18-25], Gender [Female]"
    feature_items = []
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
        {"label": design.features, "url": "design_existing_features"},
        {"label": design.metric, "url": "design_existing_select_metric"},
        {"label": design.threshold, "url": "design_existing_threshold"},
    ]

    return render(request, "design_existing_summary.html", {
        "staging_id": staging.id,
        "breadcrumb": breadcrumb,
        "features": feature_items,
        "metric": design.metric,
        "threshold": design.threshold,
        "breadcrumb_cm": breadcrumb_cm,
    })

def design_existing_save_new(request, staging_id):
    if request.method == "POST":
        # Create a new row for this staging_id (empty at first)
        staging = get_object_or_404(Staging, id=staging_id)
        new_design = DesignExistingMetrics.objects.create(sid=staging)
        request.session[f'design_id_{staging_id}'] = new_design.id
        return redirect('design_existing_features', staging_id=staging_id)
    return HttpResponseBadRequest("Invalid request method")

def design_existing_review_all(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)

    designs_raw = DesignExistingMetrics.objects.filter(sid=staging, delete_flag=False)

    # Split features into list
    designs = []
    for design in designs_raw:
        feature_list = [f.strip() for f in design.features.split(",") if f.strip()]
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

def design_existing_delete(request, staging_id):
    staging = get_object_or_404(Staging, id=staging_id)

    delete_id = request.GET.get("delete")
    if delete_id:
        design = get_object_or_404(DesignExistingMetrics, id=delete_id)
        design.delete_flag = True
        design.save()
    
    return redirect('design_existing_review_all', staging_id=staging_id)



def design_combine_existing(request, staging_id):
    
    staging = get_object_or_404(Staging, id=staging_id)

    if not request.session.get(f'design_id_{staging_id}'):
        design = DesignCombineExistingMetricsMain.objects.create(sid=staging)
        request.session[f'design_id_{staging_id}'] = design.id
    else:
        design = get_object_or_404(DesignCombineExistingMetricsMain, id=request.session[f'design_id_{staging_id}'])
    
    if not request.session.get(f'combine_id_{design.id}'):
        combine = DesignCombineExistingMetricsSub.objects.create(group_id=design.id)
        combine.priority_id = 1
        combine.save()
        request.session[f'combine_id_{design.id}'] = combine.id
    else:
        combine = get_object_or_404(DesignCombineExistingMetricsSub, id=request.session[f'combine_id_{design.id}'])

    breadcrumb = [
        {"label": staging.category, "url": "fairness_category_with_id"},
        {"label": staging.perspective, "url": "fairness_perspective"},
        {"label": staging.metric_type, "url": "metric_type"},
    ]

    return render(request, "design_combine_existing_intro.html", {
        "staging_id": staging_id,
        "design_id": combine.id,
        "breadcrumb": breadcrumb,
    })

def combine_existing_features(request, staging_id, design_id):

    staging = get_object_or_404(Staging, id=staging_id)

    edit_id = request.GET.get("edit")
    if edit_id:
        design = get_object_or_404(DesignCombineExistingMetricsSub, id=edit_id)
        request.session[f'combine_id_{design_id}'] = design.id
    else:
        if not request.session.get(f'combine_id_{design.id}'):
            design = DesignCombineExistingMetricsSub.objects.create(group_id=design.id)
            design.priority_id = 1
            design.save()
            request.session[f'combine_id_{design.id}'] = design.id
        else:
            design = get_object_or_404(DesignCombineExistingMetricsSub, id=request.session[f'combine_id_{design.id}'])

    if request.method == "POST":
        features_str = request.POST.get("features")
        if features_str:
            design.features = features_str
            design.save()
            return redirect('design_combine_existing_select_metric', staging_id=staging_id, design_id=design_id)

    breadcrumb = [
        {"label": staging.category, "url": "fairness_category_with_id"},
        {"label": staging.perspective, "url": "fairness_perspective"},
        {"label": staging.metric_type, "url": "metric_type"},
    ]

    if design.features != None:
        breadcrumb_cm = [
            {"label": design.features, "url": "design_combine_existing_features"},
        ]
    else:
        breadcrumb_cm = [
            {"label": "Select Features", "url": None},
        ]

    selected = []
    if design.features:
        selected = [s.strip() for s in design.features.split(",") if s.strip()]

    return render(request, "combine_existing_features.html", {
        "features": FEATURES,
        "staging_id": staging_id,
        "design_id": design.id,
        "breadcrumb": breadcrumb,
        "breadcrumb_cm": breadcrumb_cm,
        "selected_features": selected,
    })

def combine_existing_select_metric(request, staging_id, design_id):

    staging = get_object_or_404(Staging, id=staging_id)
    design_id = request.session.get(f'combine_id_{design_id}')
    print(design_id)
    design = get_object_or_404(DesignCombineExistingMetricsSub, id=design_id)

    if request.method == "POST":
        selected_metric = request.POST.get("selected_metric")
        if selected_metric:
            design.metric = selected_metric
            design.save()
            return redirect('combine_existing_threshold', staging_id=staging_id, design_id=design_id)

    breadcrumb = [
        {"label": staging.category, "url": "fairness_category_with_id"},
        {"label": staging.perspective, "url": "fairness_perspective"},
        {"label": staging.metric_type, "url": "metric_type"},
    ]

    if design.metric != None:
        breadcrumb_cm = [
            {"label": design.features, "url": "design_combine_existing_features"},
            {"label": design.metric, "url": "design_combine_existing_select_metric"},
        ]
    else:
        breadcrumb_cm = [
            {"label": design.features, "url": "design_combine_existing_features"},
            {"label": "Select Metric", "url": None},
        ]

    selected_metric_id = design.metric if design.metric else None

    if(staging.category == "individual"):
        metrics = [metric for metric in METRICS if metric['category'] == "Individual"]
    elif(staging.category == "group"):
        metrics = [metric for metric in METRICS if metric['category'] == "Group"]
    else:
        metrics = METRICS

    return render(request, "combine_existing_select_metric.html", {
        "staging_id": staging_id,
        "design_id": design.id,
        "breadcrumb": breadcrumb,
        "metrics": metrics,
        "breadcrumb_cm": breadcrumb_cm,
        "selected_metric_id": selected_metric_id,
    })

def combine_existing_threshold(request, staging_id, design_id):

    staging = get_object_or_404(Staging, id=staging_id)
    design_id = request.session.get(f'combine_id_{design_id}')
    design = get_object_or_404(DesignCombineExistingMetricsSub, id=design_id)

    if request.method == "POST":
        threshold = request.POST.get("threshold")

        design.threshold = threshold
        design.save()
        return redirect('combine_existing_summary', staging_id=staging_id, design_id=design_id)

    breadcrumb = [
        {"label": staging.category, "url": "fairness_category_with_id"},
        {"label": staging.perspective, "url": "fairness_perspective"},
        {"label": staging.metric_type, "url": "metric_type"},
    ]

    if design.threshold != None:
        breadcrumb_cm = [
            {"label": design.features, "url": "design_combine_existing_features"},
            {"label": design.metric, "url": "design_combine_existing_select_metric"},
            {"label": design.threshold, "url": "combine_existing_threshold"},
        ]
    else:
        breadcrumb_cm = [
            {"label": design.features, "url": "design_combine_existing_features"},
            {"label": design.metric, "url": "design_combine_existing_select_metric"},
            {"label": "Set a Threshold", "url": None},
        ]
    
    threshold = design.threshold if design.threshold is not None else ""

    return render(request, "combine_existing_threshold.html", {
        "staging_id": staging_id,
        "design_id": design.id,
        "breadcrumb": breadcrumb,
        "breadcrumb_cm": breadcrumb_cm,
        "threshold": threshold,
    })

def combine_existing_summary(request, staging_id, design_id):
    staging = get_object_or_404(Staging, id=staging_id)
    design_id = request.session.get(f'combine_id_{design_id}')
    design = get_object_or_404(DesignCombineExistingMetricsSub, id=design_id)

    # Split and clean feature strings like: "Age [18-25], Gender [Female]"
    feature_items = []
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
        {"label": design.features, "url": "design_combine_existing_features"},
            {"label": design.metric, "url": "design_combine_existing_select_metric"},
            {"label": design.threshold, "url": "combine_existing_threshold"},
    ]

    return render(request, "combine_existing_summary.html", {
        "staging_id": staging.id,
        "design_id": design.id,
        "breadcrumb": breadcrumb,
        "features": feature_items,
        "metric": design.metric,
        "threshold": design.threshold,
        "breadcrumb_cm": breadcrumb_cm,
    })

def combine_existing_save_new(request, staging_id, design_id):
    if request.method == "POST":
        # Create a new row for this staging_id (empty at first)
        staging = get_object_or_404(Staging, id=staging_id)
        design_id = request.session.get(f'combine_id_{design_id}')
        design = get_object_or_404(DesignCombineExistingMetricsSub, id=design_id)

        priority_id = len(DesignCombineExistingMetricsSub.objects.filter(group_id=design.group_id)) + 1

        new_design = DesignCombineExistingMetricsSub.objects.create(group_id=design.group_id, priority_id=priority_id)
        request.session[f'combine_id_{design_id}'] = new_design.id
        return redirect('design_combine_existing_features', staging_id=staging_id, design_id=design_id)
    return HttpResponseBadRequest("Invalid request method")

def combine_existing_review_all(request, staging_id, design_id):
    staging = get_object_or_404(Staging, id=staging_id)

    designs_raw = DesignExistingMetrics.objects.filter(sid=staging, delete_flag=False)

    # Split features into list
    designs = []
    for design in designs_raw:
        feature_list = [f.strip() for f in design.features.split(",") if f.strip()]
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

def combine_existing_delete(request, staging_id, design_id):
    staging = get_object_or_404(Staging, id=staging_id)

    delete_id = request.GET.get("delete")
    if delete_id:
        design = get_object_or_404(DesignExistingMetrics, id=delete_id)
        design.delete_flag = True
        design.save()
    
    return redirect('design_existing_review_all', staging_id=staging_id)