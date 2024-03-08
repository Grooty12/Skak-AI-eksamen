import random
import matplotlib.pyplot as plt
def generate_points(n):
    points = []
    for i in range(n):
        x = random.random()
        y = random.random()
        if x + y > 1:
            color = 'red'
        else:
            color = 'blue'
        points.append((x,y,color))
    return points
points = generate_points(10)
print(points)

def plot_points(points):
    for point in points:
        x = point[0]
        y = point[1]
        color = point[2]
        plt.plot(x,y,'o',color=color)
    plt.show()