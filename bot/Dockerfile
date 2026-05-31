FROM tensorflow/tensorflow:2.15.0

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .
COPY predictor.py .
COPY visualizer.py .

COPY model_num_zones ./model_num_zones
COPY model_1_zone_part_2 ./model_1_zone_part_2
COPY model_2_zones_part_5 ./model_2_zones_part_5
COPY model_2_zones_part_6 ./model_2_zones_part_6

COPY model_1_zone_part_1.pkl .
COPY model_2_zones_part_1.pkl .
COPY model_2_zones_part_2.pkl .
COPY model_2_zones_part_3.pkl .
COPY model_2_zones_part_4.pkl .

COPY scaler_X_num_zones.pkl .

COPY scaler_X_1_zone_part_1.pkl .
COPY scaler_X_1_zone_part_2.pkl .
COPY scaler_X_2_zones_part_1.pkl .
COPY scaler_X_2_zones_part_2.pkl .
COPY scaler_X_2_zones_part_3.pkl .
COPY scaler_X_2_zones_part_4.pkl .
COPY scaler_X_2_zones_part_5.pkl .
COPY scaler_X_2_zones_part_6.pkl .

COPY scaler_y_1_zone_part_1.pkl .
COPY scaler_y_1_zone_part_2.pkl .
COPY scaler_y_2_zones_part_1.pkl .
COPY scaler_y_2_zones_part_2.pkl .
COPY scaler_y_2_zones_part_3.pkl .
COPY scaler_y_2_zones_part_4.pkl .
COPY scaler_y_2_zones_part_5.pkl .
COPY scaler_y_2_zones_part_6.pkl .

COPY dict.csv .

COPY config.ini .

RUN mkdir -p sessions

CMD ["python", "bot.py"]