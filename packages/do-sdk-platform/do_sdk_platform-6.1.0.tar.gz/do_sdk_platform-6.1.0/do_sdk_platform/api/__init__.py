# flake8: noqa

if __import__("typing").TYPE_CHECKING:
    # import apis into api package
    from do_sdk_platform.api.billing_api import BillingApi
    from do_sdk_platform.api.data_api import DataApi
    from do_sdk_platform.api.entities_api import EntitiesApi
    from do_sdk_platform.api.file_api import FileApi
    from do_sdk_platform.api.tools_api import ToolsApi
    
else:
    from lazy_imports import LazyModule, as_package, load

    load(
        LazyModule(
            *as_package(__file__),
            """# import apis into api package
from do_sdk_platform.api.billing_api import BillingApi
from do_sdk_platform.api.data_api import DataApi
from do_sdk_platform.api.entities_api import EntitiesApi
from do_sdk_platform.api.file_api import FileApi
from do_sdk_platform.api.tools_api import ToolsApi

""",
            name=__name__,
            doc=__doc__,
        )
    )
