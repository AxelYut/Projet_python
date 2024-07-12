# auteur : Axel DUMON
# auteur : Mini jeu : Don't Fall

import pygame
import random

# Initialisation de Pygame
pygame.init()

# Définition des couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)

# Dimensions de l'écran
largeur = 500
hauteur = 800
ecran = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("Don't Fall")

# Redimensionnement des images
def resize_image(image, width, height):
    return pygame.transform.scale(image, (width, height))

# Chargement et redimensionnement des images
joueur_image = resize_image(pygame.image.load('player.png').convert_alpha(), 50, 50)
plateforme_image = resize_image(pygame.image.load('platform.png').convert_alpha(), 70, 30)
retry_image = resize_image(pygame.image.load('retry_button.png').convert_alpha(), 300, 300)

# Chargement et redimensionnement des images de fond
fond_images = [
    resize_image(pygame.image.load(f'background{i}.png').convert(), largeur, hauteur)
    for i in range(1, 6)  # Charger les images de background1.png à background5.png
]

# Chargement des fichiers son
rebond_sound = pygame.mixer.Sound('rebond.wav')
game_over_sound = pygame.mixer.Sound('game_over.wav')

# Fonction pour afficher du texte
def afficher_texte(texte, taille, x, y, couleur):
    font = pygame.font.Font(None, taille)
    text = font.render(texte, True, couleur)
    ecran.blit(text, (x, y))

