import numpy as np
import random
import time

START_ADDRESS = 0x200

FONTSET_SIZE = 80
FONTSET_START_ADDRESS = 0x50

VIDEO_WIDTH = 64
VIDEO_HEIGHT = 32

fontset = np.array([
    0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
    0x20, 0x60, 0x20, 0x20, 0x70,  # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
    0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
    0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
    0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
    0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
    0xF0, 0x80, 0xF0, 0x80, 0x80   # F
], dtype=np.uint8)

class Chip8:
    def __init__(self):
        self.registers = np.zeros(16, dtype=np.uint8)
        self.memory = np.zeros(4096, dtype=np.uint8)
        self.index = 0
        self.pc = START_ADDRESS
        self.stack = np.zeros(16, dtype=np.uint16)
        self.sp = 0
        self.delay_timer = 0
        self.sound_timer = 0
        self.keypad = np.zeros(16, dtype=np.uint8)
        self.video = np.zeros(VIDEO_WIDTH * VIDEO_HEIGHT, dtype=np.uint32)
        self.opcode = np.uint16(0)

        for i in range(FONTSET_SIZE):
            self.memory[FONTSET_START_ADDRESS + i] = fontset[i]

        self.rand_gen = random.Random(time.time_ns())

        # Main opcode table
        self.table = [self.OP_NULL] * 16

        self.table[0x0] = self.Table0
        self.table[0x1] = self.OP_1nnn
        self.table[0x2] = self.OP_2nnn
        self.table[0x3] = self.OP_3xkk
        self.table[0x4] = self.OP_4xkk
        self.table[0x5] = self.OP_5xy0
        self.table[0x6] = self.OP_6xkk
        self.table[0x7] = self.OP_7xkk
        self.table[0x8] = self.Table8
        self.table[0x9] = self.OP_9xy0
        self.table[0xA] = self.OP_Annn
        self.table[0xB] = self.OP_Bnnn
        self.table[0xC] = self.OP_Cxkk
        self.table[0xD] = self.OP_Dxyn
        self.table[0xE] = self.TableE
        self.table[0xF] = self.TableF

        # 0xxx table
        self.table0 = [self.OP_NULL] * 16

        self.table0[0x0] = self.OP_00E0
        self.table0[0xE] = self.OP_00EE

        # 8xy? table
        self.table8 = [self.OP_NULL] * 16

        self.table8[0x0] = self.OP_8xy0
        self.table8[0x1] = self.OP_8xy1
        self.table8[0x2] = self.OP_8xy2
        self.table8[0x3] = self.OP_8xy3
        self.table8[0x4] = self.OP_8xy4
        self.table8[0x5] = self.OP_8xy5
        self.table8[0x6] = self.OP_8xy6
        self.table8[0x7] = self.OP_8xy7
        self.table8[0xE] = self.OP_8xyE

        # Ex?? table
        self.tableE = [self.OP_NULL] * 16

        self.tableE[0x1] = self.OP_ExA1
        self.tableE[0xE] = self.OP_Ex9E

        # Fx?? table
        self.tableF = [self.OP_NULL] * 256

        self.tableF[0x07] = self.OP_Fx07
        self.tableF[0x0A] = self.OP_Fx0A
        self.tableF[0x15] = self.OP_Fx15
        self.tableF[0x18] = self.OP_Fx18
        self.tableF[0x1E] = self.OP_Fx1E
        self.tableF[0x29] = self.OP_Fx29
        self.tableF[0x33] = self.OP_Fx33
        self.tableF[0x55] = self.OP_Fx55
        self.tableF[0x65] = self.OP_Fx65

    def Table0(self):
        self.table0[self.opcode & 0x000F]()

    def Table8(self):
        self.table8[self.opcode & 0x000F]()

    def TableE(self):
        self.tableE[self.opcode & 0x000F]()

    def TableF(self):
        self.tableF[self.opcode & 0x00FF]()

    def OP_NULL(self):
        pass

    def cycle(self):
        self.opcode = (int(self.memory[self.pc]) << 8 | int(self.memory[self.pc + 1]))

        self.pc += 2

        self.table[(self.opcode & 0xF000) >> 12]()

    def loadROM(self, filename):
        with open(filename, "rb") as f:
            rom_data = np.frombuffer(f.read(), dtype=np.uint8)

        self.memory[START_ADDRESS:START_ADDRESS + len(rom_data)] = rom_data

    def get_random_byte(self):
        return self.rand_gen.randint(0, 255)

    # Opcodes
    def OP_00E0(self):
        self.video[:] = 0

    def OP_00EE(self):
        self.sp -= 1
        self.pc = self.stack[self.sp]

    def OP_1nnn(self):
        address = self.opcode & 0x0FFF

        self.pc = address

    def OP_2nnn(self):
        address = self.opcode & 0x0FFF

        self.stack[self.sp] = self.pc
        self.sp += 1
        self.pc = address

    def OP_3xkk(self):
        Vx = (self.opcode & 0x0F00) >> 8
        byte = self.opcode & 0x00FF

        if (self.registers[Vx] == byte):
            self.pc += 2

    def OP_4xkk(self):
        Vx = (self.opcode & 0x0F00) >> 8
        byte = self.opcode & 0x00FF

        if (self.registers[Vx] != byte):
            self.pc += 2

    def OP_5xy0(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4

        if self.registers[Vx] == self.registers[Vy]:
            self.pc += 2

    def OP_6xkk(self):
        Vx = (self.opcode & 0x0F00) >> 8
        byte = self.opcode & 0x00FF

        self.registers[Vx] = byte

    def OP_7xkk(self):
        Vx = (self.opcode & 0x0F00) >> 8
        byte = self.opcode & 0x00FF

        self.registers[Vx] = (int(self.registers[Vx]) + int(byte)) & 0xFF

    def OP_8xy0(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4

        self.registers[Vx] = self.registers[Vy]

    def OP_8xy1(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4

        self.registers[Vx] |= self.registers[Vy]

    def OP_8xy2(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4

        self.registers[Vx] &= self.registers[Vy]

    def OP_8xy3(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4

        self.registers[Vx] ^= self.registers[Vy]

    def OP_8xy4(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4

        result = int(self.registers[Vx]) + int(self.registers[Vy])

        if result > 255:
            self.registers[0xF] = 1
        else:
            self.registers[0xF] = 0

        self.registers[Vx] = result & 0xFF

    def OP_8xy5(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4

        if self.registers[Vx] > self.registers[Vy]:
            self.registers[0xF] = 1
        else:
            self.registers[0xF] = 0

        self.registers[Vx] = (int(self.registers[Vx]) - int(self.registers[Vy])) & 0xFF

    def OP_8xy6(self):
        Vx = (self.opcode & 0x0F00) >> 8

        self.registers[0xF] = (self.registers[Vx] & 0x1)

        self.registers[Vx] >>= 1

    def OP_8xy7(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4

        if self.registers[Vy] > self.registers[Vx]:
            self.registers[0xF] = 1
        else:
            self.registers[0xF] = 0

        self.registers[Vx] = (int(self.registers[Vy]) - int(self.registers[Vx])) & 0xFF

    def OP_8xyE(self):
        Vx = (self.opcode & 0x0F00) >> 8

        self.registers[0xF] = (self.registers[Vx] & 0x80) >> 7

        self.registers[Vx] <<= 1

    def OP_9xy0(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4

        if self.registers[Vx] != self.registers[Vy]:
            self.pc += 2

    def OP_Annn(self):
        address = self.opcode & 0x0FFF

        self.index = address

    def OP_Bnnn(self):
        address = self.opcode & 0x0FFF

        self.pc = self.registers[0] + address

    def OP_Cxkk(self):
        Vx = (self.opcode & 0x0F00) >> 8
        byte = self.opcode & 0x00FF

        self.registers[Vx] = self.get_random_byte() & byte

    def OP_Dxyn(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4
        height = self.opcode & 0x000F

        xPos = int(self.registers[Vx])
        yPos = int(self.registers[Vy])

        self.registers[0xF] = 0

        for row in range(height):
            spriteByte = self.memory[self.index + row]

            for col in range(8):
                if spriteByte & (0x80 >> col):

                    x = (xPos + col) % VIDEO_WIDTH
                    y = (yPos + row) % VIDEO_HEIGHT

                    pixel_index = y * VIDEO_WIDTH + x

                    if self.video[pixel_index] == 0xFFFFFFFF:
                        self.registers[0xF] = 1

                    self.video[pixel_index] ^= 0xFFFFFFFF

    def OP_Ex9E(self):
        Vx = (self.opcode & 0x0F00) >> 8

        key = self.registers[Vx]

        if self.keypad[key]:
            self.pc += 2

    def OP_ExA1(self):
        Vx = (self.opcode & 0x0F00) >> 8

        key = self.registers[Vx]

        if not self.keypad[key]:
            self.pc += 2

    def OP_Fx07(self):
        Vx = (self.opcode & 0x0F00) >> 8

        self.registers[Vx] = self.delay_timer

    def OP_Fx0A(self):
        Vx = (self.opcode & 0x0F00) >> 8

        for key in range(16):
            if self.keypad[key]:
                self.registers[Vx] = key
                return

        self.pc -= 2

    def OP_Fx15(self):
        Vx = (self.opcode & 0x0F00) >> 8

        self.delay_timer = self.registers[Vx]

    def OP_Fx18(self):
        Vx = (self.opcode & 0x0F00) >> 8
    
        self.sound_timer = self.registers[Vx]

    def OP_Fx1E(self):
        Vx = (self.opcode & 0x0F00) >> 8
    
        self.index = np.uint16(int(self.index) + int(self.registers[Vx]))

    def OP_Fx29(self):
        Vx = (self.opcode & 0x0F00) >> 8
        digit = int(self.registers[Vx])
    
        self.index = FONTSET_START_ADDRESS + (5 * digit)

    def OP_Fx33(self):
        Vx = (self.opcode & 0x0F00) >> 8
        value = int(self.registers[Vx])

        self.memory[self.index + 2] = value % 10
        value //= 10

        self.memory[self.index + 1] = value % 10
        value //= 10

        self.memory[self.index] = value % 10

    def OP_Fx55(self):
        Vx = (self.opcode & 0x0F00) >> 8
    
        for i in range(Vx + 1):
            self.memory[self.index + i] = self.registers[i]

    def OP_Fx65(self):
        Vx = (self.opcode & 0x0F00) >> 8

        for i in range(Vx + 1):
            self.registers[i] = self.memory[self.index + i]

