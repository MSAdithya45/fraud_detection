from src.model_pipeline.pipeline import FraudPipeline

print("=" * 60)
print("Loading Fraud Pipeline...")
print("=" * 60)

pipeline = FraudPipeline.load()

print("=" * 60)
print("Fraud Pipeline Loaded Successfully")
print("=" * 60)