import json
import os
import tarfile
from io import BytesIO

from txhttputil.site.BasicResource import BasicResource


class MetricsTarResource(BasicResource):
    isLeaf = True

    def __init__(self, metricsPath):
        BasicResource.__init__(self)
        self.metricsPath = metricsPath

    def _validateJsonFile(self, fullPath, request):
        """Validate a single JSON file for inclusion in tar"""
        # Security check - ensure the path is within metricsPath
        if not os.path.realpath(fullPath).startswith(
            os.path.realpath(self.metricsPath)
        ):
            request.setResponseCode(403)
            return b"SECURITY: Access denied"
        
        # Check file size is less than 5KB
        # The largest test JSON metric is 1.3KB
        if os.path.getsize(fullPath) >= 1024 * 5:
            request.setResponseCode(413)
            return b"SECURITY: File too large"
        
        # Validate JSON content
        try:
            with open(fullPath, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Validate JSON
            json.loads(content)
            return None
            
        except (json.JSONDecodeError, UnicodeDecodeError):
            request.setResponseCode(400)
            return b"SECURITY: Invalid JSON content"
        except IOError:
            request.setResponseCode(500)
            return b"SECURITY: Error reading file"

    def render_GET(self, request):
        # Create tar file in memory
        tarBuffer = BytesIO()
        
        if not os.path.exists(self.metricsPath):
            # Create empty tar if metrics path doesn't exist
            with tarfile.open(fileobj=tarBuffer, mode='w') as tar:
                pass
        else:
            # Create uncompressed tar file
            with tarfile.open(fileobj=tarBuffer, mode='w') as tar:
                # Walk through all files and validate before adding
                for root, dirs, filenames in os.walk(self.metricsPath):
                    for filename in filenames:
                        # Only process JSON files
                        if not filename.endswith(".json"):
                            continue
                            
                        fullPath = os.path.join(root, filename)
                        
                        # Validate the file - returns error bytes if validation fails
                        validationError = self._validateJsonFile(fullPath, request)
                        if validationError:
                            return validationError
                        
                        # File passed all validation, add to tar
                        relativePath = os.path.relpath(fullPath, self.metricsPath)
                        arcname = os.path.join('metrics', relativePath)
                        tar.add(fullPath, arcname=arcname)
        
        tarData = tarBuffer.getvalue()
        tarBuffer.close()

        # Set appropriate headers
        request.responseHeaders.setRawHeaders(
            "content-type", ["application/x-tar"]
        )
        request.responseHeaders.setRawHeaders(
            "content-disposition", ["attachment; filename=metrics.tar"]
        )

        return tarData