# Classe pour le joueur
class Joueur(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = joueur_image
        self.rect = self.image.get_rect()
        self.reset_position()
        self.vitesse_y = 0
        self.vitesse_x = 0
        self.premier_saut = True  # Indicateur pour le premier saut

    def update(self):
        self.gravite()
        self.rect.y += self.vitesse_y
        self.rect.x += self.vitesse_x

        # Limite de l'écran pour le joueur
        if self.rect.left < 0:  # Si le joueur touche le bord gauche
            self.rect.right = largeur  # Le placer à l'extrême droite de l'écran
        elif self.rect.right > largeur:  # Si le joueur touche le bord droit
            self.rect.left = 0  # Le placer à l'extrême gauche de l'écran

        # Vérifier si le joueur rebondit sur une plateforme
        if self.vitesse_y >= 0:  # Vérifier seulement si le joueur est en train de descendre
            collisions = pygame.sprite.spritecollide(self, plateformes, False)
            if collisions:
                plus_haut = min(collisions, key=lambda p: p.rect.bottom)
                if self.rect.bottom <= plus_haut.rect.centery:  # Vérifier si le joueur est au-dessus de la plateforme
                    self.rect.bottom = plus_haut.rect.top
                    self.sauter()  # Déclencher le saut avec la hauteur appropriée
                    rebond_sound.play()  # Jouer le son de rebond

        # Limite de la chute
        if self.rect.y >= hauteur - self.rect.height and self.vitesse_y >= 0:
            self.vitesse_y = 0
            self.rect.y = hauteur - self.rect.height

    def gravite(self):
        if self.vitesse_y == 0:
            self.vitesse_y = 1
        else:
            self.vitesse_y += 0.35

    def deplacer_gauche(self):
        self.vitesse_x = -5

    def deplacer_droite(self):
        self.vitesse_x = 5

    def arreter_deplacement(self):
        self.vitesse_x = 0

    def reset_position(self):
        self.rect.centerx = largeur // 2
        self.rect.bottom = hauteur - 50  # Positionne le joueur au-dessus de la première plateforme
        self.vitesse_y = 0
        self.vitesse_x = 0
        self.premier_saut = True  # Réinitialiser le premier saut

    def sauter(self):
        if self.premier_saut:
            self.vitesse_y = -15  # Vitesse pour le premier saut (2 fois plus haut)
            self.premier_saut = False
        else:
            self.vitesse_y = -11  # Vitesse normale pour les sauts suivants

# Classe pour les plateformes
class Plateforme(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = plateforme_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.y += game_speed
        if self.rect.top > hauteur:
            self.rect.y = random.randrange(-30, -10)
            self.rect.x = random.randrange(0, largeur - self.rect.width)

# Classe pour les plateformes mobiles
class PlateformeMobile(Plateforme):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.direction = random.choice([-1, 1])
        self.vitesse_x = 2

    def update(self):
        super().update()
        self.rect.x += self.direction * self.vitesse_x
        if self.rect.left < 0 or self.rect.right > largeur:
            self.direction *= -1

def generer_plateforme_valide():
    while True:
        x = random.randrange(0, largeur - 65)
        y = random.randrange(50, hauteur - 30)
        plateforme_valide = True

        for plateforme in plateformes:
            if abs(plateforme.rect.y - y) < 50 and abs(plateforme.rect.x - x) < 65:
                plateforme_valide = False
                break

        if plateforme_valide:
            return x, y

# Groupe de sprites
tous_sprites = pygame.sprite.Group()
plateformes = pygame.sprite.Group()

# Création du joueur
joueur = Joueur()
tous_sprites.add(joueur)

# Création des plateformes initiales
plateforme_depart = Plateforme(x=largeur // 2 - 35, y=hauteur - 30)
tous_sprites.add(plateforme_depart)
plateformes.add(plateforme_depart)

for i in range(8):
    x, y = generer_plateforme_valide()
    if random.random() < 0.2:
        plateforme = PlateformeMobile(x, y)
    else:
        plateforme = Plateforme(x, y)
    tous_sprites.add(plateforme)
    plateformes.add(plateforme)

# Charger le meilleur record depuis records.txt
def charger_meilleur_record():
    try:
        with open('records.txt', 'r') as file:
            record = file.read()
            return int(record.strip())
    except FileNotFoundError:
        return 0

# Enregistrer le meilleur record dans records.txt
def enregistrer_meilleur_record(record):
    with open('records.txt', 'w') as file:
        file.write(str(record))

# Fonction pour démarrer une nouvelle partie
def nouvelle_partie():
    joueur.reset_position()
    for plateforme in plateformes:
        plateforme.kill()
    plateforme_depart = Plateforme(x=largeur // 2 - 35, y=hauteur - 30)
    tous_sprites.add(plateforme_depart)
    plateformes.add(plateforme_depart)
    for i in range(8):
        x, y = generer_plateforme_valide()
        if random.random() < 0.2:
            nouvelle_plateforme = PlateformeMobile(x, y)
        else:
            nouvelle_plateforme = Plateforme(x, y)
        tous_sprites.add(nouvelle_plateforme)
        plateformes.add(nouvelle_plateforme)
    return pygame.time.get_ticks()  # Démarrer le timer

# Charger le meilleur record au démarrage du jeu
meilleur_record = charger_meilleur_record()

# Boucle principale du jeu
running = True
clock = pygame.time.Clock()
game_over = False
start_time = pygame.time.get_ticks()  # Chronomètre
game_speed = 2
max_game_speed = 10  # Limite supérieure de la vitesse
speed_increment_interval = 10000  # Intervalle d'incrémentation de la vitesse en millisecondes
last_speed_increment_time = start_time

retry_button = pygame.Rect(largeur // 2 - retry_image.get_width() // 2, hauteur // 2 + 100, retry_image.get_width(), retry_image.get_height())

background_index = 0  # Index de l'image de fond actuelle

while running:
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                joueur.deplacer_gauche()
            elif event.key == pygame.K_RIGHT:
                joueur.deplacer_droite()
            elif event.key == pygame.K_SPACE and game_over:
                if retry_button.collidepoint(pygame.mouse.get_pos()):
                    game_over = False
                    start_time = nouvelle_partie()
                    game_speed = 2
                    background_index = 0
                    last_speed_increment_time = start_time
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                joueur.arreter_deplacement()
        elif event.type == pygame.MOUSEBUTTONDOWN and game_over:
            if retry_button.collidepoint(event.pos):
                game_over = False
                start_time = nouvelle_partie()
                game_speed = 2
                background_index = 0
                last_speed_increment_time = start_time

    if not game_over:
        tous_sprites.update()

        # Vérifier si le joueur touche une plateforme
        if joueur.vitesse_y >= 0:
            collisions = pygame.sprite.spritecollide(joueur, plateformes, False)
            if collisions:
                plus_haut = min(collisions, key=lambda p: p.rect.bottom)
                if joueur.rect.bottom <= plus_haut.rect.centery:
                    joueur.rect.bottom = plus_haut.rect.top
                    joueur.sauter()
                    rebond_sound.play()

        # Si le joueur touche le sol, c'est la fin du jeu
        if joueur.rect.bottom >= hauteur:
            game_over = True
            game_over_sound.play()

        while len(plateformes) < 10:
            x, y = generer_plateforme_valide()
            if random.random() < 0.2:
                nouvelle_plateforme = PlateformeMobile(x, y)
            else:
                nouvelle_plateforme = Plateforme(x, y)
            tous_sprites.add(nouvelle_plateforme)
            plateformes.add(nouvelle_plateforme)

        for plateforme in plateformes:
            if plateforme.rect.top > hauteur:
                plateforme.kill()

        # Incrémenter la vitesse du jeu à intervalles réguliers
        current_time = pygame.time.get_ticks()
        if current_time - last_speed_increment_time >= speed_increment_interval:
            game_speed += 0.2
            if game_speed > max_game_speed:
                game_speed = max_game_speed
            last_speed_increment_time = current_time

        # Changer l'image de fond à 1 minute, 2 minutes, 3 minutes et 4 minutes
        elapsed_time_ms = pygame.time.get_ticks() - start_time
        elapsed_time_minutes = elapsed_time_ms // 60000
        if elapsed_time_minutes == 1:
            background_index = 1
        elif elapsed_time_minutes == 2:
            background_index = 2
        elif elapsed_time_minutes == 3:
            background_index = 3
        elif elapsed_time_minutes == 4:
            background_index = 4
       

        # Comparer avec le meilleur record et mettre à jour si nécessaire
        if elapsed_time_ms > meilleur_record:
            meilleur_record = elapsed_time_ms
            enregistrer_meilleur_record(meilleur_record)

    # Dessin sur l'écran
    ecran.blit(fond_images[background_index], (0, 0))
    tous_sprites.draw(ecran)

    if not game_over:
        # Affichage du timer
        elapsed_time_ms = pygame.time.get_ticks() - start_time
        minutes = elapsed_time_ms // 60000
        seconds = (elapsed_time_ms // 1000) % 60
        milliseconds = elapsed_time_ms % 1000
        afficher_texte(f"Temps: {minutes:02}:{seconds:02}:{milliseconds:03}", 24, 10, 10, BLANC)

        # Affichage du meilleur record
        best_minutes = meilleur_record // 60000
        best_seconds = (meilleur_record // 1000) % 60
        best_milliseconds = meilleur_record % 1000
        afficher_texte(f"Meilleur record: {best_minutes:02}:{best_seconds:02}:{best_milliseconds:03}", 18, 10, 40, BLANC)
    else:
        # Affichage du message de Game Over
        ecran.blit(retry_image, retry_button.topleft)

    # Rafraîchissement de l'écran
    pygame.display.flip()
    clock.tick(60)

# Fin du jeu
pygame.quit()
