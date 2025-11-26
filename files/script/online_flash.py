import tkinter as tk
import random
import threading
import time
import math
import pygame
import os
import socket
import json
from pynput import keyboard

class FlashBangOverlay:
    def __init__(self, mode="local", remote_ip=None, port=5555):
        """
        mode: "local" (flashs aléatoires), "receiver" (reçoit des flashs), ou "sender" (envoie des flashs)
        remote_ip: IP de l'ordinateur du pote (nécessaire en mode sender)
        port: Port de communication (doit être le même sur les 2 PC)
        """
        self.mode = mode
        self.port = port
        self.remote_ip = remote_ip
        
        # Initialiser pygame mixer dès le début
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Charger le son
        sound_file = "flash_sound.mp3"
        if os.path.exists(sound_file):
            try:
                self.sound = pygame.mixer.Sound(sound_file)
                self.sound.set_volume(0.4)  # Volume à 40%
                print(f"✓ Son chargé: {sound_file}")
            except Exception as e:
                print(f"✗ Erreur chargement son: {e}")
                self.sound = None
        else:
            print(f"✗ Fichier non trouvé: {sound_file}")
            print(f"  Chemin recherché: {os.path.abspath(sound_file)}")
            self.sound = None
        
        self.root = tk.Tk()
        self.root.title("Overlay")
        
        # Configuration de la fenêtre
        self.root.attributes('-topmost', True)  # Toujours au premier plan
        self.root.attributes('-transparentcolor', 'black')  # Fond transparent
        self.root.attributes('-alpha', 0.0)  # Complètement transparent par défaut
        
        # Plein écran sans bordures
        self.root.overrideredirect(True)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Canvas pour le flash
        self.canvas = tk.Canvas(
            self.root,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Permettre les clics à travers la fenêtre (Windows)
        try:
            self.root.wm_attributes('-transparentcolor', 'black')
        except:
            pass
            
        # Variables d'état
        self.is_flashing = False
        self.flash_intensity = 0.0
        
        # Configuration réseau selon le mode
        if self.mode == "receiver":
            # Mode récepteur : écoute les commandes de flash
            self.setup_receiver()
        elif self.mode == "sender":
            # Mode envoyeur : écoute le clavier
            self.setup_sender()
        
        # Démarrer le thread des flashs aléatoires (seulement en mode local)
        self.running = True
        if self.mode == "local":
            self.flash_thread = threading.Thread(target=self.random_flash_loop, daemon=True)
            self.flash_thread.start()
        
        # Bouton pour quitter (petit, dans le coin)
        quit_btn = tk.Button(
            self.root,
            text="X",
            command=self.quit,
            bg='red',
            fg='white',
            font=('Arial', 8, 'bold')
        )
        quit_btn.place(x=screen_width-30, y=0, width=30, height=25)
        
        # Bind pour quitter avec Echap
        self.root.bind('<Escape>', lambda e: self.quit())
    
    def setup_receiver(self):
        """Configure le mode récepteur (PC qui reçoit les flashs)"""
        print(f"Mode RÉCEPTEUR activé sur le port {self.port}")
        self.server_thread = threading.Thread(target=self.receive_flash_commands, daemon=True)
        self.server_thread.start()
    
    def setup_sender(self):
        """Configure le mode envoyeur (PC qui envoie les flashs)"""
        if not self.remote_ip:
            print("ERREUR: IP du destinataire non spécifiée en mode sender!")
            return
        
        print(f"Mode ENVOYEUR activé - Cible: {self.remote_ip}:{self.port}")
        print("Appuyez sur F9 pour envoyer un flash!")
        
        # Écouter le clavier
        def on_press(key):
            try:
                if key == keyboard.Key.f9:
                    print("F9 pressé - Envoi du flash...")
                    self.send_flash_command()
            except:
                pass
        
        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()
    
    def send_flash_command(self):
        """Envoie une commande de flash au PC distant"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(1)
            message = json.dumps({"command": "flash"}).encode()
            sock.sendto(message, (self.remote_ip, self.port))
            sock.close()
            print(f"✓ Flash envoyé à {self.remote_ip}")
        except Exception as e:
            print(f"✗ Erreur envoi: {e}")
    
    def receive_flash_commands(self):
        """Écoute les commandes de flash réseau"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(("0.0.0.0", self.port))
            print(f"✓ Serveur en écoute sur le port {self.port}")
            
            while self.running:
                try:
                    data, addr = sock.recvfrom(1024)
                    message = json.loads(data.decode())
                    
                    if message.get("command") == "flash":
                        print(f"Flash reçu de {addr[0]}")
                        # Flash avec paramètres ALÉATOIRES
                        duration = random.uniform(0.3, 1.2)  # Entre 0.3s et 1.2s
                        intensity = random.uniform(0.6, 1.0)  # Entre 60% et 100%
                        threading.Thread(
                            target=self.flash,
                            args=(duration, intensity),
                            daemon=True
                        ).start()
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Erreur réception: {e}")
        except Exception as e:
            print(f"Erreur serveur: {e}")
        
    def play_beep(self):
        """Joue un fichier son"""
        if self.sound:
            try:
                self.sound.play()
                print("♪ Son joué")
            except Exception as e:
                print(f"Erreur lecture son: {e}")
        else:
            # Fallback: bip système
            try:
                import winsound
                winsound.Beep(1500, 200)
            except:
                print('\a')
    
    def flash(self, duration=0.6, max_intensity=0.95):
        """Déclenche un flash blanc avec durée et intensité variables"""
        if self.is_flashing:
            return
            
        self.is_flashing = True
        
        # Jouer le son AU DÉBUT
        self.play_beep()
        
        # Délai aléatoire avant le flash (entre 0 et 100ms)
        delay = random.uniform(0.0, 0.1)
        time.sleep(delay)
        
        # Animation du flash (montée rapide, descente progressive)
        steps = 30
        
        # Vitesse de montée aléatoire (entre rapide et très rapide)
        rise_speed = random.randint(3, 8)
        
        # Montée rapide
        for i in range(steps // rise_speed):
            if not self.running:
                break
            intensity = (i / (steps // rise_speed)) * max_intensity
            self.set_flash_intensity(intensity)
            time.sleep(duration / (steps * 2))
        
        # Pic - durée aléatoire du blanc max
        peak_duration = random.uniform(0.1, 0.4)
        self.set_flash_intensity(max_intensity)
        time.sleep(peak_duration)
        
        # Descente progressive - courbe aléatoire
        fade_curve = random.uniform(1.5, 3.0)  # Puissance de la courbe
        for i in range(steps):
            if not self.running:
                break
            intensity = max_intensity * (1 - (i / steps)) ** fade_curve
            self.set_flash_intensity(intensity)
            time.sleep(duration / steps)
        
        self.set_flash_intensity(0.0)
        self.is_flashing = False
    
    def set_flash_intensity(self, intensity):
        """Définit l'intensité du flash (0.0 à 1.0)"""
        self.flash_intensity = max(0.0, min(1.0, intensity))
        
        if self.flash_intensity < 0.01:
            self.root.attributes('-alpha', 0.0)
            self.canvas.configure(bg='black')
        else:
            self.root.attributes('-alpha', self.flash_intensity)
            self.canvas.configure(bg='white')
    
    def random_flash_loop(self):
        """Boucle qui déclenche des flashs aléatoires avec paramètres variables"""
        while self.running:
            # Attendre entre 5 et 20 secondes
            wait_time = random.uniform(5, 20)
            time.sleep(wait_time)
            
            if self.running and not self.is_flashing:
                # Déclencher un flash avec TOUS les paramètres ALÉATOIRES
                duration = random.uniform(0.3, 1.5)      # Durée entre 0.3s et 1.5s
                intensity = random.uniform(0.6, 1.0)     # Intensité entre 60% et 100%
                
                print(f"🎲 Flash random: durée={duration:.2f}s, intensité={intensity:.0%}")
                
                threading.Thread(
                    target=self.flash,
                    args=(duration, intensity),
                    daemon=True
                ).start()
    
    def quit(self):
        """Ferme l'application"""
        self.running = False
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Lance l'application"""
        self.root.mainloop()

if __name__ == "__main__":
    print("=== Flash Bang Overlay ===")
    print("\nChoisissez un mode:")
    print("1. Local (flashs aléatoires uniquement)")
    print("2. Receiver (recevoir des flashs d'un autre PC)")
    print("3. Sender (envoyer des flashs à un autre PC avec F9)")
    
    choice = input("\nVotre choix (1/2/3): ").strip()
    
    if choice == "1":
        print("\n=== MODE LOCAL ===")
        print("Des flashs aléatoires apparaîtront.")
        print("Appuyez sur ECHAP ou X pour quitter.")
        app = FlashBangOverlay(mode="local")
        
    elif choice == "2":
        port = input("Port d'écoute (défaut 5555): ").strip() or "5555"
        print(f"\n=== MODE RÉCEPTEUR ===")
        print(f"En attente de flashs sur le port {port}...")
        print("Appuyez sur ECHAP ou X pour quitter.")
        app = FlashBangOverlay(mode="receiver", port=int(port))
        
    elif choice == "3":
        remote_ip = input("IP du PC de ton pote: ").strip()
        port = input("Port (défaut 5555): ").strip() or "5555"
        print(f"\n=== MODE ENVOYEUR ===")
        print(f"Cible: {remote_ip}:{port}")
        print("Appuyez sur F9 pour flasher ton pote!")
        print("Appuyez sur ECHAP ou X pour quitter.")
        app = FlashBangOverlay(mode="sender", remote_ip=remote_ip, port=int(port))
        
    else:
        print("Choix invalide!")
        exit()
    
    print("=" * 40)
    app.run()