import re
import requests  # para conectar a la web

# ====== COLORES ANSI ======
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BG_BLUE = "\033[44m"
    BG_CYAN = "\033[46m"


# Pesos aproximados de monedas mexicanas (en gramos)
COIN_WEIGHTS = {
    1: 3.95,     # $1
    2: 5.19,     # $2
    5: 7.07,     # $5
    10: 10.329   # $10
}


def banner_principal():
    print()
    print(C.BG_CYAN + C.BLACK + "╔══════════════════════════════════════════════════╗" + C.RESET)
    print(C.BG_CYAN + C.BLACK + "║  Calculadora de Monedas para Presionar una Tecla ║" + C.RESET)
    print(C.BG_CYAN + C.BLACK + "╚══════════════════════════════════════════════════╝" + C.RESET)
    print(C.MAGENTA + "Autor: L4 DEV :)\n" + C.RESET)


def pedir_dispositivo():
    print(C.BOLD + C.BLUE + "=== Configuración del teclado ===" + C.RESET)
    tipo_teclado = input(
        C.CYAN + "¿El teclado es 'mecanico' o 'laptop'? " + C.RESET
    ).strip().lower()

    info = {
        "tipo_teclado": tipo_teclado
    }
    return info


def obtener_fuerza_desde_web(tipo_teclado: str):

    if tipo_teclado == "laptop":
        query = "peso necesario para presionar la tecla de un teclado de laptop"
    else:
        query = "peso necesario para presionar la tecla de un teclado mecanico"

    print(C.BLUE + f"\nBuscando en la nube datos de fuerza de tecla para: '{query}'..." + C.RESET)

    try:
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1,
            },
            timeout=7
        )
        data = resp.json()

        # Tomamos texto de algunos campos típicos
        text_parts = [
            data.get("AbstractText", ""),
            data.get("Abstract", ""),
            data.get("Heading", ""),
        ]

        # También revisamos RelatedTopics (si existen)
        for rt in data.get("RelatedTopics", []):
            if isinstance(rt, dict):
                text_parts.append(rt.get("Text", ""))

        text = " ".join(p for p in text_parts if p).strip()

        if not text:
            print(C.YELLOW + "⚠ La respuesta de la web viene vacía o sin texto útil." + C.RESET)
            return None, ""

        # Intentar encontrar algo tipo "45 g", "45 grams", "45 gramos"
        match = re.search(r"(\d+(\.\d+)?)\s*(g|grams|gramos)", text, re.IGNORECASE)
        if match:
            valor = float(match.group(1))
            print(C.GREEN + f"✔ Dato obtenido desde la web: ~{valor:.2f} g" + C.RESET)
            return valor, text
        else:
            print(C.YELLOW + "⚠ No se encontró un número claro en la respuesta de la web." + C.RESET)
            return None, text

    except Exception as e:
        print(C.RED + f"✘ Error al consultar la web: {e}" + C.RESET)
        return None, ""


