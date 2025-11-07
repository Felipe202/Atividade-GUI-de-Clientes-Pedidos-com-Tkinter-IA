# views/reports_view.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from db import list_clientes, list_pedidos, get_itens_pedido
import csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import logging
from utils import log_action

logger = logging.getLogger(__name__)

class ReportsFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True, padx=8, pady=8)
        self.create_widgets()

    def create_widgets(self):
        pad={"padx":6,"pady":4}
        top = ttk.Frame(self)
        top.pack(fill="x", pady=4)
        ttk.Label(top, text="Cliente (opcional)").pack(side="left")
        clientes = list_clientes()
        self.clientes_map = {c[1]:c[0] for c in clientes}
        self.cb_cliente = ttk.Combobox(top, values=list(self.clientes_map.keys()), state="readonly")
        self.cb_cliente.pack(side="left", padx=6)
        ttk.Button(top, text="Listar", command=self.listar).pack(side="left", padx=6)

        self.tree = ttk.Treeview(self, columns=("id","cliente","data","total"), show="headings")
        for c in ("id","cliente","data","total"):
            self.tree.heading(c, text=c.title())
        self.tree.pack(fill="both", expand=True, pady=6)

        btns = ttk.Frame(self)
        btns.pack(fill="x")
        ttk.Button(btns, text="Exportar CSV", command=self.export_csv).pack(side="left", padx=6)
        ttk.Button(btns, text="Exportar PDF", command=self.export_pdf).pack(side="left", padx=6)

    def listar(self):
        cliente = self.cb_cliente.get()
        rows = list_pedidos()
        if cliente:
            rows = [r for r in rows if r[2]==cliente]
        # Show
        for r in self.tree.get_children(): self.tree.delete(r)
        for row in rows:
            pid, cid, nome, data, total = row
            self.tree.insert("", "end", values=(pid, nome, data, f"{total:.2f}"))

    def _gather_rows_for_export(self):
        rows = []
        for item in self.tree.get_children():
            vals = self.tree.item(item)["values"]
            pid = vals[0]
            itens = get_itens_pedido(pid)
            # itens: (id, produto, quantidade, preco_unit) -> map to (produto,qtd,preco)
            itens_clean = [(it[1], it[2], it[3]) for it in itens]
            rows.append((pid, vals[1], vals[2], vals[3], itens_clean))
        return rows

    def export_csv(self):
        rows = self._gather_rows_for_export()
        if not rows:
            messagebox.showinfo("Exportar CSV","Nenhum pedido para exportar.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not path: return
        try:
            with open(path, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["pedido_id","cliente","data","total","itens"])
                for pid, cliente, data, total, itens in rows:
                    itens_text = "; ".join([f"{p} x{q} R${preco:.2f}" for p,q,preco in itens])
                    writer.writerow([pid, cliente, data, total, itens_text])
            log_action("Export", "CSV", note=f"path={path}")
            messagebox.showinfo("Exportar CSV", f"Exportado: {path}")
        except Exception as e:
            logging.exception("Erro export CSV")
            messagebox.showerror("Erro", f"Falha ao exportar CSV: {e}")

    def export_pdf(self):
        rows = self._gather_rows_for_export()
        if not rows:
            messagebox.showinfo("Exportar PDF","Nenhum pedido para exportar.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files","*.pdf")])
        if not path: return
        try:
            c = canvas.Canvas(path, pagesize=A4)
            width, height = A4
            y = height - 50
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y, "Relatório de Pedidos")
            y -= 30
            c.setFont("Helvetica", 10)
            for pid, cliente, data, total, itens in rows:
                if y < 80:
                    c.showPage()
                    y = height - 50
                c.drawString(50, y, f"Pedido {pid} - Cliente: {cliente} - {data} - Total: R$ {total}")
                y -= 14
                for p,q,preco in itens:
                    c.drawString(70, y, f"- {p} | Qtd: {q} | R$ {preco:.2f}")
                    y -= 12
                y -= 8
            c.save()
            log_action("Export", "PDF", note=f"path={path}")
            messagebox.showinfo("Exportar PDF", f"PDF gerado: {path}")
        except Exception as e:
            logging.exception("Erro export PDF")
            messagebox.showerror("Erro", f"Falha ao exportar PDF: {e}")
