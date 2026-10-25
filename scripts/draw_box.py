from pymol import cmd
from pymol.cgo import BEGIN, LINES, VERTEX, END, COLOR

def draw_box(config="prep/vina_config.txt", name="vina_box"):
    v = {}
    for line in open(config):
        if "=" in line:
            key, value = line.split("=")
            v[key.strip()] = float(value)

    cx, cy, cz = v["center_x"], v["center_y"], v["center_z"]
    hx, hy, hz = v["size_x"] / 2, v["size_y"] / 2, v["size_z"] / 2
    xs, ys, zs = (cx - hx, cx + hx), (cy - hy, cy + hy), (cz - hz, cz + hz)
    corners = [(x, y, z) for x in xs for y in ys for z in zs]

    box = [BEGIN, LINES, COLOR, 1.0, 0.5, 0.0]
    for a in corners:
        for b in corners:
            if a < b and sum(i != j for i, j in zip(a, b)) == 1:
                box += [VERTEX, *a, VERTEX, *b]
    box.append(END)
    cmd.load_cgo(box, name)

cmd.extend("draw_box", draw_box)
draw_box()
