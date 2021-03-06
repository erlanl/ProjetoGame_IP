import pygame
import pygame as pg
from pygame.locals import *
import mapa
import random
import sys
from pygame import mixer
from interface import pontuacao
from interface import texto
from interface import Vida
import pygame.font
import os
from coletaveis import *
from tiro import *

#sons e volume dos sons do jogo
som_tiro= mixer.Sound("sons/atirar.wav")
som_tiro.set_volume(0.3)
som_dano= mixer.Sound("sons/dano.wav")
som_dano.set_volume(0.4)
som_morte= mixer.Sound("sons/morte.wav")
som_morte.set_volume(0.2)
som_batida= mixer.Sound("sons/batida.wav")
som_batida.set_volume(0.02)
som_passos= mixer.Sound("sons/passos.wav")
som_passos.set_volume(0.15)

mixer.music.load("sons/musica.mp3")
mixer.music.set_volume(0.2)
mixer.music.play(-1)

class Player:
    COOLDOWN = 30  # Metade de um segundo pois o jogo é 60 fps

    def __init__(self, win, x, y, tecla_cima, tecla_baixo, tecla_esquerda, tecla_direita, tecla_tiro, obj, px, py,fonte, imagem):

        self.win = win
        self.x = x
        self.y = y

        # Verificar qual é o player através da imagem
        if imagem == 'imagens/cowboy_joaquim2.png':
            self.nome = 'player1'
        else: self.nome = 'player2'

        self.imagem = pygame.image.load(imagem)
        #essa é a quantidade de balas de cada jogador
        #ela recebe a janela onde ela aparece,o x e y do canto superior esquerdo, tem cor branca,e usa a fonte
        #mandaram na construcao do player, nesse caso é a fonte relogio
        self.pontos = pontuacao(win, px, py, (255, 255, 255), fonte)


        self.tecla_cima = tecla_cima
        self.tecla_baixo = tecla_baixo
        self.tecla_esquerda = tecla_esquerda
        self.tecla_direita = tecla_direita
        self.tecla_tiro = tecla_tiro
        #velocidade da bala
        self.vel = 10
        self.quantidade_balas = 0
        # O player inicia como um quadrado em vez de pegarmos uma caracteristica por vez e montarmos o quadrado depois
        self.quadrado = pg.Rect(x, y, 30, 30)
        self.rect = self.quadrado
        self.velocidade = 6
        self.cor = 'WHITE'
        #a direcao pra onde o jogador está olhando
        #é usada na funcao do tiro
        #comeca como baixo
        self.direcao = "baixo"


        self.tiros = []
        self.cool_down = 0
        self.vida = 60
        
        # Criar um objeto de vida para cada player
        if self.nome == 'player1':
            self.vida_p = Vida(win, px - 100, py + 15 ,'imagens/coracao_vida.png', self.nome, self.vida)
        elif self.nome == 'player2':
            self.vida_p = Vida(win, px * 3.5 , py - 20,'imagens/coracao_vida.png', self.nome, self.vida)

        self.inimigo = obj
        self.balas = 0

    # Funcao que vai verificar se o player colidiu com uma plataforma
    def colisao(self, lista_plataforma):

        # Loop para verificar se o player esta colidindo com uma plataforma
        for i in range(len(lista_plataforma)):

            # Caso o retangulo do player esteja colidindo com o retangulo da plataforma
            if (self.quadrado.colliderect(lista_plataforma[i])):
                # Retornamos True e a posicao da plataforma na lista_plataforma
                return True, i

        # Caso contrario, retornamos False e um valor escolhido aleatoriamente
        return False, 0


    def movimento(self, lista_plataformas, lista_quebravel, nivelQuebravel, tecla_cima, tecla_baixo, tecla_esquerda,tecla_direita):

        self.tecla_cima = tecla_cima
        self.tecla_baixo = tecla_baixo
        self.tecla_esquerda = tecla_esquerda
        self.tecla_direita = tecla_direita

        keys = pg.key.get_pressed()

        # Variavel que diz se o jogador colidiu com uma plataforma
        colidiu: bool

        # Variavel, dentro da funcao, que ira receber o indice da plataforma que colidiu com o player
        indice: int


        #além de movimentar o jogador
        #essa funcao muda o atributo direcao do jogador
        #a partir da tecla que foi usada
        if keys[self.tecla_esquerda]:
            #
            self.direcao = "esquerda"
            self.quadrado.x -= self.velocidade

            # Chamando a funcao colisao da classe Player
            colidiu, indice = self.colisao(lista_plataformas)

            # Caso o jogador se mova para esquerda e colida com uma plataforma
            if (colidiu):
                # Modificamos a posicao do jogador para que fique a direita da plataforma
                self.quadrado.x = lista_plataformas[indice].x + lista_plataformas[indice].width

        if keys[self.tecla_direita]:
            self.quadrado.x += self.velocidade
            self.direcao = "direita"

            # Chamando a funcao colisao da classe Player
            colidiu, indice = self.colisao(lista_plataformas)

            # Caso o jogador se mova para direita e colida com uma plataforma
            if (colidiu):
                # Modificamos a posicao do jogador para que fique a esquerda da plataforma
                self.quadrado.x = lista_plataformas[indice].x - self.quadrado.width

        if keys[self.tecla_cima]:
            self.quadrado.y -= self.velocidade
            self.direcao = "cima"
            # Chamando a funcao colisao da classe Player
            colidiu, indice = self.colisao(lista_plataformas)

            # Caso o jogador se mova para frente e colida com uma plataforma
            if (colidiu):
                # Modificamos a posicao do jogador para que fique abaixo da plataforma
                self.quadrado.y = lista_plataformas[indice].y + lista_plataformas[indice].height

        if keys[self.tecla_baixo]:
            self.quadrado.y += self.velocidade
            self.direcao = "baixo"
            # Chamando a funcao colisao da classe Player
            colidiu, indice = self.colisao(lista_plataformas)

            # Caso o jogador se mova para tras e colida com uma plataforma
            if (colidiu):
                # Modificamos a posicao do jogador para que fique em cima da plataforma
                self.quadrado.y = lista_plataformas[indice].y - self.quadrado.height

        #mantem o jogador dentro da tela
        if self.quadrado.y<0:
            self.quadrado.y=0
        if self.quadrado.bottom>640:
            self.quadrado.bottom=640

        if keys[self.tecla_tiro]:
            self.tiro()

        # Bala se movimentando repetidamente até alcançar algo
        self.movimento_tiro(self.vel, self.inimigo, lista_plataformas, lista_quebravel, nivelQuebravel)

    def cooldown(self):
        """
        Método de cooldown das balas
        """
        if self.cool_down >= self.COOLDOWN: # Caso for maior que a constante de cooldown pode resetar para atirar
            self.cool_down = 0
        elif self.cool_down > 0:
            self.cool_down += 1
    
    def tiro(self):
        """
        Método de tiro 
        """
        if (self.quantidade_balas > 0):
            if self.cool_down == 0: # Caso o cool down seja 0 já pode atirar
                som_tiro.play()
                #aqui entra a direcao
                bala = Tiro(self.win, self.rect.center[0], self.rect.center[1], self.direcao)
                self.tiros.append(bala)
                self.cool_down = 1
                self.quantidade_balas -= 1
                self.pontos.soma(-1)
                print(self.quantidade_balas)

    def Ponto_soma(self, valor):
        """
        Método de adicionar balas 
        """
        #adicionado no contador de municao
        #+1 quando pega bala
        #-1 quando atira
        self.pontos.soma(valor)

    def movimento_tiro(self, vel, obj, lista_plataforma: list, list_quebravel: list, nivelQuebravel):
        """
        Método de mover a bala
        """
        vel = self.vel
        self.cooldown() # Chamar o cooldown
        for bala in self.tiros:
            
            bala.movimento(vel) # Chamar o método do movimento dentro da classe Tiro
            if bala.loops>1: # Impedir que o loop da bala fique infinito
                self.tiros.remove(bala)
            elif bala.colisao(bala, obj):
                self.tiros.remove(bala)
                self.inimigo.vida -= 10
                print(self.inimigo.vida)
                if self.vida <= 0: # Som da morte
                    som_morte.play()
                else:
                    som_dano.play()
            elif (bala.colisao_plataforma(lista_plataforma, list_quebravel, nivelQuebravel)): # Chamar método de objetos quebráveis e verificar colisão entre eles
                som_batida.play()
                self.tiros.remove(bala)

    def draw(self, screen):
        """
        Método de desenhar bala,pontuacao, player e a vida
        """
        screen.blit(self.imagem, self.rect)
        for bala in self.tiros:
            bala.draw()
        self.pontos.draw()
        self.vida_p.vida_funcao(self.vida)
        self.vida_p.draw()

