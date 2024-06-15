# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "PR Pilot"
copyright = "2024, Marco Lamina"
author = "Marco Lamina"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_material"
html_static_path = ["_static"]
html_theme_options = {
    "base_url": "https://docs.pr-pilot.ai",
    "repo_url": "https://github.com/PR-Pilot-AI/pr-pilot",
    "repo_name": "PR Pilot",
    "html_minify": True,
    "css_minify": True,
    "nav_title": "PR Pilot",
    "google_analytics_account": "G-86FJ02W45S",
    "logo_icon": "✈️",
    "globaltoc_depth": 1,
    "master_doc": False,
    "nav_links": [
        {
            "href": "https://github.com/apps/pr-pilot-ai/installations/new",
            "internal": False,
            "title": "Install",
        },
        {
            "href": "https://app.pr-pilot.ai/dashboard/tasks/",
            "internal": False,
            "title": "Dashboard",
        },
        {
            "href": "https://www.pr-pilot.ai/blog/",
            "internal": False,
            "title": "Blog",
        },
    ],
    "heroes": {
        "index": "Transform your Development Workflow",
    },
}
html_sidebars = {
    "**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"]
}
