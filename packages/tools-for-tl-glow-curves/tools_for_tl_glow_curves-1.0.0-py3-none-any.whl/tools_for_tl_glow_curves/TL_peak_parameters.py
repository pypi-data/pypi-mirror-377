import numpy as np
from IPython.display import display, Markdown

def TL_peak_parameters(T, I):
    T = np.array(T, dtype=float)
    I = np.array(I, dtype=float)

    # Tmax y Tm
    imax_idx = np.argmax(I)
    Tm = T[imax_idx]
    Imax = I[imax_idx]

    # Intensidad a la mitad de Imax
    Ihalf = Imax / 2

    # T1: temperatura a la izquierda de Tm donde I = Ihalf
    left_indices = np.where(T <= Tm)[0]
    T1_idx = left_indices[np.argmin(np.abs(I[left_indices] - Ihalf))]
    T1 = T[T1_idx]

    # T2: temperatura a la derecha de Tm donde I = Ihalf
    right_indices = np.where(T >= Tm)[0]
    T2_idx = right_indices[np.argmin(np.abs(I[right_indices] - Ihalf))]
    T2 = T[T2_idx]

    # Anchuras y factor de forma
    tau = Tm - T1
    delta = T2 - Tm
    omega = tau + delta
    mu = delta / omega

    display(Markdown(f"**Imax:** {Imax:.3f}"))
    display(Markdown(f"**I½:** {Ihalf:.3f}"))
    display(Markdown(f"**T1 (°C):** {T1-273.15:.3f}"))
    display(Markdown(f"**T2 (°C):** {T2-273.15:.3f}"))
    display(Markdown(f"**Tm (°C):** {Tm-273.15:.3f}"))
    display(Markdown(f"**τ:** {tau:.3f}"))
    display(Markdown(f"**δ:** {delta:.3f}"))
    display(Markdown(f"**ω:** {omega:.3f}"))
    display(Markdown(f"**μ:** {mu:.3f}"))

    # ====== Gráfica ======
    plt.figure(figsize=(6,6))
    plt.plot(T-273.15, I, label='TL curve', color='blue')
    plt.axvline(Tm-273.15, color='red', linestyle='--', lw=1, alpha=0.5, label=r'$T_m$ (Imax)')
    plt.axvline(T1-273.15, color='green', linestyle='--', lw=1, alpha=0.5, label=r'$T_1$')
    plt.axvline(T2-273.15, color='orange', linestyle='--', lw=1, alpha=0.5, label=r'$T_2$ ')
    plt.axhline(Ihalf, color='gray', linestyle='-', lw=1, alpha=0.5, label=r'$I_{max}/2$')


    # Marcar puntos
    plt.scatter([T1-273.15, T2-273.15, Tm-273.15], [Ihalf, Ihalf, Imax], color='black')
    
    plt.xlabel('Temperatura (°C)')
    plt.ylabel('Intensidad TL')
    plt.title('Curva TL con parámetros de la forma del pico')
    plt.legend()
    plt.grid(False)
    plt.show()

    return