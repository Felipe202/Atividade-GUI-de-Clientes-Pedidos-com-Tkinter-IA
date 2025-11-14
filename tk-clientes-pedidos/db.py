import sqlite3

DB_NAME = "app.db"


def conectar():
    # Define o row_factory para facilitar o acesso aos resultados, se necessário
    conn = sqlite3.connect(DB_NAME)
    # conn.row_factory = sqlite3.Row # Removido para manter a compatibilidade com o código existente que usa tuplas
    return conn


def create_tables():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
                CREATE TABLE IF NOT EXISTS clientes
                (
                    id
                    INTEGER
                    PRIMARY
                    KEY
                    AUTOINCREMENT,
                    nome
                    TEXT
                    NOT
                    NULL,
                    email
                    TEXT,
                    telefone
                    TEXT
                );
                """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS produtos
                (
                    id
                    INTEGER
                    PRIMARY
                    KEY
                    AUTOINCREMENT,
                    nome
                    TEXT
                    NOT
                    NULL,
                    preco
                    REAL
                    NOT
                    NULL,
                    estoque
                    INTEGER
                    DEFAULT
                    0
                );
                """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS pedidos
                (
                    id
                    INTEGER
                    PRIMARY
                    KEY
                    AUTOINCREMENT,
                    cliente_id
                    INTEGER
                    NOT
                    NULL,
                    data
                    TEXT
                    NOT
                    NULL,
                    total
                    REAL
                    NOT
                    NULL,
                    FOREIGN
                    KEY
                (
                    cliente_id
                ) REFERENCES clientes
                (
                    id
                )
                    );
                """)

    # NOTA: O nome da coluna 'produto' em itens_pedido é um TEXT, o que indica que está salvando o nome do produto,
    # e não um FOREIGN KEY. Mantendo o design original.
    cur.execute("""
                CREATE TABLE IF NOT EXISTS itens_pedido
                (
                    id
                    INTEGER
                    PRIMARY
                    KEY
                    AUTOINCREMENT,
                    pedido_id
                    INTEGER
                    NOT
                    NULL,
                    produto
                    TEXT
                    NOT
                    NULL,
                    quantidade
                    REAL
                    NOT
                    NULL,
                    preco_unit
                    REAL
                    NOT
                    NULL,
                    subtotal
                    REAL
                    NOT
                    NULL,
                    FOREIGN
                    KEY
                (
                    pedido_id
                ) REFERENCES pedidos
                (
                    id
                ) ON DELETE CASCADE
                    );
                """)

    conn.commit()
    conn.close()


# ---------- CLIENTES ----------
def list_clientes():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, email, telefone FROM clientes ORDER BY nome")
    rows = cur.fetchall()
    conn.close()
    return rows


def insert_cliente(nome, email, telefone):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)", (nome, email, telefone))
    conn.commit()
    conn.close()


def update_cliente(cliente_id, nome, email, telefone):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE clientes SET nome=?, email=?, telefone=? WHERE id=?",
            (nome, email, telefone, cliente_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print("Erro ao atualizar cliente:", e)
        return False
    finally:
        conn.close()


def delete_cliente(cliente_id):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM clientes WHERE id=?", (cliente_id,))
        conn.commit()
        return True
    except Exception as e:
        print("Erro ao deletar cliente:", e)
        return False
    finally:
        conn.close()


# ---------- PRODUTOS ----------
def insert_produto(nome, preco, estoque=0):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)", (nome, preco, estoque))
    conn.commit()
    conn.close()


def list_produtos(filtro=""):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    if filtro:
        cursor.execute(
            "SELECT id, nome, preco, estoque FROM produtos WHERE nome LIKE ? ORDER BY nome",
            (f"%{filtro}%",),
        )
    else:
        cursor.execute("SELECT id, nome, preco, estoque FROM produtos ORDER BY nome")

    rows = cursor.fetchall()
    conn.close()
    return rows


def update_produto(id_produto, nome, preco, estoque):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE produtos SET nome = ?, preco = ?, estoque = ? WHERE id = ?", (nome, preco, estoque, id_produto))
    conn.commit()
    conn.close()


def delete_produto(id_produto):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM produtos WHERE id = ?", (id_produto,))
    conn.commit()
    conn.close()


def get_produto(id_produto):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, preco, estoque FROM produtos WHERE id = ?", (id_produto,))
    row = cur.fetchone()
    conn.close()
    return row


# ---------- PEDIDOS ----------
def insert_pedido(cliente_id, data, total):
    conn = conectar()
    cur = conn.cursor()
    # aceita cliente_id numérico ou nome (tenta resolver nome -> id)
    try:
        cliente_id = int(cliente_id)
    except Exception:
        cur.execute("SELECT id FROM clientes WHERE nome = ?", (cliente_id,))
        r = cur.fetchone()
        if r:
            cliente_id = r[0]
        else:
            raise ValueError(f"Cliente '{cliente_id}' não encontrado.")

    cur.execute("INSERT INTO pedidos (cliente_id, data, total) VALUES (?, ?, ?)", (cliente_id, data, total))
    pedido_id = cur.lastrowid
    conn.commit()
    conn.close()
    return pedido_id


def insert_item_pedido(pedido_id, produto, quantidade, preco_unit):
    subtotal = float(quantidade) * float(preco_unit)
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO itens_pedido (pedido_id, produto, quantidade, preco_unit, subtotal) VALUES (?, ?, ?, ?, ?)",
        (pedido_id, produto, quantidade, preco_unit, subtotal)
    )
    conn.commit()
    conn.close()


def get_itens_pedido(pedido_id):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, produto, quantidade, preco_unit, subtotal FROM itens_pedido WHERE pedido_id = ?",
                (pedido_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def list_pedidos():
    """
    Retorna lista de tuplas padronizadas, ORDENADAS PELA DATA (mais recente primeiro):
    (id, cliente_id, cliente_nome, data, total)
    """
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
                SELECT p.id,
                       p.cliente_id,
                       COALESCE(c.nome, ''),
                       p.data,
                       p.total
                FROM pedidos p
                         LEFT JOIN clientes c ON c.id = p.cliente_id
                ORDER BY p.data DESC, p.id DESC
                """)
    rows = cur.fetchall()
    conn.close()
    return rows


