import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math

def pegar_material(raio, repeticoes, centro_x, centro_y):
    coordenadas_circulo = []
    for _ in range(int(repeticoes)):
        for angulo in range(0, 360, 1):
            radianos = math.radians(angulo)
            x = raio * math.cos(radianos) + centro_x
            y = raio * math.sin(radianos) + centro_y
            coordenadas_circulo.append((x, y))
    return coordenadas_circulo

def generate_gcode(raio, repeticoes, centro_x, centro_y, x_max, x_min, y_max, y_min, y_step_size, v_define, z_values1, z_values2, passagens_por_linha, repetitions, pause_enabled=False, pause_duration=0, geometry='zigzag'):
    gcode = "T1;\nG17;\nG0 Z20.000;\nG0 X0.000 Y0.000 S100 M3;\nM0; Aperte para iniciar a PRIMEIRA COLETA!\n" 
    gcode += f"G1 X{centro_x:.3f} Y{centro_y:.3f} Z10.0;\n"
    coordenadas_circulo = pegar_material(raio, repeticoes, centro_x, centro_y)
    
    for x, y in coordenadas_circulo:
        gcode += f"G1 X{x:.3f} Y{y:.3f} Z2.6 F3600.0;\n"
    
    gcode += "Z12.000;\nM0; Aperte para iniciar a primeira deposição\n"

    for _ in range(int(repetitions)):
        for i in range(len(z_values1)):
            current_y = y_max
            z_final = z_values2[i]
            z_initial = z_values1[i]
            while current_y >= y_min:
                if geometry == 'zigzag':
                    for _ in range(passagens_por_linha):
                        gcode += f"G1 X{x_max:.3f} Y{current_y:.3f} Z{z_initial:.3f};\n"
                        if pause_enabled:
                            gcode += f"G4 P{pause_duration};\n"
                        gcode += f"G1 Z{z_final} F{v_define};\n"
                        gcode += f"G1 X{x_min:.3f} Y{current_y:.3f} Z{z_final:.3f}; \n"
                elif geometry == 'reta':
                    for _ in range(passagens_por_linha):
                        gcode += f"G1 X{x_min:.3f} Y{current_y:.3f} Z{z_initial:.3f}; \n"
                        if pause_enabled:
                            gcode += f"G4 P{pause_duration};\n"
                        gcode += f"G1 Z{z_final} F{v_define};\n"
                        gcode += f"G1 X{x_max:.3f} Y{current_y:.3f} Z{z_final};\n"
                else:
                    raise ValueError("Geometry should be 'zigzag' or 'reta'.")
                current_y -= y_step_size

    gcode += "G0 Z20.000;\nG0 X0.000 Y0.000;\nM30;"
    return gcode

def plot_print_path(ax, x_max, x_min, y_max, y_min, y_step_size, z_values1, z_values2, passagens_por_linha, repetitions, raio, repeticoes, centro_x, centro_y, geometry='zigzag'):
    ax.clear()
    ax.set_title('Trajeto da Impressão (XY)')
    ax.set_xlabel('Coordenada X')
    ax.set_ylabel('Coordenada Y')

    # Adicionar trajetória do círculo
    coordenadas_circulo = pegar_material(raio, repeticoes, centro_x, centro_y)
    trajeto_x, trajeto_y = zip(*coordenadas_circulo)
    ax.plot(trajeto_x, trajeto_y, label='Círculo', linestyle='dashed')

      # Adicionar retângulo da área de impressão
    rectangle = plt.Rectangle((73, 58.5), 72, 22, linewidth=1, edgecolor='r', facecolor='none')
    ax.add_patch(rectangle)
    for _ in range(int(repetitions)):
        for i in range(len(z_values1)):
            current_y = y_max
            trajeto_x = []
            trajeto_y = []
            while current_y >= y_min:
                if geometry == 'zigzag':
                    for _ in range(passagens_por_linha):
                        trajeto_x.extend([x_max, x_min])
                        trajeto_y.extend([current_y, current_y])
                elif geometry == 'reta':
                    for _ in range(passagens_por_linha):
                        trajeto_x.extend([x_min, x_max])
                        trajeto_y.extend([current_y, current_y])
                else:
                    raise ValueError("Geometry should be 'zigzag' or 'reta'.")
                current_y -= y_step_size

    ax.plot(trajeto_x, trajeto_y, label=f'Repetição {_+1}')

    ax.legend()

class PrintingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Configuração de Impressão")
        self.pause_enabled = tk.BooleanVar(value=False)

        self.create_widgets()

    def create_widgets(self):
        frame_print_settings = ttk.LabelFrame(self.root, text="Configuração de Impressão")
        frame_print_settings.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        ttk.Label(frame_print_settings, text="X Máximo (mm):").grid(row=0, column=0, padx=5, pady=5)
        self.entry_x_max = ttk.Entry(frame_print_settings)
        self.entry_x_max.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_print_settings, text="X Mínimo (mm):").grid(row=1, column=0, padx=5, pady=5)
        self.entry_x_min = ttk.Entry(frame_print_settings)
        self.entry_x_min.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_print_settings, text="Y Máximo (mm):").grid(row=2, column=0, padx=5, pady=5)
        self.entry_y_max = ttk.Entry(frame_print_settings)
        self.entry_y_max.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame_print_settings, text="Y Mínimo (mm):").grid(row=3, column=0, padx=5, pady=5)
        self.entry_y_min = ttk.Entry(frame_print_settings)
        self.entry_y_min.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(frame_print_settings, text="Passo em Y (mm):").grid(row=4, column=0, padx=5, pady=5)
        self.entry_y_step = ttk.Entry(frame_print_settings)
        self.entry_y_step.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(frame_print_settings, text="Velocidade (rpm):").grid(row=5, column=0, padx=5, pady=5)
        self.entry_velocity = ttk.Entry(frame_print_settings)
        self.entry_velocity.grid(row=5, column=1, padx=5, pady=5)

        ttk.Label(frame_print_settings, text="Z Máximo (mm):").grid(row=6, column=0, padx=5, pady=5)
        self.entry_z_values1 = ttk.Entry(frame_print_settings)
        self.entry_z_values1.grid(row=6, column=1, padx=5, pady=5)

        ttk.Label(frame_print_settings, text="Z Mínimo (mm):").grid(row=7, column=0, padx=5, pady=5)
        self.entry_z_values2 = ttk.Entry(frame_print_settings)
        self.entry_z_values2.grid(row=7, column=1, padx=5, pady=5)

        ttk.Label(frame_print_settings, text="Passagens por Linha:").grid(row=8, column=0, padx=5, pady=5)
        self.entry_passagens_por_linha = ttk.Entry(frame_print_settings)
        self.entry_passagens_por_linha.grid(row=8, column=1, padx=5, pady=5)

        ttk.Label(frame_print_settings, text="Geometria:").grid(row=9, column=0, padx=5, pady=5)
        self.combo_geometry = ttk.Combobox(frame_print_settings, values=["zigzag", "reta"])
        self.combo_geometry.grid(row=9, column=1, padx=5, pady=5)
        self.combo_geometry.set("zigzag")

        ttk.Label(frame_print_settings, text="Repetições:").grid(row=10, column=0, padx=5, pady=5)
        self.entry_repetitions = ttk.Entry(frame_print_settings)
        self.entry_repetitions.grid(row=10, column=1, padx=5, pady=5)

        ttk.Label(frame_print_settings, text="Raio (mm):").grid(row=11, column=0, padx=5, pady=5)
        self.entry_raio = ttk.Entry(frame_print_settings)
        self.entry_raio.grid(row=11, column=1, padx=5, pady=5)

        ttk.Label(frame_print_settings, text="Repetiçoes Círculo:").grid(row=12, column=0, padx=5, pady=5)
        self.entry_repeticoes = ttk.Entry(frame_print_settings)
        self.entry_repeticoes.grid(row=12, column=1, padx=5, pady=5)

        tk.Label(frame_print_settings, text="Coordenada centro x (mm):").grid(row=13, column=0, padx=5, pady=5)
        self.entry_centro_x = ttk.Entry(frame_print_settings)
        self.entry_centro_x.grid(row=13, column=1, padx=5, pady=5)

        tk.Label(frame_print_settings, text="Coordenada centro y (mm):").grid(row=14, column=0, padx=5, pady=5)
        self.entry_centro_y = ttk.Entry(frame_print_settings)
        self.entry_centro_y.grid(row=14, column=1, padx=5, pady=5)

        # Adicionar todos os widgets de entrada aqui...
        
        ttk.Label(frame_print_settings, text="Pausa entre linhas:").grid(row=15, column=0, padx=5, pady=5)
        self.check_pause = ttk.Checkbutton(frame_print_settings, variable=self.pause_enabled, command=self.toggle_pause)
        self.check_pause.grid(row=15, column=1, padx=5, pady=5)

        self.entry_pause_duration = ttk.Entry(frame_print_settings, state='disabled')
        self.entry_pause_duration.grid(row=16, column=1, padx=5, pady=5)

        ttk.Label(frame_print_settings, text="Duração da pausa (ms):").grid(row=16, column=0, padx=5, pady=5)

        ttk.Button(self.root, text="Gerar GCODE", command=self.generate).grid(row=1, column=0, pady=10)
        
        # Componente para exibir o GCODE
        self.gcode_text = scrolledtext.ScrolledText(self.root, width=50, height=20, wrap=tk.WORD)
        self.gcode_text.grid(row=0, column=1, padx=10, pady=10, rowspan=2)
        
        # Gráfico
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=2, rowspan=2, padx=10, pady=10)

    def toggle_pause(self):
        if self.pause_enabled.get():
            self.entry_pause_duration.config(state='normal')
        else:
            self.entry_pause_duration.config(state='disabled')

    def generate(self):
        # Obter todas as configurações do usuário
        x_max = float(self.entry_x_max.get())
        x_min = float(self.entry_x_min.get())
        y_max = float(self.entry_y_max.get())
        y_min = float(self.entry_y_min.get())
        y_step = float(self.entry_y_step.get())
        velocity = float(self.entry_velocity.get())
        z_values1 = list(map(float, self.entry_z_values1.get().split(',')))
        z_values2 = list(map(float, self.entry_z_values2.get().split(',')))
        passagens_por_linha = int(self.entry_passagens_por_linha.get())
        geometry = self.combo_geometry.get()
        repetitions = float(self.entry_repetitions.get())
        raio = float(self.entry_raio.get())
        repeticoes = float(self.entry_repeticoes.get())
        centro_x = float(self.entry_centro_x.get())
        centro_y = float(self.entry_centro_y.get())

        # Obter a duração da pausa (se a pausa estiver habilitada)
        if self.pause_enabled.get():
            pause_duration = int(self.entry_pause_duration.get())
        else:
            pause_duration = 0

        # Gerar o GCODE com base nas configurações
        generated_gcode = generate_gcode(raio, repeticoes, centro_x, centro_y, x_max, x_min, y_max, y_min, y_step, velocity, z_values1, z_values2, passagens_por_linha, repetitions, pause_enabled=self.pause_enabled.get(), pause_duration=pause_duration, geometry=geometry)

        # Atualizar a visualização do GCODE
        self.gcode_text.delete('1.0', tk.END)
        self.gcode_text.insert(tk.END, generated_gcode)

        # Salvar o GCODE em um arquivo
        with open("1p.gcode", "w") as file:
            file.write(generated_gcode)

        # Exibir a trajetória no gráfico
        plot_print_path(self.ax, x_max, x_min, y_max, y_min, y_step, z_values1, z_values2, passagens_por_linha, repetitions, raio, repeticoes, centro_x, centro_y, geometry)
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = PrintingApp(root)
    root.mainloop()
