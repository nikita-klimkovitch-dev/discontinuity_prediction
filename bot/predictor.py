import numpy as np
import joblib
from tensorflow.keras.models import load_model
import tensorflow as tf

class ZonePredictator:
    def __init__(self):

        self.scaler_X_num_zones = joblib.load('scaler_X_num_zones.pkl')
        self.model_num_zones = tf.keras.models.load_model('model_num_zones')

        self.scaler_X_1_zone_part_1 = joblib.load('scaler_X_1_zone_part_1.pkl')
        self.scaler_y_1_zone_part_1 = joblib.load('scaler_y_1_zone_part_1.pkl')
        self.scaler_X_1_zone_part_2 = joblib.load('scaler_X_1_zone_part_2.pkl')
        self.scaler_y_1_zone_part_2 = joblib.load('scaler_y_1_zone_part_2.pkl')
        self.model_1_zone_part_1 = joblib.load('model_1_zone_part_1.pkl')
        self.model_1_zone_part_2 = tf.keras.models.load_model('model_1_zone_part_2')

        self.scaler_X_1 = joblib.load('scaler_X_2_zones_part_1.pkl')
        self.scaler_y_1 = joblib.load('scaler_y_2_zones_part_1.pkl')
        self.scaler_X_2 = joblib.load('scaler_X_2_zones_part_2.pkl')
        self.scaler_y_2 = joblib.load('scaler_y_2_zones_part_2.pkl')
        self.scaler_X_3 = joblib.load('scaler_X_2_zones_part_3.pkl')
        self.scaler_y_3 = joblib.load('scaler_y_2_zones_part_3.pkl')
        self.scaler_X_4 = joblib.load('scaler_X_2_zones_part_4.pkl')
        self.scaler_y_4 = joblib.load('scaler_y_2_zones_part_4.pkl')
        self.scaler_X_5 = joblib.load('scaler_X_2_zones_part_5.pkl')
        self.scaler_y_5 = joblib.load('scaler_y_2_zones_part_5.pkl')
        self.scaler_X_6 = joblib.load('scaler_X_2_zones_part_6.pkl')
        self.scaler_y_6 = joblib.load('scaler_y_2_zones_part_6.pkl')
        self.reg_1 = joblib.load('model_2_zones_part_1.pkl')
        self.reg_2 = joblib.load('model_2_zones_part_2.pkl')
        self.reg_3 = joblib.load('model_2_zones_part_3.pkl')
        self.reg_4 = joblib.load('model_2_zones_part_4.pkl')
        self.model_5 = tf.keras.models.load_model('model_2_zones_part_5')
        self.model_6 = tf.keras.models.load_model('model_2_zones_part_6')

        print(f"Модель загружена")
    
    def predict_num_zones(self, displacements):
        
        X_scaled = self.scaler_X_num_zones.transform([displacements])
        clf = self.model_num_zones
        pred_num = clf.predict(X_scaled)

        return np.argmax(pred_num) + 1
    
    def get_real_zones(self, displacements):

        num_of_zones = self.predict_num_zones(displacements)
        
        if num_of_zones == 1:
            X = [displacements]
            X_scaled = self.scaler_X_1_zone_part_1.transform(X)
            pred_id = self.scaler_y_1_zone_part_1.inverse_transform(self.model_1_zone_part_1.predict(X_scaled).reshape(-1,1))
            
            X_new = np.hstack((X, pred_id))
            X_scaled_new = self.scaler_X_1_zone_part_2.transform(X_new)
            ab_pred_scal = self.model_1_zone_part_2.predict(X_scaled_new)
            ab_pred = self.scaler_y_1_zone_part_2.inverse_transform(ab_pred_scal)
            pred_data = np.hstack((np.round(pred_id), ab_pred))
        elif num_of_zones == 2:
            X = [displacements]
            
            X_scaled = self.scaler_X_1.transform(X)
            pred = self.scaler_y_1.inverse_transform(self.reg_1.predict(X_scaled).reshape(-1,1))
            X_new = np.hstack((X, pred))
            
            X_scaled = self.scaler_X_2.transform(X_new)
            pred = self.scaler_y_2.inverse_transform(self.reg_2.predict(X_scaled).reshape(-1,1))
            X_new = np.hstack((X_new, pred))

            X_scaled = self.scaler_X_3.transform(X_new)
            pred = self.scaler_y_3.inverse_transform(self.reg_3.predict(X_scaled).reshape(-1,1))
            X_new = np.hstack((X_new, pred))

            X_scaled = self.scaler_X_4.transform(X_new)
            pred = self.scaler_y_4.inverse_transform(self.reg_4.predict(X_scaled).reshape(-1,1))
            X_new = np.hstack((X_new, pred))

            X_scaled = self.scaler_X_5.transform(X_new)
            pred_scal = self.model_5.predict(X_scaled)
            pred = self.scaler_y_5.inverse_transform(pred_scal)
            X_new = np.hstack((X_new, pred))

            X_scaled = self.scaler_X_6.transform(X_new)
            pred_scal = self.model_6.predict(X_scaled)
            pred = self.scaler_y_6.inverse_transform(pred_scal)
            X_new = np.hstack((X_new, pred))

            pred_data = X_new[:,3:]
            #'ar1', 'el_id1', 'el_a1', 'ar2', 'el_id2', 'el_a2'
            pred_data = pred_data[:, [1, 2, 0, 4, 5, 3]]
            #id1, a1, ar1, id2, a2, ar2
            print(pred_data)
            pred_data[:, 2] = pred_data[:, 2] / pred_data[:, 1]
            pred_data[:, 5] = pred_data[:, 5] / pred_data[:, 4]
            #id1, a1, b1, id2, a2, b2
            pred_data[:, 0] = np.round(pred_data[:, 0])
            pred_data[:, 3] = np.round(pred_data[:, 3])
        else:
            print('error')
            return None
   
        
        return [num_of_zones, pred_data[0]]