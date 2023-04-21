import pickle
from flask import Flask, request, jsonify


with open('lin_reg.bin', 'rb') as f_in:
    model = pickle.load(f_in)


def prepare_features(ride):
    features = {}
    features['PULocationID'] = ride['PULocationID']
    features['DOLocationID'] = ride['DOLocationID']
    features['trip_distance'] = ride['trip_distance']
    return features


def predict(features):
    preds = model.predict(features)
    return float(preds[0])


app = Flask('duration-prediction')


@app.route('/predict', methods=['POST'])
def predict_endpoint():
    body = request.get_json()
    ride = body['ride']
    ride_id = body['ride_id']

    features = prepare_features(ride)
    pred = predict(features)

    result = {
        'prediction': {
            'duration': pred,
        }
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)