import json
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By


def renovar_cookies_jumbo(output_path="cookies_jumbo.json"):
    options = uc.ChromeOptions()
    options.headless = True  # No se muestra la ventana del navegador
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")

    print("🚀 Abriendo navegador...")
    driver = uc.Chrome(options=options)

    try:
        url = "https://www.jumbo.com.ar"
        driver.get(url)
        print(f"🌐 Navegando a {url}...")
        time.sleep(8)  # Espera que se cargue completamente

        cookies = driver.get_cookies()
        cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(cookies_dict, f, indent=4)

        print(f"✅ Cookies guardadas en {output_path}")

    except Exception as e:
        print(f"❌ Error durante la renovación de cookies: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    renovar_cookies_jumbo()
