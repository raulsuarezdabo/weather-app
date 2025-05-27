import requests
import json
from datetime import datetime
from pprint import pprint # Para una impresión más bonita de algunos JSON complejos
import os

# --- Configuración de Claves API ---
# ¡¡¡REEMPLAZA ESTAS CLAVES CON LAS TUYAS!!!

openweathermap_api_key = os.environ.get("TU_API_KEY_DE_OPENWEATHERMAP")
weather_api_key = os.environ.get("TU_API_KEY_DE_WEATHERAPI")
aemet_api_key = os.environ.get("TU_API_KEY_DE_AEMET")

# --- Ubicación ---
CIUDAD = "Madrid"
CODIGO_PAIS_OWM = "ES" # Código de país para OpenWeatherMap
CODIGO_MUNICIPIO_AEMET = "28003" # Código INE de Madrid. Puedes encontrar otros en la web de AEMET.

# --- Funciones para cada proveedor ---

def get_weather_openweathermap(api_key, city, country_code):
    """
    Obtiene el tiempo actual de OpenWeatherMap.
    """
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": f"{city},{country_code}",
        "appid": api_key,
        "units": "metric",  # Para temperatura en Celsius
        "lang": "es"
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Lanza una excepción para códigos de error HTTP (4XX o 5XX)
        data = response.json()
        print("\n--- OpenWeatherMap ---")
        if data.get("weather") and data.get("main"):
            descripcion = data["weather"][0]["description"].capitalize()
            temperatura = data["main"]["temp"]
            sensacion_termica = data["main"]["feels_like"]
            humedad = data["main"]["humidity"]
            viento_velocidad = data["wind"]["speed"] # m/s
            presion = data["main"]["pressure"]

            print(f"Descripción: {descripcion}")
            print(f"Temperatura: {temperatura}°C")
            print(f"Sensación Térmica: {sensacion_termica}°C")
            print(f"Humedad: {humedad}%")
            print(f"Viento: {viento_velocidad:.2f} m/s ({viento_velocidad * 3.6:.2f} km/h)")
            print(f"Presión: {presion} hPa")
        else:
            print("No se pudieron obtener datos completos.")
            # pprint(data) # Descomenta para ver la respuesta completa en caso de error
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con OpenWeatherMap: {e}")
    except json.JSONDecodeError:
        print("Error al decodificar la respuesta JSON de OpenWeatherMap.")
    except Exception as e:
        print(f"Error inesperado con OpenWeatherMap: {e}")

def get_weather_weatherapi(api_key, city):
    """
    Obtiene el tiempo actual de WeatherAPI.com.
    """
    base_url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": api_key,
        "q": city,
        "aqi": "no", # No solicitar datos de calidad del aire
        "lang": "es"
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        print("\n--- WeatherAPI.com ---")
        if data.get("current"):
            current_data = data["current"]
            condicion_texto = current_data["condition"]["text"]
            temperatura_c = current_data["temp_c"]
            sensacion_termica_c = current_data["feelslike_c"]
            humedad = current_data["humidity"]
            viento_kph = current_data["wind_kph"]
            presion_mb = current_data["pressure_mb"] # milibares, equivalente a hPa
            precip_mm = current_data["precip_mm"]
            visibilidad_km = current_data["vis_km"]

            print(f"Descripción: {condicion_texto}")
            print(f"Temperatura: {temperatura_c}°C")
            print(f"Sensación Térmica: {sensacion_termica_c}°C")
            print(f"Humedad: {humedad}%")
            print(f"Viento: {viento_kph:.2f} km/h")
            print(f"Presión: {presion_mb} hPa")
            print(f"Precipitación (última hora): {precip_mm} mm")
            print(f"Visibilidad: {visibilidad_km} km")
        else:
            print("No se pudieron obtener datos completos.")
            # pprint(data)
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con WeatherAPI.com: {e}")
    except json.JSONDecodeError:
        print("Error al decodificar la respuesta JSON de WeatherAPI.com.")
    except Exception as e:
        print(f"Error inesperado con WeatherAPI.com: {e}")

