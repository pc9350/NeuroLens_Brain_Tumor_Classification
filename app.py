
import streamlit as st
import tensorflow as tf
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import plotly.graph_objects as go
import cv2
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Dropout
from tensorflow.keras.optimizers import Adamax
from tensorflow.keras.metrics import Precision, Recall
import google.generativeai as genai
from google.colab import userdata
import PIL.Image
import os
from google.colab import userdata
from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

output_dir = 'saliency_maps'
os.makedirs(output_dir, exist_ok=True)

st.markdown(
    """
    <style>
    /* Set the entire page background */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"], .block-container {
        background-color: #1c1c1c; /* Dark grey */
        color: #FFFFFF; /* White text for readability */
    }
    
    /* Hide the footer */
    footer {visibility: hidden;}

    /* Set text color for the radio button group label */
    div[data-testid="stRadio"] > label {
        color: #FFFFFF !important; /* White color for the label text */
    }

    /* Set text color for the file uploader label (e.g., "Choose an image") */
    div[data-testid="stFileUploader"] > label {
        color: #FFFFFF !important; /* White color for the file uploader label */
    }

    /* Set text color for selected and unselected options */
    div[role="radiogroup"] label p {
        color: #FFFFFF !important; /* White text color */
    }

    /* Target the image caption */
    div.stImage div {
        color: #FFFFFF !important; /* Set caption text color to white */
    }
    </style>
    """,
    unsafe_allow_html=True
)

def generate_explanation(img_path, model_prediction, confidence):

  # prompt = f"""You are an expert neurologist. You are tasked with explaining a saliency map of a brain tumor MRI scan. The saliency map was generated by a deep
  #           learning model that was trained to classify brain tumors as either glioma, meningioma, pituitary, or no tumor.

  #           The saliency map highlights the regions of the iamge that the machine learning model is focusing on to make the prediction.

  #           the deep learning model predicted the image to be of class '{model_prediction}' with a confidence of {confidence * 100}%.

  #           In your response:
  #            - Explain what regions of the brain the model is focusing on, based on the saliency map. Refer to the regions highlighted in light cyan, those are the
  #            regions where the model is focusing on.
  #            - Explain possible reasons why the model made the prediction it did.
  #            - Don't mention anything like 'The saliency map highlights the regions the model is focusing on, which are in light cyan' in your explanation.
  #            - Keep your explanation to 4 sentences max.

  #            Let's think step by step about this. Verify step by step.
  #           """
  prompt = f"""You are an expert neurologist specializing in brain tumor diagnosis through MRI scans. You have been given a saliency map generated by a deep learning model that was trained to classify brain tumors into one of four categories: glioma, meningioma, pituitary tumor, or no tumor. The saliency map identifies which areas of the MRI scan the model is focusing on to make its prediction.

            The model has predicted the scan to belong to the class '{model_prediction}' with a confidence of {confidence * 100}%. Your task is to explain the saliency map and the reasoning behind the model's prediction.

            In your explanation:
            1. Identify and describe the brain regions highlighted in the saliency map, particularly those marked in light cyan. Explain how these regions are relevant to the type of tumor the model predicts, focusing on the typical locations of such tumors in the brain.
            2. Provide a brief, scientifically-backed rationale for why the model might have made this prediction based on the highlighted regions. Refer to general knowledge of brain tumor characteristics (e.g., gliomas often appear in specific brain regions, meningiomas are typically on the outer layers of the brain, etc.).
            3. Your response should avoid stating basic facts like 'The saliency map highlights areas in light cyan,' and instead focus directly on the clinical reasoning behind the model's focus on these regions.
            4. Limit your explanation to no more than 4 sentences.

            Please carefully consider the model’s prediction and the anatomical and clinical implications of the highlighted regions. Let's think step by step about this. Verify step by step."""

  img = PIL.Image.open(img_path)

  model = genai.GenerativeModel(model_name="gemini-1.5-flash")
  response = model.generate_content([prompt, img])

  return response.text

def generate_saliency_map(model, img_array, class_index, img_size):
  with tf.GradientTape() as tape:
    img_tensor = tf.convert_to_tensor(img_array)
    tape.watch(img_tensor)
    predictions = model(img_tensor)
    target_class = predictions[:, class_index]

  gradients = tape.gradient(target_class, img_tensor)
  gradients = tf.math.abs(gradients)
  gradients = tf.reduce_max(gradients, axis=-1)
  gradients = gradients.numpy().squeeze()

  # Resize gradietns to match original image size
  gradients = cv2.resize(gradients, img_size)

  # Create a circular mask for the brain area
  center = (gradients.shape[0] // 2, gradients.shape[1] // 2)
  radius = min(center[0], center[1]) - 10
  y, x = np.ogrid[:gradients.shape[0], :gradients.shape[1]]
  mask = (x - center[0])**2 + (y - center[1])**2 <= radius**2

  # Apply mask to gradients
  gradients = gradients * mask

  # Normalize only the brain area
  brain_gradients = gradients[mask]
  if brain_gradients.max() > brain_gradients.min():
    brain_gradients = (brain_gradients - brain_gradients.min()) / (brain_gradients.max() - brain_gradients.min())
  gradients[mask] = brain_gradients

  # Apply a higher threshold
  threshold = np.percentile(gradients[mask], 80)
  gradients[gradients < threshold] = 0

  # Apply more aggressive smoothing
  gradients = cv2.GaussianBlur(gradients, (11, 11), 0)

  # Create a heatmap overlay with enhanced contrast
  heatmap = cv2.applyColorMap(np.uint8(255 * gradients), cv2.COLORMAP_JET)
  heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)

  # Resize heatmap to match original image size
  heatmap = cv2.resize(heatmap, img_size)

  # Superimpose the heatmap on original image with increased opacity
  original_img = image.img_to_array(img)
  superimposed_img = heatmap * 0.7 + original_img * 0.3
  superimposed_img = superimposed_img.astype(np.uint8)

  img_path = os.path.join(output_dir, uploaded_file.name)
  with open(img_path, "wb") as f:
    f.write(uploaded_file.getbuffer())

  saliency_map_path = f'saliency_maps/{uploaded_file.name}'

  # Save the saliency map
  cv2.imwrite(saliency_map_path, cv2.cvtColor(superimposed_img, cv2.COLOR_RGB2BGR))

  return superimposed_img

