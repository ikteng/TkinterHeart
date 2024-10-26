import random
from math import sin, cos, pi, log
from tkinter import *

# Constants
CANVAS_WIDTH = 640
CANVAS_HEIGHT = 480
CANVAS_CENTER_X = CANVAS_WIDTH / 2
CANVAS_CENTER_Y = CANVAS_HEIGHT / 2
IMAGE_ENLARGE = 11
HEART_COLOR = '#ff2121'

def heart_function(t, shrink_ratio=IMAGE_ENLARGE):
    """Calculate heart shape coordinates."""
    x = 16 * (sin(t) ** 3)
    y = -(13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))

    # Scale and center the heart shape
    return int(x * shrink_ratio + CANVAS_CENTER_X), int(y * shrink_ratio + CANVAS_CENTER_Y)

def scatter_inside(x, y, beta=0.15):
    """Generate random scatter within a certain range."""
    ratio_x = -beta * log(random.random())
    ratio_y = -beta * log(random.random())

    return x - ratio_x * (x - CANVAS_CENTER_X), y - ratio_y * (y - CANVAS_CENTER_Y)

def shrink(x, y, ratio):
    """Shrink the position towards the center based on a force."""
    distance_squared = (x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2
    if distance_squared == 0:  # Avoid division by zero
        return x, y
    force = -1 / (distance_squared ** 1.6)
    
    dx = ratio * force * (x - CANVAS_CENTER_X)
    dy = ratio * force * (y - CANVAS_CENTER_Y)

    return x - dx, y - dy

def curve(p):
    """Return a curve value based on the input parameter."""
    return 2 * (2 * sin(3 * p)) / (2 * pi)

class Heart:
    def __init__(self, generate_frame=20):
        """Initialize the heart with random points."""
        self._points = set()
        self._edge_diffusion_points = set()
        self._center_diffusion_points = set()
        self.all_points = {}
        self.build(3000)  # Increased number of points
        self.random_halo = 1000
        self.generate_frame = generate_frame

        for frame in range(generate_frame):
            self.calc(frame)

    def build(self, number):
        """Build the heart shape points and diffusion points."""
        for _ in range(number):
            t = random.uniform(0, 2 * pi)
            x, y = heart_function(t)
            self._points.add((x, y))

        # Create edge diffusion points
        for _x, _y in self._points:
            for _ in range(3):
                x, y = scatter_inside(_x, _y, 0.05)
                self._edge_diffusion_points.add((x, y))

        # Create center diffusion points
        point_list = list(self._points)
        for _ in range(10000):
            x, y = random.choice(point_list)
            x, y = scatter_inside(x, y, 0.17)
            self._center_diffusion_points.add((x, y))

    @staticmethod
    def calc_position(x, y, ratio):
        """Calculate the position based on force and return adjusted coordinates."""
        distance_squared = (x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2
        if distance_squared == 0:  # Avoid division by zero
            return x, y
        force = 1 / (distance_squared ** 0.520)

        dx = ratio * force * (x - CANVAS_CENTER_X) * 0.5
        dy = ratio * force * (y - CANVAS_CENTER_Y) * 0.5

        return x - dx, y - dy

    def calc(self, generate_frame):
        """Calculate the points for each frame based on a sine curve."""
        ratio = 10 * curve(generate_frame / 10 * pi)  # Adjusted ratio for smoother movement
        halo_radius = int(4 + 6 * (1 + curve(generate_frame / 10 * pi)))
        halo_number = int(3000 + 4000 * abs(curve(generate_frame / 10 * pi) ** 2))

        all_points = []
        heart_halo_points = set()

        # Create halo points around the heart
        for _ in range(halo_number):
            t = random.uniform(0, 2 * pi)
            x, y = heart_function(t, shrink_ratio=11.6)
            x, y = shrink(x, y, halo_radius)

            if (x, y) not in heart_halo_points:
                heart_halo_points.add((x, y))
                x += random.randint(-6, 6)  # Reduced randomness for smoother halo
                y += random.randint(-6, 6)
                size = random.choice((1, 2))  # Reduced size variability
                all_points.append((x, y, size))

        # Adjust existing heart points
        for x, y in self._points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)  # Reduced size variability
            all_points.append((x, y, size))

        # Adjust center diffusion points
        for x, y in self._center_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)  # Reduced size variability
            all_points.append((x, y, size))

        self.all_points[generate_frame] = all_points

    def render(self, render_canvas, render_frame):
        """Render the heart shape and its points on the canvas."""
        for x, y, size in self.all_points[render_frame % self.generate_frame]:
            render_canvas.create_rectangle(x, y, x + size, y + size, width=0, fill=HEART_COLOR)

def draw(main: Tk, render_canvas: Canvas, render_heart: Heart, render_frame=0):
    """Draw function to update the canvas."""
    render_canvas.delete('all')
    render_heart.render(render_canvas, render_frame)
    main.after(50, draw, main, render_canvas, render_heart, render_frame + 1)  # Keep the smoother transition

if __name__ == '__main__':
    root = Tk()
    canvas = Canvas(root, bg='black', height=CANVAS_HEIGHT, width=CANVAS_WIDTH)
    canvas.pack()
    heart = Heart()
    draw(root, canvas, heart)
    root.mainloop()
