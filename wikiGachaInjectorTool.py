import base64
import gzip
import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes


def decrypt_wgbak(file_path, password):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
        return None, None, f"Couldn't read the file: {e}"

    if len(lines) < 2:
        return None, None, "The file doesn't have the expected format."

    try:
        header = json.loads(lines[0])
        chunk = json.loads(lines[1])

        kdf_params = header["kdf"]
        salt_bytes = base64.b64decode(kdf_params["salt"])
        iterations = kdf_params["iterations"]

        key = PBKDF2(
            password.encode("utf-8"),
            salt_bytes,
            dkLen=32,
            count=iterations,
            hmac_hash_module=SHA256,
        )

        iv_bytes = base64.b64decode(chunk["iv"])
        ciphertext_bytes = base64.b64decode(chunk["ciphertext"])

        tag_bytes = ciphertext_bytes[-16:]
        actual_ciphertext = ciphertext_bytes[:-16]

        cipher = AES.new(key, AES.MODE_GCM, nonce=iv_bytes)
        compressed_data = cipher.decrypt_and_verify(actual_ciphertext, tag_bytes)

        plain_data = gzip.decompress(compressed_data)
        return plain_data.decode("utf-8"), header, None
    except Exception as e:
        return (
            None,
            None,
            "Incorrect password, damaged file or invalid format.",
        )


def encrypt_safe_backup(
    file_path_output, original_header, modified_plain_text, password
):
    try:
        kdf_params = original_header["kdf"]
        salt_bytes = base64.b64decode(kdf_params["salt"])
        iterations = kdf_params["iterations"]

        key = PBKDF2(
            password.encode("utf-8"),
            salt_bytes,
            dkLen=32,
            count=iterations,
            hmac_hash_module=SHA256,
        )

        plain_bytes = modified_plain_text.encode("utf-8")
        compressed_bytes = gzip.compress(plain_bytes)

        new_iv_bytes = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_GCM, nonce=new_iv_bytes)
        ciphertext_bytes, tag_bytes = cipher.encrypt_and_digest(compressed_bytes)

        payload_bytes = ciphertext_bytes + tag_bytes
        ciphertext_b64 = base64.b64encode(payload_bytes).decode("utf-8")
        iv_b64 = base64.b64encode(new_iv_bytes).decode("utf-8")

        try:
            card_list = json.loads(modified_plain_text)
            new_count = len(card_list)
        except:
            new_count = 250

        new_chunk = {
            "type": "chunk",
            "store": "cards_es",
            "part": 0,
            "count": new_count,
            "iv": iv_b64,
            "ciphertext": ciphertext_b64,
        }

        with open(file_path_output, "w", encoding="utf-8") as f:
            f.write(json.dumps(original_header) + "\n")
            f.write(json.dumps(new_chunk) + "\n")
        return True, None
    except Exception as e:
        return False, str(e)


