import streamlit as st
import time
import os
import shutil
import subprocess
import smtplib
from email.mime.text import MIMEText
import webbrowser # For opening URLs in browser
import zipfile # For zipping/unzipping files
import json # For parsing Docker inspect output and JSON input for ML prediction
import platform # Required for system information in Windows tasks

# Import ML libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import joblib # For model persistence

from sklearn.model_selection import train_test_split, GridSearchCV, KFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
from sklearn.cluster import KMeans
from sklearn.metrics import (
    accuracy_score, r2_score, silhouette_score,
    precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix,
    mean_absolute_error, mean_squared_error, roc_curve # Added roc_curve for ROC plot
)
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

# Interactive plotting library
import plotly.express as px
import plotly.graph_objects as go

# Conditional imports for libraries that might not be present by default
try:
    import pyautogui # For simulating mouse/keyboard interactions
except ImportError:
    pyautogui = None

try:
    import cv2 # For webcam access and video recording
except ImportError:
    cv2 = None

try:
    import psutil # For system information (disk usage, processes)
except ImportError:
    psutil = None

try:
    import wmi # For Windows Management Instrumentation (e.g., listing installed programs)
except ImportError:
    wmi = None
    # st.warning("`wmi` not found. Install with `pip install wmi` for some Windows functionalities.") # Removed warning to avoid early Streamlit call

try:
    import pywhatkit # For sending WhatsApp messages
except ImportError:
    pywhatkit = None

try:
    import paramiko # For SSH connections
except ImportError:
    paramiko = None
    # st.warning("`paramiko` not found. Install with `pip install paramiko` for SSH functionality.") # Removed warning to avoid early Streamlit call

try:
    import xgboost as xgb # For XGBoost models
except ImportError:
    xgb = None
    # st.warning("`xgboost` not found. Install with `pip install xgboost` for XGBoost models.") # Removed warning to avoid early Streamlit call

try:
    import lightgbm as lgb # For LightGBM models
except ImportError:
    lgb = None
    # st.warning("`lightgbm` not found. Install with `pip install lightgbm` for LightGBM models.") # Removed warning to avoid early Streamlit call

from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC, SVR
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB


