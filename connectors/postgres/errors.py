class SchemaReaderError(Exception):
    """Erreur levée lors de la connexion ou de l'analyse d'un schéma PostgreSQL.

    Porte un code stable pour que l'appelant (Schema Service) puisse catégoriser
    l'erreur sans avoir à parser le message.
    """

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class DataWriteError(Exception):
    """Erreur levée lors de l'insertion de données dans PostgreSQL.

    Porte un code stable pour que l'appelant (Insert Service) puisse catégoriser
    l'erreur sans avoir à parser le message.
    """

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)
