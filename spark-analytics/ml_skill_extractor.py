#!/usr/bin/env python3
"""
Skill Extraction using NLP-based techniques
Extracts and mines skills from job descriptions using MLlib NLP capabilities
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer, StopWordsRemover, CountVectorizer, NGram, IDF, HashingTF
from pyspark.ml.clustering import KMeans
import re


class SkillExtractor:
    """Extract skills from job descriptions using NLP"""
    
    def __init__(self, spark_session):
        self.spark = spark_session
        
        # Comprehensive skill vocabulary
        self.known_skills = {
            # Programming Languages
            'programming_languages': [
                'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'go', 'rust', 'ruby',
                'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'html', 'css'
            ],
            # Frameworks & Libraries
            'frameworks': [
                'react', 'vue', 'angular', 'node.js', 'express', 'django', 'flask', 'spring',
                'laravel', 'rails', 'asp.net', 'next.js', 'nuxt', 'svelte', 'ember'
            ],
            # Databases
            'databases': [
                'postgresql', 'mysql', 'mongodb', 'redis', 'cassandra', 'elasticsearch',
                'dynamodb', 'oracle', 'sqlite', 'neo4j', 'couchdb'
            ],
            # Cloud & DevOps
            'cloud_devops': [
                'aws', 'azure', 'gcp', 'kubernetes', 'docker', 'jenkins', 'terraform',
                'ansible', 'chef', 'puppet', 'ci/cd', 'github actions', 'gitlab'
            ],
            # Tools & Technologies
            'tools': [
                'git', 'linux', 'bash', 'nginx', 'apache', 'graphql', 'rest', 'microservices',
                'api', 'grpc', 'rabbitmq', 'kafka', 'spark', 'hadoop', 'airflow'
            ],
            # Specialized Domains
            'specialized': [
                'machine learning', 'deep learning', 'ai', 'data science', 'nlp', 'computer vision',
                'blockchain', 'web3', 'cryptocurrency', 'cybersecurity', 'penetration testing'
            ],
            # Soft Skills & Concepts
            'concepts': [
                'agile', 'scrum', 'devops', 'tdd', 'bdd', 'code review', 'pair programming',
                'microservices', 'serverless', 'containerization', 'orchestration'
            ]
        }
    
    def extract_skill_patterns(self, text):
        """Extract skills using pattern matching"""
        if not text:
            return []
        
        text_lower = text.lower()
        found_skills = []
        
        # Check each skill category
        for category, skills in self.known_skills.items():
            for skill in skills:
                # Use word boundary matching for better accuracy
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.append(skill)
        
        return list(set(found_skills))  # Remove duplicates
    
    def prepare_text_features(self, df):
        """Prepare text features for skill extraction"""
        print("\n🛠️  Preparing text features for skill extraction...")
        
        # Combine title and description
        df = df.withColumn(
            "combined_text",
            concat_ws(" ",
                coalesce(col("title"), lit("")),
                coalesce(col("description_text"), lit(""))
            )
        )
        
        # Clean text
        df = df.withColumn(
            "clean_text",
            lower(regexp_replace(
                regexp_replace(col("combined_text"), "[^a-zA-Z0-9\\s+#./-]", " "),
                "\\s+", " "
            ))
        )
        
        # Extract known skills
        extract_skills_udf = udf(self.extract_skill_patterns, ArrayType(StringType()))
        df = df.withColumn("extracted_skills", extract_skills_udf(col("clean_text")))
        
        # Count skills per job
        df = df.withColumn("skill_count", size(col("extracted_skills")))
        
        return df
    
    def build_skill_tfidf(self, df):
        """Build TF-IDF features for skill mining"""
        print("\n📊 Building TF-IDF features for skill extraction...")
        
        df_prepared = self.prepare_text_features(df)
        
        # Filter jobs with meaningful text
        df_prepared = df_prepared.filter(
            length(col("clean_text")) > 50
        )
        
        if df_prepared.count() == 0:
            print("❌ No valid job descriptions for skill extraction")
            return None, None
        
        print(f"📚 Processing {df_prepared.count()} job descriptions")
        
        # Tokenization and feature extraction
        tokenizer = Tokenizer(inputCol="clean_text", outputCol="words")
        remover = StopWordsRemover(
            inputCol="words",
            outputCol="filtered_words",
            stopWords=StopWordsRemover.loadDefaultStopWords("english")
        )
        
        # Create n-grams for multi-word skills (bigrams and trigrams)
        bigram = NGram(n=2, inputCol="filtered_words", outputCol="bigrams")
        trigram = NGram(n=3, inputCol="filtered_words", outputCol="trigrams")
        
        # TF-IDF for unigrams
        hashingTF = HashingTF(inputCol="filtered_words", outputCol="raw_features", numFeatures=1000)
        idf = IDF(inputCol="raw_features", outputCol="features")
        
        # TF-IDF for bigrams (useful for skills like "machine learning")
        bigram_tf = HashingTF(inputCol="bigrams", outputCol="bigram_features", numFeatures=500)
        bigram_idf = IDF(inputCol="bigram_features", outputCol="bigram_tfidf")
        
        # Build pipeline
        pipeline = Pipeline(stages=[
            tokenizer,
            remover,
            bigram,
            trigram,
            hashingTF,
            idf,
            bigram_tf,
            bigram_idf
        ])
        
        model = pipeline.fit(df_prepared)
        df_transformed = model.transform(df_prepared)
        
        return df_transformed, model
    
    def cluster_jobs_by_skills(self, df, n_clusters=5):
        """Cluster jobs based on skill similarity using KMeans"""
        print(f"\n🔍 Clustering jobs into {n_clusters} skill-based groups...")
        
        df_prepared, tfidf_model = self.build_skill_tfidf(df)
        
        if df_prepared is None:
            return None, None, None
        
        # Use TF-IDF features for clustering
        kmeans = KMeans(
            featuresCol="features",
            k=n_clusters,
            seed=42,
            maxIter=20
        )
        
        cluster_model = kmeans.fit(df_prepared)
        df_clustered = cluster_model.transform(df_prepared)
        
        # Analyze clusters
        print("\n📊 Skill-based Job Clusters:")
        for cluster_id in range(n_clusters):
            cluster_jobs = df_clustered.filter(col("prediction") == cluster_id)
            count = cluster_jobs.count()
            
            if count > 0:
                # Get most common skills in this cluster
                cluster_skills = cluster_jobs.select(
                    explode(col("extracted_skills")).alias("skill")
                ).groupBy("skill").count().orderBy(desc("count")).limit(5)
                
                print(f"\n   Cluster {cluster_id} ({count} jobs):")
                top_skills = [row['skill'] for row in cluster_skills.collect()]
                print(f"      Top Skills: {', '.join(top_skills)}")
        
        return df_clustered, cluster_model, tfidf_model
    
    def extract_top_skills(self, df, top_n=20):
        """Extract and rank top skills across all jobs"""
        print(f"\n🏆 Extracting top {top_n} skills from job descriptions...")
        
        df_prepared = self.prepare_text_features(df)
        
        # Aggregate skills across all jobs
        all_skills_df = df_prepared.select(
            explode(col("extracted_skills")).alias("skill")
        ).groupBy("skill").count().orderBy(desc("count"))
        
        top_skills = all_skills_df.limit(top_n).collect()
        
        print(f"\n📊 Top {top_n} Skills:")
        for i, row in enumerate(top_skills, 1):
            skill = row['skill']
            count = row['count']
            percentage = (count / df_prepared.count() * 100) if df_prepared.count() > 0 else 0
            print(f"   {i:2d}. {skill:25s}: {count:4d} jobs ({percentage:5.1f}%)")
        
        return all_skills_df
    
    def analyze_skill_combinations(self, df):
        """Analyze common skill combinations (e.g., Python + Django)"""
        print("\n🔗 Analyzing skill combinations...")
        
        df_prepared = self.prepare_text_features(df)
        
        # Get jobs with multiple skills
        multi_skill_jobs = df_prepared.filter(col("skill_count") >= 2)
        
        if multi_skill_jobs.count() == 0:
            print("⚠️  No jobs with multiple skills found")
            return None
        
        # Create skill pairs (limited to avoid explosion)
        skill_pairs = []
        for row in multi_skill_jobs.select("extracted_skills").limit(1000).collect():
            skills = row['extracted_skills']
            if skills and len(skills) >= 2:
                # Create pairs
                for i in range(len(skills)):
                    for j in range(i + 1, len(skills)):
                        pair = tuple(sorted([skills[i], skills[j]]))
                        skill_pairs.append(pair)
        
        if skill_pairs:
            # Count pair frequencies
            from collections import Counter
            pair_counts = Counter(skill_pairs)
            
            print(f"\n📊 Top 10 Skill Combinations:")
            for pair, count in pair_counts.most_common(10):
                print(f"   • {pair[0]} + {pair[1]}: {count} jobs")
        
        return skill_pairs
    
    def extract_skills_for_job(self, df, job_title=None):
        """Extract skills for a specific job or all jobs"""
        df_prepared = self.prepare_text_features(df)
        
        if job_title:
            job_df = df_prepared.filter(col("title").rlike(f"(?i){job_title}"))
        else:
            job_df = df_prepared
        
        # Return skills per job
        skills_df = job_df.select(
            "title", "company", "extracted_skills", "skill_count"
        ).orderBy(desc("skill_count"))
        
        return skills_df


def main():
    """Standalone testing"""
    from daily_analytics import YCJobAnalytics
    
    analytics = YCJobAnalytics()
    
    try:
        # Load data
        df = analytics.load_data_from_worker()
        
        if df and df.count() > 0:
            extractor = SkillExtractor(analytics.spark)
            
            # Extract top skills
            top_skills = extractor.extract_top_skills(df)
            
            # Analyze skill combinations
            combinations = extractor.analyze_skill_combinations(df)
            
            # Cluster jobs by skills
            clustered_df, cluster_model, tfidf_model = extractor.cluster_jobs_by_skills(df)
            
            print("\n✅ Skill extraction completed successfully!")
        else:
            print("📭 No data available for skill extraction")
    
    finally:
        analytics.cleanup()


if __name__ == "__main__":
    main()

