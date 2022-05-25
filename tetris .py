
import pygame, random, sys
from piece import Tetris

#色の初期設定
RED = (200,9,9)
GREEN = (0,161,90)
BLUE = (0,111,212)
CYAN = (50,255,243)
PINK = (255,75,140)
YELLOW = (236,218,10)
LIGHTGREEN = (94,200,9)
PURPLE = (137,0,255)
ORANGE = (228,133,9)
WHITE  = (255,255,255)

TETRIS_COLORS = [YELLOW,PURPLE,RED,LIGHTGREEN,BLUE,
                 ORANGE,CYAN]

#物の初期設定
BOX_W = 800
BOX_H = 650

FIELD_X = 50
FIELD_Y = 100
FIELD_W = 250
FIELD_H = 500

CELL = 25
NEXT_D = 120

ADD_SCORE = 100

BGM = ["hoge.mp3","hogehoge.mp3"]

#画面の初期設定
#============

FONT_SIZE = 40

#スコア表示位置
SCORE_X = FIELD_X     
SCORE_Y = FIELD_Y - FONT_SIZE -10


#============

#初期設定
FPS = 30

COUNT = 360 

#状態遷移
STAGE_START = 1
STAGE_RUN = 2
STAGE_PAUSE = 3
STAGE_OVER = 4
STAGE_QUIT = 5

LINE_SPEEDUP = 5 #defalt 10

#============

#minoの設定
minos = [None] * 7

figures = [[[1,1],
            [1,1]], #■
           [[0,1,0],
            [1,1,1]], #T
           [[1,1,0],
            [0,1,1]], #Z
           [[0,1,1],
            [1,1,0]], #S
           [[1,0,0],
            [1,1,1]], #J
           [[0,0,1],
            [1,1,1]], #L
           [[1,1,1,1]] #I
           ]

for i in range(0, 7):
    minos[i] = Tetris(figures[i],TETRIS_COLORS[i],i+1)

#============

class Field:
    def __init__(self,x,y,w,h,color = WHITE):
        self.rect = pygame.Rect(x,y,w,h)
        self.color = color

#============

