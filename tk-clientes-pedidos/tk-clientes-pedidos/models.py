from dataclasses import dataclass
from typing import List

@dataclass
class Cliente:
    id: int | None
    nome: str
    email: str | None
    telefone: str | None

@dataclass
class ItemPedido:
    produto: str
    quantidade: int
    preco_unit: float

@dataclass
class Pedido:
    id: int | None
    cliente_id: int
    data: str
    total: float
    itens: List[ItemPedido]

@dataclass
class Produto:
    id: int | None
    nome: str
    preco: float
    estoque: int
