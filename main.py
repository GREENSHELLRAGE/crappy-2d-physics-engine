# python3 main.py
import pygame
import math

# Screen parameters
screen_x = 1080
screen_y = 1080
fps = 120
fps_clock = pygame.time.Clock()

# Size of 1 unit in pixels
unit_size = 27

# Settings
draw_hitboxes = True
draw_velocity = True
draw_forces = True

# Text parameters
text_size = 20
text_font = "freesansbold.ttf"
text_color = pygame.Color(255, 255, 255)

# Set up the drawing window
pygame.init()
screen = pygame.display.set_mode([screen_x, screen_y])
text_font = pygame.font.Font(text_font, text_size)

# Physics parameters
coefficient_of_restitution = 0.5
# Gravity values
earth = -9.81
moon = -1.6
sun = -275


# Class for vectors
class Vector:
    x = 0
    y = 0
    magnitude = 0
    angle = 0
    
    def __init__(self, value1, value2, format='xy'):
        if format == 'xy':
            self.x = value1
            self.y = value2
            self.angle = math.atan2(value2, value1)
            self.magnitude = math.sqrt(value1 ** 2 + value2 ** 2)
        elif format == 'ma':
            self.magnitude = value1
            self.angle = value2
            self.x = value1 * math.cos(value2)
            self.y = value1 * math.sin(value2)

    def setX(self, new_x):
        self.x = new_x
        self.angle = math.atan2(self.y, new_x)
        self.magnitude = math.sqrt(new_x ** 2 + self.y ** 2)

    def setY(self, new_y):
        self.y = new_y
        self.angle = math.atan2(new_y, self.x)
        self.magnitude = math.sqrt(self.x ** 2 + new_y ** 2)

    def setMagnitude(self, new_magnitude):
        self.magnitude = new_magnitude
        self.x = new_magnitude * math.cos(self.angle)
        self.y = new_magnitude * math.sin(self.angle)

    def setAngle(self, new_angle):
        self.angle = new_angle
        self.x = self.magnitude * math.cos(new_angle)
        self.y = self.magnitude * math.sin(new_angle)

    def __str__(self) -> str:
        return "(" + str(self.x) + ", " + str(self.y) + ")"
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)


# Function to add vectors
def add_vectors(vectors):
    new_x = 0
    new_y = 0
    for v in vectors:
        new_x += v.x
        new_y += v.y
    return Vector(new_x, new_y, 'xy')

