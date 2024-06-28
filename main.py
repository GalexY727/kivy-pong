from kivy.uix.actionbar import ColorProperty
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
import random

class PongBall(Widget):

    # velocity of the ball on x and y axis
    velocity_x = NumericProperty(1)
    velocity_y = NumericProperty(0)

    # referencelist property so we can use ball.velocity as
    # a shorthand, just like e.g. w.pos for w.x and w.y
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    # ``move`` function will move the ball one step. This
    #  will be called in equal intervals to animate the ball
    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

def clamp(n, min, max): 
    if n < min: 
        return min
    elif n > max: 
        return max
    else: 
        return n 
class PongPaddle(Widget):

    score = NumericProperty(0)
    previous_speed = 0

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.1
            ball.velocity = vel.x, vel.y + offset + 1/4 * self.previous_speed

class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    computer = ObjectProperty(None)
    winner = StringProperty(None)
    winner_color = ColorProperty(defaultvalue=[1, 0, 0, 1])

    def serve(self, vel=(-4, -1)):
        self.ball.center = self.center
        self.ball.velocity = vel
        self.winner = ''

    def callback(self, instance):
        self.player1.score = 0
        self.computer.score = 0
        self.remove_widget(instance)
        self.serve()

    def update(self, dt):
        self.ball.move()

        # bounce off top and bottom
        if (self.ball.y < 0) or (self.ball.top > self.height):
            self.ball.velocity_y *= -1

        # bounce off left and right
        if (self.ball.x < 0) or (self.ball.right > self.width):
            self.ball.velocity_x = 0
            self.ball.velocity_y = 0
            vel = (4, -1)
            if self.ball.x < 0:
                self.computer.score += 1
                vel = (-4, 1)
            else:
                self.player1.score += 1
            self.serve(vel=vel)
            if self.player1.score == 2 or self.computer.score == 2:
                self.serve(vel=(0, 0))
                if (self.player1.score == 2):
                    self.winner = 'U Win! :>'
                    self.winner_color = 'green'
                else:
                    self.winner = 'U Lost :<'
                    self.winner_color = 'red'
                winnerbutton = Button(text='Play Again', font_size=14)
                winnerbutton.bind(on_press=self.callback)
                self.add_widget(winnerbutton)

        # bounce off paddles
        self.player1.bounce_ball(self.ball)
        self.computer.bounce_ball(self.ball)
        
        computer_speed = clamp((self.ball.velocity_y + self.ball.velocity_x)/2, 2, 7)
        if self.ball.y > self.computer.center_y + self.computer.height/2:
            self.computer.center_y += computer_speed
        elif self.ball.y < self.computer.center_y - self.computer.height/2:
            self.computer.center_y -= computer_speed

    def on_touch_move(self, touch):
        last_position = self.player1.center_y
        self.player1.center_y = clamp(touch.y, self.player1.height/2, self.height - self.player1.height/2)
        self.player1.previous_speed = self.player1.center_y - last_position

class PongApp(App):

    def build(self):
        game = PongGame()
        game.serve()
        Clock.schedule_interval(game.update, 1.0/60.0)
        return game

if __name__ == '__main__':
    PongApp().run()