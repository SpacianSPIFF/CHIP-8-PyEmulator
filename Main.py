import sys
import time

from Chip8 import Chip8
from Platform_sdl import Platform

VIDEO_WIDTH = 64
VIDEO_HEIGHT = 32

def main():
    if len(sys.argv) != 4:
        print(f'Usage: {sys.argv[0]} <Scale> <Delay> <ROM>', file=sys.stderr)
        sys.exit(1)

    videoScale = int(sys.argv[1])
    cycleDelay = int(sys.argv[2])
    romFilename = sys.argv[3]

    platform = Platform("CHIP-8 Emulator", VIDEO_WIDTH * videoScale, VIDEO_HEIGHT * videoScale, VIDEO_WIDTH, VIDEO_HEIGHT)

    chip8 = Chip8()
    chip8.loadROM(romFilename)

    videoPitch = 4 * VIDEO_WIDTH

    lastCycleTime = time.perf_counter()
    lastTimerTime = time.perf_counter()

    quit = False

    while not quit:
        quit = platform.process_input(chip8.keypad)

        currentTime = time.perf_counter()

        dt = (currentTime - lastCycleTime) * 1000

        if dt > cycleDelay:
            lastCycleTime = currentTime
            chip8.cycle()
            platform.update(chip8.video, videoPitch)

        timerDt = (currentTime - lastTimerTime) * 1000

        if timerDt > (1000.0 / 60.0):
            lastTimerTime = currentTime

            if chip8.delay_timer > 0:
                chip8.delay_timer -= 1

            if chip8.sound_timer > 0:
                chip8.sound_timer -= 1

        if chip8.sound_timer > 0:
            platform.beep_start()
        else:
            platform.beep_stop()

    platform.close()

if __name__ == "__main__":
    main()
