import pygame
import random
import os
import time
import neat
import pickle
pygame.font.init()    #字體引入

window_width=580
window_height=780
Floor=730
Stat_font=pygame.font.SysFont("comicsans", 50)
End_font=pygame.font.SysFont("comicsans", 70)
Draw_lines=False


WIN = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Flappy Bird")


Bird_Images=[pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))),
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))),
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]
Pipe_Images=pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))
Base_Images=pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))
Bg_Images=pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))

gen =0

class Bird:
    Images=Bird_Images
    MAX_ROTATION=25  #bird跳躍高上限
    ROT_VEL=20       
    ANIMATION_TIME=5 #每個bird的顯示時間

    def __init__(self,x,y):  #bird 初始位置
        self.x=x
        self.y=y
        self.tilt=0
        self.tick_count=0
        self.vel=0
        self.height=self.y
        self.img_count=0
        self.img=self.Images[0]

    def jump(self):
        self.vel= -10.5
        self.tick_count=0
        self.height=self.y

    def move(self):
        
        self.tick_count+=1
        
        d=self.vel*(self.tick_count)+1.5*(self.tick_count)**2
        
        if d>=16:
             d= (d/abs(d)) * 16
        
        if d<0:
            d-=2
            
        self.y=self.y+d
        
        if d<0 or self.y<self.height+50:
            if self.tilt<self.MAX_ROTATION:
                self.tilt=self.MAX_ROTATION
        else:
            if self.tilt>-90:
                self.tilt-=self.ROT_VEL

    def draw(self,win):
        self.img_count+=1
        
        if self.img_count <= self.ANIMATION_TIME:
            self.img=self.Images[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img=self.Images[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img=self.Images[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img=self.Images[1]
        elif self.img_count == self.ANIMATION_TIME*4+1:
            self.img=self.Images[0]
            self.img_count=0
            
        if self.tilt<=-80:
            self.img=self.Images[1]
            self.img_count=self.ANIMATION_TIME*2
            
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe():    
    Gap=200
    Vel=5
    
    def __init__(self,x):
        self.x=x
        self.height=0
        self.top=0
        self.bottom=0
        self.PIPE_top=pygame.transform.flip(Pipe_Images,False,True)
        self.PIPE_bottom=Pipe_Images
        self.passed=False
        self.set_height()
        
    def set_height(self):
        self.height=random.randrange(50,450)
        self.top=self.height-self.PIPE_top.get_height()
        self.bottom=self.height+self.Gap
        
    def move(self):
        self.x-=self.Vel
        
    def draw(self,win):
        win.blit(self.PIPE_top,(self.x,self.top))
        win.blit(self.PIPE_bottom,(self.x,self.bottom))
        
    def collide(self,bird,win):
        
        bird_mask=bird.get_mask()
        top_mask=pygame.mask.from_surface(self.PIPE_top)
        bottom_mask=pygame.mask.from_surface(self.PIPE_bottom)
        
        top_offset=(self.x-bird.x,self.top-round(bird.y)) 
        bottom_offset=(self.x-bird.x,self.bottom-round(bird.y)) 
        
        bottom_point=bird_mask.overlap(bottom_mask,bottom_offset)  #overlap
        top_point=bird_mask.overlap(top_mask,top_offset)
        
        if bottom_point or top_point:
            return True
        return False    

class Base:   
    
    VEL=50
    WIDTH=Base_Images.get_width()
    IMG=Base_Images
    def __init__(self,y):
        self.y=y
        self.x1=0
        self.x2=self.WIDTH

    def move(self):
        self.x1-=self.VEL
        self.x2-=self.VEL
        
        if self.x1+self.WIDTH<0:
            self.x1=self.x2+self.WIDTH #底下圖1與圖2做連接
        if self.x2+self.WIDTH<0:
            self.x2=self.x1+self.WIDTH #底下圖2與圖1做連接
        
    def draw(self,win):
        win.blit(self.IMG,(self.x1,self.y))
        win.blit(self.IMG,(self.x2,self.y))

def blitRotateCenter(surf, image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def draw_window(win,birds,pipes,base,score,gen,pipe_ind):
    
    if gen==0:
        gen=1
    win.blit(Bg_Images,(0,0))
    
    for pipe in pipes:
        pipe.draw(win)
    
    base.draw(win)
    for bird in birds:
        if Draw_lines:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), 
                                (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), 
                                (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
            except:
                break
        bird.draw(win)
        
    # score
    score_label = Stat_font.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (window_width - score_label.get_width() - 15, 10))

    # generations
    score_label = Stat_font.render("Gens: " + str(gen-1),1,(255,255,255))
    win.blit(score_label, (10, 10))

    # alive
    score_label = Stat_font.render("Alive: " + str(len(birds)),1,(255,255,255))
    win.blit(score_label, (10, 50))

    pygame.display.update()

def main(genomes,config):
    
    global WIN, gen
    win = WIN
    gen += 1
    
    nets=[]
    ge=[]
    birds=[]
    
    for genome_id, genome in genomes:
        genome.fitness = 0   # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome,config)
        nets.append(net)
        birds.append(Bird(230,350))
        ge.append(genome)
        
        
        
    base=Base(Floor)
    pipes=[Pipe(700)]   #柱子間距離
    score=0

    clock=pygame.time.Clock() #Bird的時間 

    run=True
    while run and len(birds) > 0:
        clock.tick(30)   #設定Bird掉落時間
        
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                run=False
                pygame.quit()   #類似exit()
                quit()
                break

        pipe_ind=0
        if len(birds) > 0:
            if len(pipes)>1 and birds[0].x>pipes[0].x+pipes[0].PIPE_top.get_width():
                pipe_ind=1

        for x,bird in enumerate(birds):
            ge[x].fitness+=0.1
            bird.move()
            
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height),abs(bird.y - pipes[pipe_ind].bottom)))
            
            if output[0]>0.5:
                bird.jump()

        base.move()

        rem=[]
        add_pipe=False
        for pipe in pipes:    #柱子動畫，並連續
            pipe.move()
            
            for bird in birds:
                if pipe.collide(bird, win):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))
                    
            if pipe.x+pipe.PIPE_top.get_width()<0:
                rem.append(pipe)
                
            if not pipe.passed and pipe.x<bird.x:
                pipe.passed=True
                add_pipe=True
            
        if add_pipe:         
            score+=1
            
            for genome in ge:
                genome.fitness+=5
                
            pipes.append(Pipe(window_width))   #柱子間距離
        
        for r in rem:
            pipes.remove(r)
            
        for bird in birds:
            if bird.y+bird.img.get_height() - 10>=Floor or bird.y<-50:   #小鳥撞到柱子
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))
        
        draw_window(WIN, birds, pipes, base, score, gen, pipe_ind)
        # 如果分數超過15分結束
        if score > 30:
            pickle.dump(nets[0],open("best.pickle", "wb"))
            break


def run(config_file):
    config=neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,
                            neat.DefaultSpeciesSet,neat.DefaultStagnation,
                            config_file)
    
    p=neat.Population(config)  #設定population
    
    p.add_reporter(neat.StdOutReporter(True))  #找解釋，設置output
    stats=neat.StatisticsReporter()
    p.add_reporter(stats)
    
    winner=p.run(main,50)    #基因模組幾個，呼叫main幾次
    
    print('\nBest genome:\n{!s}'.format(winner))

if __name__=='__main__':
    local_dir=os.path.dirname(__file__)
    config_path=os.path.join(local_dir,'config-feedforward.txt')
    run(config_path)