import pygame
import random

pygame.init()
# 屏幕大小的常量
SCREEN_RECT = pygame.Rect(0, 0, 480, 720)
# 刷新的帧率
FRAME_PER_SEC = 60
# 创建敌机的定时器常量
CREATE_ENEMY_EVENT = pygame.USEREVENT  # 用户事件的常量
# 英雄发射子弹事件
HERO_FIRE_EVENT = pygame.USEREVENT + 1


class GameSprite(pygame.sprite.Sprite):  # (继承父类) 其中sprite是模块 Sprite是类名称
    """飞机大战游戏精灵"""

    # 构造函数/初始化
    def __init__(self, image_name, speed=1):
        # 调用父类初始化方法
        super().__init__()
        # 定义对象的属性
        self.image = pygame.image.load(image_name)
        self.rect = self.image.get_rect()  # 图像的属性
        self.speed = speed
        # print("init已被调用")

    def update(self, *args):  # *args 一定保留
        # 屏幕上垂直移动
        self.rect.y += self.speed


# 继承了父类 GameSprite 拥有 读图 纵向移动
class Background(GameSprite):
    """游戏背景精灵"""

    def __init__(self, is_alt=False):

        # 调用父类方法
        super().__init__("./image/background.png")  # 往父类初始化传入参数

        # 判断交替图像
        if is_alt:
            self.rect.y = -self.rect.height

    def update(self, *args):
        # 1.调用父类的方法实现
        super().update()
        # 2.判断是否移出屏幕
        if self.rect.y >= SCREEN_RECT.height:
            self.rect.y = -self.rect.height


# 敌机类
class Enemy(GameSprite):
    def __init__(self):
        # 调用父类 指定图片
        super().__init__("./image/enemy1.png")

        # 指定随机速度
        self.speed = random.randint(1, 3)

        # 敌机初始位置
        # 垂直方向
        self.rect.bottom = 0
        # 水平方向
        max_x = SCREEN_RECT.width - self.rect.width
        self.rect.x = random.randint(0, max_x)

    def update(self, *args):
        super().update()
        if self.rect.y >= SCREEN_RECT.height:
            # 将精灵从所有的组移出  并被del调用
            self.kill()
            # print("飞出了屏幕")

    # 销毁时调用敌机挂了
    def __del__(self):
        if self.rect.bottom < 720:
            self.image = pygame.image.load("./image/enemy1_down1.png")
            self.rect = self.image.get_rect()  # 图像的属性

        # print("敌机挂了 %s" %self.rect)


class Hero(GameSprite):
    def __init__(self):
        # 调用父类方法.设置图片
        super().__init__("./image/me1.png", 0)
        # 设置英雄的初始位置
        self.rect.centerx = SCREEN_RECT.centerx
        self.rect.bottom = SCREEN_RECT.bottom - 120
        # 创建子弹精灵组
        self.bullets = pygame.sprite.Group()

    def update(self, *args):
        # 水平方向移动 不调用父类方法 自己适配子类方法
        self.rect.x += self.speed
        # 判断是否移出屏幕
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.right > SCREEN_RECT.right:
            self.rect.right = SCREEN_RECT.right

    def fire(self):
        print("发射子弹")
        # 一次发射三个子弹
        for i in (0, 1, 2):
            # 创建子弹精灵
            bullet = Bullet()
            # 设置精灵的位置
            bullet.rect.bottom = self.rect.y - i * 20
            bullet.rect.centerx = self.rect.centerx
            # 添加到子弹精灵组
            self.bullets.add(bullet)


class Bullet(GameSprite):

    def __init__(self):
        super().__init__("./image/bullet1.png", -2)

    def update(self, *args):
        super().update()
        if self.rect.bottom < 0:
            # 调用kill方法移出精灵组
            self.kill()

    def __del__(self):
        print("子弹被销毁")


class PlaneGame(object):
    """飞机大战主游戏"""

    def __init__(self):
        print("游戏初始化")

        # 1.创建游戏的窗口
        self.screen = pygame.display.set_mode(SCREEN_RECT.size)  # 常量 > 700
        # 2.创建游戏的时钟
        self.clock = pygame.time.Clock()
        # 3.调用私有方法，精灵和精灵组的创建
        self.__create_sprites()
        # 4.设定定时器实践 - 创建敌机 1s
        pygame.time.set_timer(CREATE_ENEMY_EVENT, 1000)  # 时间一到，触发名叫CREAT_ENEMY_EVENT的事件
        pygame.time.set_timer(HERO_FIRE_EVENT, 500)  # 时间一到，触发名叫CREAT_ENEMY_EVENT的事件

    # 私有方法 双下划线  __
    # 创建精灵
    def __create_sprites(self):
        # 背景精灵组
        bg1 = Background()
        bg2 = Background(True)
        self.back_group = pygame.sprite.Group(bg1, bg2)

        # 创建敌机的精灵组
        self.enemy_group = pygame.sprite.Group()
        self.hero = Hero()
        self.hero_group = pygame.sprite.Group(self.hero)

    # 事件监听
    def __event_handler(self):
        for event in pygame.event.get():

            # 退出事件
            if event.type == pygame.QUIT:
                PlaneGame.__game_over()  # 静态方法通过类名调用
            elif event.type == CREATE_ENEMY_EVENT:
                # print("敌机出场...")
                # 创建敌机精灵
                enemy = Enemy()
                # 添加到精灵组
                self.enemy_group.add(enemy)
            elif event.type == HERO_FIRE_EVENT:
                self.hero.fire()

            # 第一种方式：需要不停摁下
            # elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            # print("向右移动")
        # 第二种方式：不需要不停摁
        key_press = pygame.key.get_pressed()
        if key_press[pygame.K_RIGHT]:
            self.hero.speed = 5
        elif key_press[pygame.K_LEFT]:
            self.hero.speed = -5
        else:
            self.hero.speed = 0

    def __check_collide(self):
        # 子弹摧毁敌机
        pygame.sprite.groupcollide(self.hero.bullets, self.enemy_group, True, True)
        # 敌机撞毁英雄
        enemies = pygame.sprite.spritecollide(self.hero, self.enemy_group, True)
        if len(enemies) > 0:
            self.hero.kill()
            PlaneGame.__game_over()

    def __updata_sprites(self):
        self.back_group.update()
        self.back_group.draw(self.screen)

        self.enemy_group.update()
        self.enemy_group.draw(self.screen)

        self.hero_group.update()
        self.hero_group.draw(self.screen)

        self.hero.bullets.update()
        self.hero.bullets.draw(self.screen)

    @staticmethod
    def __game_over():  # 静态方法 就不接受self的东西
        print("游戏结束")
        pygame.QUIT 
        # 有问题
        exit()

    def start_game(self):
        print("游戏开始...")
        while True:
            # 1.刷新频率
            self.clock.tick(FRAME_PER_SEC)
            # 2.事件监听
            self.__event_handler()
            # 3.碰撞检测
            self.__check_collide()
            # 4.更新/绘制精灵
            self.__updata_sprites()
            # 5.更新检测
            pygame.display.update()
            print(SCREEN_RECT.size)


if __name__ == '__main__':
    # 创建游戏对象
    game = PlaneGame()
    # 启动游戏
    game.start_game()
