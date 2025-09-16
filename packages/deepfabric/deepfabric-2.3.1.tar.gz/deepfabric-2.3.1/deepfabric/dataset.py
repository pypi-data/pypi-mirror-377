import json
import re


class Dataset:
    """
    A class to represent a dataset consisting of samples, where each sample contains messages with specific roles.
    Methods:
        __init__():
            Initialize an empty dataset.
        from_jsonl(file_path: str) -> "Dataset":
            Create a Dataset instance from a JSONL file.
        from_list(sample_list: list[dict]) -> "Dataset":
            Create a Dataset instance from a list of samples.
        validate_sample(sample: dict) -> bool:
            Validate if a sample has the correct format.
        add_samples(samples: list[dict]) -> tuple[list[dict], list[str]]:
            Add multiple samples to the dataset and return any failures.
        remove_linebreaks_and_spaces(input_string: str) -> str:
            Clean up a string by removing extra whitespace and normalizing linebreaks.
        save(save_path: str):
            Save the dataset to a JSONL file.
        __len__() -> int:
            Get the number of samples in the dataset.
        __getitem__(idx: int) -> dict:
            Get a sample from the dataset by index.
        filter_by_role(role: str) -> list[dict]:
            Filter samples to only include messages with a specific role.
        get_statistics() -> dict:
            Calculate basic statistics about the dataset.
    """

    def __init__(self):
        """Initialize an empty dataset."""
        self.samples = []
        self.failed_samples = []

    @classmethod
    def from_jsonl(cls, file_path: str) -> "Dataset":
        """Create a Dataset instance from a JSONL file.

        Args:
            file_path: Path to the JSONL file containing the dataset.

        Returns:
            A new Dataset instance populated with the data from the file.
        """
        instance = cls()
        with open(file_path) as f:
            for line in f:
                sample = json.loads(line)
                if cls.validate_sample(sample):
                    instance.samples.append(sample)
                else:
                    instance.failed_samples.append(sample)

        return instance

    @classmethod
    def from_list(cls, sample_list: list[dict]) -> "Dataset":
        """Create a Dataset instance from a list of samples.

        Args:
            sample_list: List of dictionaries containing the samples.

        Returns:
            A new Dataset instance populated with the provided samples.
        """
        instance = cls()
        for sample in sample_list:
            if cls.validate_sample(sample):
                instance.samples.append(sample)
            else:
                instance.failed_samples.append(sample)

        return instance

    @staticmethod
    def validate_sample(sample: dict) -> bool:
        """Validate if a sample has the correct format.

        Args:
            sample: Dictionary containing the sample data.

        Returns:
            bool: True if the sample is valid, False otherwise.
        """
        if "messages" not in sample:
            return False

        for message in sample["messages"]:
            if "role" not in message or "content" not in message:
                return False
            if message["role"] not in ["user", "assistant", "system"]:
                return False

            # Validate that content is a string
            if not isinstance(message["content"], str):
                return False

        return True

    def add_samples(self, samples: list[dict]) -> tuple[list[dict], list[str]]:
        """Add multiple samples to the dataset and return any failures.

        Args:
            samples: List of dictionaries containing the samples to add.

        Returns:
            tuple: (list of failed samples, list of failure descriptions)
        """
        failed_samples = []
        failure_descriptions = []

        for sample in samples:
            if self.validate_sample(sample):
                self.samples.append(sample)
            else:
                failed_samples.append(sample)
                failure_descriptions.append(f"Invalid sample format: {sample}")
                self.failed_samples.append(sample)

        return failed_samples, failure_descriptions

    @staticmethod
    def remove_linebreaks_and_spaces(input_string: str) -> str:
        """Clean up a string by removing extra whitespace and normalizing linebreaks.

        Args:
            input_string: The string to clean up.

        Returns:
            str: The cleaned string.
        """
        # Remove line breaks
        no_linebreaks = re.sub(r"\s+", " ", input_string)
        # Remove extra spaces
        return " ".join(no_linebreaks.split())

    def save(self, save_path: str):
        """Save the dataset to a JSONL file.

        Args:
            save_path: Path where the JSONL file should be saved.
        """
        with open(save_path, "w") as f:
            for sample in self.samples:
                # Clean up the JSON string before writing
                clean_json = self.remove_linebreaks_and_spaces(json.dumps(sample))
                f.write(clean_json + "\n")

    def __len__(self) -> int:
        """Get the number of samples in the dataset.

        Returns:
            int: The number of samples in the dataset.
        """
        return len(self.samples)

    def __getitem__(self, idx: int) -> dict:
        """Get a sample from the dataset by index.

        Args:
            idx: Index of the sample to retrieve.

        Returns:
            Dict: The sample at the specified index.
        """
        return self.samples[idx]

    def filter_by_role(self, role: str) -> list[dict]:
        """Filter samples to only include messages with a specific role.

        Args:
            role: The role to filter by ('user', 'assistant', or 'system').

        Returns:
            List[Dict]: Filtered list of samples.
        """
        filtered_samples = []
        for sample in self.samples:
            filtered_messages = [msg for msg in sample["messages"] if msg["role"] == role]
            if filtered_messages:
                filtered_sample = sample.copy()
                filtered_sample["messages"] = filtered_messages
                filtered_samples.append(filtered_sample)
        return filtered_samples

    def get_statistics(self) -> dict:
        """Calculate basic statistics about the dataset.

        Returns:
            Dict: Statistics about the dataset including:
                - Total number of samples
                - Average messages per sample
                - Role distribution
                - Average content length
        """
        if not self.samples:
            return {"error": "Dataset is empty"}

        total_samples = len(self.samples)
        total_messages = sum(len(sample["messages"]) for sample in self.samples)
        role_counts = {"user": 0, "assistant": 0, "system": 0}
        total_content_length = 0
        message_count = 0

        for sample in self.samples:
            for message in sample["messages"]:
                role_counts[message["role"]] += 1
                total_content_length += len(message["content"])
                message_count += 1

        return {
            "total_samples": total_samples,
            "avg_messages_per_sample": total_messages / total_samples,
            "role_distribution": {
                role: count / message_count for role, count in role_counts.items()
            },
            "avg_content_length": total_content_length / message_count,
        }
