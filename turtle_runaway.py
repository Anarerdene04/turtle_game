import tkinter as tk
import turtle, random, time

class RunawayGame:
    def __init__(self, canvas, runner, chaser, catch_radius=50, player_role='chaser'):
        self.canvas = canvas
        self.runner = runner
        self.chaser = chaser
        self.catch_radius2 = catch_radius ** 2
        self.player_role = player_role  
        
        self.runner.shape('turtle'); self.runner.color('blue'); self.runner.penup()
        self.chaser.shape('turtle'); self.chaser.color('red');  self.chaser.penup()

        self.drawer = turtle.RawTurtle(canvas)
        self.drawer.hideturtle(); self.drawer.penup()

        self.ai_timer_msec = 100
        self.game_over = False
        self.start_time = None

        self.score = 0                 
        self.best_score = 0          
        self.best_ttc = None           

        margin = 20
        self.left, self.right = -350 + margin, 350 - margin
        self.top,  self.bottom =  350 - margin, -350 + margin

        canvas.onkeypress(self.restart, 'r')
        canvas.listen()

    def get_score(self):
        """Return current score (elapsed seconds)."""
        return self.score

    def is_catched(self):
        p, q = self.runner.pos(), self.chaser.pos()
        dx, dy = p[0]-q[0], p[1]-q[1]
        return dx*dx + dy*dy < self.catch_radius2

    def clamp_or_bounce(self, turt):
        x, y = turt.pos(); bounced = False
        if x < self.left: x = self.left; bounced = True
        elif x > self.right: x = self.right; bounced = True
        if y < self.bottom: y = self.bottom; bounced = True
        elif y > self.top: y = self.top; bounced = True
        if bounced:
            turt.setpos(x, y)
            turt.setheading((turt.heading() + 180) % 360)

    def start(self, init_dist=400, ai_timer_msec=100):
        self.ai_timer_msec = ai_timer_msec

        self.runner.setpos((-init_dist/2, 0)); self.runner.setheading(0)
        self.chaser.setpos((+init_dist/2, 0)); self.chaser.setheading(180)
        self.game_over = False
        self.start_time = time.time()
        self.score = 0

        role_line = "YOU are CHASER — Catch the blue!" if self.player_role=='chaser' \
                    else "YOU are RUNNER — Survive!"
        self._write_hud(f"{role_line}\nTime: 0 s  Score: 0  "
                        f"{'Best TTC: -' if self.best_ttc is None else f'Best TTC: {self.best_ttc} s'}  "
                        f"Best (Runner): {self.best_score}   [R] Restart")

        self.canvas.ontimer(self.step, self.ai_timer_msec)

    def restart(self):
        self.start()

    def _write_hud(self, text):
        self.drawer.clear()
        self.drawer.setpos(-340, 310)
        self.drawer.write(text, font=('Arial', 12, 'bold'))

    def step(self):
        if self.game_over:
            return

        self.runner.run_ai(self.chaser.pos(), self.chaser.heading())
        self.chaser.run_ai(self.runner.pos(), self.runner.heading())

        self.clamp_or_bounce(self.runner)
        self.clamp_or_bounce(self.chaser)

        elapsed = int(time.time() - self.start_time)
        self.score = elapsed  

        if self.is_catched():
            self.game_over = True
            if self.player_role == 'chaser':
                ttc = elapsed  
                if (self.best_ttc is None) or (ttc < self.best_ttc):
                    self.best_ttc = ttc

                self.drawer.clear()
                self.drawer.setpos(-90, 10)
                self.drawer.write("YOU WIN!", font=('Arial', 20, 'bold'))
                self.drawer.setpos(-200, -20)
                self.drawer.write(f"Time to Catch (Score): {ttc} s   Best TTC: {self.best_ttc} s",
                                  font=('Arial', 16, 'bold'))
                self.drawer.setpos(-120, -50)
                self.drawer.write("[R] Restart", font=('Arial', 14, 'normal')

            else:                
            
            self.best_score = max(self.best_score, self.score)

                self.drawer.clear()
                self.drawer.setpos(-80, 10)
                self.drawer.write("GAME OVER", font=('Arial', 20, 'bold'))
                self.drawer.setpos(-260, -20)
                self.drawer.write(f"Final Score: {self.score} s   Best (Runner): {self.best_score} s",
                                  font=('Arial', 16, 'bold'))
                self.drawer.setpos(-120, -50)
                self.drawer.write("[R] Restart", font=('Arial', 14, 'normal'))

            return

        role_line = "Catch the blue" if self.player_role=='chaser' else "Survive"
        ttc_text = "-" if self.best_ttc is None else f"{self.best_ttc} s"
        self._write_hud(
            f"Goal: {role_line}\nTime: {elapsed} s  Score: {self.score}  "
            f"Best TTC: {ttc_text}  Best (Runner): {self.best_score}   [R] Restart"
        )

        self.canvas.ontimer(self.step, self.ai_timer_msec)

class ManualMover(turtle.RawTurtle):
    def __init__(self, canvas, step_move=10, step_turn=10):
        super().__init__(canvas)
        self.step_move = step_move; self.step_turn = step_turn
        self.penup()
        canvas.onkeypress(lambda: self.forward(self.step_move), 'Up')
        canvas.onkeypress(lambda: self.backward(self.step_move), 'Down')
        canvas.onkeypress(lambda: self.left(self.step_turn), 'Left')
        canvas.onkeypress(lambda: self.right(self.step_turn), 'Right')
        canvas.listen()
    def run_ai(self, opp_pos, opp_heading):
        pass

class RandomMover(turtle.RawTurtle):
    def __init__(self, canvas, step_move=10, step_turn=10):
        super().__init__(canvas)
        self.step_move = step_move; self.step_turn = step_turn
        self.penup()
    def run_ai(self, opp_pos, opp_heading):
        mode = random.randint(0, 2)
        if mode == 0: self.forward(self.step_move)
        elif mode == 1: self.left(self.step_turn)
        else: self.right(self.step_turn)

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Turtle Runaway")
    canvas = tk.Canvas(root, width=700, height=700); canvas.pack()
    screen = turtle.TurtleScreen(canvas); screen.bgcolor("#b3e5fc")

    runner = RandomMover(screen)      
    chaser = ManualMover(screen)       

    game = RunawayGame(screen, runner, chaser,
                       catch_radius=50,
                       player_role='chaser')  
    game.start(init_dist=400, ai_timer_msec=100)

screen.mainloop()