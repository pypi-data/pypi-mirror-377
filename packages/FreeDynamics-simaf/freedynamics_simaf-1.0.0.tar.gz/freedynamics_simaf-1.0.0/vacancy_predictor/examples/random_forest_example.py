#!/usr/bin/env python
"""
Example usage of RandomForestModel from Vacancy Predictor
"""

import pandas as pd
import numpy as np
from vacancy_predictor.models import RandomForestModel, get_model

def create_sample_data(n_samples=1000, task_type='regression'):
    """Create sample data for demonstration"""
    np.random.seed(42)
    
    # Generate features
    data = {
        'feature_1': np.random.normal(0, 1, n_samples),
        'feature_2': np.random.uniform(-1, 1, n_samples),
        'feature_3': np.random.exponential(1, n_samples),
        'feature_4': np.random.randint(0, 5, n_samples),
        'feature_5': np.random.beta(2, 3, n_samples)
    }
    
    X = pd.DataFrame(data)
    
    if task_type == 'regression':
        # Create regression target
        y = (2 * X['feature_1'] + 
             1.5 * X['feature_2'] - 
             0.5 * X['feature_3'] + 
             X['feature_4'] + 
             np.random.normal(0, 0.5, n_samples))
        y = pd.Series(y, name='target_regression')
    else:
        # Create classification target
        scores = (X['feature_1'] + X['feature_2'] * 2 + 
                 np.random.normal(0, 0.5, n_samples))
        y = pd.Series((scores > scores.median()).astype(int), name='target_classification')
    
    return X, y

def regression_example():
    """Example with regression task"""
    print("=" * 50)
    print("RANDOM FOREST REGRESSION EXAMPLE")
    print("=" * 50)
    
    # Create sample data
    X, y = create_sample_data(task_type='regression')
    print(f"Created dataset: {X.shape[0]} samples, {X.shape[1]} features")
    
    # Split data
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Create and train model
    model = RandomForestModel(
        task_type='regression',
        n_estimators=100,
        max_depth=10,
        random_state=42
    )
    
    print("\nTraining Random Forest Regressor...")
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Evaluate
    results = model.evaluate(X_test, y_test)
    print(f"\nEvaluation Results:")
    print(f"R² Score: {results['r2_score']:.4f}")
    print(f"RMSE: {results['rmse']:.4f}")
    print(f"MAE: {results['mae']:.4f}")
    print(f"CV Score: {results['cv_score_mean']:.4f} ± {results['cv_score_std']:.4f}")
    
    # Feature importance
    importance_df = model.get_feature_importance_detailed()
    print(f"\nTop 3 Feature Importance:")
    print(importance_df.head(3)[['feature', 'importance', 'importance_percentage']])
    
    # Tree information
    tree_info = model.get_tree_info()
    print(f"\nTree Statistics:")
    print(f"Average tree depth: {tree_info['avg_depth']:.1f}")
    print(f"Average leaves per tree: {tree_info['avg_leaves']:.1f}")
    
    return model

def classification_example():
    """Example with classification task"""
    print("\n" + "=" * 50)
    print("RANDOM FOREST CLASSIFICATION EXAMPLE")
    print("=" * 50)
    
    # Create sample data
    X, y = create_sample_data(task_type='classification')
    print(f"Created dataset: {X.shape[0]} samples, {X.shape[1]} features")
    print(f"Class distribution: {y.value_counts().to_dict()}")
    
    # Split data
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Create model using factory function
    model = get_model('random_forest', 
                     task_type='classification',
                     n_estimators=100,
                     max_depth=10,
                     random_state=42)
    
    print("\nTraining Random Forest Classifier...")
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)
    
    # Evaluate
    results = model.evaluate(X_test, y_test)
    print(f"\nEvaluation Results:")
    print(f"Accuracy: {results['accuracy']:.4f}")
    print(f"CV Score: {results['cv_score_mean']:.4f} ± {results['cv_score_std']:.4f}")
    
    # Classification report
    print(f"\nDetailed Classification Report:")
    report = results['classification_report']
    for class_name in ['0', '1']:
        if class_name in report:
            print(f"Class {class_name}: Precision={report[class_name]['precision']:.3f}, "
                  f"Recall={report[class_name]['recall']:.3f}, "
                  f"F1={report[class_name]['f1-score']:.3f}")
    
    # Feature importance
    importance_df = model.get_feature_importance_detailed()
    print(f"\nTop 3 Feature Importance:")
    print(importance_df.head(3)[['feature', 'importance', 'importance_percentage']])
    
    return model

def hyperparameter_optimization_example():
    """Example of hyperparameter optimization"""
    print("\n" + "=" * 50)
    print("HYPERPARAMETER OPTIMIZATION EXAMPLE")
    print("=" * 50)
    
    # Create sample data
    X, y = create_sample_data(task_type='regression')
    
    # Create model
    model = RandomForestModel(task_type='auto', random_state=42)
    
    # Define parameter grid
    param_grid = {
        'n_estimators': [50, 100],
        'max_depth': [5, 10, None],
        'min_samples_split': [2, 5]
    }
    
    print("Optimizing hyperparameters...")
    results = model.optimize_hyperparameters(X, y, param_grid, cv_folds=3)
    
    print(f"\nOptimization Results:")
    print(f"Best Score: {results['best_score']:.4f}")
    print(f"Best Parameters: {results['best_params']}")
    
    return model

def model_persistence_example():
    """Example of saving and loading models"""
    print("\n" + "=" * 50)
    print("MODEL PERSISTENCE EXAMPLE")
    print("=" * 50)
    
    # Create and train a model
    X, y = create_sample_data(task_type='regression')
    model = RandomForestModel(n_estimators=50, random_state=42)
    model.fit(X, y)
    
    # Save model
    model_path = 'random_forest_model.pkl'
    model.save_model(model_path)
    print(f"Model saved to: {model_path}")
    
    # Load model
    loaded_model = RandomForestModel.load_model(model_path)
    print(f"Model loaded successfully")
    
    # Verify they produce same predictions
    original_pred = model.predict(X.head(5))
    loaded_pred = loaded_model.predict(X.head(5))
    
    print(f"Predictions match: {np.allclose(original_pred, loaded_pred)}")
    
    # Model info
    print(f"\nModel Info:")
    info = loaded_model.get_model_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Clean up
    import os
    if os.path.exists(model_path):
        os.remove(model_path)
    
    return loaded_model

def main():
    """Run all examples"""
    print("Random Forest Model Examples")
    print("Vacancy Predictor Package")
    
    # Run examples
    regression_model = regression_example()
    classification_model = classification_example()
    optimized_model = hyperparameter_optimization_example()
    persistent_model = model_persistence_example()
    
    print("\n" + "=" * 50)
    print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
    print("=" * 50)

if __name__ == "__main__":
    main()