
fake_lights = True # Turn this on for testing without the real lights fixture
num_lights = 0

if fake_lights:
    lights = []

def set_num_lights(num):
    global num_lights, lights

    num_lights = num

    if fake_lights:
        lights = [0] * num_lights

def set_light(index, rgb):
    global num_lights, lights
    if index > num_lights or index <= 0:
        return None

    if fake_lights:
        lights[index-1] = rgb
        print_lights()

def clear_all():
    global num_lights, lights

    if fake_lights:
        lights = [0] * num_lights

def print_lights():
    global num_lights, lights
    seen_values = []

    for i in range(0, num_lights):
        if lights[i] == 0 or lights[i] in seen_values:
            continue
        print("Light(s) "+str(i+1), end='')
        for j in range(i+1, num_lights):
            if lights[j] == lights[i]:
                print(", "+str(j+1), end='')
        print(" have color " + str(lights[i]))
        seen_values.append(lights[i])
