import sqlite3

DB_NAME = "app.db"

# --------------------------------------------------
# CONEXÃO
# --------------------------------------------------
def conectar():
    return sqlite3.connect(DB_NAME)


# --------------------------------------------------
# CRIAÇÃO DAS TABELAS
# --------------------------------------------------
def create_tables():
    conn = conectar()
    cur = conn.cursor()

    # Clientes
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT,
        telefone TEXT
    );
    """)

    # Produtos (com campo estoque)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        preco REAL NOT NULL,
        estoque INTEGER DEFAULT 0
    );
    """)

    # Pedidos
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        data TEXT NOT NULL,
        total REAL NOT NULL,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
    );
    """)

    # Itens do pedido
    cur.execute("""
    CREATE TABLE IF NOT EXISTS itens_pedido (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER NOT NULL,
        produto TEXT NOT NULL,
        quantidade REAL NOT NULL,
        preco_unit REAL NOT NULL,
        subtotal REAL NOT NULL,
        FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
    );
    """)

    conn.commit()
    conn.close()


# --------------------------------------------------
# CLIENTES
# --------------------------------------------------
def list_clientes():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, email, telefone FROM clientes ORDER BY nome")
    data = cur.fetchall()
    conn.close()
    return data


def insert_cliente(nome, email, telefone):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)", (nome, email, telefone))
    conn.commit()
    conn.close()


def update_cliente(id_cliente, nome, email, telefone):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        UPDATE clientes
        SET nome = ?, email = ?, telefone = ?
        WHERE id = ?
    """, (nome, email, telefone, id_cliente))
    conn.commit()
    conn.close()


def delete_cliente(id_cliente):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE id = ?", (id_cliente,))
    conn.commit()
    conn.close()


# --------------------------------------------------
# PRODUTOS
# --------------------------------------------------
def insert_produto(nome, preco, estoque):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)", (nome, preco, estoque))
    conn.commit()
    conn.close()


def list_produtos(*args):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, preco, estoque FROM produtos ORDER BY nome")
    rows = cur.fetchall()
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
    cur.execute("SELECT * FROM produtos WHERE id = ?", (id_produto,))
    produto = cur.fetchone()
    conn.close()
    return produto


# --------------------------------------------------
# PEDIDOS
# --------------------------------------------------
def insert_pedido(cliente_nome, data, total):
    conn = conectar()
    cur = conn.cursor()

    # Busca o ID do cliente pelo nome
    cur.execute("SELECT id FROM clientes WHERE nome = ?", (cliente_nome,))
    cliente = cur.fetchone()
    if not cliente:
        raise Exception("Cliente não encontrado.")
    cliente_id = cliente[0]

    cur.execute("INSERT INTO pedidos (cliente_id, data, total) VALUES (?, ?, ?)", (cliente_id, data, total))
    pedido_id = cur.lastrowid

    conn.commit()
    conn.close()
    return pedido_id


def insert_item_pedido(pedido_id, produto, quantidade, preco_unit):
    subtotal = float(quantidade) * float(preco_unit)
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO itens_pedido (pedido_id, produto, quantidade, preco_unit, subtotal)
        VALUES (?, ?, ?, ?, ?)
    """, (pedido_id, produto, quantidade, preco_unit, subtotal))
    conn.commit()
    conn.close()


def list_pedidos():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, c.nome AS cliente, p.data, p.total
        FROM pedidos p
        JOIN clientes c ON c.id = p.cliente_id
        ORDER BY p.id DESC
    """)
    data = cur.fetchall()
    conn.close()
    return data


def get_itens_pedido(pedido_id):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT produto, quantidade, preco_unit, subtotal
        FROM itens_pedido
        WHERE pedido_id = ?
    """, (pedido_id,))
    data = cur.fetchall()
    conn.close()
    return data
