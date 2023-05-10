from sshkeyboard import listen_keyboard
from motor_driver import AStar

shield = AStar()
speed = 0
steering = 0

delta_speed = 80
max_speed = 260
max_steering = 800

def drive_wasd(key):
    global shield, speed, steering

    print(f"Have pressed: {key}| speed: {-speed} | steering: {steering}")
    if key == 'w':
        speed = min(max((speed - delta_speed), -max_speed), max_speed)
    elif key == 'a':
        steering = max_steering
    elif key == 'd':
        steering = -max_steering
    elif key == 's':
        speed = max(min((speed + delta_speed), max_speed), -max_speed)
    else:
        speed = 0
        steering = 0

    shield.motors(speed, steering)

listen_keyboard(on_press=drive_wasd)

while 1:
    speed = 0
    steering = 0
