import json
import os

from txhttputil.site.BasicResource import BasicResource


class PeekMetricsListResource(BasicResource):
    isLeaf = True

    def __init__(self, metricsPath):
        BasicResource.__init__(self)
        self.metricsPath = metricsPath

    def render_GET(self, request):
        request.responseHeaders.setRawHeaders(
            "content-type", ["application/json"]
        )

        files = []

        if os.path.exists(self.metricsPath):
            for root, dirs, filenames in os.walk(self.metricsPath):
                for filename in filenames:
                    if filename.endswith(".json"):
                        fullPath = os.path.join(root, filename)
                        relativePath = os.path.relpath(
                            fullPath, self.metricsPath
                        )
                        resourcePath = "/metrics/" + relativePath.replace(
                            os.sep, "/"
                        )
                        files.append(resourcePath)

        filesJson = json.dumps({"files": files}, ensure_ascii=False)

        return filesJson.encode("utf-8")