def buscar_fuerza_en_nube(info_dispositivo):
  
    tipo_teclado = info_dispositivo["tipo_teclado"]

    print()
    print(C.BOLD + C.BLUE + "=== Búsqueda de fuerza de tecla en la 'nube' ===" + C.RESET)

    fuerza_min = None

    # 1) Intentar obtener desde internet
    valor_web, texto_web = obtener_fuerza_desde_web(tipo_teclado)

    if valor_web is not None:
        # Tenemos un número claro desde la web
        fuerza_min = valor_web
    else:
        # No se pudo extraer número, pero quizá hay texto
        if texto_web:
            print(C.MAGENTA + "\nTexto obtenido desde la web (resumen):" + C.RESET)
            # Mostrar solo los primeros caracteres para no saturar
            snippet = texto_web[:400].replace("\n", " ")
            print(C.WHITE + snippet + "..." + C.RESET)

            # Preguntar si el usuario quiere meter un valor manual basado en eso
            usar_manual = input(
                C.CYAN + "\n¿Quieres introducir tú un valor en gramos basado en esta info? (s/n): " + C.RESET
            ).strip().lower()
            if usar_manual == "s":
                while True:
                    try:
                        fuerza_min = float(
                            input(C.CYAN + "Introduce la fuerza mínima aproximada en gramos: " + C.RESET)
                        )
                        break
                    except ValueError:
                        print(C.RED + "✘ Por favor introduce un número válido." + C.RESET)

        # Si aún no hay fuerza_min (usuario dijo que no, o no había texto), usar valores típicos
        if fuerza_min is None:
            if tipo_teclado == "laptop":
                fuerza_min = 29.0
                print(C.GREEN + "✔ Se usa un valor típico aproximado de 29 g para teclado de laptop." + C.RESET)
            elif tipo_teclado == "mecanico":
                fuerza_min = 45.0
                print(C.GREEN + "✔ Se usa un valor típico aproximado de 45 g para teclado mecánico." + C.RESET)
            else:
                print(C.YELLOW + "⚠ No se reconoce el tipo de teclado. Introduce un valor manual." + C.RESET)
                while True:
                    try:
                        fuerza_min = float(
                            input(C.CYAN + "Introduce la fuerza mínima aproximada en gramos: " + C.RESET)
                        )
                        break
                    except ValueError:
                        print(C.RED + "✘ Por favor introduce un número válido." + C.RESET)

    print(C.MAGENTA + f"\nFuerza mínima estimada para presionar la tecla: {fuerza_min:.2f} g\n" + C.RESET)
    return fuerza_min


def pedir_monedas():
    print(C.BOLD + C.BLUE + "=== Monedas disponibles ===" + C.RESET)
    monedas_disponibles = {}
    for denom in sorted(COIN_WEIGHTS.keys()):
        while True:
            try:
                cantidad = int(
                    input(C.CYAN + f"¿Cuántas monedas de ${denom} tienes? " + C.RESET)
                )
                if cantidad < 0:
                    print(C.RED + "✘ No puede ser un número negativo. Intenta de nuevo." + C.RESET)
                    continue
                monedas_disponibles[denom] = cantidad
                break
            except ValueError:
                print(C.RED + "✘ Por favor introduce un número entero válido." + C.RESET)
    print()
    return monedas_disponibles


def generar_combinaciones(monedas_disponibles, fuerza_minima):
    resultados = []

    max_1 = monedas_disponibles.get(1, 0)
    max_2 = monedas_disponibles.get(2, 0)
    max_5 = monedas_disponibles.get(5, 0)
    max_10 = monedas_disponibles.get(10, 0)

    w1 = COIN_WEIGHTS[1]
    w2 = COIN_WEIGHTS[2]
    w5 = COIN_WEIGHTS[5]
    w10 = COIN_WEIGHTS[10]

    for n1 in range(max_1 + 1):
        for n2 in range(max_2 + 1):
            for n5 in range(max_5 + 1):
                for n10 in range(max_10 + 1):
                    if n1 == n2 == n5 == n10 == 0:
                        continue

                    peso_total = n1 * w1 + n2 * w2 + n5 * w5 + n10 * w10
                    valor_total = n1 * 1 + n2 * 2 + n5 * 5 + n10 * 10
                    num_monedas = n1 + n2 + n5 + n10

                    resultados.append({
                        "peso": peso_total,
                        "n1": n1,
                        "n2": n2,
                        "n5": n5,
                        "n10": n10,
                        "valor": valor_total,
                        "monedas": num_monedas,
                        "diff": peso_total - fuerza_minima
                    })

    return resultados


