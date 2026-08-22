import sdl2
import ctypes

class Platform:
    def __init__(self, title, windowWidth, windowHeight, textureWidth, textureHeight):
        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)

        self.window = sdl2.SDL_CreateWindow(title.encode("utf-8"), sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED, windowWidth, windowHeight, sdl2.SDL_WINDOW_SHOWN)

        self.renderer = sdl2.SDL_CreateRenderer(self.window, -1, sdl2.SDL_RENDERER_ACCELERATED)

        self.texture = sdl2.SDL_CreateTexture(self.renderer, sdl2.SDL_PIXELFORMAT_RGBA8888, sdl2.SDL_TEXTUREACCESS_STREAMING, textureWidth, textureHeight)

        self.keymap = {
            sdl2.SDLK_x: 0,
            sdl2.SDLK_1: 1,
            sdl2.SDLK_2: 2,
            sdl2.SDLK_3: 3,

            sdl2.SDLK_q: 4,
            sdl2.SDLK_w: 5,
            sdl2.SDLK_e: 6,
            sdl2.SDLK_a: 7,

            sdl2.SDLK_s: 8,
            sdl2.SDLK_d: 9,
            sdl2.SDLK_z: 0xA,
            sdl2.SDLK_c: 0xB,

            sdl2.SDLK_4: 0xC,
            sdl2.SDLK_r: 0xD,
            sdl2.SDLK_f: 0xE,
            sdl2.SDLK_v: 0xF,
        }

    def __del__(self):
        self.close()

    def close(self):
        if self.texture:
            sdl2.SDL_DestroyTexture(self.texture)
            self.texture = None

        if self.renderer:
            sdl2.SDL_DestroyRenderer(self.renderer)
            self.renderer = None

        if self.window:
            sdl2.SDL_DestroyWindow(self.window)
            self.window = None

        sdl2.SDL_Quit()

    def update(self, buffer, pitch):
        sdl2.SDL_UpdateTexture(self.texture, None, buffer.ctypes.data_as(ctypes.c_void_p), pitch)
        sdl2.SDL_RenderClear(self.renderer)
        sdl2.SDL_RenderCopy(self.renderer, self.texture, None, None)
        sdl2.SDL_RenderPresent(self.renderer)

    def process_input(self, keys):
        quit = False
        event = sdl2.SDL_Event()

        while sdl2.SDL_PollEvent(event):

            if event.type == sdl2.SDL_QUIT:
                quit = True

            elif event.type == sdl2.SDL_KEYDOWN:
                key = event.key.keysym.sym

                if key == sdl2.SDLK_ESCAPE:
                    quit = True
                else:
                    chip8_key = self.keymap.get(key)

                    if chip8_key is not None:
                        keys[chip8_key] = 1

            elif event.type == sdl2.SDL_KEYUP:
                key = event.key.keysym.sym

                chip8_key = self.keymap.get(key)

                if chip8_key is not None:
                    keys[chip8_key] = 0

        return quit