"""
Método de spawnar um objeto em um lugar aleatório
"""
def spawnarObjeto(screen, classe, evitaveis: list = [], borda: int = 0, quantidade: int = 1):
    # cria uma copia pra evitar a modificação da lista original
    evitaveis = evitaveis.copy()

    for i in range(quantidade):
        contagem_loops = 0
        lugar_valido = False
        # fecha o loop se achar um lugar valido ou tentar mais de 50 vezes
        while not lugar_valido and contagem_loops < 50:
            contagem_loops += 1
            # pega o tamanho da tela
            tamanho_tela_x, tamanho_tela_y = pygame.display.get_surface().get_size()

            # gera coordenadas aleatorias
            objeto_x = random.uniform(borda, tamanho_tela_x-borda)
            objeto_y = random.uniform(borda, tamanho_tela_y-borda)

            # cria o objeto
            objeto = classe(screen, objeto_x, objeto_y)
            # infla o retangulo pra simular a borda
            objeto.rect.inflate_ip(borda, borda)

            # checa se o objeto colide com algum evitavel
            lugar_valido = True
            for evitavel in evitaveis:
                if objeto.rect.colliderect(evitavel.rect):
                    lugar_valido = False
                    objeto.remover()
                    break
            # desinfla o retangulo
            objeto.rect.inflate_ip(-borda, -borda)
        # adiciona ao evitaveis para impedir que alguem spawne sobre ele
        evitaveis.append(objeto)

