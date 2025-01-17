def global_variables(request):
    return {
        "main_menu_items": [
            {"title": "Dashboard", "app": "dashboard", "index_url": "core:dashboard"},
            {"title": "Catalog", "app": "catalog", "index_url": "catalog:index"},
            {"title": "Notebooks", "app": "notebooks", "index_url": "notebooks:index"},
            {"title": "Pipelines", "app": "pipelines", "index_url": "pipelines:index"},
            {
                "title": "Visualizations",
                "app": "visualizations",
                "index_url": "visualizations:visualization_index",
            },
        ]
    }
