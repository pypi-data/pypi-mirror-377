import json
from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View

from .backends import get_backend
from .forms import IssueForm


class IssueAPIView(View):
    def get(self, request: "HttpRequest", *args: Any, **kwargs: Any) -> HttpResponse:
        backend = get_backend(request)
        form = IssueForm(backend=backend)
        return render(request, "issues/issue_form.html", {"form": form})

    def post(self, request: "HttpRequest", *args: Any, **kwargs: Any) -> JsonResponse:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "errors": "Invalid JSON payload."}, status=400)

        backend = get_backend(request)
        form = IssueForm(data, backend=backend)
        if form.is_valid():
            backend.create_ticket(form.cleaned_data)  # type: ignore[arg-type]
            return JsonResponse({"success": True, "message": "Ticket created successfully!"})
        return JsonResponse({"success": False, "errors": form.errors, "message": "Please correct the errors below."})
