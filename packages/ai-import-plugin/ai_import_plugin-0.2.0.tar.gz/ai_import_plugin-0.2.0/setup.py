from setuptools import setup, find_packages

setup(
    name="ai-import-plugin",
    version="0.2.0",
    description="Django CMS plugin for Open edX to add an 'Import from AI' button",
    packages=find_packages(),
    include_package_data=True,   # include templates/static files
    python_requires='>=3.10',
    install_requires=[
        "Django>=4.2.20",      # adjust to your Open edX release
    ],
    entry_points={
        # Register the plugin with Open edX
        "lms.djangoapp": [
            # no LMS part, but required to declare
        ],
        "cms.djangoapp": [
            "ai_import_plugin = ai_import_plugin.cms_app:AIImportCMSAppConfig",
        ],
    },
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
    ],
)