# =====================================================================
# --- GUI ---
# =====================================================================
class WikiGachaEditorApp:

    def __init__(self, root):
        self.root = root
        self.root.title("WikiGacha Backup Injector Tool")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        self.input_file_path = ""
        self.cards_to_inject = []

        # --- 1: File Selection and Password ---
        frame_file = ttk.LabelFrame(root, text=" Backup File ", padding=10)
        frame_file.pack(fill="x", padx=15, pady=10)

        self.btn_browse = tuple
        tk.Button(
            frame_file, text="Browse .wgbak File", command=self.browse_file
        ).grid(row=0, column=0, padx=5, pady=5)
        self.lbl_file = tk.Label(
            frame_file, text="No file selected", fg="gray", anchor="w"
        )
        self.lbl_file.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        tk.Label(frame_file, text="Password:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        self.entry_password = tk.Entry(frame_file, show="*")
        self.entry_password.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        frame_file.columnconfigure(1, weight=1)

        # --- 2: Add New Card ---
        frame_cards = ttk.LabelFrame(root, text=" Add New Card ", padding=10)
        frame_cards.pack(fill="x", padx=15, pady=5)

        tk.Label(frame_cards, text="Wikipedia ID:").grid(row=0, column=0, padx=5)
        self.entry_id = tk.Entry(frame_cards, width=15)
        self.entry_id.grid(row=0, column=1, padx=5)

        tk.Label(frame_cards, text="Title/Name:").grid(
            row=0, column=2, padx=5
        )
        self.entry_title = tk.Entry(frame_cards, width=25)
        self.entry_title.grid(row=0, column=3, padx=5)

        tk.Button(
            frame_cards, text="Add to list", command=self.add_card_to_list
        ).grid(row=0, column=4, padx=5)

        # --- 3: Table of Items to Inject ---
        frame_table = tk.Frame(root)
        frame_table.pack(fill="both", expand=True, padx=15, pady=10)

        columns = ("id", "title")
        self.tree = ttk.Treeview(
            frame_table, columns=columns, show="headings", height=8
        )
        self.tree.heading("id", text="Wikipedia ID")
        self.tree.heading("title", text="Card Title")
        self.tree.column("id", width=150, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            frame_table, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Delete list button
        tk.Button(
            root, text="Delete Selected", command=self.delete_selected
        ).pack(anchor="e", padx=15)

        # --- 4: Process Button ---
        tk.Button(
            root,
            text="PROCESS AND INJECT BACKUP",
            bg="#28a745",
            fg="white",
            font=("Arial", 11, "bold"),
            command=self.process_backup,
        ).pack(fill="x", padx=15, pady=15)

    def browse_file(self):
        file_selected = filedialog.askopenfilename(
            filetypes=[("WikiGacha Backup", "*.wgbak")]
        )
        if file_selected:
            self.input_file_path = file_selected
            self.lbl_file.config(
                text=os.path.basename(file_selected), fg="black"
            )

    def add_card_to_list(self):
        card_id = self.entry_id.get().strip()
        card_title = self.entry_title.get().strip()

        if not card_id.isdigit():
            messagebox.showerror(
                "Error", "The Wikipedia ID must be a valid integer."
            )
            return
        if not card_title:
            messagebox.showerror(
                "Error", "The card title cannot be empty."
            )
            return

        # Save locally in the list and update the Treeview
        self.cards_to_inject.append({"id": int(card_id), "title": card_title})
        self.tree.insert("", "end", values=(card_id, card_title))

        # Clear the entry fields
        self.entry_id.delete(0, tk.END)
        self.entry_title.delete(0, tk.END)

    def delete_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        for item in selected_item:
            values = self.tree.item(item, "values")
            self.cards_to_inject = [
                c for c in self.cards_to_inject if c["id"] != int(values[0])
            ]
            self.tree.delete(item)

    def process_backup(self):
        password = self.entry_password.get()

        if not self.input_file_path:
            messagebox.showerror(
                "Error", "Please select a valid .wgbak file."
            )
            return
        if not password:
            messagebox.showerror(
                "Error", "You must enter the backup password."
            )
            return
        if not self.cards_to_inject:
            messagebox.showerror(
                "Error", "The list of cards to inject is empty."
            )
            return

        # 1. Decrypt the original backup file
        result, original_header, error_msg = decrypt_wgbak(
            self.input_file_path, password
        )
        if error_msg:
            messagebox.showerror("Decryption Error", error_msg)
            return

        cards_json = json.loads(result)

        # 2. Inject new cards (Avoiding duplicates)
        existing_ids = {card["id"] for card in cards_json if "id" in card}
        added_count = 0

        for new_card in self.cards_to_inject:
            if new_card["id"] not in existing_ids:
                cards_json.append(
                    {"id": new_card["id"], "title": new_card["title"]}
                )
                existing_ids.add(new_card["id"])
                added_count += 1

        # 3. Save the modified file
        file_path_output = filedialog.asksaveasfilename(
            defaultextension=".wgbak",
            filetypes=[("WikiGacha Backup", "*.wgbak")],
            initialfile="wikigacha_backup_modified.wgbak",
        )

        if not file_path_output:
            return  # The user canceled the save

        modified_text = json.dumps(cards_json, ensure_ascii=False)
        success, enc_error = encrypt_safe_backup(
            file_path_output, original_header, modified_text, password
        )

        if success:
            messagebox.showinfo(
                "Success",
                f"Process completed.\n{added_count} new cards injected successfully.",
            )
            self.root.destroy()  # Close the app upon successful completion

        else:
            messagebox.showerror(
                "Encryption Error", f"Couldn't save the file: {enc_error}"
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = WikiGachaEditorApp(root)
    root.mainloop()