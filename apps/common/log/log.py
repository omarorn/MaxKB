# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： log.py
    @date：2025/3/14 16:09
    @desc:
"""

from setting.models.log_management import Log


def _get_ip_address(request):
    """
    获取ip地址
    @param request:
    @return:
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def _get_user(request):
    """
    获取用户
    @param request:
    @return:
    """
    user = request.user
    return {
        "id": str(user.id),
        "email": user.email,
        "phone": user.phone,
        "nick_name": user.nick_name,
        "username": user.username,
        "role": user.role,
    }


def _get_details(request):
    path = request.path
    body = request.data
    query = request.query_params
    return {
        'path': path,
        'body': body,
        'query': query
    }


def log(menu: str, operate, get_user=_get_user, get_ip_address=_get_ip_address, get_details=_get_details):
    """
    记录审计日志
    @param menu: 操作菜单 str
    @param operate: 操作 str|func 如果是一个函数 入参将是一个request 响应为str def operate(request): return "操作菜单"
    @param get_user: 获取用户
    @param get_ip_address:获取IP地址
    @param get_details: 获取执行详情
    @return:
    """

    def inner(func):
        def run(view, request, **kwargs):
            status = 200
            try:
                return func(view, request, **kwargs)
            except Exception as e:
                status = 500
            finally:
                ip = get_ip_address(request)
                user = get_user(request)
                details = get_details(request)
                _operate = operate
                if callable(operate):
                    _operate = operate(request)
                # 插入审计日志
                Log(menu=menu, operate=_operate, user=user, status=status, ip_address=ip, details=details).save()

        return run

    return inner
