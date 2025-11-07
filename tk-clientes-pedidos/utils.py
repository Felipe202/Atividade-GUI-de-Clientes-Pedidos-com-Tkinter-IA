# utils.py
import re
import logging
import os
from datetime import datetime
from tkinter import messagebox

# Logging app actions
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

def is_valid_email(email: str) -> bool:
    if not email:
        return True
    return bool(EMAIL_RE.match(email))

def is_valid_phone(phone: str) -> bool:
    if not phone:
        return True
    digits = re.sub(r"\D", "", phone)
    return 8 <= len(digits) <= 15

# App action logger (create/edit/delete)
def log_action(action: str, entity: str, entity_id: int | None = None, note: str = ""):
    msg = f"{action} {entity} id={entity_id} {note}".strip()
    logging.info(msg)

# Simple helper to show messages
def show_info(title, msg):
    messagebox.showinfo(title, msg)

def show_error(title, msg):
    messagebox.showerror(title, msg)

def show_confirm(title, msg) -> bool:
    return messagebox.askyesno(title, msg)

# Analysis helper (local) + hook for external LLM
def analyze_pedidos_summary(pedidos_rows):
    """
    Recebe lista de pedidos (cada item: (id, cliente_id, nome, data, total, itens_list))
    Retorna um dicionário com resumo: total_pedidos, soma_total, ticket_medio, produtos_mais_vendidos
    """
    resumo = {"total_pedidos": 0, "soma_total": 0.0, "ticket_medio": 0.0, "produtos": {}}
    if not pedidos_rows:
        return resumo
    resumo["total_pedidos"] = len(pedidos_rows)
    for pid, cid, nome, data, total, itens in pedidos_rows:
        resumo["soma_total"] += float(total)
        # itens expected as list of tuples (produto, qtd, preco)
        for prod, qtd, preco in itens:
            resumo["produtos"].setdefault(prod, 0)
            resumo["produtos"][prod] += int(qtd)
    resumo["ticket_medio"] = resumo["soma_total"] / resumo["total_pedidos"] if resumo["total_pedidos"] else 0.0
    # top products
    produtos_ordenados = sorted(resumo["produtos"].items(), key=lambda x: x[1], reverse=True)
    resumo["produtos_mais_vendidos"] = produtos_ordenados[:5]
    return resumo

def build_prompt_from_summary(resumo: dict) -> str:
    lines = [
        "Analise de vendas (resumo):",
        f"Total de pedidos: {resumo.get('total_pedidos',0)}",
        f"Soma total: {resumo.get('soma_total',0):.2f}",
        f"Ticket médio: {resumo.get('ticket_medio',0):.2f}",
        "Produtos mais vendidos:"
    ]
    for prod, qtd in resumo.get("produtos_mais_vendidos", []):
        lines.append(f"- {prod}: {qtd} unidades")
    prompt = "\n".join(lines)
    return prompt

# Hook to call an LLM (optional). We do NOT call any remote API here by default.
def call_llm_api(prompt: str, provider: str = "none", api_key: str | None = None) -> str:
    """
    provider: 'openai' | 'ollama' | 'none'
    If provider == 'none', just return the prompt as a 'simulated' analysis.
    If you want to enable real calls, implement and provide api_key in secure way.
    """
    if provider == "none" or not api_key:
        return "=== Simulated IA Response ===\n\n" + prompt
    # Placeholder for actual implementations (left intentionally simple)
    if provider == "openai":
        # user can implement their own call here
        raise NotImplementedError("Implement OpenAI call if desired.")
    if provider == "ollama":
        raise NotImplementedError("Implement Ollama call if desired.")
    return "Provider not supported."
