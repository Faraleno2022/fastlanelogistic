from django.apps import AppConfig


class PaieConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'paie'
    verbose_name = 'Gestion de la paie'
    
    def ready(self):
        import paie.signals  # noqa
        self._patch_json_decimal()
        self._write_ready_marker()

    @staticmethod
    def _patch_json_decimal():
        import json
        from decimal import Decimal
        from datetime import date, datetime
        if getattr(json.JSONEncoder, '_gestionrh_patched', False):
            return
        _orig = json.JSONEncoder.default

        def _default(self, o):
            if isinstance(o, Decimal):
                return str(o)
            if isinstance(o, (datetime, date)):
                return o.isoformat()
            return _orig(self, o)

        json.JSONEncoder.default = _default
        json.JSONEncoder._gestionrh_patched = True

    @staticmethod
    def _write_ready_marker():
        import os, sys, json
        from datetime import datetime as _dt
        paths = []
        try:
            from django.conf import settings
            base = getattr(settings, 'BASE_DIR', None)
            if base:
                paths.append(os.path.join(str(base), 'logs', 'paie_ready.log'))
        except Exception:
            pass
        try:
            import tempfile
            paths.append(os.path.join(tempfile.gettempdir(), 'paie_ready.log'))
        except Exception:
            pass
        paths.append(os.path.expanduser(r'~\paie_ready.log'))
        for p in paths:
            try:
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, 'a', encoding='utf-8') as fp:
                    fp.write(f"{_dt.now().isoformat()} ready() fired, patched={getattr(json.JSONEncoder, '_gestionrh_patched', False)}, sys.prefix={sys.prefix}\n")
            except Exception:
                pass
