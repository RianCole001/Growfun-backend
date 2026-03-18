"""
URL configuration for growfund project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import traceback


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_migrations(request):
    """Admin-only: run pending migrations on the live server."""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'success': False, 'error': 'Admin only'}, status=403)
    try:
        from django.core.management import call_command
        from io import StringIO
        out = StringIO()
        call_command('migrate', '--noinput', stdout=out, stderr=out)
        # Invalidate demo column cache so views re-check after migration
        try:
            from demo.views import _COL_CACHE
            _COL_CACHE.clear()
        except Exception:
            pass
        return Response({'success': True, 'output': out.getvalue()})
    except Exception as e:
        return Response({'success': False, 'error': str(e), 'traceback': traceback.format_exc()}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def db_check(request):
    """Admin-only: check migration state and DB column existence."""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'success': False, 'error': 'Admin only'}, status=403)
    from django.db import connection
    from django.db.migrations.executor import MigrationExecutor

    executor = MigrationExecutor(connection)
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    pending = [f"{app}.{name}" for (app, name), _ in plan] if plan else []

    def col_exists(table, col):
        try:
            with connection.cursor() as cursor:
                cols = [c.name for c in connection.introspection.get_table_description(cursor, table)]
            return col in cols
        except Exception as e:
            return f"error: {e}"

    def table_exists(table):
        try:
            return table in connection.introspection.table_names()
        except Exception as e:
            return f"error: {e}"

    return Response({
        'success': True,
        'pending_migrations': pending,
        'columns': {
            'demo_demoinvestment.current_price': col_exists('demo_demoinvestment', 'current_price'),
            'binary_trading_houseedgeconfig.atm_is_loss': col_exists('binary_trading_houseedgeconfig', 'atm_is_loss'),
        },
        'tables': {
            'binary_trading_demotradingstats': table_exists('binary_trading_demotradingstats'),
        },
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/investments/', include('investments.urls')),
    path('api/crypto/', include('investments.urls')),
    path('api/transactions/', include('transactions.urls')),
    path('api/admin/deposits/', include('transactions.urls')),
    path('api/admin/withdrawals/', include('transactions.urls')),
    path('api/admin/investments/', include('transactions.urls')),
    path('api/admin/transactions/', include('transactions.urls')),
    path('api/referrals/', include('referrals.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/demo/', include('demo.urls')),
    path('api/settings/', include('settings_app.urls')),
    path('api/binary/', include('binary_trading.urls')),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/admin/run-migrations/', run_migrations, name='run-migrations'),
    path('api/admin/db-check/', db_check, name='db-check'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = 'GrowFund Administration'
admin.site.site_title = 'GrowFund Admin'
admin.site.index_title = 'Welcome to GrowFund Admin Portal'