# Game object class
class GameObject:
    # Position
    position = Vector
    # Size
    size = Vector
    # Velocity
    velocity = Vector
    # Rotation
    rotation = 0 # Radians
    # Mass
    mass = 0 # Kilograms
    # Forces currently acting on object
    forces = [] # list of Vectors
    # Hit box rect for collision
    hit_box = pygame.Rect

    selected = False

    # Constructor
    def __init__(self, position, size, velocity, rotation, mass):
        self.position = position
        self.size = size
        self.rotation = rotation
        self.velocity = velocity
        self.mass = mass

        # Calculate rotated points of object
        center_dist = math.sqrt((self.size.x / 2) ** 2 + (self.size.y / 2) ** 2)
        p1_angle = math.atan2(self.size.y / 2, self.size.x / 2) + self.rotation
        x1 = self.position.x + center_dist * math.cos(p1_angle)
        y1 = self.position.y + center_dist * math.sin(p1_angle)
        
        p2_angle = math.atan2(self.size.y / 2, -self.size.x / 2) + self.rotation
        x2 = self.position.x + center_dist * math.cos(p2_angle)
        y2 = self.position.y + center_dist * math.sin(p2_angle)

        p3_angle = math.atan2(-self.size.y / 2, -self.size.x / 2) + self.rotation
        x3 = self.position.x + center_dist * math.cos(p3_angle)
        y3 = self.position.y + center_dist * math.sin(p3_angle)
        
        p4_angle = math.atan2(-self.size.y / 2, self.size.x / 2) + self.rotation
        x4 = self.position.x + center_dist * math.cos(p4_angle)
        y4 = self.position.y + center_dist * math.sin(p4_angle)

        # Draw object and get hit box
        self.hit_box = pygame.draw.polygon(screen, (0, 0, 0), ((x1 * unit_size, screen_y - y1 * unit_size), (x2 * unit_size, screen_y - y2 * unit_size), (x3 * unit_size, screen_y - y3 * unit_size), (x4 * unit_size, screen_y - y4 * unit_size)))
    
    # Method to add a force
    def addForce(self, force):
        self.forces = self.forces.copy()
        self.forces.append(force)

    # Draw function
    def drawObject(self, surface, color):
        # Calculate net force
        net_force = add_vectors(self.forces)
        # Calculate acceleration
        acceleration = Vector(net_force.x / self.mass, net_force.y / self.mass)

        bounce_threshold = 0.5

        # ----- HANDLE COLLISION -----
        if self.position.x * unit_size < self.hit_box.height / 2 or self.position.x * unit_size > screen_x - self.hit_box.height / 2 or self.position.y * unit_size > screen_y - self.hit_box.height / 2 or self.position.y * unit_size < self.hit_box.height / 2:
            # Collision for left side of screen
            if self.position.x * unit_size < self.hit_box.height / 2:
                if not -bounce_threshold < self.velocity.x < bounce_threshold:
                    print("hit left wall at " + str(self.velocity.x) + "m/s")
                    # Set velocity to -velocity * coefficient of restitution
                    self.velocity.setX(-self.velocity.x * coefficient_of_restitution + acceleration.x / fps)
                    # Move just barely away from the wall if bouncing at a high enough velocity
                    self.position.setX(self.hit_box.height / 2 / unit_size + self.velocity.x / fps)
                else:
                    # Round velocity to 0
                    self.velocity.x = 0
                    
                    if net_force.x > 0:
                        # Move 1 pixel away from the wall if being pulled away from wall
                        self.position.setX(self.hit_box.height / 2 / unit_size + 1 / unit_size)
                    else:
                        # Move 1 pixel into the wall if not being pulled away from wall
                        self.position.setX(self.hit_box.height / 2 / unit_size - 1 / unit_size)

                # Calculate y velocity
                self.velocity.setY(self.velocity.y + acceleration.y / fps)
                # Calculate y position
                self.position.setY(self.position.y + self.velocity.y / fps)
            
            
            # Collision for right side of screen
            if self.position.x * unit_size > screen_x - self.hit_box.height / 2:
                if not -bounce_threshold < self.velocity.x < bounce_threshold:
                    print("hit right wall at " + str(self.velocity.x) + "m/s")
                    # Set velocity to -velocity * coefficient of restitution
                    self.velocity.setX(-self.velocity.x * coefficient_of_restitution + acceleration.x / fps)
                    # Move just barely away from the wall if bouncing at a high enough velocity
                    self.position.setX(screen_x / unit_size - self.hit_box.height / 2 / unit_size + self.velocity.x / fps)
                else:
                    # Round velocity to 0
                    self.velocity.x = 0
                    
                    if net_force.x > 0:
                        # Move 1 pixel away from the wall if being pulled away from wall
                        self.position.setX(screen_x / unit_size - self.hit_box.height / 2 / unit_size + 1 / unit_size)
                    else:
                        # Move 1 pixel into the wall if not being pulled away from wall
                        self.position.setX(screen_x / unit_size - self.hit_box.height / 2 / unit_size - 1 / unit_size)

                # Calculate y velocity
                self.velocity.setY(self.velocity.y + acceleration.y / fps)
                # Calculate y position
                self.position.setY(self.position.y + self.velocity.y / fps)
            
            
            # Collision for top of screen
            if self.position.y * unit_size > screen_y - self.hit_box.height / 2:
                if not -bounce_threshold < self.velocity.y < bounce_threshold:
                    print("hit top wall at " + str(self.velocity.y) + "m/s")
                    # Set velocity to -velocity * coefficient of restitution
                    self.velocity.setY(-self.velocity.y * coefficient_of_restitution + acceleration.y / fps)
                    # Move just barely away from the wall if bouncing at a high enough velocity
                    self.position.setY(screen_y / unit_size - self.hit_box.height / 2 / unit_size + self.velocity.y / fps)
                else:
                    # Round velocity to 0
                    self.velocity.y = 0
                    
                    if net_force.y > 0:
                        # Move 1 pixel away from the wall if being pulled away from wall
                        self.position.setY(screen_y / unit_size - self.hit_box.height / 2 / unit_size + 1 / unit_size)
                    else:
                        # Move 1 pixel into the wall if not being pulled away from wall
                        self.position.setY(screen_y / unit_size - self.hit_box.height / 2 / unit_size - 1 / unit_size)

                # Calculate x velocity
                self.velocity.setX(self.velocity.x + acceleration.x / fps)
                # Calculate x position
                self.position.setX(self.position.x + self.velocity.x / fps)
    
            
            # Collision for bottom of screen
            if self.position.y * unit_size < self.hit_box.height / 2:
                if not -bounce_threshold < self.velocity.y < bounce_threshold:
                    print("hit bottom wall at " + str(self.velocity.y) + "m/s")
                    # Set velocity to -velocity * coefficient of restitution
                    self.velocity.setY(-self.velocity.y * coefficient_of_restitution + acceleration.y / fps)
                    # Move just barely away from the wall if bouncing at a high enough velocity
                    self.position.setY(self.hit_box.height / 2 / unit_size + self.velocity.y / fps)
                else:
                    # Round velocity to 0
                    self.velocity.y = 0
                    
                    if net_force.y > 0:
                        # Move 1 pixel away from the wall if being pulled away from wall
                        self.position.setY(self.hit_box.height / 2 / unit_size + 1 / unit_size)
                    else:
                        # Move 1 pixel into the wall if not being pulled away from wall
                        self.position.setY(self.hit_box.height / 2 / unit_size - 1 / unit_size)

                # Calculate x velocity
                self.velocity.setX(self.velocity.x + acceleration.x / fps)
                # Calculate x position
                self.position.setX(self.position.x + self.velocity.x / fps)
  
        # No collision
        else:
            # Add acceleration to velocity
            self.velocity.setX(self.velocity.x + acceleration.x / fps)
            self.velocity.setY(self.velocity.y + acceleration.y / fps)
            # Add velocity to position
            self.position = add_vectors((self.position, Vector(self.velocity.x / fps, self.velocity.y / fps)))
        
        # ----- DRAW OBJECT -----
        
        # Calculate rotated points of object
        center_dist = math.sqrt((self.size.x / 2) ** 2 + (self.size.y / 2) ** 2)
        p1_angle = math.atan2(self.size.y / 2, self.size.x / 2) + self.rotation
        x1 = self.position.x + center_dist * math.cos(p1_angle)
        y1 = self.position.y + center_dist * math.sin(p1_angle)
        
        p2_angle = math.atan2(self.size.y / 2, -self.size.x / 2) + self.rotation
        x2 = self.position.x + center_dist * math.cos(p2_angle)
        y2 = self.position.y + center_dist * math.sin(p2_angle)

        p3_angle = math.atan2(-self.size.y / 2, -self.size.x / 2) + self.rotation
        x3 = self.position.x + center_dist * math.cos(p3_angle)
        y3 = self.position.y + center_dist * math.sin(p3_angle)
        
        p4_angle = math.atan2(-self.size.y / 2, self.size.x / 2) + self.rotation
        x4 = self.position.x + center_dist * math.cos(p4_angle)
        y4 = self.position.y + center_dist * math.sin(p4_angle)

        # Draw object and get hit box
        self.hit_box = pygame.draw.polygon(surface, color, ((x1 * unit_size, screen_y - y1 * unit_size), (x2 * unit_size, screen_y - y2 * unit_size), (x3 * unit_size, screen_y - y3 * unit_size), (x4 * unit_size, screen_y - y4 * unit_size)))

        # Draw hitbox
        if draw_hitboxes:
            pygame.draw.rect(surface, (255, 0, 0), self.hit_box, width=1)

        # Draw velocity and acceleration
        if draw_velocity:
            # Draw velocity
            text_render = text_font.render("x=" + str(self.position.x) + " y=" + str(self.position.y), True, (255, 0, 0), (0, 0, 0))
            text_rect = text_render.get_rect().center = (self.position.x * unit_size, screen_y - self.position.y * unit_size)
            surface.blit(text_render, text_rect)
            # Draw velocity
            text_render = text_font.render("Vx=" + str(self.velocity.x) + " Vy=" + str(self.velocity.y), True, (255, 0, 0), (0, 0, 0))
            text_rect = text_render.get_rect().center = (self.position.x * unit_size, screen_y - self.position.y * unit_size + text_size)
            surface.blit(text_render, text_rect)
            # Draw acceleration
            text_render = text_font.render("Ax=" + str(acceleration.x) + " Ay=" + str(acceleration.y), True, (255, 0, 0), (0, 0, 0))
            text_rect = text_render.get_rect().center = (self.position.x * unit_size, screen_y - self.position.y * unit_size + text_size * 2)
            surface.blit(text_render, text_rect)

        # Draw forces
        if draw_forces:
            # Draw line and label for each force
            for force in self.forces:
                pygame.draw.line(surface, (255, 0, 0), (self.position.x * unit_size, screen_y - self.position.y * unit_size), (self.position.x * unit_size + Vector(unit_size * force.magnitude, force.angle, 'ma').x, screen_y - self.position.y * unit_size - Vector(unit_size * force.magnitude, force.angle, 'ma').y), width=2)
                text_render = text_font.render("F=" + str(force.magnitude) + "N", True, (255, 0, 0), (0, 0, 0))
                text_rect = text_render.get_rect().center = (self.position.x * unit_size + Vector(unit_size * force.magnitude, force.angle, 'ma').x, screen_y - self.position.y * unit_size - Vector(unit_size * force.magnitude, force.angle, 'ma').y)
                surface.blit(text_render, text_rect)

            # Draw line and label for net force
            pygame.draw.line(surface, (0, 255, 255), (self.position.x * unit_size, screen_y - self.position.y * unit_size), (self.position.x * unit_size + Vector(unit_size * net_force.magnitude, net_force.angle, 'ma').x, screen_y - self.position.y * unit_size - Vector(unit_size * net_force.magnitude, net_force.angle, 'ma').y), width=2)
            text_render = text_font.render("Fnet=" + str(net_force.magnitude) + "N", True, (0, 255, 255), (0, 0, 0))
            text_rect = text_render.get_rect().center = (self.position.x * unit_size + Vector(unit_size * net_force.magnitude, net_force.angle, 'ma').x, screen_y - self.position.y * unit_size - Vector(unit_size * net_force.magnitude, net_force.angle, 'ma').y)
            surface.blit(text_render, text_rect)


