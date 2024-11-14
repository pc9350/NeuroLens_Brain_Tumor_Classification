
# NeuroLens: Brain Tumor Classification with Neural Networks

NeuroLens is a deep learning project designed to classify brain tumors in MRI scans using two neural network models: the **Xception model** (a pre-trained model using transfer learning) and a **custom Convolutional Neural Network (CNN)**. This project demonstrates how to build and train neural networks for healthcare applications, specifically for identifying tumor types such as gliomas, meningiomas, and pituitary tumors.

## Project Overview
- **Models Used:** Xception model with transfer learning, custom CNN model
- **Data:** MRI scans of brain tumors
- **Goal:** Classify tumors based on MRI images and provide model explanations using the Gemini 1.5 Flash model

## Features
- **Custom CNN Architecture:** Build and train a custom convolutional neural network from scratch.
- **Transfer Learning with Xception:** Use a pre-trained Xception model to enhance performance and reduce training time.
- **Model Explainability:** Generate explanations for model predictions using Gemini 1.5 Flash, highlighting key regions of the MRI scans.
- **End-to-End Pipeline:** From loading MRI data to prediction and visualization, the project provides a full classification and explanation pipeline.

## Table of Contents
1. [Installation](#installation)
2. [Usage](#usage)
3. [Model Training](#model-training)
4. [Explanation Generation](#explanation-generation)
5. [Results](#results)
6. [Technologies Used](#technologies-used)
7. [License](#license)

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/NeuroLens_Brain_Tumor_Classification.git
   cd NeuroLens_Brain_Tumor_Classification
   ```

2. **Install Dependencies:**
   Ensure you have Python 3.8 or higher, and then install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup API Key for Explanation Generation:**
   - Place your Google API key in a `.env` file:
     ```plaintext
     GOOGLE_API_KEY=your_api_key
     ```

## Usage

To run the application, use Streamlit:
```bash
streamlit run app.py
```
- Upload an MRI scan to classify.
- Choose between the **Xception** model or the **Custom CNN** model for predictions.
- The app will display classification results, confidence scores, and saliency maps with explanations generated by Gemini 1.5 Flash.

## Model Training

1. **Xception Model:** Utilizes transfer learning with pre-trained weights.
2. **Custom CNN Model:** A neural network built from scratch with convolutional and pooling layers tailored for MRI data.

Training scripts are available within the repository. You can adjust hyperparameters and model architecture as needed in the code.

## Explanation Generation

Using the **Gemini 1.5 Flash model**, this project provides model interpretability by highlighting the MRI regions that influence the predictions. Explanations are generated using the saliency map method, which shows areas of focus in each MRI scan.

## Results

The results section in the app displays:
- **Predicted Class**: The tumor type predicted by the model.
- **Confidence Score**: Model confidence in its prediction.
- **Saliency Map**: Visual representation of areas the model focused on during classification.

## Technologies Used
- **Python** and **TensorFlow/Keras** for building and training models.
- **Xception Model** for transfer learning.
- **Google Generative AI** (Gemini 1.5 Flash) for generating interpretability explanations.
- **Streamlit** for the interactive web app.
- **Plotly** and **OpenCV** for visualizations.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements
- Dataset and MRI scans sourced for research purposes.
- Inspired by healthcare AI applications and model interpretability research.