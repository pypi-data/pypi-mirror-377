from openedx.core.djangoapps.plugins.constants import ProjectType, SettingsType
from openedx.core.djangoapps.plugins.plugin_settings import PluginSettings

class AIImportCMSAppConfig(PluginSettings):
    """
    Plugin configuration for CMS.
    """
    plugin_app = {
#        "settings_config": {
#            "cms.djangoapp": {
#                "common": {"relative_path": "settings.common"},
#            },
#        },
#        "urls": {
#            "cms.djangoapp": {
#                "namespace": "ai_import_plugin",
#                "regex": r"^ai-import/",
#                "relative_path": "urls",
#            }
#        },
        "template_extensions": {
            ProjectType.CMS: {
                "index.html": {   # inject into cms/templates/index.html
                    "before": ["new_course_button"],  # hook point
                    "template": "ai_import_plugin/import_button.html",
                }
            }
        },
    }

