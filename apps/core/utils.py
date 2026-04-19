from decimal import Decimal

from django.db.models import ProtectedError


def format_protected_error(e: ProtectedError) -> str:
    """Message utilisateur listant les objets bloquant une suppression."""
    objs = list(e.protected_objects)
    noms = ", ".join(str(o) for o in objs[:5])
    suite = "…" if len(objs) > 5 else ""
    return (
        "Suppression impossible : cet élément est référencé par "
        f"{len(objs)} enregistrement(s) lié(s) "
        f"({noms}{suite}). Supprimez ou réaffectez-les d'abord."
    )


def money(value):
    """Format d'un montant GNF avec espaces milliers."""
    if value is None:
        return "-"
    try:
        v = Decimal(value)
    except Exception:
        return str(value)
    neg = v < 0
    v = abs(v)
    s = f"{v:,.0f}".replace(",", " ")
    return f"({s})" if neg else s


def pct(value, decimals=1):
    if value is None:
        return "-"
    return f"{float(value)*100:.{decimals}f}%"
