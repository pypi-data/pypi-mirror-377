from txhttputil.site.BasicResource import BasicResource
from vortex.VortexFactory import VortexFactory

from peek_logic_service.server.sw_download.PeekSwDownloadResource import (
    PeekSwUpdateDownloadResource,
)
from peek_logic_service.server.sw_download.PluginSwDownloadResource import (
    PluginSwDownloadResource,
)
from peek_logic_service.server.peek_metrics_list_resource import (
    PeekMetricsListResource,
)
from peek_logic_service.server.json_metrics_resource import JsonMetricsResource
from peek_logic_service.server.metrics_tar_resource import MetricsTarResource

platformSiteRoot = BasicResource()


def setupPlatformSite():
    from peek_platform import PeekPlatformConfig

    # Add the platform download resource
    platformSiteRoot.putChild(
        b"peek_logic_service.sw_install.platform.download",
        PeekSwUpdateDownloadResource(),
    )

    # Add the plugin download resource
    platformSiteRoot.putChild(
        b"peek_logic_service.sw_install.plugin.download",
        PluginSwDownloadResource(),
    )
    vortexWebsocketResource = VortexFactory.createHttpWebsocketResource(
        PeekPlatformConfig.componentName
    )
    platformSiteRoot.putChild(b"vortexws", vortexWebsocketResource)

    metricsResource = JsonMetricsResource(
        PeekPlatformConfig.config.platformMetricsPath
    )
    platformSiteRoot.putChild(b"metrics", metricsResource)

    platformSiteRoot.putChild(
        b"metrics-ls",
        PeekMetricsListResource(PeekPlatformConfig.config.platformMetricsPath),
    )

    platformSiteRoot.putChild(
        b"metrics.tar",
        MetricsTarResource(PeekPlatformConfig.config.platformMetricsPath),
    )
