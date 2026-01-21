"""
Sample test dataset for RAG evaluation.

Add your own test cases based on your ingested documents.
"""

TEST_CASES = [
    {
        "question": "What is the main topic of the document?",
        "ground_truth": "The main topic is...",  # Update with actual ground truth
        "ground_truth_contexts": [
            "Context from the document that answers this question..."
        ]
    },
    # Add more test cases here
]


def get_test_dataset():
    """Return the test dataset."""
    return TEST_CASES
