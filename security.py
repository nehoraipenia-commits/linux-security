import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import psutil
import os

class LinuxSentinel:
    def __init__(self, root):
        self.root = root
        self.root.title("LINUX SENTINEL")
        self.root.geometry("900x600")
        self.root.configure(bg="#1a1a1a")

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TNotebook", background="#1a1a1a", borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#333333", foreground="white", padding=[10, 5])
        self.style.map("TNotebook.Tab", background=[("selected", "#2ecc71")], foreground=[("selected", "black")])

        self.header = tk.Frame(root, bg="#1a1a1a", pady=10)
        self.header.pack(fill="x")
        
        self.title_label = tk.Label(self.header, text="🛡️ LINUX SENTINEL", font=("Arial", 18, "bold"), fg="#2ecc71", bg="#1a1a1a")
        self.title_label.pack(side="left", padx=20)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_dashboard = tk.Frame(self.notebook, bg="#262626")
        self.tab_network = tk.Frame(self.notebook, bg="#262626")
        self.tab_firewall = tk.Frame(self.notebook, bg="#262626")
        self.tab_audit = tk.Frame(self.notebook, bg="#262626")

        self.notebook.add(self.tab_dashboard, text=" Dashboard ")
        self.notebook.add(self.tab_network, text=" Ports & Network ")
        self.notebook.add(self.tab_firewall, text=" Firewall (UFW) ")
        self.notebook.add(self.tab_audit, text=" System Audit ")

        self.setup_dashboard()
        self.setup_network()
        self.setup_firewall()
        self.setup_audit()

    def setup_dashboard(self):
        frame = tk.Frame(self.tab_dashboard, bg="#262626", padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="System Information", font=("Arial", 14, "bold"), fg="white", bg="#262626").pack(anchor="w")
        
        self.dash_text = tk.Text(frame, height=15, bg="#1a1a1a", fg="#2ecc71", font=("Courier", 10), borderwidth=0)
        self.dash_text.pack(fill="x", pady=10)
        
        tk.Button(frame, text="Refresh Status", command=self.refresh_dashboard, bg="#333333", fg="white", relief="flat", padx=15).pack(anchor="e")
        self.refresh_dashboard()

    def refresh_dashboard(self):
        self.dash_text.delete("1.0", tk.END)
        users = subprocess.getoutput("who")
        uptime = subprocess.getoutput("uptime -p")
        kernel = subprocess.getoutput("uname -r")
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        
        info = f"Kernel Version: {kernel}\n"
        info += f"System Uptime: {uptime}\n"
        info += f"CPU Usage: {cpu}%\n"
        info += f"RAM Usage: {ram}%\n"
        info += "-"*40 + "\n"
        info += f"Connected Users:\n{users}"
        
        self.dash_text.insert(tk.END, info)

    def setup_network(self):
        frame = tk.Frame(self.tab_network, bg="#262626", padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        cols = ("Proto", "Local Address", "Status", "PID", "Program")
        self.net_tree = ttk.Treeview(frame, columns=cols, show="headings", height=15)
        
        for col in cols:
            self.net_tree.heading(col, text=col)
            self.net_tree.column(col, width=120)
        
        self.net_tree.pack(fill="both", expand=True)

        btn_frame = tk.Frame(frame, bg="#262626")
        btn_frame.pack(fill="x", pady=10)
        
        tk.Button(btn_frame, text="Scan Listening Ports", command=self.refresh_network, bg="#2ecc71", fg="black").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Kill Selected Process", command=self.kill_process, bg="#e74c3c", fg="white").pack(side="left", padx=5)

    def refresh_network(self):
        for item in self.net_tree.get_children():
            self.net_tree.delete(item)
            
        connections = psutil.net_connections(kind='inet')
        for conn in connections:
            if conn.status == 'LISTEN':
                try:
                    process = psutil.Process(conn.pid)
                    name = process.name()
                except:
                    name = "Unknown"
                
                self.net_tree.insert("", tk.END, values=(
                    "TCP" if conn.type == 1 else "UDP",
                    f"{conn.laddr.ip}:{conn.laddr.port}",
                    conn.status,
                    conn.pid,
                    name
                ))

    def kill_process(self):
        selected = self.net_tree.selection()
        if not selected:
            return
        
        pid = self.net_tree.item(selected[0])['values'][3]
        try:
            os.system(f"sudo kill -9 {pid}")
            messagebox.showinfo("Success", f"Process {pid} terminated.")
            self.refresh_network()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def setup_firewall(self):
        frame = tk.Frame(self.tab_firewall, bg="#262626", padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        self.fw_status_label = tk.Label(frame, text="UFW Status: Checking...", font=("Arial", 12, "bold"), fg="white", bg="#262626")
        self.fw_status_label.pack(pady=10)

        tk.Button(frame, text="Enable UFW", command=lambda: self.run_ufw("enable"), bg="#2ecc71", width=30, pady=5).pack(pady=5)
        tk.Button(frame, text="Disable UFW", command=lambda: self.run_ufw("disable"), bg="#e74c3c", width=30, pady=5).pack(pady=5)
        
        self.fw_log = tk.Text(frame, height=10, bg="#1a1a1a", fg="white", font=("Courier", 9))
        self.fw_log.pack(fill="x", pady=10)
        
        self.check_ufw()

    def check_ufw(self):
        status = subprocess.getoutput("sudo ufw status")
        self.fw_status_label.config(text=f"UFW Status: {'ACTIVE' if 'active' in status.lower() and 'inactive' not in status.lower() else 'INACTIVE'}")
        self.fw_log.delete("1.0", tk.END)
        self.fw_log.insert(tk.END, status)

    def run_ufw(self, cmd):
        try:
            subprocess.run(["sudo", "ufw", "--force", cmd], check=True)
            self.check_ufw()
            messagebox.showinfo("Firewall", f"UFW successfully {cmd}d.")
        except Exception as e:
            messagebox.showerror("Firewall Error", f"Failed to {cmd} UFW.\nEnsure you are root.\n{str(e)}")

    def setup_audit(self):
        frame = tk.Frame(self.tab_audit, bg="#262626", padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Button(frame, text="Check System Updates", command=self.check_updates, bg="#3498db", fg="white", width=25).pack(pady=5)
        tk.Button(frame, text="Clean Temp Files", command=self.clean_system, bg="#9b59b6", fg="white", width=25).pack(pady=5)
        
        self.audit_log = tk.Text(frame, height=15, bg="#1a1a1a", fg="#f1c40f", font=("Courier", 9))
        self.audit_log.pack(fill="both", expand=True, pady=10)

    def check_updates(self):
        self.audit_log.insert(tk.END, "> Checking for security updates...\n")
        try:
            out = subprocess.getoutput("apt list --upgradable")
            self.audit_log.insert(tk.END, out + "\n" + "-"*30 + "\n")
        except:
            self.audit_log.insert(tk.END, "Error: Package manager not found or permission denied.\n")

    def clean_system(self):
        try:
            subprocess.run(["sudo", "apt", "autoclean"], check=True)
            self.audit_log.insert(tk.END, "> System cleaning completed.\n")
        except:
            self.audit_log.insert(tk.END, "> Cleaning failed.\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = LinuxSentinel(root)
    root.mainloop()
