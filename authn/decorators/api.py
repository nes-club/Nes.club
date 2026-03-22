import functools

from django.http import JsonResponse, HttpResponse

from club.exceptions import ApiException, ClubException, ApiAuthRequired


def api(require_auth=True, scopes=None):
    def decorator(view):
        @functools.wraps(view)
        def wrapper(request, *args, **kwargs):
            if require_auth and not request.me:
                raise ApiAuthRequired()

            status_code = 200
            try:
                results = view(request, *args, **kwargs)
            except ApiException:
                raise
            except ClubException as ex:
                raise ApiException(
                    code=ex.code,
                    title=ex.title,
                    message=ex.message,
                    data=ex.data,
                )
            except Exception as ex:
                raise ApiException(
                    code=ex.__class__.__name__,
                    title=str(ex),
                )

            if is_ajax(request):
                return JsonResponse(data=results, status=status_code, json_dumps_params=dict(ensure_ascii=False))
            elif isinstance(results, dict):
                return JsonResponse(data=results, status=status_code, json_dumps_params=dict(ensure_ascii=False))
            elif isinstance(results, str):
                return HttpResponse(results, content_type="text/plain; charset=utf-8")
            else:
                return results

        return wrapper
    return decorator


def is_ajax(request):
    return bool(request.GET.get("is_ajax"))
