import requests
from flask import Flask, jsonify
from flask_cors import CORS  # Importar la extensión

app = Flask(__name__)
# CORS(app)  # Habilitar CORS para toda la aplicación
CORS(app, origins='http://127.0.0.1:5500')


# Datos de ejemplo (puedes usar una base de datos en su lugar)
data = [
    {"id": 1, "nombre": "Producto 1", "precio": 10.99},
    {"id": 2, "nombre": "Producto 2", "precio": 20.99},
    {"id": 3, "nombre": "Producto 3", "precio": 45.66}
]


def kangu_rastreo(tracking_number, token):
    url = f"https://portal.kangu.com.br/tms/transporte/rastrear/{tracking_number}"
    headers = {"token": token}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lanzará una excepción si hay un error en la solicitud
        data = response.json()

        if 'historico' in data:
            return {
                "dtPrevEnt": data.get('dtPrevEnt', ""),
                "error": data.get('error', {}),
                "historico": data['historico'],
                "situacion": data.get('situacion', {})
            }
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud de rastreo: {e}")
        return None


def frenet_rastreo(tracking_number, token):
    url = "https://private-anon-fd78d2c5ba-frenetapi.apiary-mock.com/tracking/trackinginfo"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "ShippingServiceCode": "04669",
        "TrackingNumber": tracking_number,
        "InvoiceNumber": "",
        "InvoiceSerie": "",
        "RecipientDocument": "",
        "OrderNumber": ""
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Lanzará una excepción si hay un error en la solicitud
        data = response.json()

        if 'TrackingEvents' in data:
            return {
                "ServiceDescription": data.get('ServiceDescription', ""),
                "TrackingEvents": data['TrackingEvents'],
                "TrackingNumber": data.get('TrackingNumber', "")
            }
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud de rastreo: {e}")
        return None


@app.route('/productos', methods=['GET'])
def get_productos():
    return jsonify(data)


@app.route('/kangu/<tracking_number>', methods=['GET'])
def rastrear_pedido_kangu(tracking_number):
    token = "040c0c1e1850e2aa468ea3efb2dc1735"  # Tu token aquí

    if not tracking_number:
        return jsonify({"error": "Número de seguimiento no proporcionado"}), 400

    kangu_data = kangu_rastreo(tracking_number, token)

    if kangu_data:
        formatted_data = {
            "TrackingNumber": tracking_number,
            "ServiceDescription": "Kangu",  # Puedes ajustar este valor según tu necesidad
            "TrackingEvents": kangu_data["historico"]  # Aquí usamos el historico de Kangu
        }
        return jsonify(formatted_data)
    else:
        return jsonify({"error": "Error en la solicitud de rastreo"}), 500


@app.route('/frenet/<tracking_number>', methods=['GET'])
def rastrear_pedido_frenet(tracking_number):
    token = "53D94A52RE1C6R449DRB38DR0B838E70B39D"  # Tu token aquí

    if not tracking_number:
        return jsonify({"error": "Número de seguimiento no proporcionado"}), 400

    frenet_data = frenet_rastreo(tracking_number, token)

    if frenet_data:
        formatted_data = {
            "TrackingNumber": frenet_data["TrackingNumber"],
            "ServiceDescription": frenet_data["ServiceDescription"],  # Corrección aquí
            "TrackingEvents": frenet_data["TrackingEvents"]
        }
        return jsonify(formatted_data)
    else:
        return jsonify({"error": "Error en la solicitud de rastreo"}), 500


if __name__ == '__main__':
    app.run(debug=True)