def display_ml_upload_filter_tasks():
    st.title("📁 Data Upload & Preprocessing")

    uploaded_file = st.file_uploader("Upload CSV file", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.session_state.df = df
        st.session_state.filtered_df = df.copy()

        st.subheader("🔍 Data Preview")
        st.dataframe(df.head())

        st.subheader("🔧 Preprocessing Options")
        col1, col2 = st.columns(2)
        with col1:
            imputation_strategy = st.selectbox(
                "Missing Value Imputation Strategy",
                ["Median (Numeric)", "Most Frequent (Categorical)", "Mean (Numeric)"],
                key="imputation_strategy"
            )
        with col2:
            scaling_strategy = st.selectbox(
                "Feature Scaling Strategy (Numeric)",
                ["None", "StandardScaler", "MinMaxScaler"],
                key="scaling_strategy"
            )

        one_hot_encode_cols = st.multiselect(
            "Select columns for One-Hot Encoding (Categorical)",
            [col for col in df.columns if df[col].dtype == 'object' or df[col].dtype.name == 'category'],
            key="ohe_cols"
        )

        if st.button("Apply Preprocessing"):
            processed_df = df.copy()
            numeric_cols = processed_df.select_dtypes(include=np.number).columns
            categorical_cols = processed_df.select_dtypes(include=['object', 'category']).columns

            # Imputation
            for col in processed_df.columns:
                if processed_df[col].isnull().any():
                    if processed_df[col].dtype == 'object' or processed_df[col].dtype.name == 'category':
                        imputer = SimpleImputer(strategy='most_frequent')
                        # FIX: Use .ravel() to convert the 2D array to a 1D array
                        processed_df[col] = imputer.fit_transform(processed_df[[col]]).ravel()
                    elif processed_df[col].dtype == 'int64' or processed_df[col].dtype == 'float64':
                        if imputation_strategy == "Median (Numeric)":
                            imputer = SimpleImputer(strategy='median')
                        elif imputation_strategy == "Mean (Numeric)":
                            imputer = SimpleImputer(strategy='mean')
                        else: # Most Frequent (Numeric)
                            imputer = SimpleImputer(strategy='most_frequent')
                        # FIX: Use .ravel() here as well
                        processed_df[col] = imputer.fit_transform(processed_df[[col]]).ravel()
            st.success("Missing values imputed.")

            # One-Hot Encoding
            if one_hot_encode_cols:
                # Identify columns that are truly categorical and not already numeric after LabelEncoding
                cols_to_ohe = [col for col in one_hot_encode_cols if col in categorical_cols]
                if cols_to_ohe:
                    preprocessor = ColumnTransformer(
                        transformers=[
                            ('cat', OneHotEncoder(handle_unknown='ignore'), cols_to_ohe)
                        ],
                        remainder='passthrough'
                    )
                    # Fit and transform, then convert back to DataFrame
                    transformed_array = preprocessor.fit_transform(processed_df)
                    # Get new column names
                    ohe_feature_names = preprocessor.named_transformers_['cat'].get_feature_names_out(cols_to_ohe)
                    remaining_cols = [col for col in processed_df.columns if col not in cols_to_ohe]
                    new_columns = list(ohe_feature_names) + remaining_cols
                    processed_df = pd.DataFrame(transformed_array, columns=new_columns, index=processed_df.index)
                    st.success(f"Columns {', '.join(cols_to_ohe)} One-Hot Encoded.")
                else:
                    st.info("No suitable categorical columns found for One-Hot Encoding among selected.")

            # Label Encoding for remaining categorical columns not OHE'd
            for col in processed_df.columns:
                if (processed_df[col].dtype == 'object' or processed_df[col].dtype.name == 'category') and col not in one_hot_encode_cols:
                    processed_df[col] = LabelEncoder().fit_transform(processed_df[col])
                    st.info(f"Column '{col}' Label Encoded.")

            # Feature Scaling
            if scaling_strategy != "None":
                numeric_cols_after_ohe = processed_df.select_dtypes(include=np.number).columns.tolist()
                if scaling_strategy == "StandardScaler":
                    scaler = StandardScaler()
                elif scaling_strategy == "MinMaxScaler":
                    scaler = MinMaxScaler()
                
                if numeric_cols_after_ohe:
                    processed_df[numeric_cols_after_ohe] = scaler.fit_transform(processed_df[numeric_cols_after_ohe])
                    st.success(f"Numeric columns scaled using {scaling_strategy}.")
                else:
                    st.warning("No numeric columns found for scaling after imputation and encoding.")

            st.session_state.filtered_df = processed_df
            st.success("Preprocessing complete!")
            st.dataframe(processed_df.head())

        st.subheader("🔧 Multi-Column Filters")
        filter_cols = st.multiselect("Select columns to filter", df.columns.tolist())
        filter_values = {}

        filtered_df = df.copy()
        for col in filter_cols:
            options = df[col].dropna().unique().tolist()
            if options: # Ensure options are not empty
                default_index = 0
                if f"filter_{col}" in st.session_state and st.session_state[f"filter_{col}"] in options:
                    default_index = options.index(st.session_state[f"filter_{col}"])
                val = st.selectbox(f"Filter {col}", options, index=default_index, key=f"filter_{col}")
                filter_values[col] = val
                filtered_df = filtered_df[filtered_df[col] == val]
            else:
                st.warning(f"No unique values found for filtering in column '{col}'.")


        st.session_state.filtered_df = filtered_df

        st.success(f"✅ Filtered rows: {len(filtered_df)}")
        st.dataframe(filtered_df)

        with st.expander("📊 Data Summary", expanded=True):
            st.write("Shape:", filtered_df.shape)
            st.write("📊 Summary Statistics")
            st.dataframe(filtered_df.describe())
            st.write("Missing Values:")
            st.dataframe(filtered_df.isnull().sum().rename("Missing Count"))

        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇ Download Filtered CSV", data=csv, file_name="filtered_data.csv", mime="text/csv")

    else:
        st.info("Upload a CSV file to start.")

def display_ml_visualize_tasks():
    st.title("📊 Visualize Data")

    df = st.session_state.filtered_df if st.session_state.filtered_df is not None else st.session_state.df

    if df is None:
        st.warning("Please upload and filter your data first on 'Data Upload & Preprocessing' page.")
    else:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

        chart_type = st.selectbox("Select Chart Type", ["Line", "Bar", "Area", "Pie", "Histogram", "Scatter"])

        # Helper function for plotting and downloading charts (using Plotly for interactivity)
        def plot_and_download_chart_plotly(df_to_plot, chart_type, x_col=None, y_col=None, pie_col=None, hist_col=None, bins=None):
            fig = None
            if chart_type == "Scatter":
                fig = px.scatter(df_to_plot, x=x_col, y=y_col, title=f"Scatter Plot: {x_col} vs {y_col}")
            elif chart_type == "Bar":
                fig = px.bar(df_to_plot, x=x_col, y=y_col, title=f"Bar Chart: {x_col} vs {y_col}")
            elif chart_type == "Line":
                fig = px.line(df_to_plot, x=x_col, y=y_col, title=f"Line Plot: {x_col} vs {y_col}")
            elif chart_type == "Pie":
                if pie_col and not df_to_plot[pie_col].empty:
                    counts = df_to_plot[pie_col].value_counts().reset_index()
                    counts.columns = [pie_col, 'count']
                    fig = px.pie(counts, values='count', names=pie_col, title=f"Pie Chart of {pie_col}")
                else:
                    st.error("No data or column selected for Pie Chart.")
                    return
            elif chart_type == "Histogram":
                if hist_col and not df_to_plot[hist_col].empty:
                    fig = px.histogram(df_to_plot, x=hist_col, nbins=bins, title=f"Histogram of {hist_col}")
                else:
                    st.error("No data or column selected for Histogram.")
                    return
            elif chart_type == "Area":
                fig = px.area(df_to_plot, x=x_col, y=y_col, title=f"Area Chart: {x_col} vs {y_col}")
            else:
                st.error("Unsupported chart type!")
                return

            if fig:
                st.plotly_chart(fig, use_container_width=True)

                # Download button for Plotly figures (can save as HTML or static image)
                # For simplicity, we'll offer HTML which is interactive.
                html_export = fig.to_html(full_html=False, include_plotlyjs='cdn')
                st.download_button(
                    label=f"📥 Download {chart_type} Chart as HTML",
                    data=html_export,
                    file_name=f"{chart_type.lower()}_chart.html",
                    mime="text/html"
                )


        if chart_type in ["Line", "Bar", "Area", "Scatter"]:
            x_col = st.selectbox("X-axis", numeric_cols, key="x_col_viz")
            y_col = st.selectbox("Y-axis", numeric_cols, key="y_col_viz")
            if st.button("Generate Chart", key="generate_xy_chart"):
                if x_col and y_col:
                    plot_and_download_chart_plotly(df, chart_type, x_col=x_col, y_col=y_col)
                else:
                    st.warning("Please select both X and Y axes.")

        elif chart_type == "Pie":
            if categorical_cols:
                pie_col = st.selectbox("Select categorical column", categorical_cols, key="pie_col_viz")
                if st.button("Generate Pie Chart", key="generate_pie_chart"):
                    if pie_col:
                        plot_and_download_chart_plotly(df, chart_type, pie_col=pie_col)
                    else:
                        st.warning("Please select a categorical column.")
            else:
                st.warning("No categorical columns available for Pie Chart.")

        elif chart_type == "Histogram":
            if numeric_cols:
                hist_col = st.selectbox("Select numeric column", numeric_cols, key="hist_col_viz")
                bins = st.slider("Bins", 5, 50, 10, key="hist_bins_viz")
                if st.button("Generate Histogram", key="generate_hist_chart"):
                    if hist_col:
                        plot_and_download_chart_plotly(df, chart_type, hist_col=hist_col, bins=bins)
                    else:
                        st.warning("Please select a numeric column.")
            else:
                st.warning("No numeric columns available for Histogram.")

def display_ml_trainer_tasks():
    st.title("🧠 Smart ML Trainer")

    df = st.session_state.filtered_df if st.session_state.filtered_df is not None else st.session_state.df

    if df is None:
        st.info("Upload and filter dataset first on 'Data Upload & Preprocessing' page.")
        return

    st.write("### 🔍 Data Preview")
    st.dataframe(df.head())

    # Helper functions for ML Trainer (defined locally to avoid global namespace pollution)
    def auto_target_col(df_input):
        for col in df_input.columns:
            if 2 <= df_input[col].nunique() <= 20: # Heuristic for classification target
                return col
        return df_input.columns[-1] # Default to last column for regression

    target = st.selectbox("🎯 Select Target Column", df.columns, index=df.columns.get_loc(auto_target_col(df)))

    # Determine task type based on target column's unique values
    # Ensure target column is preprocessed before checking nunique
    temp_target_series = df[target].copy()
    if temp_target_series.dtype == 'object' or temp_target_series.dtype.name == 'category':
        temp_target_series = LabelEncoder().fit_transform(temp_target_series.astype(str).fillna(temp_target_series.mode()[0]))
    
    task_type = "Classification" if pd.Series(temp_target_series).nunique() <= 20 else "Regression"
    st.info(f"Detected: {task_type} Problem")

    # Split data into X and y
    X = df.drop(columns=[target])
    y = df[target]

    # Preprocessing pipeline for ML models
    # Identify numerical and categorical columns for the pipeline
    numerical_cols = X.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()

    # Preprocessing options
    st.sidebar.subheader("ML Preprocessing Options")
    imputation_strategy = st.sidebar.selectbox(
        "Missing Value Imputation",
        ["median", "mean", "most_frequent"],
        key="ml_imputation_strategy"
    )
    scaling_strategy = st.sidebar.selectbox(
        "Feature Scaling",
        ["None", "StandardScaler", "MinMaxScaler"],
        key="ml_scaling_strategy"
    )
    apply_ohe = st.sidebar.checkbox("Apply One-Hot Encoding to Categorical Features", value=True, key="ml_ohe_checkbox")

    # Create preprocessing steps
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy=imputation_strategy))
    ])
    if scaling_strategy == "StandardScaler":
        numeric_transformer.steps.append(('scaler', StandardScaler()))
    elif scaling_strategy == "MinMaxScaler":
        numeric_transformer.steps.append(('scaler', MinMaxScaler()))

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent'))
    ])
    if apply_ohe:
        categorical_transformer.steps.append(('onehot', OneHotEncoder(handle_unknown='ignore')))
    else:
        pass # If not OHE, we rely on LabelEncoder from initial preprocessing or model's ability to handle integers.

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numerical_cols),
            ('cat', categorical_transformer, categorical_cols)
        ],
        remainder='passthrough' # Keep other columns (e.g., if some are already numeric and not in numerical_cols)
    )

    # Model Selection & Hyperparameters
    st.sidebar.subheader("Model Configuration")
    selected_model_name = st.sidebar.selectbox("Select ML Model",
                                             ["Random Forest", "Gradient Boosting", "Logistic Regression", "K-Nearest Neighbors", "Support Vector Machine", "Decision Tree", "Naive Bayes", "Linear Regression", "Ridge Regression", "Lasso Regression", "XGBoost", "LightGBM"],
                                             key="selected_ml_model")

    # Model Persistence
    st.sidebar.subheader("Model Persistence")
    model_filename = st.sidebar.text_input("Model Filename (e.g., my_model.joblib)", "trained_model.joblib")
    
    if st.sidebar.button("Save Trained Model", key="save_model_btn"):
        if 'best_trained_model' in st.session_state and st.session_state.best_trained_model is not None:
            try:
                joblib.dump(st.session_state.best_trained_model, model_filename)
                st.sidebar.success(f"Model saved as '{model_filename}'")
            except Exception as e:
                st.sidebar.error(f"Error saving model: {e}")
        else:
            st.sidebar.warning("No model has been trained yet to save.")

    uploaded_model_file = st.sidebar.file_uploader("Upload Model to Load (.joblib)", type=["joblib"], key="load_model_uploader")
    if uploaded_model_file:
        try:
            loaded_model = joblib.load(uploaded_model_file)
            st.session_state.loaded_model = loaded_model
            st.sidebar.success(f"Model '{uploaded_model_file.name}' loaded successfully.")
            st.sidebar.info(f"Loaded model type: {type(loaded_model['classifier_regressor']).__name__}")
        except Exception as e:
            st.sidebar.error(f"Error loading model: {e}")

    # Train and Evaluate Models Button
    if st.button("🚀 Train & Evaluate Model", key="train_evaluate_btn"):
        # Model Instantiation and Pipeline creation moved inside the button click
        model_instance = None
        model_params = {}

        if selected_model_name == "Random Forest":
            n_estimators = st.sidebar.slider("n_estimators", 50, 500, 100, key="rf_n_estimators_run") # Changed key
            max_depth = st.sidebar.slider("max_depth", 2, 20, 10, key="rf_max_depth_run") # Changed key
            model_params = {'n_estimators': n_estimators, 'max_depth': max_depth, 'random_state': 42}
            model_instance = RandomForestClassifier(**model_params) if task_type == "Classification" else RandomForestRegressor(**model_params)
        elif selected_model_name == "Gradient Boosting":
            n_estimators = st.sidebar.slider("n_estimators", 50, 500, 100, key="gb_n_estimators_run") # Changed key
            learning_rate = st.sidebar.slider("learning_rate", 0.01, 0.5, 0.1, key="gb_learning_rate_run") # Changed key
            model_params = {'n_estimators': n_estimators, 'learning_rate': learning_rate, 'random_state': 42}
            model_instance = GradientBoostingClassifier(**model_params) if task_type == "Classification" else GradientBoostingRegressor(**model_params)
        elif selected_model_name == "Logistic Regression":
            C = st.sidebar.slider("C (Regularization)", 0.01, 10.0, 1.0, key="lr_C_run") # Changed key
            model_params = {'C': C, 'max_iter': 5000}
            model_instance = LogisticRegression(**model_params)
        elif selected_model_name == "Linear Regression":
            model_instance = LinearRegression()
        elif selected_model_name == "K-Nearest Neighbors":
            n_neighbors = st.sidebar.slider("n_neighbors", 1, 20, 5, key="knn_n_neighbors_run") # Changed key
            model_params = {'n_neighbors': n_neighbors}
            model_instance = KNeighborsClassifier(**model_params)
        elif selected_model_name == "Support Vector Machine":
            C_svm = st.sidebar.slider("C (SVM)", 0.1, 10.0, 1.0, key="svm_C_run") # Changed key
            kernel = st.sidebar.selectbox("Kernel", ["rbf", "linear", "poly", "sigmoid"], key="svm_kernel_run") # Changed key
            model_params = {'C': C_svm, 'kernel': kernel}
            model_instance = SVC(**model_params) if task_type == "Classification" else SVR(**model_params)
        elif selected_model_name == "Decision Tree":
            max_depth_dt = st.sidebar.slider("max_depth", 2, 20, 10, key="dt_max_depth_run") # Changed key
            model_params = {'max_depth': max_depth_dt, 'random_state': 42}
            model_instance = DecisionTreeClassifier(**model_params)
        elif selected_model_name == "Naive Bayes":
            model_instance = GaussianNB()
        elif selected_model_name == "Ridge Regression":
            alpha_ridge = st.sidebar.slider("alpha (Regularization)", 0.01, 10.0, 1.0, key="ridge_alpha_run") # Changed key
            model_params = {'alpha': alpha_ridge}
            model_instance = Ridge(**model_params)
        elif selected_model_name == "Lasso Regression":
            alpha_lasso = st.sidebar.slider("alpha (Regularization)", 0.01, 10.0, 1.0, key="lasso_alpha_run") # Changed key
            model_params = {'alpha': alpha_lasso}
            model_instance = Lasso(**model_params)
        elif selected_model_name == "XGBoost":
            if xgb:
                n_estimators_xgb = st.sidebar.slider("n_estimators", 50, 500, 100, key="xgb_n_estimators_run") # Changed key
                learning_rate_xgb = st.sidebar.slider("learning_rate", 0.01, 0.5, 0.1, key="xgb_learning_rate_run") # Changed key
                model_params = {'n_estimators': n_estimators_xgb, 'learning_rate': learning_rate_xgb, 'random_state': 42, 'use_label_encoder': False, 'eval_metric': 'logloss' if task_type == 'Classification' else 'rmse'}
                model_instance = xgb.XGBClassifier(**model_params) if task_type == "Classification" else xgb.XGBRegressor(**model_params)
            else:
                st.warning("XGBoost not installed. Please install with `pip install xgboost`.")
                model_instance = None # Explicitly set to None if not available
        elif selected_model_name == "LightGBM":
            if lgb:
                n_estimators_lgb = st.sidebar.slider("n_estimators", 50, 500, 100, key="lgb_n_estimators_run") # Changed key
                learning_rate_lgb = st.sidebar.slider("learning_rate", 0.01, 0.5, 0.1, key="lgb_learning_rate_run") # Changed key
                model_params = {'n_estimators': n_estimators_lgb, 'learning_rate': learning_rate_lgb, 'random_state': 42}
                model_instance = lgb.LGBMClassifier(**model_params) if task_type == "Classification" else lgb.LGBMRegressor(**model_params)
            else:
                st.warning("LightGBM not installed. Please install with `pip install lightgbm`.")
                model_instance = None # Explicitly set to None if not available

        # Create a full pipeline with preprocessing and model
        if model_instance is not None:
            full_pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                             ('classifier_regressor', model_instance)])
        else:
            full_pipeline = None

        if full_pipeline is None:
            st.error("Selected model is not available or could not be initialized. Please check installations.")
            return

        # Data Splitting and Cross-Validation Options (re-read from sidebar as they are outside the button)
        test_size = st.sidebar.slider("Test Set Size (%)", 10, 50, 30, key="test_size_slider") / 100.0
        use_cross_val = st.sidebar.checkbox("Use K-Fold Cross-Validation", key="use_cv_checkbox") # This key is outside the button, so it's fine
        if use_cross_val:
            n_splits = st.sidebar.slider("Number of Folds (K)", 2, 10, 5, key="cv_n_splits") # This key is outside the button, so it's fine


        # Convert target to numeric if it's still object/category (after initial preprocessing)
        if y.dtype == 'object' or y.dtype.name == 'category':
            y = LabelEncoder().fit_transform(y.astype(str).fillna(y.mode()[0]))

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

        st.session_state.best_trained_model = None # Reset best model on new training run

        with st.spinner("Training and evaluating model..."):
            try:
                if use_cross_val:
                    cv_scores = cross_val_score(full_pipeline, X, y, cv=n_splits, scoring='accuracy' if task_type == 'Classification' else 'r2')
                    st.success(f"Cross-Validation Scores: {cv_scores}")
                    st.success(f"Mean CV Score: {np.mean(cv_scores):.3f} (Std: {np.std(cv_scores):.3f})")
                    # For CV, we train on full data for the 'best_trained_model' to be saved
                    full_pipeline.fit(X, y)
                    st.session_state.best_trained_model = full_pipeline
                    st.info("Model trained on full dataset for saving after cross-validation.")
                else:
                    full_pipeline.fit(X_train, y_train)
                    pred = full_pipeline.predict(X_test)
                    
                    st.session_state.best_trained_model = full_pipeline # Store the trained model

                    if task_type == "Classification":
                        score = accuracy_score(y_test, pred)
                        st.success(f"✅ Model Accuracy: {score:.3f}")
                        st.write("### Classification Metrics")
                        st.write(f"Precision: {precision_score(y_test, pred, average='weighted', zero_division=0):.3f}")
                        st.write(f"Recall: {recall_score(y_test, pred, average='weighted', zero_division=0):.3f}")
                        st.write(f"F1-Score: {f1_score(y_test, pred, average='weighted', zero_division=0):.3f}")
                        try:
                            auc_score = roc_auc_score(y_test, full_pipeline.predict_proba(X_test)[:, 1], multi_class='ovr')
                            st.write(f"ROC AUC: {auc_score:.3f}")
                        except Exception as e:
                            st.warning(f"Could not calculate ROC AUC (might need binary classification or specific `multi_class` for `predict_proba`): {e}")

                        st.write("### Confusion Matrix")
                        cm = confusion_matrix(y_test, pred)
                        fig_cm = px.imshow(cm, text_auto=True, color_continuous_scale='Blues',
                                            labels=dict(x="Predicted", y="Actual", color="Count"),
                                            x=[str(i) for i in np.unique(y_test)],
                                            y=[str(i) for i in np.unique(y_test)],
                                            title='Confusion Matrix')
                        st.plotly_chart(fig_cm, use_container_width=True)

                        # ROC Curve (for binary classification)
                        if len(np.unique(y_test)) == 2:
                            try:
                                y_proba = full_pipeline.predict_proba(X_test)[:, 1]
                                fpr, tpr, _ = roc_curve(y_test, y_proba)
                                fig_roc = go.Figure()
                                fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, mode='lines', name='ROC curve (area = %0.2f)' % roc_auc_score(y_test, y_proba)))
                                fig_roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines', name='Random Classifier', line=dict(dash='dash')))
                                fig_roc.update_layout(title='Receiver Operating Characteristic (ROC) Curve',
                                                    xaxis_title='False Positive Rate',
                                                    yaxis_title='True Positive Rate')
                                st.plotly_chart(fig_roc, use_container_width=True)
                            except Exception as e:
                                st.warning(f"Could not plot ROC Curve: {e}")


                    else: # Regression
                        score = r2_score(y_test, pred)
                        st.success(f"✅ Model R2 Score: {score:.3f}")
                        st.write("### Regression Metrics")
                        st.write(f"Mean Absolute Error (MAE): {mean_absolute_error(y_test, pred):.3f}")
                        st.write(f"Mean Squared Error (MSE): {mean_squared_error(y_test, pred):.3f}")
                        st.write(f"Root Mean Squared Error (RMSE): {np.sqrt(mean_squared_error(y_test, pred)):.3f}")

                        st.write("### Residual Plot")
                        residuals = y_test - pred
                        fig_res = px.scatter(x=pred, y=residuals, labels={'x': 'Predicted Values', 'y': 'Residuals'},
                                             title='Residual Plot')
                        fig_res.add_hline(y=0, line_dash="dash", line_color="red")
                        st.plotly_chart(fig_res, use_container_width=True)


                st.write("### 🔍 Sample Predictions")
                # Ensure X_test is a DataFrame for display
                if not isinstance(X_test, pd.DataFrame):
                    # If preprocessor transformed it to numpy array, convert back for display
                    # This is a simplification; ideally, store feature names from preprocessor
                    st.info("Displaying sample predictions. Note: Input features might be transformed.")
                    # Attempt to get feature names after preprocessing if available
                    try:
                        # This works for ColumnTransformer with OneHotEncoder
                        # Need to get feature names from the preprocessor within the pipeline
                        processed_feature_names = full_pipeline.named_steps['preprocessor'].get_feature_names_out(X.columns)
                        result_df = pd.DataFrame(X_test, columns=processed_feature_names)
                    except Exception as e:
                        st.warning(f"Could not get processed feature names for display: {e}. Using generic names.")
                        result_df = pd.DataFrame(X_test, columns=[f'feature_{i}' for i in range(X_test.shape[1])])
                else:
                    result_df = X_test.copy()

                result_df["Actual"] = y_test.values
                result_df["Predicted"] = pred
                st.dataframe(result_df.head(10))

                st.write("### 📈 Prediction vs Actual Graph")
                # Convert to DataFrame for Plotly
                plot_data = pd.DataFrame({'Actual': y_test.values, 'Predicted': pred}).head(20)
                fig_pred_actual = px.line(plot_data, y=['Actual', 'Predicted'], title="Actual vs Predicted Values (First 20 Samples)",
                                         labels={'value': 'Value', 'index': 'Sample Index'})
                st.plotly_chart(fig_pred_actual, use_container_width=True)

            except Exception as e:
                st.error(f"An error occurred during model training/evaluation: {e}")

        st.markdown("---")
        st.markdown("## 🌀 Unsupervised Learning (Clustering)")
        with st.expander("⚙ KMeans Clustering"):
            # Ensure X_unsup is processed with the selected preprocessing options
            X_unsup_processed = preprocessor.fit_transform(X) # Apply the same preprocessing pipeline
            
            clusters = st.slider("🔢 Number of Clusters (K)", 2, 10, 3, key="kmeans_clusters")

            if st.button("📍 Run Clustering"):
                try:
                    model = KMeans(n_clusters=clusters, random_state=42, n_init='auto')
                    labels = model.fit_predict(X_unsup_processed)
                    sil_score = silhouette_score(X_unsup_processed, labels)

                    # Add cluster labels to the original (or filtered) DataFrame for display
                    clustered_df_display = df.copy()
                    clustered_df_display["Cluster"] = labels
                    st.success(f"🧩 Clustering Done! Silhouette Score: {sil_score:.2f}")
                    st.dataframe(clustered_df_display.head(10))

                    st.write("### 🖼 Cluster Graph (via PCA)")
                    pca = PCA(n_components=2)
                    reduced = pca.fit_transform(X_unsup_processed)
                    cluster_df_plot = pd.DataFrame(reduced, columns=["PC1", "PC2"])
                    cluster_df_plot["Cluster"] = labels.astype(str) # Convert to string for discrete colors in Plotly

                    fig_cluster = px.scatter(cluster_df_plot, x="PC1", y="PC2", color="Cluster", palette="Set2",
                                             title=f"KMeans Clustering with {clusters} Clusters (PCA Reduced)",
                                             labels={"PC1": "Principal Component 1", "PC2": "Principal Component 2"})
                    st.plotly_chart(fig_cluster, use_container_width=True)

                except Exception as e:
                    st.error(f"Error during clustering: {e}")

        st.markdown("---")
        st.markdown("## 💾 Load Saved Model for Prediction")
        if 'loaded_model' in st.session_state and st.session_state.loaded_model is not None:
            st.info(f"Loaded model: {type(st.session_state.loaded_model.named_steps['classifier_regressor']).__name__}")
            st.write("Enter new data for prediction:")
            
            # Create input fields for each feature based on the training data's columns
            input_data = {}
            
            # Attempt to get original feature names from the preprocessor's transformers within the loaded model
            original_X_cols_from_df = []
            if 'df' in st.session_state and st.session_state.df is not None:
                original_X_cols_from_df = st.session_state.df.drop(columns=[target]).columns.tolist()

            # Now, use the original_X_cols_from_df as the definitive list for input fields
            # This assumes the input data schema will match the original training data schema
            if original_X_cols_from_df:
                for col in original_X_cols_from_df:
                    if col in df.columns: # Check against the current df from session state
                        if df[col].dtype == 'object' or df[col].dtype.name == 'category':
                            input_data[col] = st.text_input(f"Enter value for {col} (Categorical)", key=f"pred_input_{col}")
                        elif df[col].dtype in [np.number, 'int64', 'float64']:
                            input_data[col] = st.number_input(f"Enter value for {col} (Numeric)", key=f"pred_input_{col}")
                        else:
                            st.warning(f"Could not infer type for feature '{col}'. Using text input.")
                            input_data[col] = st.text_input(f"Enter value for {col}", key=f"pred_input_{col}")
            else:
                st.warning("Original DataFrame not found in session state. Cannot infer input features for prediction. Please re-upload data.")
                # Fallback to manual JSON input if original_X_cols_from_df is empty
                st.text_area("Enter input features as JSON (e.g., {'feature1': 10, 'feature2': 'A'})", key="manual_pred_input_json")
                if st.button("Make Prediction from JSON", key="make_prediction_json_btn_fallback"):
                    try:
                        manual_input = json.loads(st.session_state.manual_pred_input_json)
                        input_df = pd.DataFrame([manual_input])
                        prediction = st.session_state.loaded_model.predict(input_df)
                        st.success(f"Prediction: {prediction[0]}")
                    except Exception as e:
                        st.error(f"Error parsing JSON or making prediction: {e}")
                return # Exit early if we can't generate dynamic inputs


            if st.button("Make Prediction", key="make_prediction_btn"):
                try:
                    input_df = pd.DataFrame([input_data])
                    for col in input_df.columns:
                        if col in df.columns:
                            if df[col].dtype == 'object' or df[col].dtype.name == 'category':
                                input_df[col] = input_df[col].astype(str)
                            elif df[col].dtype in [np.number, 'int64', 'float64']:
                                input_df[col] = pd.to_numeric(input_df[col], errors='coerce')
                            input_df[col] = input_df[col].replace('', np.nan)

                    prediction = st.session_state.loaded_model.predict(input_df)
                    st.success(f"Prediction: {prediction[0]}")
                except Exception as e:
                    st.error(f"Error making prediction: {e}. Ensure input data matches expected format and types.")
        else:
            st.info("No model loaded. Please train a model or upload a saved model to enable prediction.")

