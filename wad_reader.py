import struct
from pygame.math import Vector2 as vec2
from data_types import *


class WADReader:
    def __init__(self, wad_path):
        self.wad_file = open(wad_path, 'rb')
        self.header = self.read_header()
        self.directory = self.read_directory()

    def read_texture_map(self, offset):
        read_2_bytes = self.read_2_bytes
        read_4_bytes = self.read_4_bytes
        read_string = self.read_string

        tex_map = TextureMap()
        tex_map.name = read_string(offset + 0, num_bytes=8)
        tex_map.flags = read_4_bytes(offset + 8, byte_format='I')
        tex_map.width = read_2_bytes(offset + 12, byte_format='H')
        tex_map.height = read_2_bytes(offset + 14, byte_format='H')
        tex_map.column_dir = read_4_bytes(offset + 16, byte_format='I')  # unused
        tex_map.patch_count = read_2_bytes(offset + 20, byte_format='H')

        tex_map.patch_maps = []
        for i in range(tex_map.patch_count):
            tex_map.patch_maps.append(
                # 10 bytes each
                self.read_patch_map(offset + 22 + i * 10)
            )
        return tex_map

    def read_patch_map(self, offset):
        # defining how the patch should be drawn inside the texture
        read_2_bytes = self.read_2_bytes

        patch_map = PatchMap()
        patch_map.x_offset = read_2_bytes(offset + 0, byte_format='h')
        patch_map.y_offset = read_2_bytes(offset + 2, byte_format='h')
        patch_map.p_name_index = read_2_bytes(offset + 4, byte_format='H')
        patch_map.step_dir = read_2_bytes(offset + 6, byte_format='H')  # unused
        patch_map.color_map = read_2_bytes(offset + 8, byte_format='H')  # unused
        return patch_map

    def read_texture_header(self, offset):
        read_4_bytes = self.read_4_bytes

        tex_header = TextureHeader()
        tex_header.texture_count = read_4_bytes(offset + 0, byte_format='I')
        tex_header.texture_offset = read_4_bytes(offset + 4, byte_format='I')

        tex_header.texture_data_offset = []
        for i in range(tex_header.texture_count):
            tex_header.texture_data_offset.append(read_4_bytes(offset + 4 + i * 4,
                                                               byte_format='I'))
        return tex_header

    def read_patch_column(self, offset):
        read_1_byte = self.read_1_byte

        patch_column = PatchColumn()
        patch_column.top_delta = read_1_byte(offset + 0)

        if patch_column.top_delta != 0xFF:
            patch_column.length = read_1_byte(offset + 1)
            patch_column.padding_pre = read_1_byte(offset + 2)  # unused

            patch_column.data = []
            for i in range(patch_column.length):
                patch_column.data.append(read_1_byte(offset + 3 + i))
            patch_column.padding_post = read_1_byte(offset + 3 + patch_column.length)  # unused

            return patch_column, offset + 4 + patch_column.length

        return patch_column, offset + 1

    def read_patch_header(self, offset):
        read_2_bytes = self.read_2_bytes
        read_4_bytes = self.read_4_bytes

        patch_header = PatchHeader()
        patch_header.width = read_2_bytes(offset + 0, byte_format='H')
        patch_header.height = read_2_bytes(offset + 2, byte_format='H')
        patch_header.left_offset = read_2_bytes(offset + 4, byte_format='h')
        patch_header.top_offset = read_2_bytes(offset + 6, byte_format='h')

        patch_header.column_offset = []
        for i in range(patch_header.width):
            patch_header.column_offset.append(read_4_bytes(offset + 8 + 4 * i, byte_format='I'))
        return patch_header

    def read_palette(self, offset):
        # 3 bytes = B + B + B
        read_1_byte = self.read_1_byte

        palette = []
        for i in range(256):
            r = read_1_byte(offset + i * 3 + 0)
            g = read_1_byte(offset + i * 3 + 1)
            b = read_1_byte(offset + i * 3 + 2)
            palette.append((r, g, b),)
        return palette

    def read_sector(self, offset):
        # 26 bytes = 2h + 2h + 8c + 8c + 2H x 3
        read_2_bytes = self.read_2_bytes
        read_string = self.read_string

        sector = Sector()
        sector.floor_height = read_2_bytes(offset, byte_format='h')
        sector.ceil_height = read_2_bytes(offset + 2, byte_format='h')
        sector.floor_texture = read_string(offset + 4, num_bytes=8)
        sector.ceil_texture = read_string(offset + 12, num_bytes=8)
        sector.light_level = read_2_bytes(offset + 20, byte_format='H') / 255.0
        sector.type = read_2_bytes(offset + 22, byte_format='H')
        sector.tag = read_2_bytes(offset + 24, byte_format='H')
        return sector

    def read_sidedef(self, offset):
        # 30 bytes = 2h + 2h + 8c + 8c + 8c + 2H
        read_2_bytes = self.read_2_bytes
        read_string = self.read_string

        sidedef = Sidedef()
        sidedef.x_offset = read_2_bytes(offset, byte_format='h')
        sidedef.y_offset = read_2_bytes(offset + 2, byte_format='h')
        sidedef.upper_texture = read_string(offset + 4, num_bytes=8)
        sidedef.lower_texture = read_string(offset + 12, num_bytes=8)
        sidedef.middle_texture = read_string(offset + 20, num_bytes=8)
        sidedef.sector_id = read_2_bytes(offset + 28, byte_format='H')
        return sidedef

    def read_thing(self, offset):
        # 10 bytes = 2h + 2h + 2H x 3
        read_2_bytes = self.read_2_bytes

        thing = Thing()
        x = read_2_bytes(offset, byte_format='h')
        y = read_2_bytes(offset + 2, byte_format='h')
        thing.angle = read_2_bytes(offset + 4, byte_format='H')
        thing.type = read_2_bytes(offset + 6, byte_format='H')
        thing.flags = read_2_bytes(offset + 8, byte_format='H')
        thing.pos = vec2(x, y)
        return thing

    def read_segment(self, offset):
        # 12 bytes = 2h x 6
        read_2_bytes = self.read_2_bytes

        seg = Seg()
        seg.start_vertex_id = read_2_bytes(offset, byte_format='h')
        seg.end_vertex_id = read_2_bytes(offset + 2, byte_format='h')
        seg.angle = read_2_bytes(offset + 4, byte_format='h')
        seg.linedef_id = read_2_bytes(offset + 6, byte_format='h')
        seg.direction = read_2_bytes(offset + 8, byte_format='h')
        seg.offset = read_2_bytes(offset + 10, byte_format='h')
        return seg

    def read_sub_sector(self, offset):
        # 4 bytes = 2h + 2h
        read_2_bytes = self.read_2_bytes

        sub_sector = SubSector()
        sub_sector.seg_count = read_2_bytes(offset, byte_format='h')
        sub_sector.first_seg_id = read_2_bytes(offset + 2, byte_format='h')
        return sub_sector

    def read_node(self, offset):
        # 28 bytes = 2h x 12 + 2H x 2
        read_2_bytes = self.read_2_bytes

        node = Node()
        node.x_partition = read_2_bytes(offset, byte_format='h')
        node.y_partition = read_2_bytes(offset + 2, byte_format='h')
        node.dx_partition = read_2_bytes(offset + 4, byte_format='h')
        node.dy_partition = read_2_bytes(offset + 6, byte_format='h')

        node.bbox['front'].top = read_2_bytes(offset + 8, byte_format='h')
        node.bbox['front'].bottom = read_2_bytes(offset + 10, byte_format='h')
        node.bbox['front'].left = read_2_bytes(offset + 12, byte_format='h')
        node.bbox['front'].right = read_2_bytes(offset + 14, byte_format='h')

        node.bbox['back'].top = read_2_bytes(offset + 16, byte_format='h')
        node.bbox['back'].bottom = read_2_bytes(offset + 18, byte_format='h')
        node.bbox['back'].left = read_2_bytes(offset + 20, byte_format='h')
        node.bbox['back'].right = read_2_bytes(offset + 22, byte_format='h')

        node.front_child_id = read_2_bytes(offset + 24, byte_format='H')
        node.back_child_id = read_2_bytes(offset + 26, byte_format='H')
        return node

    def read_linedef(self, offset):
        # 14 bytes = 2H x 7
        read_2_bytes = self.read_2_bytes

        linedef = Linedef()
        linedef.start_vertex_id = read_2_bytes(offset, byte_format='H')
        linedef.end_vertex_id = read_2_bytes(offset + 2, byte_format='H')
        linedef.flags = read_2_bytes(offset + 4, byte_format='H')
        linedef.line_type = read_2_bytes(offset + 6, byte_format='H')
        linedef.sector_tag = read_2_bytes(offset + 8, byte_format='H')
        linedef.front_sidedef_id = read_2_bytes(offset + 10, byte_format='H')
        linedef.back_sidedef_id = read_2_bytes(offset + 12, byte_format='H')
        return linedef

    def read_vertex(self, offset):
        # 4 bytes = 2h + 2h
        x = self.read_2_bytes(offset, byte_format='h')
        y = self.read_2_bytes(offset + 2, byte_format='h')
        return vec2(x, y)

    def read_directory(self):
        directory = []
        for i in range(self.header['lump_count']):
            offset = self.header['init_offset'] + i * 16
            lump_info = {
                'lump_offset': self.read_4_bytes(offset),
                'lump_size': self.read_4_bytes(offset + 4),
                'lump_name': self.read_string(offset + 8, num_bytes=8)
            }
            directory.append(lump_info)
        return directory

    def read_header(self):
        return {
            'wad_type': self.read_string(offset=0, num_bytes=4),
            'lump_count': self.read_4_bytes(offset=4),
            'init_offset': self.read_4_bytes(offset=8)
        }

    def read_1_byte(self, offset, byte_format='B'):
        # B - unsigned char, b - signed char
        return self.read_bytes(offset=offset, num_bytes=1, byte_format=byte_format)[0]

    def read_2_bytes(self, offset, byte_format):
        # H - uint16, h - int16
        return self.read_bytes(offset=offset, num_bytes=2, byte_format=byte_format)[0]

    def read_4_bytes(self, offset, byte_format='i'):
        # I - uint32, i - int32
        return self.read_bytes(offset=offset, num_bytes=4, byte_format=byte_format)[0]

    def read_string(self, offset, num_bytes=8):
        # c - char
        return ''.join(b.decode('ascii') for b in
                       self.read_bytes(offset, num_bytes, byte_format='c' * num_bytes)
                       if ord(b) != 0).upper()

    def read_bytes(self, offset, num_bytes, byte_format):
        self.wad_file.seek(offset)
        buffer = self.wad_file.read(num_bytes)
        return struct.unpack(byte_format, buffer)

    def close(self):
        self.wad_file.close()