"""
Método de spawnar coletaveis com nos pesos em um lugar aleatorio
"""
def spawnarColetaveis(screen, evitar: list = []):
    # so permite que 8 coletaveis existam no maximo
    if len(Coletaveis.lista_coletaveis) >= 8:
        return None

    # pesos para probabilidade de spawnar
    pesos = [70, 10, 10, 10]
    classes = [Balas, Velocidade, Velocidade_Tiro, Cadencia]

    escolhido = None

    soma_pesos = sum(pesos)
    rand = random.uniform(1, soma_pesos)

    soma_parcial = 0
    # escolhe uma classe aleatoria com base nos pesos
    for i in range(len(pesos)):
        if pesos[i] + soma_parcial > rand:
            escolhido = classes[i]
            break
        soma_parcial += pesos[i]

    spawnarObjeto(screen, escolhido, evitar, 20)

"""
Exibe o texto de Game Over do jogo
"""
def game_over(screen, ganhador):
    fonte=pg.font.Font(os.path.join('Assets/OXYGENE1.ttf'), 50)
    frase = fonte.render("GAME OVER",True,"WHITE")
    screen.blit(frase,(140,260,40,40))

    fonte2=pg.font.Font(os.path.join('Assets/OXYGENE1.ttf'), 20)
    frase2 = fonte2.render(f"JOGADOR {ganhador} VENCEU",True,"WHITE")
    screen.blit(frase2,(190,320,40,40))

    fonte3=pg.font.Font(os.path.join('Assets/OXYGENE1.ttf'), 15)
    frase3 = fonte3.render(f"APERTE ESPACO PARA CONTINUAR",True,"WHITE")
    screen.blit(frase3,(165,350,40,40))