class Box:
    def __init__(self, width, height):
        pygame.init()
        pygame.mouse.set_visible(False) #マウスのカーソルを見せなくさせる
        self.screen = pygame.display.set_mode((width, height))
        self.width, self.height = (width, height)
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Impact', FONT_SIZE)
        self.font2 = pygame.font.SysFont('Impact', int(FONT_SIZE*0.6))
        
        #frame
        self.field = Field(FIELD_X,FIELD_Y,FIELD_W,FIELD_H,PINK)
        self.next_field = Field(self.field.rect.right+100,self.field.rect.top,\
                          NEXT_D,NEXT_D)
        self.hold_field = Field(self.field.rect.right+100 + NEXT_D + 20,\
                                self.field.rect.top,\
                          NEXT_D,NEXT_D)

        #BGM
        self.bgm = None #BGMファイルのディレクトリをリストに入れる　ex)["hoge.wav","huga.wav"]
        pygame.mixer.music.set_volume(0.3)
        
        #sound
        
        self.put_sound = pygame.mixer.Sound("poka01.wav") #テトリミノが落ち切った時の効果音
        self.delete_sound = pygame.mixer.Sound("jump09.wav") #ラインが消えるときの効果音
        self.start_sound = pygame.mixer.Sound("coin01.wav") #ゲームが始まる時の効果音
        self.s_up_sound = pygame.mixer.Sound("coin05.wav") #speed upする時の効果音
        self.move_sound = pygame.mixer.Sound("select03.wav") #左右ボタンを押したときの効果音
        self.over_sound = pygame.mixer.Sound("game_over.wav") #ゲームオーバーした時の効果音
        
        
    def setup(self): #ゲームごとにリセットする項目の初期化        
        self.stage = STAGE_START

        self.score = 0
        
        #置いたピースの情報を持つ↓
        self.grid = [[0 for i in range(10)] for j in range(20)]
        self.grid.append([8,8,8,8,8,8,8,8,8,8])#座標:10*20
        self.checker = False #当たり判定

        self.before_minos=[0,0]
        self.mino = self.make_mino()
        self.next_mino = self.make_mino()
        self.hold_mino = None
        

        self.speed = 12 #小さいほど速くなる
        self.time_count = 0
    
        self.line_count = 0 #消したlineの数

        #bgm
        bgm = random.choice(BGM)
        while(bgm == self.bgm):
            bgm = random.choice(BGM)
        self.bgm = bgm
        #print(self.bgm)
        pygame.mixer.music.load(self.bgm) #プレイするごとにBGM変わる
        pygame.mixer.music.set_volume(0.3)

    #ミノ系       
    def make_mino(self): #deep copy
        number = random.randint(0,6)
        if (number == self.before_minos[0]-1 and number == self.before_minos[1]-1):
           # print("change")
            while(number == self.before_minos[0]-1):
                number = random.randint(0,6)       
        mino = minos[number]
        new_mino = Tetris(mino.figure,mino.color,number+1)
        self.record_mino(new_mino)
        return new_mino
    
    def record_mino(self,mino): #3連続で同じものが来ないようにする
        p = self.before_minos[0]
        self.before_minos[0] = mino.number
        self.before_minos[1] = p
            
    def draw_block(self,x,y,color):
        pygame.draw.rect(self.screen,color,((x,y,CELL,CELL)))
        pygame.draw.rect(self.screen,WHITE,((x,y,CELL,CELL)),2)

    def draw_placed_block(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                if self.grid[i][j] != 0 and self.grid[i][j] != 8:
                    x,y = self.grid_to(j,i)
                    if self.grid[i][j] == 9: #消える時
                        self.draw_block(x,y,WHITE)
                    else:
                        self.draw_block(x,y,TETRIS_COLORS[self.grid[i][j]-1])                

    def grid_to(self,grid_x,grid_y):#gridから座標に
        x = self.field.rect.left + CELL * grid_x
        y = self.field.rect.top + CELL * grid_y
        return(x,y)

    def next_put_check(self,mino,grid_x,grid_y):
        height = len(mino.real_figure)
        width = len(mino.real_figure[0])
        
        for i in range(height):
            for j in range(width):
                if mino.real_figure[i][j] == 1:
                    if self.grid[grid_y+i+1][grid_x+j] != 0: #すでに置いてあって置けない
                        return True
        return False

    def put_mino(self,mino,grid_x,grid_y):

        height = len(mino.real_figure)
        width = len(mino.real_figure[0])
        
        cell_y = grid_y
        for i in range(height):
            cell_x = grid_x
            for j in range(width):
                if mino.real_figure[i][j] == 1:
                    x,y = self.grid_to(cell_x,cell_y)
                    self.draw_block(x,y,\
                                    mino.color)
                cell_x += 1
            cell_y += 1

    def put_mino2(self,mino,x_,y_): #左上の座標で置く
        height = len(mino.real_figure)
        width = len(mino.real_figure[0])

        y = y_
        for i in range(height):
            x = x_
            for j in range(width):
                if mino.real_figure[i][j] == 1:
                    self.draw_block(x,y,\
                                    mino.color)
                x += CELL
            y += CELL

    def add_mino(self,mino,grid_x,grid_y):
        height = len(mino.real_figure)
        width = len(mino.real_figure[0])
        
        cell_y = grid_y
        for i in range(height):
            cell_x = grid_x
            for j in range(width):
                if mino.real_figure[i][j] == 1:
                    if self.grid[cell_y][cell_x] == 0:
                        self.grid[cell_y][cell_x] = mino.number
                    else:
                        pass
                cell_x += 1
            cell_y += 1
        self.put_sound.play() #効果音
    
    def rotate(self,direction): #direction 1:left -1:right
        self.mino.pose = (self.mino.pose + direction)%4
        self.mino.rotate(self.mino.pose)

        width = len(self.mino.real_figure[0])
        height = len(self.mino.real_figure)

        if (self.mino.grid_x + width >10):
            while (self.mino.grid_x + width >10):#右に突き出る
                self.mino.grid_x -=1
        elif (self.mino.grid_x + width <0):
            while (self.mino.grid_x + width <0):#左に突き出る
                self.mino.grid_x +=1
        if (self.mino.grid_y + height >20):
            while (self.mino.grid_y + height >20):#下に突き出る
                self.mino.grid_y -=1
        self.move_sound.play() #効果音
    #========        
    #ハンドラ系
    def move_left(self):
        if self.mino.grid_x > 0:
            self.mino.grid_x -= 1
            self.move_sound.play() #効果音
        else:
            pass
        
    def move_right(self):
        if self.mino.grid_x + len(self.mino.real_figure[0]) < 10:
            self.mino.grid_x += 1
            self.move_sound.play() #効果音
        else:
            pass

    def speed_up(self):
        if self.speed >1:
            self.speed -= 1
            print(self.speed)
            self.s_up_sound.play() #効果音
        else:
            pass

    def hold(self):
        if self.hold_mino: #holdがあったら
            save = self.mino
            self.mino = self.hold_mino
            self.hold_mino = save
            self.mino.grid_x = save.grid_x
            self.mino.grid_y = save.grid_y
        else:
            self.hold_mino = self.mino
            self.mino = self.next_mino
            self.next_mino = self.make_mino()
    #========
    #ミノ系２
    def clear_line(self):
        del_list = []
        count = 0
        add_score = 0
        for s in range(20):
            i = 19 - s #下から調べる
            row = self.grid[i]
            if 0 not in row and 8 not in row:
                for j in range(10):
                    row[j] = 9 #消える
                del_list.append(i)
            if len(del_list) >= 4: #4行以上は消えない
                break
            
        if del_list != []:
            self.line_count += len(del_list)
            for s in range (int(FPS/2)):#1/2秒
                self.clock.tick(FPS)
                if len(del_list) == 4:
                    self.show_text("Tetris!",self.next_field.rect.centerx,\
                                   self.next_field.rect.bottom+(FONT_SIZE+10)*2,\
                                   ORANGE)
                if self.line_count >= LINE_SPEEDUP:
                    self.show_score()            
                    self.draw_placed_block()
                    self.frame()
                    self.draw_next_mino()
                    self.show_text("Speed Up!",self.next_field.rect.centerx,\
                               self.next_field.rect.bottom+FONT_SIZE+10,\
                               YELLOW)
                    pygame.display.flip()
                    self.screen.fill((0,0,0))
                    
                else:
                    self.show_all()
                    
            if self.line_count >= LINE_SPEEDUP:
                self.speed_up()
                self.line_count -= LINE_SPEEDUP 
                            
            for i in del_list:
                del self.grid[i+count]
                self.grid.insert(0,[0 for s in range(10)])
                count += 1
                add_score += ADD_SCORE * count
            self.score += add_score
            self.clock.tick(FPS)
            self.show_all()
            self.delete_sound.play() #効果音
            
        if self.grid[0][4] != 0 or self.grid[0][5] != 0:
            self.stage = STAGE_OVER
                
    def draw_next_mino(self):
        if self.next_mino.number == 7:#i型
            x = self.next_field.rect.centerx - CELL * 2
        elif self.next_mino.number == 1:#■型
            x = self.next_field.rect.centerx  - CELL * 1
        else:
            x = self.next_field.rect.centerx  - CELL * 1.5
            
        self.put_mino2(self.next_mino,x,self.next_field.rect.centery - CELL)

    def draw_hold_mino(self):
        if self.hold_mino: #holdがあったら    
            if self.hold_mino.number == 7:#i型
                x = self.hold_field.rect.centerx - CELL * 2
            elif self.hold_mino.number == 1:#■型
                x = self.hold_field.rect.centerx  - CELL * 1
            else:
                x = self.hold_field.rect.centerx  - CELL * 1.5

            if self.hold_mino.pose != 0:
                #print("rotate")
                self.hold_mino.pose = 0 #向きを直す
                self.hold_mino.rotate(0)
                
            self.put_mino2(self.hold_mino,x,self.hold_field.rect.centery - CELL)
        else:
            pass
    #========
    #表示
    def show_score(self):
        text = self.font.render("Score:"+ str(self.score),True,WHITE)
        self.screen.blit(text,(SCORE_X,SCORE_Y))

    def show_description(self):
        text_size = int(FONT_SIZE*0.6) +10 #10 = margin
        self.show_text2("x or SPACE:Turn Right",self.width * 3/5,\
                        self.field.rect.bottom - text_size*3)
        self.show_text2("z:Turn Left",self.width * 3/5,\
                        self.field.rect.bottom - text_size*2)
        self.show_text2("p:Pause",self.width * 3/5,\
                        self.field.rect.bottom - text_size)
        self.show_text2("f:Hold",self.width * 3/5,\
                        self.field.rect.bottom )
    
    def show_text(self,text,c_x,c_y,color = WHITE): #c_x,c_yは中心の座標
        text_image = self.font.render(text,True,color)
        width,height = self.font.size(text)
        self.screen.blit(text_image,(c_x - width/2,c_y - height/2))

    def show_text2(self,text,x,y,color = WHITE): #
        text_image = self.font2.render(text,True,color)
        width,height = self.font2.size(text)
        self.screen.blit(text_image,(x , y))

    def frame(self):
        pygame.draw.rect(self.screen,CYAN ,\
                         self.next_field.rect, 3)
        text = self.font.render("Next→",True,WHITE)
        self.screen.blit(text,(self.next_field.rect.left,\
                               self.next_field.rect.top - FONT_SIZE - 10))

        pygame.draw.rect(self.screen,YELLOW ,\
                         self.hold_field.rect, 3)
        text = self.font.render("Hold→",True,WHITE)
        self.screen.blit(text,(self.hold_field.rect.left,\
                               self.hold_field.rect.top - FONT_SIZE - 10))
            
        pygame.draw.rect(self.screen, self.field.color,self.field.rect, 3)

    
    def show_all(self):
        self.show_score()            
        self.draw_placed_block()
        self.frame()
        self.show_description()
        self.draw_next_mino()
        self.draw_hold_mino()
        pygame.display.flip()
        self.screen.fill((0,0,0))
    #========
    #実働部分    
    def run(self):#stageごとのふるまい
        while (self.stage != STAGE_QUIT):
            if self.stage == STAGE_START:
                self.intro()
            if self.stage == STAGE_RUN:
                self.animate()
            if self.stage == STAGE_PAUSE:
                self.pause()
            if self.stage != STAGE_QUIT:
                if self.stage == STAGE_OVER:
                    self.game_over()
                else:       # 再開する
                    self.stage = STAGE_RUN
                    
    #stageごとの動き    
    def intro(self):

        self.setup()
        #print("intro")

        while(self.stage == STAGE_START):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stage = STAGE_QUIT
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.stage = STAGE_RUN
                        self.start_sound.play() #効果音
            
            self.time_count += 1
            if (self.time_count <20):
                self.show_text("Tetris",self.width/2,\
                           self.height /2 - 10 - FONT_SIZE,LIGHTGREEN)
                self.show_text("""Press "SPACE" """,self.width/2,\
                               self.height /2 + 10 + FONT_SIZE)
                self.show_text("to Start",self.width/2,\
                               self.height /2 + 10*2 + FONT_SIZE*2)

                
                
            if self.time_count >= 40:
                self.time_count = 0
            
            self.clock.tick(FPS)
            pygame.display.flip()
            self.screen.fill((0,0,0))
        
        
        
    def pause(self):
        pygame.mixer.music.pause() #BGM一旦停止
        while(self.stage == STAGE_PAUSE):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stage = STAGE_QUIT
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        pygame.mixer.music.unpause() #BGM再開
                        self.stage = STAGE_RUN
            
            self.show_score()            
            self.frame()
            self.show_description()
            self.draw_next_mino()
            self.draw_hold_mino()
            self.show_text("Pause",self.field.rect.centerx,self.field.rect.centery)
            pygame.display.flip()
            self.screen.fill((0,0,0))
    

    def game_over(self):
        self.time_count = 0
        pygame.mixer.music.stop() #BGM停止
        self.over_sound.play()
        while (self.stage == STAGE_OVER):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stage = STAGE_QUIT
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.stage = STAGE_START

            self.show_score()            
            self.frame()

            self.time_count += 1
            if (self.time_count <20):
                self.show_text("Game Over!",self.next_field.rect.centerx,\
                           self.next_field.rect.bottom + 10 + FONT_SIZE)
                self.show_text("""PRESS "SPACE" """,self.next_field.rect.centerx,\
                               self.next_field.rect.bottom + 10*2 + FONT_SIZE*2)
                self.show_text("to Restart",self.next_field.rect.centerx,\
                               self.next_field.rect.bottom + 10*3 + FONT_SIZE*3)

                
                
            if self.time_count >= 40:
                self.time_count = 0
            
            self.clock.tick(FPS)
            pygame.display.flip()
            self.screen.fill((0,0,0))


    def animate(self):#ゲーム中の動き
        if pygame.mixer.music.get_busy() == False:
            pygame.mixer.music.play(-1) #BGMループ再生
        while (self.stage == STAGE_RUN):
            self.checker = self.next_put_check(self.mino,self.mino.grid_x,\
                                               self.mino.grid_y) #次に置けるかどうか
            down_count = 1 #突き抜け防止

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stage = STAGE_QUIT
                    
                if event.type == pygame.KEYDOWN:
                     #「z」キーを処理する
                    if event.key == pygame.K_z:
                        self.rotate(1)
                     #「x」キーを処理する   
                    if event.key == pygame.K_x or\
                       event.key == pygame.K_SPACE:
                        self.rotate(-1)
                            
                    #「←」キーを処理する
                    if event.key == pygame.K_LEFT:
                        self.move_left()
                    #「→」キーを処理する
                    if event.key == pygame.K_RIGHT:
                        self.move_right()
                    #「↓」キーを処理する
                    if event.key == pygame.K_DOWN:
                        if self.next_put_check(self.mino,self.mino.grid_x,\
                                               self.mino.grid_y+down_count) != True: #突き抜けないのなら
                            self.mino.grid_y += 1
                            down_count += 1
                    #「f」キーを処理する
                    if event.key == pygame.K_f:
                        self.hold()
                    #「p」キーを処理する
                    if event.key == pygame.K_p:
                        self.stage = STAGE_PAUSE
                    
            
            if self.checker:#当たっていたら
                self.add_mino(self.mino,self.mino.grid_x,self.mino.grid_y)
                self.mino = self.next_mino
                self.next_mino = self.make_mino()
                # print(self.mino)
            
            else:
                self.time_count += 1
                if (self.time_count % self.speed == 0):
                    self.mino.grid_y += 1 #次の場所へ移動
                self.put_mino(self.mino,self.mino.grid_x,\
                                  self.mino.grid_y)
                if self.time_count >= COUNT:
                    self.time_count = 0
                
            self.clear_line()    
            self.clock.tick(FPS)
            self.show_all()

            
def main():
    box = Box(BOX_W,BOX_H)
    box.setup()
    box.run()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