def get_weather_aemet(api_key, idema):
    """
    Obtiene la observación convencional más reciente de una estación de AEMET.
    'idema' es el indicativo climatológico de la estación.
    Para Madrid (Retiro) es "3195", Madrid (Aeropuerto) es "3129A".
    Usaremos la predicción por municipio ya que la observación directa puede no estar siempre disponible para todos.
    """
    print("\n--- AEMET (Agencia Estatal de Meteorología) ---")
    print(f"Intentando obtener predicción para el municipio: {CODIGO_MUNICIPIO_AEMET}")

    # AEMET requiere que la API key se pase en la cabecera
    headers = {
        'api_key': api_key,
        'Accept': 'application/json' # Solicitamos JSON
    }
    # URL para la predicción diaria del municipio
    url_prediccion_municipio = f"https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/diaria/{CODIGO_MUNICIPIO_AEMET}"

    try:
        # 1. Solicitar la URL de los datos específicos
        response_url_datos = requests.get(url_prediccion_municipio, headers=headers, verify=True) # verify=True es el default, se puede omitir
        response_url_datos.raise_for_status()
        datos_respuesta_url = response_url_datos.json()

        if datos_respuesta_url.get("estado") == 200 and datos_respuesta_url.get("datos"):
            url_datos_finales = datos_respuesta_url["datos"]

            # 2. Obtener los datos meteorológicos desde la URL proporcionada
            response_datos_finales = requests.get(url_datos_finales, headers=headers, verify=True)
            response_datos_finales.raise_for_status()
            prediccion_data = response_datos_finales.json()

            if prediccion_data and isinstance(prediccion_data, list) and len(prediccion_data) > 0:
                # La respuesta es una lista, tomamos el primer elemento que contiene la predicción
                prediccion_hoy = prediccion_data[0]["prediccion"]["dia"][0] # Predicción para hoy

                print(f"Fecha de predicción: {prediccion_hoy.get('fecha')}")

                # Estado del cielo (puede haber varios periodos)
                print("Estado del cielo:")
                for item in prediccion_hoy.get("estadoCielo", []):
                    periodo = item.get("periodo", "N/A")
                    descripcion = item.get("descripcion", "N/A")
                    print(f"  - Periodo {periodo}: {descripcion}")

                # Precipitación
                print("Precipitación:")
                for item in prediccion_hoy.get("probPrecipitacion", []):
                    periodo = item.get("periodo", "N/A")
                    probabilidad = item.get("value", "N/A")
                    print(f"  - Periodo {periodo}: {probabilidad}%")

                # Viento (puede haber varios periodos)
                print("Viento:")
                for item in prediccion_hoy.get("viento", []):
                    periodo = item.get("periodo", "N/A")
                    direccion = item.get("direccion", "N/A")
                    velocidad = item.get("velocidad", "N/A")
                    print(f"  - Periodo {periodo}: {direccion} a {velocidad} km/h")

                # Temperatura
                print(f"Temperatura Máxima: {prediccion_hoy['temperatura']['maxima']}°C")
                print(f"Temperatura Mínima: {prediccion_hoy['temperatura']['minima']}°C")
                if prediccion_hoy['sensTermica'].get('maxima') is not None:
                    print(f"Sensación Térmica Máxima: {prediccion_hoy['sensTermica']['maxima']}°C")
                if prediccion_hoy['sensTermica'].get('minima') is not None:
                    print(f"Sensación Térmica Mínima: {prediccion_hoy['sensTermica']['minima']}°C")

                # Humedad
                print(f"Humedad Relativa Máxima: {prediccion_hoy['humedadRelativa']['maxima']}%")
                print(f"Humedad Relativa Mínima: {prediccion_hoy['humedadRelativa']['minima']}%")

            else:
                print("No se encontraron datos de predicción detallados.")
                # pprint(prediccion_data) # Descomenta para ver la estructura si falla
        else:
            print(f"AEMET: No se pudo obtener la URL de los datos. Estado: {datos_respuesta_url.get('estado')}")
            print(f"Descripción: {datos_respuesta_url.get('descripcion')}")
            # pprint(datos_respuesta_url)

    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con AEMET: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Respuesta del servidor de AEMET: {e.response.text}")
    except json.JSONDecodeError:
        print("Error al decodificar la respuesta JSON de AEMET.")
    except Exception as e:
        print(f"Error inesperado con AEMET: {e}")

# --- Ejecución del Script ---
if __name__ == "__main__":
    print(f"Tiempo actual para {CIUDAD} según diferentes fuentes:")
    print(f"Fecha y Hora Actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Verificar si las claves API están configuradas (simple verificación)
    if "TU_API_KEY" in openweathermap_api_key:
        print("\nADVERTENCIA: La API Key de OpenWeatherMap no parece estar configurada.")
    else:
        get_weather_openweathermap(openweathermap_api_key, CIUDAD, CODIGO_PAIS_OWM)

    if "TU_API_KEY" in weather_api_key:
        print("\nADVERTENCIA: La API Key de WeatherAPI.com no parece estar configurada.")
    else:
        get_weather_weatherapi(weather_api_key, CIUDAD)

    if "TU_API_KEY" in aemet_api_key:
        print("\nADVERTENCIA: La API Key de AEMET no parece estar configurada.")
    else:
        # Para AEMET, usamos la predicción del municipio.
        # Si quieres observación directa de una estación, necesitarías un 'idema' diferente
        # y usar el endpoint de observación: /api/observacion/convencional/datos/estacion/{idema}
        # pero la predicción municipal es más robusta.
        get_weather_aemet(aemet_api_key, CODIGO_MUNICIPIO_AEMET)

    print("\n--- Fin del reporte del tiempo ---")
