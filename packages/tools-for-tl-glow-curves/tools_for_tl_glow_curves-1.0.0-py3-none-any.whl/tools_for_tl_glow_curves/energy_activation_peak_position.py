import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, Markdown

def energy_activation_peak_position(T,I,s):
    T = np.array(T, dtype=float)
    I = np.array(I, dtype=float)

    # Tmax y Tm
    imax_idx = np.argmax(I)
    Tm = T[imax_idx]
    Imax = I[imax_idx]

            # ====== Gráfica ======
    plt.figure(figsize=(6,6))
    plt.plot(T-273.15, I, label='TL curve', color='blue')
    plt.axvline(Tm-273.15, color='red', linestyle='--', lw=1, alpha=0.5, label=r'$T_m$ (Imax)')  
    plt.xlabel('Temperatura (°C)')
    plt.ylabel('Intensidad TL')
    plt.title('Ea basados en la posicion del pico')
    plt.legend()
    plt.grid(False)
    plt.show()

    C = 1/500  # valor típico de Urbach
    E_simple = C * Tm
    coef = 8.35e-5 * np.log(s) + 3.963e-4
    E_K = coef * Tm
    display(Markdown(f"**Energía de activación simple:** {E_simple:.3f} eV"))
    display(Markdown(f"**Energía de activación:** {E_K:.3f} eV"))
    return 