def display_ml_sub_menu():
    st.title("Machine Learning Tasks Sub-Categories")
    st.write("Select a sub-category to manage your ML workflow.")

    if st.button("⬅️ Back to Main Menu", key="back_to_main_ml"):
        st.session_state.current_view = "main_menu"
        st.session_state.selected_category = None
        st.session_state.selected_ml_sub_category = None
        st.rerun()

    st.markdown("---")

    col_ml1, col_ml2, col_ml3 = st.columns(3)
    with col_ml1:
        if st.button("Data Upload & Preprocessing", key="ml_upload_filter_sub_btn"):
            st.session_state.current_view = "ml_tasks_detail"
            st.session_state.selected_ml_sub_category = "Data Upload & Preprocessing"
            st.rerun()
    with col_ml2:
        if st.button("Data Visualization", key="ml_visualize_sub_btn"):
            st.session_state.current_view = "ml_tasks_detail"
            st.session_state.selected_ml_sub_category = "Data Visualization"
            st.rerun()
    with col_ml3:
        if st.button("Model Training & Evaluation", key="ml_trainer_sub_btn"):
            st.session_state.current_view = "ml_tasks_detail"
            st.session_state.selected_ml_sub_category = "Model Training & Evaluation"
            st.rerun()

def display_ml_tasks_detail():
    st.title(f"{st.session_state.selected_category} - {st.session_state.selected_ml_sub_category}")

    if st.button(f"⬅️ Back to {st.session_state.selected_category} Sub-Categories", key="back_to_ml_sub"):
        st.session_state.current_view = "ml_sub_menu"
        st.session_state.selected_ml_sub_category = None
        st.rerun()

    st.markdown("---")

    if st.session_state.selected_ml_sub_category == "Data Upload & Preprocessing":
        display_ml_upload_filter_tasks()
    elif st.session_state.selected_ml_sub_category == "Data Visualization":
        display_ml_visualize_tasks()
    elif st.session_state.selected_ml_sub_category == "Model Training & Evaluation":
        display_ml_trainer_tasks()