def main():
    spawn_cooldown = 0
    screen = pg.display.set_mode((600, 640))
    nivel = mapa.Mapa('mapa.txt')
    tela_fundo = pygame.image.load('imagens/background.png')

    #Lista com as partes do cenario que tem colisao
    quantidade_plataform = []

    #Lista com os barris que podem ser quebrados
    quantidade_plataformQuebravel = []

    clock = pg.time.Clock()

    fonte_pontuacao = pg.font.Font(os.path.join('Assets/alarm clock.ttf'), 40)
    fonte_texto = pg.font.Font(os.path.join('Assets/SEASRN__.ttf'), 20)

    #criando os jogadores
    #com os controles, a posicao deles, a fonte que vai ser usada na pontuacao, a imagem do sprite...
    player1 = Player(screen, 260, 530, pg.K_w, pg.K_s, pg.K_a, pg.K_d, pg.K_f, None,(screen.get_width()-90),530,fonte_pontuacao,'imagens/cowboy_joaquim2.png' )
    player2 = Player(screen, 260, 70, pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT, pg.K_RCTRL, None,40,70,fonte_pontuacao, 'imagens/cowgirl_leila.png')
    player1.inimigo=player2
    player2.inimigo=player1

    #esse é o texto de Jogador 1 ou Jogador 2
    # os argumentos sao a janela, o texto, posicao x , posicao y, cor e a fonte
    id1 = texto(screen, 'Jogador 1', (screen.get_width() - 175), 570, (255, 255, 255), fonte_texto)
    id2 = texto(screen, 'Jogador 2', 40, 40, (255, 255, 255), fonte_texto)

    evitar_lista = [player1, player2]

    #Pegando as partes do cenario que irao ter colisao
    for objeto in nivel.grupo:
        quantidade_plataform.append(objeto.rect)
        evitar_lista.append(objeto)

    #Pegando os barris que podem ser quebrados
    for obj in nivel.grupo_quebravel:
        quantidade_plataformQuebravel.append([obj, 3])
        quantidade_plataform.append(obj.rect)
        evitar_lista.append(obj)

    done = False

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True

        # Chamando a funcao movimento do player, dentro dessa funcao movimento sera chamada a funcao colisao do player
        player1.movimento(quantidade_plataform, quantidade_plataformQuebravel, nivel.grupo_quebravel, pg.K_w, pg.K_s,
                          pg.K_a, pg.K_d)
        player2.movimento(quantidade_plataform, quantidade_plataformQuebravel, nivel.grupo_quebravel, pg.K_UP,
                          pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT)

        screen.blit(tela_fundo, (0, 0))

        nivel.atualizar_tela(screen)

        player1.draw(screen)
        player2.draw(screen)

        id1.draw()
        id2.draw()
        
        #exibe a tela de game over mostrando qual jogador ganhou
        if player1.vida <= 0:
            game_over(screen, 2)
        elif player2.vida <= 0:
            game_over(screen, 1)

        #esses condicionais olham pra qual direcao o jogador está olhando
        # e muda o sprite dependendo da direcao
        #mas como só temos 2 sprites ele só olha e muda se está olhando pra baixo ou pra cima
        if player1.direcao == "baixo":
            player1.imagem = pygame.image.load('imagens/cowboy_joaquim2.png')
        elif player1.direcao == "cima":
            player1.imagem = pygame.image.load('imagens/cowboy_joaquim2_costas.png')

        if player2.direcao == "baixo":
            player2.imagem = pygame.image.load('imagens/cowgirl_leila.png')
        elif player2.direcao == "cima":
            player2.imagem = pygame.image.load('imagens/cowgirl_leila.costas.png')

        #reseta o jogo depois de um game over ao apertar espaço
        if player1.vida <= 0 or player2.vida <= 0:
            keys = pg.key.get_pressed()

            if keys[pg.K_SPACE]:
                Coletaveis.lista_coletaveis=[]
                player1 = Player(screen, 260, 530, pg.K_w, pg.K_s, pg.K_a, pg.K_d, pg.K_f, None,(screen.get_width()-90),530,fonte_pontuacao,'imagens/cowboy_joaquim2.png' )
                player2 = Player(screen, 260, 70, pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT, pg.K_RCTRL, None,40,70,fonte_pontuacao, 'imagens/cowgirl_leila.png')
                player1.inimigo=player2
                player2.inimigo=player1
                nivel = mapa.Mapa('mapa.txt')

        
        #spawna um coletavel dependendo do cooldown
        spawn_cooldown += 1
        if spawn_cooldown >= 120:
            spawn_cooldown = 0
            spawnarColetaveis(screen, evitar_lista + Coletaveis.lista_coletaveis)

        # desenha todas as balas da lista e checa colisão com os jogadores
        for coletavel in Coletaveis.lista_coletaveis.copy():
            coletavel.draw(screen)

            if coletavel.rect.colliderect(player1.rect):
                coletavel.colisao_jogador(player1)
                player1.pontos.set_valor(player1.quantidade_balas)

            if coletavel.rect.colliderect(player2.rect):
                coletavel.colisao_jogador(player2)
                player2.pontos.set_valor(player2.quantidade_balas)

        

        pg.display.flip()
        clock.tick(30)

        pygame.display.update()


pygame.init()
screen = pygame.display.set_mode((600, 640))
menu = pygame.image.load('imagens/tela_menu.png')


class Botao(pygame.sprite.Sprite):
    def __init__(self, imagem, posx, posy):
        super().__init__()
        self.image = pygame.image.load(imagem)
        self.rect = self.image.get_rect()
        self.x = posx
        self.y = posy
    # coordenadas da área do botão
    def coord(self):
        self.rect.topleft = self.x, self.y
    # verifica se o click do mouse foi feito na área do botão
    def apertado(self, mx, my):
        if mx > self.x and mx < (self.x + self.image.get_width()):
            if my > self.y and my < (self.y + self.image.get_height()):
                return True
        return False
    # desenha o botão na tela
    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))


def menu_principal():
    while True:
        jogar = Botao('imagens/botao_jogar.png', 196, 364)
        jogar.draw(screen)
        sair = Botao('imagens/botao_sair.png', 196, 470)
        sair.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # começa a rodar o jogo
                if jogar.apertado(mouse_x, mouse_y):
                    main()
                # fecha a janela do pygame
                if sair.apertado(mouse_x, mouse_y):

                    pygame.quit()
                    sys.exit()
        pygame.display.update()
        screen.blit(menu, (0, 0))


menu_principal()
