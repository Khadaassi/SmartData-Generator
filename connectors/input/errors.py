class DataReaderError(Exception):
    """Erreur de lecture levée par un connecteur d'entrée (CSV, JSON, ...).

    Porte un code stable pour que l'appelant (API, Execution Reporter) puisse
    catégoriser l'erreur sans avoir à parser le message.
    """

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)
