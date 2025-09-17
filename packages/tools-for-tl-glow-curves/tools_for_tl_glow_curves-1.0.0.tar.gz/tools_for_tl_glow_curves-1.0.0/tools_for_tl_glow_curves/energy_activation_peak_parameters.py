import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, Markdown

def energy_activation_peak_parameters(T, I):
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

    k=8.617e-5
       # Método tau
    c_tau = 1.52 + 3*(mu - 0.42)
    b_tau = 1.58 + 4.2*(mu - 0.42)
    E_tau = c_tau*(k*Tm**2/tau) - b_tau*2*k*Tm
    
    # Método delta
    c_delta = 0.976 + 7.3*(mu - 0.42)
    b_delta = 0
    E_delta = c_delta*(k*Tm**2/delta) - b_delta*2*k*Tm
    
    # Método omega
    c_omega = 2.52 + 10.2*(mu - 0.42)
    b_omega = 1
    E_omega = c_omega*(k*Tm**2/omega) - b_omega*2*k*Tm
    
    display(Markdown(f"**Shape factor μg:** {mu:.3f}"))
    display(Markdown(f"**Energía de activación (τ):** {E_tau:.3f} eV"))
    display(Markdown(f"**Energía de activación (δ):** {E_delta:.3f} eV"))
    display(Markdown(f"**Energía de activación (ω):** {E_omega:.3f} eV"))

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
    plt.title('Ea basados en la forma del pico')
    plt.legend()
    plt.grid(False)
    plt.show()

    return
