#!/usr/bin/env python
"""
Command line interface for Vacancy Predictor
"""

import click
import pandas as pd
import logging
from pathlib import Path
from typing import Optional

from ..core.data_processor import DataProcessor
from ..core.model_trainer import ModelTrainer
from ..core.predictor import Predictor
from ..__version__ import __version__

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

@click.group()
@click.version_option(version=__version__)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def main(verbose):
    """Vacancy Predictor - ML tool for vacancy prediction"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

@main.command()
@click.option('--data', '-d', required=True, help='Path to training data file')
@click.option('--target', '-t', required=True, help='Target column name')
@click.option('--features', '-f', help='Comma-separated list of feature columns (default: all except target)')
@click.option('--algorithm', '-a', default='random_forest', 
              help='ML algorithm to use (default: random_forest)')
@click.option('--output', '-o', help='Output path for trained model (default: model.pkl)')
@click.option('--test-size', default=0.2, help='Test set size (default: 0.2)')
@click.option('--cv-folds', default=5, help='Cross-validation folds (default: 5)')
def train(data, target, features, algorithm, output, test_size, cv_folds):
    """Train a machine learning model"""
    try:
        # Load and process data
        processor = DataProcessor()
        click.echo(f"Loading data from: {data}")
        data_df = processor.load_data(data)
        
        # Select features
        if features:
            feature_list = [f.strip() for f in features.split(',')]
        else:
            feature_list = [col for col in data_df.columns if col != target]
        
        processor.select_features(feature_list)
        processor.set_target(target)
        
        # Train model
        trainer = ModelTrainer()
        click.echo(f"Training {algorithm} model...")
        
        training_data = processor.get_training_data()
        results = trainer.train(
            training_data,
            algorithm=algorithm,
            test_size=test_size,
            cv_folds=cv_folds
        )
        
        # Save model
        if not output:
            output = f"model_{algorithm}.pkl"
        
        trainer.save_model(output)
        
        # Print results
        click.echo(f"\nTraining completed!")
        click.echo(f"Algorithm: {results['algorithm']}")
        click.echo(f"Test Score: {results['test_score']:.4f}")
        click.echo(f"CV Score: {results['cv_score_mean']:.4f} ± {results['cv_score_std']:.4f}")
        click.echo(f"Model saved to: {output}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

@main.command()
@click.option('--model', '-m', required=True, help='Path to trained model file')
@click.option('--input', '-i', required=True, help='Path to input data file for prediction')
@click.option('--output', '-o', help='Output path for predictions (default: predictions.csv)')
def predict(model, input, output):
    """Make predictions using a trained model"""
    try:
        # Load model
        predictor = Predictor()
        click.echo(f"Loading model from: {model}")
        predictor.load_model(model)
        
        # Load input data
        click.echo(f"Loading input data from: {input}")
        input_data = pd.read_csv(input)
        
        # Make predictions
        click.echo("Making predictions...")
        predictions = predictor.predict(input_data)
        
        # Save predictions
        if not output:
            output = "predictions.csv"
        
        result_df = input_data.copy()
        result_df['prediction'] = predictions
        result_df.to_csv(output, index=False)
        
        click.echo(f"Predictions completed!")
        click.echo(f"Processed {len(predictions)} samples")
        click.echo(f"Results saved to: {output}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

@main.command()
@click.option('--data', '-d', required=True, help='Path to data file')
@click.option('--target', '-t', required=True, help='Target column name')
@click.option('--features', '-f', help='Comma-separated list of feature columns')
@click.option('--output', '-o', help='Output directory for comparison results')
def compare(data, target, features, output):
    """Compare multiple ML algorithms"""
    try:
        # Load and process data
        processor = DataProcessor()
        click.echo(f"Loading data from: {data}")
        data_df = processor.load_data(data)
        
        # Select features
        if features:
            feature_list = [f.strip() for f in features.split(',')]
        else:
            feature_list = [col for col in data_df.columns if col != target]
        
        processor.select_features(feature_list)
        processor.set_target(target)
        
        # Compare algorithms
        trainer = ModelTrainer()
        click.echo("Comparing algorithms...")
        
        training_data = processor.get_training_data()
        comparison_df = trainer.compare_algorithms(training_data)
        
        # Display results
        click.echo("\nAlgorithm Comparison Results:")
        click.echo("=" * 50)
        
        for _, row in comparison_df.iterrows():
            click.echo(f"{row['algorithm']:<20} Score: {row['test_score']:.4f}")
        
        # Save results
        if output:
            output_path = Path(output)
            output_path.mkdir(parents=True, exist_ok=True)
            comparison_df.to_csv(output_path / "algorithm_comparison.csv", index=False)
            click.echo(f"\nResults saved to: {output_path / 'algorithm_comparison.csv'}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

@main.command()
@click.option('--input', '-i', required=True, help='Path to dump file')
@click.option('--output', '-o', required=True, help='Output CSV file path')
def convert(input, output):
    """Convert dump file to CSV format"""
    try:
        from ..utils.file_handlers import FileHandler
        
        file_handler = FileHandler()
        click.echo(f"Converting {input} to {output}...")
        
        conversion_info = file_handler.convert_dump_to_csv(input, output)
        
        click.echo("Conversion completed!")
        click.echo(f"Rows: {conversion_info['rows']}")
        click.echo(f"Columns: {conversion_info['columns']}")
        click.echo(f"Output size: {conversion_info['converted_size_mb']:.2f} MB")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    main()