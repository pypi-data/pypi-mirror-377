import json
import os

from txhttputil.site.BasicResource import BasicResource


class JsonMetricsResource(BasicResource):
    def __init__(self, metricsPath):
        BasicResource.__init__(self)
        self.metricsPath = metricsPath

    def getChild(self, path, request):
        return self

    def render_GET(self, request):
        # Get the requested file path from the URL
        pathSegments = [
            segment.decode("utf-8") for segment in request.prepath[1:]
        ]

        if not pathSegments:
            request.setResponseCode(404)
            return b"File not found"

        # Reconstruct the file path
        requestedFile = os.path.join(*pathSegments)
        fullPath = os.path.join(self.metricsPath, requestedFile)

        # Security check - ensure the path is within metricsPath
        if not os.path.realpath(fullPath).startswith(
            os.path.realpath(self.metricsPath)
        ):
            request.setResponseCode(403)
            return b"SECURITY: Access denied"

        # Check if file exists and is a JSON file
        if not os.path.exists(fullPath):
            request.setResponseCode(404)
            return b"File not found"

        if not fullPath.endswith(".json"):
            request.setResponseCode(404)
            return b"File not found"

        # Check file size is less than 5KB
        # The largest test JSON metric is 1.3KB
        if os.path.getsize(fullPath) >= 1024 * 5:
            request.setResponseCode(413)
            return b"SECURITY: File too large"

        # Read and validate JSON content
        try:
            with open(fullPath, "r", encoding="utf-8") as f:
                content = f.read()

            # Validate JSON
            json.loads(content)

            # Set appropriate headers and return content
            request.responseHeaders.setRawHeaders(
                "content-type", ["application/json"]
            )
            return content.encode("utf-8")

        except (json.JSONDecodeError, UnicodeDecodeError):
            request.setResponseCode(400)
            return b"SECURITY: Invalid JSON content"
        except IOError:
            request.setResponseCode(500)
            return b"SECURITY: Error reading file"