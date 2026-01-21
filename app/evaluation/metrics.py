from typing import List, Dict, Any
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    context_precision,
    context_recall,
    faithfulness,
    answer_relevancy
)
import logging

logger = logging.getLogger(__name__)


class RAGEvaluator:
    """Evaluate RAG system using RAGAS metrics."""
    
    def __init__(self):
        self.metrics = [
            context_precision,
            context_recall,
            faithfulness,
            answer_relevancy
        ]
    
    def evaluate(
        self,
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Evaluate RAG system on test cases.
        
        Args:
            test_cases: List of test cases with:
                - question: User question
                - answer: Generated answer
                - contexts: List of retrieved context strings
                - ground_truth: Expected answer
                
        Returns:
            Dictionary of metric scores
        """
        try:
            # Convert to RAGAS dataset format
            dataset_dict = {
                "question": [],
                "answer": [],
                "contexts": [],
                "ground_truth": []
            }
            
            for case in test_cases:
                dataset_dict["question"].append(case["question"])
                dataset_dict["answer"].append(case["answer"])
                dataset_dict["contexts"].append(case["contexts"])
                dataset_dict["ground_truth"].append(case["ground_truth"])
            
            dataset = Dataset.from_dict(dataset_dict)
            
            # Run evaluation
            logger.info(f"Evaluating {len(test_cases)} test cases...")
            results = evaluate(dataset, metrics=self.metrics)
            
            # Extract scores
            scores = {
                "context_precision": results["context_precision"],
                "context_recall": results["context_recall"],
                "faithfulness": results["faithfulness"],
                "answer_relevancy": results["answer_relevancy"]
            }
            
            logger.info("Evaluation complete!")
            for metric, score in scores.items():
                logger.info(f"  {metric}: {score:.3f}")
            
            return scores
            
        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}")
            raise
