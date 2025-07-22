# SPDX-License-Identifier: EUPL-1.2
# Copyright (C) 2019 - 2020 Dimpact
import os
from typing import Dict, Optional

from django.conf import settings
from django.http import HttpResponse

from rest_framework.response import Response
from rest_framework.reverse import reverse
from vng_api_common.middleware import (
    VERSION_HEADER,
    APIVersionHeaderMiddleware as _APIVersionHeaderMiddleware,
)


def reverse_with_version(api: str, version: Optional[str] = None) -> str:
    """Helper to reverse API root with version injected."""
    version = version or "1"
    return reverse(f"api-root-{api}", kwargs={"version": version})


def get_version_mapping() -> Dict[str, str]:
    apis = ["zaken"]
    return {}
    return {
        reverse_with_version(api, version="1"): getattr(
            settings, f"{api.upper()}_API_VERSION"
        )
        for api in apis
    }


class APIVersionHeaderMiddleware(_APIVersionHeaderMiddleware):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.version_mapping = get_version_mapping()

    def __call__(self, request):
        if self.get_response is None:
            return None

        response = self.get_response(request)

        if not isinstance(response, Response):
            return response

        version = self._get_version(request.path)
        if version is not None:
            response[VERSION_HEADER] = version

        return response

    def _get_version(self, path: str) -> Optional[str]:
        return None
        for prefix, version in self.version_mapping.items():
            if path.startswith(prefix):
                return version
        return None


class PyInstrumentMiddleware:  # pragma:no cover
    """
    Middleware that's included in dev environments if `USE_PYINSTRUMENT=true`,
    allows profiling of the request/response cycle. Profiling results can be viewed
    at `/_profiling`
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.profiler_output_path = "/tmp/pyinstrument_profile.html"

    def __call__(self, request):
        if request.path.startswith("/_profiling"):
            return self._serve_profile()

        # Local import to avoid having to install this in production environments
        from pyinstrument import Profiler

        profiler = Profiler()
        profiler.start()

        response = self.get_response(request)

        profiler.stop()

        # Save the profile to an HTML file
        with open(self.profiler_output_path, "w") as f:
            f.write(profiler.output_html())

        return response

    def _serve_profile(self):
        """Serve the latest profiling report"""
        if os.path.exists(self.profiler_output_path):
            with open(self.profiler_output_path, "r") as f:
                return HttpResponse(f.read(), content_type="text/html")
        return HttpResponse("No profiling report available yet.", status=404)
