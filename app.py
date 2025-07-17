from flask import Flask, render_template, Response
import cv2
import pygame
import numpy as np

app = Flask(__name__)

# Initialize pygame
pygame.init()
screen = pygame.Surface((500, 700))  # same as your game screen size

# Replace this with your own game loop logic
def generate_frames():
    clock = pygame.time.Clock()
    while True:
        # Run your game frame update and draw here
        screen.fill((0, 0, 0))  # draw your game

        # Convert pygame surface to image
        frame = pygame.surfarray.array3d(screen)
        frame = np.rot90(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Encode image as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
        clock.tick(30)  # FPS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
