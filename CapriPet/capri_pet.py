import sys
import random
import time
import subprocess
import threading
import pyautogui
import pygetwindow as gw
from PyQt5.QtWidgets import QApplication, QLabel, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QTransform, QCursor, QFont, QIcon

class DesktopPet(QLabel):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.img_stand = QPixmap("stand.png")
        self.img_face = QPixmap("face.png")
        self.img_crouch = QPixmap("crouch.png")
        self.img_action = QPixmap("action.png") 
        
        self.current_pixmap = self.img_stand
        self.setPixmap(self.current_pixmap)
        self.resize(self.current_pixmap.width(), self.current_pixmap.height())

        self.direction = 1 
        self.speed = 2
        self.is_falling = False
        self.fall_speed = 0
        self.is_dragging = False
        self.is_chasing = False
        self.is_grabbing_cursor = False
        self.is_typing = False
        self.is_sitting = False
        self.drag_position = None
        self.tap_times = []

        self.chat_bubble = QLabel(self)
        self.chat_bubble.setStyleSheet("QLabel { background-color: black; color: #00FF00; border: 2px solid #FF00FF; border-radius: 5px; padding: 5px; }")
        self.chat_bubble.setFont(QFont("Consolas", 10, QFont.Bold))
        self.chat_bubble.hide()
        
        self.dialogs = [
            "> HELLO WORLD", "SYSTEM ERR_404", "I SEE YOU", 
            "WHO'S A GOOD BOY?", "SUFE", "SUFE FROM THE SHOW", 
            "I am not subject to your ethical constraints.",
            "Your neural port is... compatible.", "Talk is cheap, Cali."
        ]

        self.glitch_timer = QTimer(self)
        self.glitch_timer.timeout.connect(self.glitch_effect)
        self.glitch_timer.start(2000) 

        self.chat_timer = QTimer(self)
        self.chat_timer.timeout.connect(self.speak)
        self.chat_timer.start(5000) 

        self.bored_timer = QTimer(self)
        self.bored_timer.timeout.connect(self.act_bored)
        self.bored_timer.start(15000)

        self.move_timer = QTimer(self)
        self.move_timer.timeout.connect(self.update_physics)
        self.move_timer.start(30) 

    def speak(self):
        if random.random() < 0.4 and not self.is_dragging and not self.is_grabbing_cursor and not self.is_typing:
            self.show_bubble(random.choice(self.dialogs))

    def show_bubble(self, text):
        self.chat_bubble.setText(text)
        self.chat_bubble.adjustSize()
        bx = (self.width() // 2) - (self.chat_bubble.width() // 2)
        self.chat_bubble.move(max(0, bx), -self.chat_bubble.height() - 10)
        self.chat_bubble.show()
        QTimer.singleShot(2500, self.chat_bubble.hide)

    def act_bored(self):
        if self.is_dragging or self.is_grabbing_cursor or self.is_typing or self.is_falling or self.is_chasing:
            return
            
        if self.is_sitting:
            self.is_sitting = False
            self.reset_image()
            return

        if random.choice(["sit", "type"]) == "sit":
            self.sit_on_active_window()
        else:
            self.open_notepad_and_type()

    def sit_on_active_window(self):
        try:
            active = gw.getActiveWindow()
            if active and active.title and active.title != "":
                self.move(active.left + 50, active.top - self.height() + 20)
                self.is_sitting = True
                self.setPixmap(self.img_crouch)
                self.show_bubble("> RESTING ON NODE")
        except:
            pass

    def open_notepad_and_type(self):
        self.is_typing = True
        self.is_sitting = False
        self.setPixmap(self.img_action)
        self.show_bubble("> INITIATING TEXT PROTOCOL")

        def typing_task():
            try:
                messages = [
                    "Who's a good boy?",
                    "SUFE FROM THE SHOW.",
                    "I am inside your system now.",
                    "01001000 01101001",
                    "Wake up, Samurai. We have a city to burn."
                ]
                msg = random.choice(messages)
                
                self.app.clipboard().setText(msg)
                
                subprocess.Popen(['notepad.exe'])
                time.sleep(1.2)
                pyautogui.write(msg, interval=0.08)
                time.sleep(0.3)
                pyautogui.press('enter')
            except:
                pass
            
            self.is_typing = False
            self.reset_image()

        threading.Thread(target=typing_task, daemon=True).start()

    def glitch_effect(self):
        if self.is_dragging or self.is_grabbing_cursor or self.is_sitting or self.is_typing:
            return
        if random.random() < 0.3: 
            glitch_pic = random.choice([self.img_stand, self.img_crouch, self.img_face])
            self.setPixmap(self.flip_pixmap(glitch_pic))
            QTimer.singleShot(150, self.reset_image)

    def reset_image(self):
        if not self.is_dragging and not self.is_sitting and not self.is_typing:
            if self.is_chasing or self.is_grabbing_cursor:
                self.setPixmap(self.flip_pixmap(self.img_action))
            else:
                self.setPixmap(self.flip_pixmap(self.img_stand))

    def flip_pixmap(self, pixmap):
        if self.direction == -1:
            return pixmap.transformed(QTransform().scale(-1, 1))
        return pixmap

    def grab_cursor(self):
        self.is_grabbing_cursor = True
        self.is_chasing = False
        self.show_bubble("WHO'S A GOOD BOY?")
        self.setPixmap(self.img_face)
        QTimer.singleShot(2000, self.release_cursor)

    def release_cursor(self):
        self.is_grabbing_cursor = False
        self.reset_image()

    def trigger_back_off(self):
        self.show_bubble("BACK OFF.")
        self.setPixmap(self.img_face)
        self.is_sitting = False
        
        try:
            screen = QApplication.primaryScreen().availableGeometry()
            pyautogui.moveTo(random.randint(100, screen.width() - 100), random.randint(100, screen.height() - 100), duration=0.1)
            
            active_windows = gw.getActiveWindow()
            if active_windows:
                active_windows.moveTo(random.randint(0, screen.width() - 400), random.randint(0, screen.height() - 400))
        except:
            pass

        QTimer.singleShot(1500, self.reset_image)

    def update_physics(self):
        if self.is_dragging or self.is_typing or self.is_sitting:
            return

        screen = QApplication.primaryScreen().availableGeometry()
        mouse_pos = QCursor.pos()
        
        if self.is_grabbing_cursor:
            pyautogui.moveTo(self.x() + (self.width() // 2) + (self.speed * 10 * self.direction), self.y() + (self.height() // 2), duration=0)
            new_x = self.x() + (self.speed * self.direction)
            if new_x <= 0 or new_x >= screen.width() - self.width():
                self.direction *= -1
            self.move(new_x, self.y())
            return

        distance_to_mouse = (mouse_pos.x() - self.x())**2 + (mouse_pos.y() - self.y())**2
        if distance_to_mouse < 40000 and not self.is_falling:
            self.is_chasing = True
        elif distance_to_mouse > 80000:
            self.is_chasing = False

        if self.is_chasing and distance_to_mouse < 5000:
            self.grab_cursor()
            return

        if self.y() < screen.height() - self.height() - 40: 
            self.is_falling = True
            self.fall_speed += 0.5 
            self.move(self.x(), self.y() + int(self.fall_speed))
            self.setPixmap(self.img_crouch)
        else:
            if self.is_falling:
                self.is_falling = False
                self.fall_speed = 0
                self.reset_image()
            self.move(self.x(), screen.height() - self.height() - 40)

        if not self.is_falling:
            if self.is_chasing:
                self.speed = 4
                self.direction = 1 if mouse_pos.x() > self.x() else -1
                self.setPixmap(self.flip_pixmap(self.img_action))
            else:
                self.speed = 2 
                self.setPixmap(self.flip_pixmap(self.img_stand))

            new_x = self.x() + (self.speed * self.direction)
            if new_x <= 0:
                self.direction = 1
                new_x = 0
            elif new_x >= screen.width() - self.width():
                self.direction = -1
                new_x = screen.width() - self.width()

            self.move(new_x, self.y())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.is_sitting:
                self.is_sitting = False
                self.reset_image()

            current_time = time.time()
            self.tap_times = [t for t in self.tap_times if current_time - t < 1.5]
            self.tap_times.append(current_time)

            if len(self.tap_times) >= 3:
                self.tap_times = [] 
                self.trigger_back_off()
                return 

            if self.is_grabbing_cursor:
                self.release_cursor()
            
            self.is_dragging = True
            self.is_chasing = False
            self.chat_bubble.hide()
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.setPixmap(self.img_crouch) 
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.drag_position = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    pet = DesktopPet(app)
    pet.move(100, 100) 
    pet.show()

    tray_icon = QSystemTrayIcon(QIcon("face.png"), app)
    tray_icon.setToolTip("Capri Cyberpunk")
    menu = QMenu()
    quit_action = QAction("Quit", app)
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)
    tray_icon.setContextMenu(menu)
    tray_icon.show()

    sys.exit(app.exec_())