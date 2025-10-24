import sqlite3
from contextlib import closing
import logging

DB_NAME = "clientes_pedidos.db"
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def get_conn():
    return sqlite3.connect(DB_NAME)

def init_db():
    with closing(get_conn()) as conn:
        cur = conn.cursor()
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT,
            telefone TEXT
        );

        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            total REAL NOT NULL,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        );

        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            produto TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unit REAL NOT NULL,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
        );

        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            estoque INTEGER DEFAULT 0
        );
        """)
        conn.commit()
    logging.info("Banco inicializado")

def execute(query, params=()):
    try:
        with closing(get_conn()) as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            return cur.lastrowid
    except Exception as e:
        logging.exception("Erro no DB execute")
        raise

def fetchall(query, params=()):
    with closing(get_conn()) as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()

def fetchone(query, params=()):
    with closing(get_conn()) as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchone()

# Clientes
def insert_cliente(nome, email, telefone):
    return execute("INSERT INTO clientes (nome,email,telefone) VALUES (?,?,?)", (nome,email,telefone))

def update_cliente(cliente_id, nome, email, telefone):
    execute("UPDATE clientes SET nome=?, email=?, telefone=? WHERE id=?", (nome,email,telefone,cliente_id))

def delete_cliente(cliente_id):
    execute("DELETE FROM clientes WHERE id=?", (cliente_id,))

def list_clientes(filter_text=""):
    if filter_text:
        term = f"%{filter_text}%"
        return fetchall("SELECT id,nome,email,telefone FROM clientes WHERE nome LIKE ? OR email LIKE ? ORDER BY nome", (term,term))
    return fetchall("SELECT id,nome,email,telefone FROM clientes ORDER BY nome")

# Pedidos
def insert_pedido_with_items(cliente_id, data, total, items):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("BEGIN")
        cur.execute("INSERT INTO pedidos (cliente_id,data,total) VALUES (?,?,?)", (cliente_id,data,total))
        pedido_id = cur.lastrowid
        for produto, quantidade, preco_unit in items:
            cur.execute("INSERT INTO itens_pedido (pedido_id,produto,quantidade,preco_unit) VALUES (?,?,?,?)",
                        (pedido_id,produto,quantidade,preco_unit))
        conn.commit()
        return pedido_id
    except Exception:
        conn.rollback()
        logging.exception("Falha ao salvar pedido")
        raise
    finally:
        conn.close()

def list_pedidos():
    return fetchall("""
    SELECT p.id,p.cliente_id,c.nome,p.data,p.total
    FROM pedidos p JOIN clientes c ON c.id = p.cliente_id
    ORDER BY p.data DESC
    """)

def get_itens_pedido(pedido_id):
    return fetchall("SELECT id,produto,quantidade,preco_unit FROM itens_pedido WHERE pedido_id=?", (pedido_id,))

def delete_pedido(pedido_id):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("BEGIN")
        cur.execute("DELETE FROM itens_pedido WHERE pedido_id=?", (pedido_id,))
        cur.execute("DELETE FROM pedidos WHERE id=?", (pedido_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        logging.exception("Falha ao deletar pedido")
        raise
    finally:
        conn.close()

# Produtos
def insert_produto(nome, preco, estoque):
    return execute("INSERT INTO produtos (nome, preco, estoque) VALUES (?,?,?)", (nome, preco, estoque))

def update_produto(produto_id, nome, preco, estoque):
    execute("UPDATE produtos SET nome=?, preco=?, estoque=? WHERE id=?", (nome, preco, estoque, produto_id))

def delete_produto(produto_id):
    execute("DELETE FROM produtos WHERE id=?", (produto_id,))

def list_produtos(filter_text=""):
    if filter_text:
        term = f"%{filter_text}%"
        return fetchall("SELECT id,nome,preco,estoque FROM produtos WHERE nome LIKE ? ORDER BY nome", (term,))
    return fetchall("SELECT id,nome,preco,estoque FROM produtos ORDER BY nome")
