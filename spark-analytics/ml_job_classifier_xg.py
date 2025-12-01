#!/usr/bin/env python3
"""
Job Classification using XGBoost (XGBoost4J-Spark) - IMPROVED VERSION
Categorizes jobs into role categories with better labeling and class balancing
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml import Pipeline
from pyspark.ml.feature import (
    Tokenizer, StopWordsRemover, CountVectorizer, IDF,
    StringIndexer, VectorAssembler
)
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from xgboost.spark import SparkXGBClassifier
import re
import logging
import sys

# Suppress ALL verbose logs
logging.getLogger("py4j").setLevel(logging.CRITICAL)
logging.getLogger("XGBoost-PySpark").setLevel(logging.CRITICAL)
logging.getLogger("pyspark").setLevel(logging.ERROR)

# Redirect XGBoost output to null
class SuppressOutput:
    def __enter__(self):
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = open('/dev/null', 'w')
        sys.stderr = open('/dev/null', 'w')
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr

class JobClassifier:
    """Classify jobs into categories using XGBoost with improved labeling"""
    
    def __init__(self, spark_session):
        self.spark = spark_session
        
    @staticmethod
    def categorize_job_title(title, description):
        """
        IMPROVED: Map job to category using BOTH title AND description
        More comprehensive keyword matching
        """
        if not title and not description:
            return 'Other'
        
        # Combine title and description for better matching
        text = f"{title or ''} {description or ''}".lower()
        
        # Enhanced keyword sets with more variations
        job_categories = {
            'Software Engineer': [
                # Core programming
                'software engineer', 'developer', 'programmer', 'coder',
                # Specializations
                'full stack', 'fullstack', 'full-stack', 
                'backend', 'back-end', 'frontend', 'front-end',
                'devops', 'dev ops', 'sre', 'site reliability',
                # Technologies (strong indicators)
                'java developer', 'python developer', '.net developer',
                'react developer', 'angular developer', 'node.js',
                'software development', 'application developer',
                'web developer', 'mobile developer', 'ios developer', 'android developer'
            ],
            'Data Scientist': [
                'data scientist', 'data science', 'machine learning engineer',
                'ml engineer', 'ai engineer', 'artificial intelligence',
                'data engineer', 'data analyst', 'business intelligence',
                'analytics engineer', 'deep learning', 'nlp engineer',
                'computer vision', 'mlops', 'data mining'
            ],
            'Product Manager': [
                'product manager', 'product owner', 'pm ', ' pm,',
                'product management', 'technical product manager',
                'associate product manager', 'senior product manager',
                'chief product officer', 'vp product', 'head of product'
            ],
            'Designer': [
                'designer', 'ui designer', 'ux designer', 'ui/ux',
                'user experience', 'user interface', 'product designer',
                'graphic designer', 'visual designer', 'interaction designer',
                'design lead', 'creative director', 'art director',
                'web designer', 'brand designer'
            ],
            'Marketing': [
                'marketing', 'marketing manager', 'digital marketing',
                'content marketing', 'growth marketing', 'seo specialist',
                'social media manager', 'brand manager', 'campaign manager',
                'marketing analyst', 'marketing coordinator', 'cmo',
                'content strategist', 'copywriter', 'growth hacker'
            ],
            'Sales': [
                'sales', 'account executive', 'sales representative',
                'account manager', 'business development', 'sales manager',
                'sales engineer', 'inside sales', 'outside sales',
                'sales director', 'vp sales', 'chief revenue officer',
                'customer success', 'sales operations'
            ],
            'Operations': [
                'operations', 'operations manager', 'ops manager',
                'supply chain', 'logistics', 'operations analyst',
                'operations coordinator', 'chief operating officer', 'coo',
                'operations director', 'process manager', 'project manager',
                'program manager', 'business operations'
            ]
        }
        
        # Score each category based on keyword matches
        category_scores = {}
        for category, keywords in job_categories.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    # Give higher weight to matches in title
                    if title and keyword in title.lower():
                        score += 2
                    else:
                        score += 1
            category_scores[category] = score
        
        # Return category with highest score, or 'Other' if no matches
        # Use Python's built-in max, not PySpark's
        score_list = list(category_scores.values())
        max_score = score_list[0] if score_list else 0
        for score in score_list:
            if score > max_score:
                max_score = score
        
        if max_score >= 1:  # At least one keyword match required
            for cat, score in category_scores.items():
                if score == max_score:
                    return cat
        
        return 'Other'
    
    def prepare_features(self, df):
        """Prepare features from job title and description"""
        # Create UDF that takes both title and description
        categorize_udf = udf(
            lambda title, desc: JobClassifier.categorize_job_title(title, desc),
            StringType()
        )
        
        df = df.withColumn(
            "job_category",
            categorize_udf(col("title"), col("description_text"))
        )
        
        # Combine text features
        df = df.withColumn(
            "text_features",
            concat_ws(" ",
                coalesce(col("title"), lit("")),
                coalesce(col("description_text"), lit(""))
            )
        )
        
        # Clean text
        df = df.withColumn(
            "text_features",
            regexp_replace(
                regexp_replace(col("text_features"), "[^a-zA-Z0-9\\s]", " "),
                "\\s+", " "
            )
        )
        
        return df
    
    def train_classifier(self, df, test_size=0.2, min_samples_per_class=10):
        """Train XGBoost classifier with improved data handling"""
        print("\n" + "="*70)
        print("🎯 JOB CLASSIFICATION USING XGBOOST - IMPROVED VERSION")
        print("="*70)
        
        df_prepared = self.prepare_features(df)
        
        # Filter valid data
        df_prepared = df_prepared.filter(
            col("text_features").isNotNull() &
            (length(col("text_features")) > 10)
        )
        
        if df_prepared.count() == 0:
            print("❌ No valid data for classification")
            return None, None
        
        # Sample if dataset is too large
        total_count = df_prepared.count()
        print(f"\n📊 Initial Dataset: {total_count:,} job postings")
        
        if total_count > 15000:
            sample_fraction = 15000 / total_count
            df_prepared = df_prepared.sample(fraction=sample_fraction, seed=42)
            print(f"📉 Sampled to: {df_prepared.count():,} jobs for efficiency")
        
        # Show original distribution
        category_dist = df_prepared.groupBy("job_category").count().orderBy(desc("count"))
        print("\n📈 Category Distribution:")
        category_counts = {}
        for row in category_dist.collect():
            category_counts[row['job_category']] = row['count']
            print(f"   {row['job_category']:<20} {row['count']:>6,} jobs")
        
        # Remove categories with too few samples
        print(f"\n⚙️  Filtering categories (minimum {min_samples_per_class} samples)...")
        valid_categories = [cat for cat, count in category_counts.items() 
                          if count >= min_samples_per_class]
        
        removed_categories = [cat for cat in category_counts.keys() 
                            if cat not in valid_categories]
        if removed_categories:
            print(f"   Removed: {', '.join(removed_categories)}")
        
        df_prepared = df_prepared.filter(col("job_category").isin(valid_categories))
        
        # Balance dataset
        print("\n⚖️  Balancing dataset...")
        
        # Separate classes
        class_dfs = {}
        for category in valid_categories:
            class_dfs[category] = df_prepared.filter(col("job_category") == category)
        
        # Find median class size
        class_sizes = [class_dfs[cat].count() for cat in valid_categories]
        median_size = sorted(class_sizes)[len(class_sizes) // 2]
        
        # Balance: undersample large classes, keep small classes as-is
        balanced_dfs = []
        for category in valid_categories:
            cat_df = class_dfs[category]
            cat_count = cat_df.count()
            
            # Cap at 3x median to reduce imbalance
            max_allowed = median_size * 3
            target_size = cat_count if cat_count < max_allowed else max_allowed
            
            if cat_count > target_size:
                sample_fraction = target_size / cat_count
                cat_df = cat_df.sample(fraction=sample_fraction, seed=42)
                print(f"   {category:<20} {cat_count:>6,} → {cat_df.count():>6,}")
            
            balanced_dfs.append(cat_df)
        
        # Union all balanced classes
        df_prepared = balanced_dfs[0]
        for i in range(1, len(balanced_dfs)):
            df_prepared = df_prepared.union(balanced_dfs[i])
        
        print(f"\n📚 Training Dataset: {df_prepared.count():,} jobs")
        
        # Build pipeline
        label_indexer = StringIndexer(
            inputCol="job_category",
            outputCol="label",
            handleInvalid="skip"
        )
        
        tokenizer = Tokenizer(inputCol="text_features", outputCol="words")
        remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")
        
        # CountVectorizer + IDF for better features
        cv = CountVectorizer(
            inputCol="filtered_words",
            outputCol="raw_features",
            vocabSize=3000,
            minDF=2.0
        )
        
        idf = IDF(
            inputCol="raw_features",
            outputCol="text_features_vec"
        )
        
        location_indexer = StringIndexer(
            inputCol="location",
            outputCol="location_index",
            handleInvalid="keep"
        )
        
        experience_indexer = StringIndexer(
            inputCol="experience_level",
            outputCol="experience_index",
            handleInvalid="keep"
        )
        
        assembler = VectorAssembler(
            inputCols=["text_features_vec", "experience_index", "location_index"],
            outputCol="features",
            handleInvalid="skip"
        )
        
        # Optimized XGBoost
        xgb = SparkXGBClassifier(
            label_col="label",
            features_col="features",
            num_workers=1,
            use_gpu=False,
            max_depth=7,
            n_estimators=100,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            tree_method="hist",
            min_child_weight=1,
            gamma=0.2,
            reg_alpha=0.3,
            reg_lambda=1.5,
            seed=42
        )
        
        pipeline = Pipeline(stages=[
            label_indexer,
            tokenizer,
            remover,
            cv,
            idf,
            location_indexer,
            experience_indexer,
            assembler,
            xgb
        ])
        
        # Split and train
        train_df, test_df = df_prepared.randomSplit([1 - test_size, test_size], seed=42)
        
        print(f"\n🔄 Training model on {train_df.count():,} samples...")
        print("   (This may take 2-3 minutes...)\n")
        
        train_df = train_df.cache()
        
        # Suppress XGBoost verbose output
        import os
        os.environ['XGBOOST_VERBOSITY'] = '0'
        
        model = pipeline.fit(train_df)
        predictions = model.transform(test_df)
        
        # Evaluate
        correct_predictions = predictions.filter(col("prediction") == col("label")).count()
        total_predictions = predictions.count()
        accuracy = (correct_predictions / total_predictions) * 100
        
        evaluator_f1 = MulticlassClassificationEvaluator(
            labelCol="label", predictionCol="prediction", metricName="f1"
        )
        evaluator_precision = MulticlassClassificationEvaluator(
            labelCol="label", predictionCol="prediction", metricName="weightedPrecision"
        )
        evaluator_recall = MulticlassClassificationEvaluator(
            labelCol="label", predictionCol="prediction", metricName="weightedRecall"
        )
        
        f1_score = evaluator_f1.evaluate(predictions) * 100
        precision = evaluator_precision.evaluate(predictions) * 100
        recall = evaluator_recall.evaluate(predictions) * 100
        
        print("\n" + "="*70)
        print("📊 MODEL PERFORMANCE")
        print("="*70)
        print(f"Overall Accuracy:  {accuracy:.1f}%")
        print(f"Precision:         {precision:.1f}%")
        print(f"Recall:            {recall:.1f}%")
        print(f"F1 Score:          {f1_score:.1f}%")
        
        # Per-category performance
        print("\n" + "="*70)
        print("📈 PER-CATEGORY PERFORMANCE")
        print("="*70)
        
        label_to_category = predictions.select("label", "job_category").distinct().collect()
        label_map = {int(row['label']): row['job_category'] for row in label_to_category}
        
        category_metrics = []
        
        for label_idx in sorted(label_map.keys()):
            category = label_map[label_idx]
            category_preds = predictions.filter(col("label") == label_idx)
            total = category_preds.count()
            correct = category_preds.filter(col("prediction") == col("label")).count()
            accuracy_pct = (correct / total * 100) if total > 0 else 0
            
            # Calculate precision and recall
            all_pred_this_class = predictions.filter(col("prediction") == label_idx).count()
            precision_cat = (correct / all_pred_this_class * 100) if all_pred_this_class > 0 else 0
            recall_cat = (correct / total * 100) if total > 0 else 0
            
            category_metrics.append({
                'category': category,
                'total': total,
                'correct': correct,
                'accuracy': accuracy_pct,
                'precision': precision_cat,
                'recall': recall_cat
            })
            
            print(f"\n{category}:")
            print(f"  Accuracy:  {accuracy_pct:>5.1f}% ({correct}/{total})")
            print(f"  Precision: {precision_cat:>5.1f}%")
            print(f"  Recall:    {recall_cat:>5.1f}%")
        
        # Summary
        print("\n" + "="*70)
        print("💡 SUMMARY")
        print("="*70)
        
        # Calculate average manually
        total_accuracy = 0
        for m in category_metrics:
            total_accuracy += m['accuracy']
        avg_accuracy = total_accuracy / len(category_metrics)
        print(f"Average per-category accuracy: {avg_accuracy:.1f}%")
        
        # Find best/worst
        best_category = category_metrics[0]
        worst_category = category_metrics[0]
        for m in category_metrics:
            if m['accuracy'] > best_category['accuracy']:
                best_category = m
            if m['accuracy'] < worst_category['accuracy']:
                worst_category = m
        
        print(f"Best:  {best_category['category']} ({best_category['accuracy']:.1f}%)")
        print(f"Worst: {worst_category['category']} ({worst_category['accuracy']:.1f}%)")
        
        # Check for bias
        pred_counts = predictions.groupBy("prediction").count().orderBy(desc("count")).collect()
        most_predicted = pred_counts[0]['count'] if pred_counts else 0
        bias_ratio = (most_predicted / total_predictions * 100) if total_predictions > 0 else 0
        
        if bias_ratio > 50:
            print(f"⚠️  Prediction bias detected: {bias_ratio:.1f}% in one class")
        else:
            print(f"✓ Predictions are well-balanced")
        
        train_df.unpersist()
        
        print("\n" + "="*70)
        print("✅ TRAINING COMPLETED")
        print("="*70 + "\n")
        
        return model, predictions
    
    def classify_jobs(self, model, df):
        """Classify jobs using trained XGBoost model"""
        if model is None:
            print("❌ No trained model available")
            return df
        
        print("\n🔮 Classifying jobs...")
        df_prepared = self.prepare_features(df)
        predictions = model.transform(df_prepared)
        
        predictions = predictions.withColumn(
            "predicted_category_index",
            col("prediction").cast(IntegerType())
        )
        
        return predictions

def main():
    """Standalone testing with improved configuration"""
    import os
    import sys
    
    # Suppress ALL logs aggressively
    os.environ['XGBOOST_VERBOSITY'] = '0'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    
    logging.getLogger("py4j").setLevel(logging.CRITICAL)
    logging.getLogger("XGBoost-PySpark").setLevel(logging.CRITICAL)
    logging.getLogger("pyspark").setLevel(logging.ERROR)
    
    os.environ['PYSPARK_DRIVER_MEMORY'] = '4g'
    os.environ['PYSPARK_EXECUTOR_MEMORY'] = '4g'
    os.environ['SPARK_DRIVER_MEMORY'] = '4g'
    os.environ['SPARK_EXECUTOR_MEMORY'] = '4g'
    
    try:
        import findspark
        findspark.init()
    except:
        pass
    
    from data_loader import DataLoader
    
    loader = DataLoader()
    
    try:
        loader.spark.conf.set("spark.sql.shuffle.partitions", "4")
        loader.spark.conf.set("spark.default.parallelism", "4")
    except Exception as e:
        pass
    
    try:
        df = loader.load_postings()
        
        if df and df.count() > 0:
            classifier = JobClassifier(loader.spark)
            
            # Train model (require at least 30 samples per category)
            model, predictions = classifier.train_classifier(
                df, 
                test_size=0.2,
                min_samples_per_class=30
            )
        else:
            print("📭 No data available for classification")
    
    finally:
        loader.cleanup()

if __name__ == "__main__":
    main()