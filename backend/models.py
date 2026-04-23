
from pydantic import BaseModel
class Investigacao(BaseModel):
    id: str
    titulo: str
    alvo: str
    descricao: str
