from opensimplex import OpenSimplex
from perlin_noise import PerlinNoise

from timer_decorator import timer_dec
import random

print("Script to compare performance of Perlin and Simplex Noise")
noise = PerlinNoise(octaves=1)
@timer_dec
def test_perlin_noise(): 
	for i in range(50000): #50K 6.139 Seconds
		noise([random.uniform(0.0, 128.0), random.uniform(0.0, 128.0)])
test_perlin_noise()

noise = OpenSimplex().noise2d
@timer_dec
def test_os_noise():
	for i in range(50000): #50K .181 ms
		noise(random.uniform(0.0, 128.0), random.uniform(0.0, 128.0))
test_os_noise()