def load_xception_model(model_path):
  img_shape=(299,299,3)
  base_model = tf.keras.applications.Xception(include_top=False, weights="imagenet", input_shape=img_shape, pooling='max')

  model = Sequential([
      base_model,
      Flatten(),
      Dropout(rate=0.3),
      Dense(128, activation='relu'),
      Dropout(rate=0.25),
      Dense(4, activation='softmax')
  ])

  model.build((None,) + img_shape)

  # Compile the model
  model.compile(Adamax(learning_rate=0.001),
                loss='categorical_crossentropy',
                metrics=['accuracy',
                         Precision(), Recall()])

  model.load_weights(model_path)

  return model


st.title("Brain Tumor Classification")

st.write("Upload an image of a brain MRI scan to classify.")

uploaded_file = st.file_uploader("Choose an image....", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:

  selected_model = st.radio(
      "Select Model",
      {"Transfer Learning - Xception", "Custom CNN"}
  )

  if selected_model == "Transfer Learning - Xception":
    model = load_xception_model('/content/xception_model.weights.h5')
    img_size = (299,299)
  else:
    model = load_model('/content/cnn_model.h5')
    img_size = (224,224)


  labels = ['Glioma', 'Meningioma', 'No Tumor', 'Pituitary']
  img = image.load_img(uploaded_file, target_size=img_size)
  img_array = image.img_to_array(img)
  img_array = np.expand_dims(img_array, axis=0) / 255.0

  prediction = model.predict(img_array)

  # Get the class with the highest probability
  class_index = np.argmax(prediction[0])
  result = labels[class_index]

  st.write(f"Predicted Class: {result}")
  st.write("Predictions:")
  for label, prob in zip(labels, prediction[0]):
    st.write(f"{label}: {prob:.4f}")


  saliency_map = generate_saliency_map(model, img_array, class_index, img_size)

  col1, col2 = st.columns(2)
  with col1:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
  with col2:
    st.image(saliency_map, caption="Saliency Map", use_container_width=True)

  st.write("## Classification Results")

  result_container = st.container()
  result_container = st.container()
  result_container.markdown(
      f"""
      <div style="background-color: #000000; color: #ffffff; padding: 30px; border-radius: 15px;">
        <div style="display: flex; justify-content: space-between; align-items: center:">
          <div style="flex: 1; text-align: center;">
            <h3 style="color: #ffffff; margin-bottom: 10px; font-size: 20px;">Prediction</h3>
            <p style="font-size: 36px; font-weight: 800; color: #FF0000; margin: 0;">
              {result}
            </p>
          </div>
          <div style="width: 2px; height: 80px; background-color: #ffffff; margin: 0 20px;"></div>
          <div style="flex: 1; text-align: center;">
            <h3 style="color: #ffffff; margin-bottom: 10px; font-size: 20px;">Confidence</h3>
            <p style="font-size: 36px; font-weight: 800; color: #2196F3; margin: 0;">
              {prediction[0][class_index]:.4%}
            </p>
          </div>
        </div>
      </div>
      """,
      unsafe_allow_html=True
  )

  # Prepare data for the plotly chart
  probabilities = prediction[0]
  sorted_indices = np.argsort(probabilities)[::-1]
  sorted_labels = [labels[i] for i in sorted_indices]
  sorted_probabilities = probabilities[sorted_indices]

  # Create a plotly bar chart
  fig = go.Figure(go.Bar(
      x=sorted_probabilities,
      y=sorted_labels,
      orientation='h',
      marker_color=['red' if label == result else 'blue' for label in sorted_labels]
  ))

  # Customize the chart layout
  fig.update_layout(
      title='Probabilities for each class',
      xaxis=dict(
        title='Probability',
        title_font=dict(color='#FFFFFF'),  # Set x-axis label color to white
        tickfont=dict(color='#FFFFFF')     # Set x-axis tick values color to white
      ),
      yaxis=dict(
        title='Class',
        title_font=dict(color='#FFFFFF'),  # Set y-axis label color to white
        tickfont=dict(color='#FFFFFF'),    # Set y-axis tick values color to white
        autorange='reversed'               # Keep y-axis reversed as before
      ),
      height=400,
      width=600,
      plot_bgcolor='#1c1c1c',  # Set the plot area background to match page color
      paper_bgcolor='#1c1c1c',  # Set the outer area background to match page color
      font=dict(color='#FFFFFF'),  # Set text color to white
      title_font=dict(color='#FFFFFF')  # Set title text color to white
  )

  # Add value labels to the bars
  for i, prob in enumerate(sorted_probabilities):
    fig.add_annotation(
        x=prob,
        y=i,
        text=f'{prob:.4f}',
        showarrow=False,
        xanchor='left',
        xshift=5
    )

  # Display the plotly chart
  st.plotly_chart(fig)

  saliency_map_path = f'saliency_maps/{uploaded_file.name}'
  explanation = generate_explanation(saliency_map_path, result, prediction[0][class_index])

  st.write("## Explanation:")
  st.write(explanation)

