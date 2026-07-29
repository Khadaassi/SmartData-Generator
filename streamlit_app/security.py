import re

_CREDENTIALS_PATTERN = re.compile(r"^(?P<prefix>[a-zA-Z][a-zA-Z0-9+.\-]*://)(?P<credentials>[^@/]+)@(?P<rest>.+)$")


def mask_database_url(url: str) -> str:
    """Masque le mot de passe d'une URL de connexion (user:password@host) pour un
    affichage sûr : seul l'identifiant utilisateur reste visible."""
    if not url:
        return url
    match = _CREDENTIALS_PATTERN.match(url)
    if not match:
        return url
    user = match.group("credentials").split(":", 1)[0]
    return f"{match.group('prefix')}{user}:***@{match.group('rest')}"
