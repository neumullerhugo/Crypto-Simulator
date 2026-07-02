import customtkinter as ctk
import requests
import winsound  # Module Windows pour les bruits d'alerte

# Configuration du thème
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class CryptoTrader(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Crypto Trader Simulator")
        self.geometry("450x720")
        self.resizable(False, False)

        # --- PORTFOLIO & ALERT DATA ---
        self.solde_eur = 10000.0  
        self.solde_btc = 0.0      
        self.current_btc_price = 0.0
        self.target_price = None 

        # --- INTERFACE ---
        self.title_label = ctk.CTkLabel(self, text="₿ CRYPTO SIMULATOR", font=("Arial", 24, "bold"))
        self.title_label.pack(pady=15)

        # Box Portefeuille
        self.wallet_frame = ctk.CTkFrame(self, width=400, height=110)
        self.wallet_frame.pack(pady=5)
        self.wallet_frame.pack_propagate(False)

        self.eur_label = ctk.CTkLabel(self.wallet_frame, text=f"Solde EUR : {self.solde_eur:,.2f} €", font=("Arial", 16, "bold"))
        self.eur_label.pack(pady=(15, 5))
        
        self.btc_label = ctk.CTkLabel(self.wallet_frame, text=f"Mon Bitcoin : {self.solde_btc:.6f} BTC", font=("Arial", 14), text_color="gray")
        self.btc_label.pack(pady=5)

        # Affichage du cours en direct
        self.price_label = ctk.CTkLabel(self, text="Cours du BTC : Chargement...", font=("Arial", 20, "bold"), text_color="#2ecc71")
        self.price_label.pack(pady=15)

        # --- ZONE ALERTE PRIX ---
        self.alert_frame = ctk.CTkFrame(self, width=400, height=100, fg_color="#2c3e50")
        self.alert_frame.pack(pady=10)
        self.alert_frame.pack_propagate(False)

        self.alert_title = ctk.CTkLabel(self.alert_frame, text="🔔 Alerte si le prix descend sous :", font=("Arial", 13, "bold"))
        self.alert_title.pack(pady=5)

        self.alert_sub_frame = ctk.CTkFrame(self.alert_frame, fg_color="transparent")
        self.alert_sub_frame.pack()

        self.alert_input = ctk.CTkEntry(self.alert_sub_frame, placeholder_text="Ex: 53000", width=120)
        self.alert_input.pack(side="left", padx=5)

        self.btn_set_alert = ctk.CTkButton(self.alert_sub_frame, text="Placer l'alerte", width=100, command=self.set_price_alert)
        self.btn_set_alert.pack(side="left", padx=5)

        self.alert_status_label = ctk.CTkLabel(self.alert_frame, text="Aucune alerte active", font=("Arial", 11, "italic"), text_color="gray")
        self.alert_status_label.pack(pady=5)

        # Zone d'action (Achat / Vente)
        self.action_label = ctk.CTkLabel(self, text="Montant de la transaction (en EUR) :", font=("Arial", 13))
        self.action_label.pack(pady=5)

        self.amount_input = ctk.CTkEntry(self, placeholder_text="Ex: 500", width=200, font=("Arial", 14))
        self.amount_input.pack(pady=5)

        # Boutons d'action
        self.btn_buy = ctk.CTkButton(self, text="ACHETER BTC", fg_color="#2ecc71", hover_color="#27ae60", font=("Arial", 14, "bold"), command=self.buy_btc)
        self.btn_buy.pack(pady=5, ipady=2)

        self.btn_sell = ctk.CTkButton(self, text="VENDRE BTC", fg_color="#e74c3c", hover_color="#c0392b", font=("Arial", 14, "bold"), command=self.sell_btc)
        self.btn_sell.pack(pady=5, ipady=2)

        self.btn_sell_all = ctk.CTkButton(self, text="⚠️ TOUT VENDRE (PANIC SELL)", fg_color="#962d22", hover_color="#78241b", font=("Arial", 14, "bold"), command=self.sell_all_btc)
        self.btn_sell_all.pack(pady=10, ipady=4)

        # Message d'état
        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 12, "italic"))
        self.status_label.pack(pady=5)

        self.update_price()

    def update_price(self):
        try:
            url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCEUR"
            response = requests.get(url).json()
            self.current_btc_price = float(response['price'])
            self.price_label.configure(text=f"Cours du BTC : {self.current_btc_price:,.2f} €")

            # VERIFICATION DE L'ALERTE + SON
            if self.target_price is not None:
                if self.current_btc_price <= self.target_price:
                    self.alert_frame.configure(fg_color="#d35400") 
                    self.alert_status_label.configure(text=f"📉 CIBLE ({self.target_price:,.2f} €) ATTEINTE ! ACHÈTE !", text_color="white")
                    
                    # 🔊 ON JOUE LE SON D'ALERTE (Bip Windows : Fréquence 1000Hz, Durée 300ms)
                    # Le flag SND_ASYNC évite que l'interface freeze pendant le bruit
                    winsound.Beep(1000, 300)
                else:
                    self.alert_frame.configure(fg_color="#2c3e50")
                    self.alert_status_label.configure(text=f"⏳ En attente... (Cible : {self.target_price:,.2f} €)", text_color="#f1c40f")

        except Exception:
            self.price_label.configure(text="Cours du BTC : Erreur Connexion")
        
        self.after(2000, self.update_price)

    def set_price_alert(self):
        try:
            valeur = float(self.alert_input.get())
            if valeur <= 0: raise ValueError
            self.target_price = valeur
            self.alert_status_label.configure(text=f"⏳ En attente... (Cible : {self.target_price:,.2f} €)", text_color="#f1c40f")
            self.alert_input.delete(0, 'end')
        except ValueError:
            self.alert_status_label.configure(text="❌ Entre un prix cible valide !", text_color="#e74c3c")

    def buy_btc(self):
        try:
            montant_eur = float(self.amount_input.get())
            if montant_eur <= 0: raise ValueError
            if montant_eur > self.solde_eur:
                self.status_label.configure(text="❌ Fonds insuffisants en Euros !", text_color="#e74c3c")
                return

            btc_achete = montant_eur / self.current_btc_price
            self.solde_eur -= montant_eur
            self.solde_btc += btc_achete

            self.update_ui_wallet()
            self.status_label.configure(text=f"✅ Achat réussi de {btc_achete:.6f} BTC !", text_color="#2ecc71")
            self.amount_input.delete(0, 'end')
            
            # Reset de l'alerte après l'achat pour couper le son
            self.target_price = None
            self.alert_frame.configure(fg_color="#2c3e50")
            self.alert_status_label.configure(text="Aucune alerte active", text_color="gray")
        except ValueError:
            self.status_label.configure(text="❌ Entre un montant valide !", text_color="#e74c3c")

    def sell_btc(self):
        try:
            montant_eur = float(self.amount_input.get())
            if montant_eur <= 0: raise ValueError

            btc_a_vendre = montant_eur / self.current_btc_price
            if btc_a_vendre > self.solde_btc:
                self.status_label.configure(text="❌ Vous n'avez pas assez de Bitcoin !", text_color="#e74c3c")
                return

            self.solde_btc -= btc_a_vendre
            self.solde_eur += montant_eur

            self.update_ui_wallet()
            self.status_label.configure(text=f"✅ Vente réussie de {btc_a_vendre:.6f} BTC !", text_color="#2ecc71")
            self.amount_input.delete(0, 'end')
        except ValueError:
            self.status_label.configure(text="❌ Entre un montant valide !", text_color="#e74c3c")

    def sell_all_btc(self):
        if self.solde_btc <= 0:
            self.status_label.configure(text="❌ Tu n'as aucun Bitcoin à vendre !", text_color="#e74c3c")
            return
        
        gains_eur = self.solde_btc * self.current_btc_price
        self.solde_eur += gains_eur
        btc_vendu = self.solde_btc
        self.solde_btc = 0.0 
        
        self.update_ui_wallet()
        self.status_label.configure(text=f"💥 PANIC SELL ! {btc_vendu:.6f} BTC vendus pour {gains_eur:,.2f} € !", text_color="#e67e22")
        self.amount_input.delete(0, 'end')

    def update_ui_wallet(self):
        self.eur_label.configure(text=f"Solde EUR : {self.solde_eur:,.2f} €")
        self.btc_label.configure(text=f"Mon Bitcoin : {self.solde_btc:.6f} BTC")

if __name__ == "__main__":
    app = CryptoTrader()
    app.mainloop()