def elegir_mejor_combinacion(resultados, fuerza_minima):
    if not resultados:
        return None, "No hay resultados (no tienes monedas)."

    alcanzan = [r for r in resultados if r["peso"] >= fuerza_minima]
    no_alcanzan = [r for r in resultados if r["peso"] < fuerza_minima]

    if alcanzan:
        alcanzan_ordenadas = sorted(
            alcanzan,
            key=lambda r: (r["diff"], r["monedas"], r["valor"])
        )
        return alcanzan_ordenadas[0], "ok_arriba"
    else:
        no_alcanzan_ordenadas = sorted(
            no_alcanzan,
            key=lambda r: (abs(r["diff"]), r["monedas"], r["valor"])
        )
        return no_alcanzan_ordenadas[0], "solo_abajo"


def imprimir_resumen(mejor, estado, fuerza_minima):
    print(C.BOLD + C.BLUE + "\n=== Resultado ===" + C.RESET)
    if mejor is None:
        print(C.RED + "✘ No se pudo encontrar ninguna combinación." + C.RESET)
        return

    peso = mejor["peso"]
    n1 = mejor["n1"]
    n2 = mejor["n2"]
    n5 = mejor["n5"]
    n10 = mejor["n10"]
    valor = mejor["valor"]
    diff = mejor["diff"]

    if estado == "ok_arriba":
        print(C.GREEN + f"✔ La mejor combinación que ALCANZA o SUPERA la fuerza mínima ({fuerza_minima:.2f} g) es:" + C.RESET)
    else:
        print(C.YELLOW + f"⚠ No hay suficientes monedas para llegar a {fuerza_minima:.2f} g." + C.RESET)
        print(C.YELLOW + "La combinación que más se acerca (por DEBAJO) es:" + C.RESET)

    print(C.BOLD + f"- Peso total: {peso:.2f} g" + C.RESET + f"  (diferencia: {diff:+.2f} g respecto al mínimo)")
    print(f"- Monedas de $1 : {C.CYAN}{n1}{C.RESET}")
    print(f"- Monedas de $2 : {C.CYAN}{n2}{C.RESET}")
    print(f"- Monedas de $5 : {C.CYAN}{n5}{C.RESET}")
    print(f"- Monedas de $10: {C.CYAN}{n10}{C.RESET}")
    print(f"- Valor total usado: {C.MAGENTA}${valor}{C.RESET}")
    print(f"- Número total de monedas: {C.MAGENTA}{mejor['monedas']}{C.RESET}")


def imprimir_tabla_cercanas(resultados, fuerza_minima, max_filas=20):
    print(C.BOLD + C.BLUE + "\n=== Algunas combinaciones cercanas al mínimo ===" + C.RESET)

    ordenados = sorted(
        resultados,
        key=lambda r: (abs(r["peso"] - fuerza_minima), r["monedas"], r["valor"])
    )

    header = (
        f"{C.BOLD}{C.WHITE}"
        "Peso(g)\tdiff(g)\t$1\t$2\t$5\t$10\tmonedas\tvalor"
        f"{C.RESET}"
    )
    print(header)

    for r in ordenados[:max_filas]:
        linea = (
            f"{r['peso']:7.2f}\t"
            f"{r['peso'] - fuerza_minima:+7.2f}\t"
            f"{r['n1']}\t{r['n2']}\t{r['n5']}\t{r['n10']}\t"
            f"{r['monedas']}\t${r['valor']}"
        )
        print(C.CYAN + linea + C.RESET)


def main():
    banner_principal()

    info = pedir_dispositivo()
    fuerza_minima = buscar_fuerza_en_nube(info)
    monedas_disponibles = pedir_monedas()
    resultados = generar_combinaciones(monedas_disponibles, fuerza_minima)

    if not resultados:
        print(C.RED + "✘ No se generaron combinaciones (probablemente no tienes monedas)." + C.RESET)
        return

    mejor, estado = elegir_mejor_combinacion(resultados, fuerza_minima)
    imprimir_resumen(mejor, estado, fuerza_minima)
    imprimir_tabla_cercanas(resultados, fuerza_minima, max_filas=20)

    print()
    print(C.GREEN + "✔ Proceso terminado. Puedes probar con otras cantidades de monedas si quieres." + C.RESET)
    print()


if __name__ == "__main__":
    main()

