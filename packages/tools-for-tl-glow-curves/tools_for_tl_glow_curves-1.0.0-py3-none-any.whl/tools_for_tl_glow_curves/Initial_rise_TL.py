import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from IPython.display import display, Markdown

def Initial_rise_TL(T, I, Tini, Tfin):
    kB = 8.617e-5  # eV/K
    
    # Convertir a arrays de float
    T = np.array(T, dtype=float)
    I = np.array(I, dtype=float)
    
    # Selección por rango de temperatura (convertimos °C a K)
    mask = (T >= Tini+273.15) & (T <= Tfin+273.15)
    x = T[mask]
    y = I[mask]
    
    # Transformaciones ln(y) vs 1/(kT)
    y_log = np.log(y)
    x_inv = 1 / (kB * x)
    
    # Ajuste lineal
    X = x_inv.reshape(-1, 1)
    model = LinearRegression().fit(X, y_log)
    slope, intercept = model.coef_[0], model.intercept_
    # Calcular energía de activación (en eV)
    Ea = -slope
    
    # ----------------------------
    # Gráficas
    plt.figure(figsize=(12,6))

    # (a) TL vs Temperatura
    plt.subplot(1,2,1)
    plt.plot(T - 273.15, I, color="blue", label="Datos")
    plt.plot(x - 273.15, y, color="red", linewidth=3, label="Rango")
    plt.xlabel("Temperatura [°C]")
    plt.ylabel("TL (a.u.)")
    plt.legend(["Datos completos","Rango analizado"])

    # (b) ln(TL) vs 1/(kT)
    plt.subplot(1,2,2)
    plt.scatter(x_inv, y_log, color="blue", label="Datos transformados")
    plt.plot(x_inv, model.predict(X), color="red", label="Ajuste lineal")
    plt.xlabel("1/(kT) [1/eV]")
    plt.ylabel("ln(TL)")
    plt.legend()
    plt.suptitle("Ea basados en Initial Rise Method")
    plt.tight_layout()
    plt.show()

        # Mostrar resultados correctamente
    display(Markdown(f"**Ea:** {Ea:.3f}"))
    return