# Gravity vector
gravity = Vector(0, earth, 'xy')

# Test objects
test_objects = [
    GameObject(Vector(3, 6), Vector(1, 1), Vector(0, 0), 0, 1),
    GameObject(Vector(7, 7), Vector(2, 2), Vector(0, 0), 0, 2),
    GameObject(Vector(11, 7.5), Vector(3, 3), Vector(0, 0), 0, 3),
    #GameObject(Vector(20, 9), Vector(5, 5), Vector(0, 0), 0, 0.1),
]

# Run until the user asks to quit
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Draw background
    screen.fill((255, 255, 255))

    # Draw grid of units
    for x in range(int(screen_x / unit_size)):
        pygame.draw.line(screen, (0, 0, 0), (unit_size * x, 0), (unit_size * x, screen_y))
    for y in range(int(screen_y / unit_size)):
        pygame.draw.line(screen, (0, 0, 0), (0, unit_size * y), (screen_x, unit_size * y))

    # Clear forces
    for body in test_objects:
        # Reset forces on object
        body.forces.clear()

        # Apply gravity to objects
        body_gravity = Vector(gravity.x * body.mass, gravity.y * body.mass, 'xy')
        body.addForce(body_gravity)

        # Measure distance to mouse
        pressed = pygame.key.get_pressed()
        mouse_distance = Vector(pygame.mouse.get_pos()[0] - body.hit_box.centerx, pygame.mouse.get_pos()[1] - body.hit_box.centery)

        # Apply force with mouse
        if mouse_distance.magnitude < body.hit_box.width / 2:
            body.selected = True
            body.drawObject(screen, (50, 177, 255))
        elif body.selected and pygame.mouse.get_pressed()[0]:
            mouse_unit_x = pygame.mouse.get_pos()[0] / unit_size
            mouse_unit_y = screen_y / unit_size - pygame.mouse.get_pos()[1] / unit_size
            mouse_force = Vector(mouse_unit_x - body.position.x, mouse_unit_y - body.position.y, 'xy')
            body.addForce(mouse_force)
            body.rotation = mouse_force.angle + math.pi / 2
            body.drawObject(screen, (50, 225, 255))
        else:
            body.selected = False
            body.rotation = 0
            body.drawObject(screen, (0, 127, 255))

    # Flip the display
    pygame.display.flip()

    fps_clock.tick(fps)

# Done! Time to quit.
pygame.quit()