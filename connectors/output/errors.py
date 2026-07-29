class DataWriterError(Exception):
    """Erreur de production levée par un connecteur de sortie (CSV, JSON, ...).

    Porte un code stable pour que l'appelant (Export Service) puisse catégoriser
    l'erreur sans avoir à parser le message.
    """

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)
