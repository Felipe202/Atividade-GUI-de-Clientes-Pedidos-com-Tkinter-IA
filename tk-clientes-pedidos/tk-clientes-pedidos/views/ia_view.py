# views/ia_view.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox
from db import list_pedidos, get_itens_pedido
from utils import analyze_pedidos_summary, build_prompt_from_summary, call_llm_api, log_action

class IAView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True, padx=8, pady=8)
        self.create_widgets()

    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(fill="x")
        ttk.Button(top, text="Analisar últimos 5 pedidos", command=self.analyze_last_5).pack(side="left", padx=6)
        ttk.Label(top, text="Provider (none/openai/ollama):").pack(side="left", padx=6)
        self.provider_var = tk.StringVar(value="none")
        ttk.Entry(top, textvariable=self.provider_var, width=10).pack(side="left")
        ttk.Label(top, text="API Key (opcional)").pack(side="left", padx=6)
        self.key_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.key_var, width=20).pack(side="left")

        self.txt = tk.Text(self, height=20)
        self.txt.pack(fill="both", expand=True, pady=6)

    def analyze_last_5(self):
        try:
            pedidos = list_pedidos()
            # pedidos rows: (id, cliente_id, nome, data, total)
            pedidos_sorted = sorted(pedidos, key=lambda r: r[3], reverse=True)[:5]
            pedidos_with_items = []
            for p in pedidos_sorted:
                pid = p[0]
                itens = get_itens_pedido(pid)
                # convert to (produto,qtd,preco)
                itens_clean = [(it[1], it[2], it[3]) for it in itens]
                pedidos_with_items.append((p[0], p[1], p[2], p[3], p[4], itens_clean))
            resumo = analyze_pedidos_summary([(pid,cid,nome,data,total,itens) for pid,cid,nome,data,total,itens in pedidos_with_items])
            prompt = build_prompt_from_summary(resumo)
            provider = self.provider_var.get().strip() or "none"
            api_key = self.key_var.get().strip() or None
            result = call_llm_api(prompt, provider=provider, api_key=api_key)
            self.txt.delete("1.0", "end")
            self.txt.insert("end", result)
            log_action("Analyze", "Pedidos", note=f"provider={provider}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha na análise: {e}")
