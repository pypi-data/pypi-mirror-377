#!/usr/bin/env python
"""
Main entry point for Vacancy Predictor GUI application
"""

import sys
import logging
import argparse
from pathlib import Path

def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('vacancy_predictor.log')
        ]
    )

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Vacancy Predictor - ML Tool with GUI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  vacancy-predictor-gui                    # Launch GUI
  vacancy-predictor-gui --log-level DEBUG # Launch with debug logging
        """
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Vacancy Predictor 3.0.0'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Vacancy Predictor GUI...")
    
    try:
        # OPCIÓN 1: Si app.py está en la raíz
        try:
            from .gui.app import VacancyPredictorApp
        except ImportError:
            # OPCIÓN 2: Si app.py está en gui/
            try:
                from .gui.app import VacancyPredictorApp
            except ImportError:
                # OPCIÓN 3: Si el archivo se llama app_simplified.py
                from .gui.app import VacancyPredictorApp
        
        app = VacancyPredictorApp()
        app.run()
        
    except ImportError as e:
        logger.error(f"Failed to import GUI components: {e}")
        print("Error: GUI dependencies not available. Please install required packages.")
        print(f"Import error details: {e}")
        
        # Sugerir solución
        print("\nTroubleshooting:")
        print("1. Make sure your app.py file contains the class 'VacancyPredictorApp'")
        print("2. Check that all required dependencies are installed:")
        print("   pip install pandas numpy scikit-learn matplotlib seaborn")
        print("3. Verify your file structure matches the imports")
        
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    
    logger.info("Vacancy Predictor GUI closed.")

if __name__ == "__main__":
    main()