# --- FUNÇÃO NOVA ---
def delete_pedido(pedido_id):
    """
    Remove um pedido e seus itens associados.
    A exclusão é feita em cascata (primeiro itens, depois o pedido).
    """
    conn = conectar()
    cur = conn.cursor()
    try:
        # 1. Exclui os itens associados ao pedido
        cur.execute("DELETE FROM itens_pedido WHERE pedido_id = ?", (pedido_id,))

        # 2. Exclui o pedido principal
        cur.execute("DELETE FROM pedidos WHERE id = ?", (pedido_id,))

        conn.commit()
        return True
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Erro ao deletar pedido {pedido_id}: {e}")
        raise e
    finally:
        conn.close()


# --- FIM FUNÇÃO NOVA ---


def get_pedidos_detalhados():
    """
    Retorna uma lista de dicionários, onde cada dicionário contém o resumo do pedido
    e uma lista de seus itens. Útil para relatórios.

    Estrutura:
    [
        {
            'id': 1,
            'cliente_nome': 'Cliente A',
            'data': '2025-01-01',
            'total': 150.00,
            'itens': [
                {'produto': 'Produto X', 'quantidade': 10, 'preco_unit': 10.0, 'subtotal': 100.0},
                {'produto': 'Produto Y', 'quantidade': 5, 'preco_unit': 10.0, 'subtotal': 50.0},
            ]
        },
        ...
    ]
    """
    conn = conectar()
    cur = conn.cursor()

    # Consulta que retorna todos os pedidos (ordenados) e seus itens em uma única lista grande
    cur.execute("""
                SELECT p.id,
                       COALESCE(c.nome, ''),
                       p.data,
                       p.total,
                       ip.produto,
                       ip.quantidade,
                       ip.preco_unit,
                       ip.subtotal
                FROM pedidos p
                         LEFT JOIN clientes c ON c.id = p.cliente_id
                         JOIN itens_pedido ip ON ip.pedido_id = p.id
                ORDER BY p.data DESC, p.id DESC
                """)

    rows = cur.fetchall()
    conn.close()

    pedidos_map = {}

    # Processa as linhas e agrupa os itens pelo ID do pedido
    for row in rows:
        (pedido_id, cliente_nome, data, total,
         produto, quantidade, preco_unit, subtotal) = row

        if pedido_id not in pedidos_map:
            # Cria o registro do pedido principal se ainda não existir
            pedidos_map[pedido_id] = {
                'id': pedido_id,
                'cliente_nome': cliente_nome,
                'data': data,
                'total': total,
                'itens': []
            }

        # Adiciona o item ao pedido
        pedidos_map[pedido_id]['itens'].append({
            'produto': produto,
            'quantidade': quantidade,
            'preco_unit': preco_unit,
            'subtotal': subtotal
        })

    # Converte o mapa de volta para uma lista de pedidos ordenados
    return list(pedidos_map.values())


# utilitário de debug
def debug_list_clientes():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, nome FROM clientes ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows


create_tables()  # Chamada para criar as tabelas na inicialização