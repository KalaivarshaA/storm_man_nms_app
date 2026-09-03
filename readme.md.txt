Storm Impact & Restoration Dashboard
This is a Streamlit app designed to visualize and simulate storm impact, restoration tracking, and outage management. The app generates simulated storm impact data and displays insights on affected customers, devices, restoration timelines, and crew requirements.

Features:
Customers Impacted vs Hours
Devices Impacted vs Customers per Device
Hours to Restore (Timeline)
Crews Required vs Days vs Existing Crews
Past vs Current Comparison (Pole counts)
Pie Charts and Tables
Simple Outage Detection
NMS Event Correlation (simulated)
Model for Outage Prediction (Random Forest Classifier)
How to Run:
Install the required dependencies:
   pip install streamlit pandas numpy plotly pydeck scikit-learn joblib
Run the Streamlit app:
   streamlit run storm_dashboard_streamlit.py
The app will open in your default web browser, displaying the dashboard with various interactive visualizations.
Overview:
This Streamlit app allows users to simulate storm impact data, track the restoration process, and correlate simulated Network Management System (NMS) events with actual outages. The data includes storm severity, restoration times, crews required, and customer impacts. Additionally, the app includes an Outage Prediction Model trained using a Random Forest Classifier, which allows users to predict outages based on key features.

App Components:
Storm Area & Poles Map: A map showing the storm-affected areas and poles, color-coded based on severity and wind speed. The map visualizes the storm's geographical impact.

Charts & Graphs:

Customers Impacted vs Restoration Hours: A line graph showing how customer impact changes with restoration time.
Devices Impacted vs Customers per Device: A bar chart showing customer impact per device type.
Hours to Restore (Timeline): A time-series chart displaying the average restoration time.
Crews Required vs Days vs Existing Crews: A bar and line chart showing the crews needed and available to handle the restoration.
Historical Data Comparison:
Past vs Current Pole Events: A bar chart comparing pole events from past storms versus current ones.
Outage Detection & NMS Correlation: Correlates actual outages with NMS events, showing the reliability of outage detection.
Outage Prediction: A trained Random Forest model can predict the likelihood of an outage based on inputs such as the number of customers impacted, restoration hours, crews required, and asset age. The model can be retrained on the current data set.

Data Export: Users can download the simulated data and the NMS correlation data as CSV files for further analysis.

Quick Actions:
Generate Data: Users can specify the number of records and other parameters to regenerate the mock data.
Train & Save Model: The app trains a Random Forest model to predict outages based on storm data and saves the model for future predictions.
Dependencies:
Streamlit: For building the interactive dashboard.
Pandas: For data manipulation.
NumPy: For generating mock data and performing mathematical operations.
Plotly: For creating interactive charts and visualizations.
PyDeck: For map visualizations.
Joblib: For saving and loading the trained machine learning model.
scikit-learn: For training and evaluating the Random Forest Classifier.
Example Usage:
Generate Mock Data: The app will generate storm-related data based on user inputs, such as the number of records, customer ranges, and crew requirements. This data is used for visualizing the storm impact, restoration times, and crew requirements.

Outage Prediction: Users can input data (e.g., the number of customers impacted, restoration hours, crews required, and asset age) to predict whether an outage is likely to occur using the trained Random Forest model.

NMS Correlation: The app correlates NMS event logs with storm outage records, providing insights into the accuracy of the NMS in detecting actual outages.

Future Enhancements:
Replace the mock data generator with real-world data or telemetry from storm management systems.
Integrate with actual asset databases to improve outage prediction accuracy.
Add more detailed severity models based on historical data or weather patterns.
Implement user authentication and role-based access for deployment in operational environments.
Contact:
For any questions or contributions, please reach out to the repository owner or submit an issue.
